#!/bin/python3

from pyquery import PyQuery as pq
import os, argparse, re, json, fcntl, termios, struct, requests

def lead0(num, max):
    return str(num).zfill(len(str(max)))

def terminal_size():
    try:
        th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
    except IOError:
        th, tw = 80, 200
    return tw, th

def printLine(msg='', noNewLine=False):
    terminalWidth = terminal_size()[0]
    spaces = terminalWidth - len(msg)

    if noNewLine:
        print(msg + (' ' * spaces), end='\r')
    else:
        print(msg + (' ' * spaces))

# parse input and settup help
parser = argparse.ArgumentParser(description='Downloads Comics from \'https://tapas.io\'.', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('url', metavar='URL/name', type=str, nargs='+',
                    help='URL or URL name to comic\nGo to the comic you want to download (any page)\nRightclick on the comic name in the upper left corner and select "Copy linkaddress" (Or similar) or just use the name behind series in the url\nExamples: https://tapas.io/series/Erma, RavenWolf, ...')

args = parser.parse_args()

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

    # Extract pages data and name from JS object
    page = pq(pageReqest.text)
    dataStr = page('body > script:nth-child(23)').html().replace('\n', '') # TODO: Improve selector
    data = json.loads(dataStr[dataStr.index('episodeList : ') + 14:dataStr.index('isSeriesView :') - 9])
    name = dataStr[dataStr.index('seriesTitle : \'') + 15:dataStr.index('\',', dataStr.index('seriesTitle : \'') + 15)]

    printLine('{} [{}] ({} pages):'.format(name, urlName, len(data)))

    # Check if folder exsists, if not create it
    printLine('Checking folder...', True)
    if not os.path.isdir(name + ' [' + urlName + ']'):
        os.mkdir(name + ' [' + urlName + ']')
        printLine('Creating folder...', True)

    # Download header
    printLine('Downloading header...', True)

    customCssStr = page('head > style').html()
    headerSrc = re.search('url\(".+"\)', customCssStr).group(0)[5:-2]
    with open(os.path.join(name + ' [' + urlName + ']', '-1 - header.{}'.format(headerSrc[headerSrc.rindex('.') + 1:])), 'wb') as f:
        f.write(requests.get(headerSrc).content)

    printLine('Downloaded header')

    # Get images from page from JS api
    allImgCount = 0
    for pageCount, pageData in enumerate(data):
        printLine('Downloaded imageData from {} images (pages {}/{})...'.format(allImgCount, pageCount, len(data)), True)

        pageJson = requests.get('https://tapas.io/episode/view/' + str(pageData['id']), headers={'user-agent': 'tapas-dl'}).json()
        pageHtml = pq(pageJson['data']['html'])

        pageData['imgs'] = []
        for img in pageHtml('img.art-image'):
            pageData['imgs'].append(pq(img).attr('src'))

            allImgCount += 1

    # Download images
    imgCount = 0
    for pageCount, pageData in enumerate(data):
        for imgOfPageCount, img in enumerate(pageData['imgs']):
            with open(os.path.join(name + ' [' + urlName + ']', '{} - {} - {} - {} - #{}.{}'.format(lead0(imgCount, allImgCount), lead0(pageCount, len(pageData)),
                                                                                                    lead0(imgOfPageCount, len(pageData['imgs'])), pageData['title'],
                                                                                                    pageData['id'], img[img.rindex('.') + 1:])), 'wb') as f:
                f.write(requests.get(img).content)

            imgCount += 1

            printLine('Downloaded image {}/{} from pages {}/{} ({}/{} images)...'.format(imgOfPageCount + 1, len(pageData['imgs']), pageCount, len(data), imgCount, allImgCount), True)

    printLine('Downloaded {} images'.format(allImgCount))

    if urlCount + 1 != len(args.url):
        printLine()
