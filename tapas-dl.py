#!/bin/env python3
from pyquery import PyQuery as pq
from pathlib import Path
import os
import argparse
import re
import requests


def lead0(num, max):
    return str(num).zfill(len(str(max)))


def terminal_size():
    try:
        import fcntl
        import termios
        import struct

        th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
    except (IOError, ModuleNotFoundError):
        th, tw = 80, 200
    return tw, th


def printLine(msg='', noNewLine=False):
    terminalWidth = terminal_size()[0]
    spaces = terminalWidth - len(msg)

    if noNewLine:
        if args.verbose:
            print(' ' + msg + (' ' * (spaces - 1)))
        else:
            print(msg + (' ' * spaces), end='\r')
    else:
        print(msg + (' ' * spaces))


def check_path(path, slash=True, fat=False):
    evil_chars = []
    if slash:
        evil_chars.append('/')
    if fat:
        evil_chars += ['?', '<', '>', '\\', ':', '*', '|', '"', '^']
    return ''.join([char for char in path if char not in evil_chars])


# parse input and settup help
parser = argparse.ArgumentParser(description='Downloads Comics from \'https://tapas.io\'.\nIf folder of downloaded comic is found, it will only update (can be disabled with -f/--force).', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('url', metavar='URL/name', type=str, nargs='+',
                    help='URL or URL name to comic\nGo to the comic you want to download (any page)\nRightclick on the comic name in the upper left corner and select "Copy linkaddress" (Or similar) or just use the name behind series in the url\nExamples: https://tapas.io/series/Erma, RavenWolf, ...')
parser.add_argument('-f', '--force', action="store_true", help='Disables updater.')
parser.add_argument('-v', '--verbose', action="store_true", help='Enables verbose mode.')
parser.add_argument('-c', '--restrict-characters', action="store_true", help='Removes \'? < > \\ : * | " ^\' from file names')
parser.add_argument('-o', type=str, nargs='?', default="", dest='baseDir', metavar='C:\\',
                    help='Output directory where comics should be placed.\nIf left blank, the script folder will be used.')

args = parser.parse_args()

basePath = ""
if (args.baseDir):
    basePath = Path(args.baseDir)

for urlCount, url in enumerate(args.url):
    # check url/name
    if re.match(r'^https://tapas\.io/series/.+$', url):
        urlName = url[url.rindex('/') + 1:]
    else:
        urlName = url

    printLine('Loading ' + urlName + '...', True)

    # Get comic start page and test if comic exsists
    pageReqest = requests.get('https://tapas.io/series/' + urlName, headers={'user-agent': 'tapas-dl'})

    if pageReqest.status_code != 200:
        printLine('Error: Comic "{}" not found\n'.format(urlName))
        break

    page = pq(pageReqest.text)

    try:
        page_count = int(page('.paging .paging__button.paging__button--num.g-act')[-1].text)
    except IndexError:
        page_count = 1

    name = page('.desc__title').text()

    data = []
    for i in range(page_count):
        page = pq(url=f'https://tapas.io/series/{urlName}?pageNumber={i + 1}&sort_order=asc', headers={'user-agent': 'tapas-dl'})
        for episode in page('.content a[href*="/episode/"]'):
            data.append({'id': int(episode.attrib['href'][episode.attrib['href'].rfind('/') + 1:])})

        printLine(f'Crawling {i+1}/{page_count}...', True)

    printLine('{} [{}] ({} pages):'.format(name, urlName, len(data)))

    # Check if folder exsists, if not create it
    printLine('Checking folder...', True)
    # If the user specified a base output directory, prepend that on our folder
    savePath = '{} [{}]'.format(name, urlName)
    if (basePath != ""):
        savePath = basePath / savePath
        printLine('Full path is: ' + str(savePath))
    if os.path.isdir(savePath) and not args.force:
        printLine('Found directory, only updating (use -f/--force to disable)')

        filesInDir = list(os.scandir(savePath))

        fileNames = []
        for fileInDir in filesInDir:
            fileNames.append(fileInDir.name)
        fileNames.sort()

        imgOffset = len(fileNames)

        if imgOffset > 1:
            lastFile = fileNames[-1]
            lastPageId = int(lastFile[lastFile.rindex('#') + 1:lastFile.rindex('.')])

            pageOffset = next(i for i, page in enumerate(data) if page['id'] == lastPageId) + 1

            data = data[pageOffset:]
        else:
            pageOffset = 0
    else:
        if not os.path.isdir(savePath):
            os.mkdir(savePath)
            printLine('Creating folder...', True)

        # Download header
        printLine('Downloading header...', True)

        if len(page('.header__thumb img')) > 0:
            headerSrc = page('.header__thumb img').attr('src')
        else:
            headerSrc = None

        if headerSrc is not None:
            with open(os.path.join(savePath, '-1 - header.{}'.format(headerSrc[headerSrc.rindex('.') + 1:])), 'wb') as f:
                f.write(requests.get(headerSrc).content)

            printLine('Downloaded header')
        else:
            printLine('Header not found')

        pageOffset = 0
        imgOffset = 0

    # Check if series is comic or novel
    if len(pq(f'https://tapas.io/episode/{data[0]["id"]}', headers={'user-agent': 'tapas-dl'})('.ep-epub-contents')) > 0:
        printLine('Detected comic')
        # Get images from page from JS api
        allImgCount = 0
        for pageCount, pageData in enumerate(data):
            printLine('Downloaded image data from {} images (pages {}/{})...'.format(allImgCount, pageCount + pageOffset, len(data) + pageOffset), True)

            pageHtml = pq(f'https://tapas.io/episode/{pageData["id"]}', headers={'user-agent': 'tapas-dl'})

            pageData['title'] = pageHtml('.info__title').text()

            pageData['imgs'] = []
            for img in pageHtml('.content__img'):
                pageData['imgs'].append(pq(img).attr('data-src'))

                allImgCount += 1

        # Download images
        imgCount = 0
        for pageCount, pageData in enumerate(data):
            for imgOfPageCount, img in enumerate(pageData['imgs']):
                with open(os.path.join(savePath, check_path('{} - {} - {} - {} - #{}.{}'.format(lead0(imgCount + imgOffset, allImgCount + imgOffset), lead0(pageCount + pageOffset, len(pageData) + pageOffset),
                                                                                                                       lead0(imgOfPageCount, len(pageData['imgs'])), pageData['title'],
                                                                                                                       pageData['id'], img[img.rindex('.') + 1:]), fat=args.restrict_characters)), 'wb') as f:
                    f.write(requests.get(img).content)

                imgCount += 1

                printLine('Downloaded image {}/{} from page {}/{} ({}/{} images)...'.format(imgOfPageCount + 1, len(pageData['imgs']), pageCount + pageOffset, len(data) + pageOffset, imgCount + imgOffset, allImgCount + imgOffset), True)

        if data != []:
            printLine('Downloaded {} images'.format(allImgCount))
        else:
            printLine('Nothing to do')

        if urlCount + 1 != len(args.url):
            printLine()
    else:
        printLine('Detected novel')

        from ebooklib import epub

        # download/create epub
        book = epub.EpubBook()

        customCss = None

        # Add meta data
        book.set_identifier(urlName)
        book.set_title(page('.series-header-title').text())
        book.set_language('en')

        book.add_author(page('.tag__author').text())

        header_name = os.path.join(savePath, list(filter(re.compile(r'.+header\..+').match, os.listdir(savePath)))[0])
        book.set_cover("cover.jpg", open(header_name, 'rb').read())

        book.toc = []
        book.spine = ['cover']

        # create about page
        chapter = epub.EpubHtml(title='about', file_name='about.xhtml')
        chapter.content = f'<h1>About</h1><p>Title: {name}</p><p>Author: {book.metadata["http://purl.org/dc/elements/1.1/"]["creator"][0][0]}</p><p>Source: <a href="{"https://tapas.io/series/" + urlName}">{"https://tapas.io/series/" + urlName}</a></p>'

        book.add_item(chapter)
        book.spine.append(chapter)

        # Append nav page
        book.spine.append('nav')

        # create chapters
        for pageCount, pageData in enumerate(data):
            printLine('Downloaded page {}/{}...'.format(pageCount, len(data)), True)

            pagePq = pq(url='https://tapas.io/episode/' + str(pageData['id']), headers={'user-agent': 'tapas-dl'})
            pageTitle = pagePq('.main__title').text()

            pageHtml = f'<h1>{pageTitle}</h1>'
            for p in pagePq('article.main__body > p'):
                p = pq(p)
                if p.text() is not None:
                    pageHtml += '<p>' + p.text() + '</p>'

            chapter = epub.EpubHtml(title=pageTitle, file_name=str(pageData['id']) + '.xhtml')
            chapter.content = pageHtml

            book.add_item(chapter)

            # define Table Of Contents
            book.toc.append(epub.Link(str(pageData['id']) + '.xhtml', pageTitle, str(pageData['id'])))

            # basic spine
            book.spine.append(chapter)

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # add CSS
        style = ''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # write to the file
        epub.write_epub(os.path.join(savePath, name, '.epub'), book)

        # remove tmp folder
        for file in os.listdir(savePath):
            os.remove(os.path.join(savePath, file))
        os.removedirs(savePath)
