#!/usr/bin/python3
from pyquery import PyQuery as pq
import os
import argparse
import re
import json
import struct
import requests


def lead0(num, max):
    return str(num).zfill(len(str(max)))

def printLine(msg='', noNewLine=False):
    terminalWidth = 80
    spaces = terminalWidth - len(msg)

    if noNewLine:
        if args.verbose:
            print(' ' + msg + (' ' * (spaces - 1)))
        else:
            print(msg + (' ' * spaces), end='\r')
    else:
        print(msg + (' ' * spaces))


# parse input and settup help
parser = argparse.ArgumentParser(description='Downloads Comics from \'https://tapas.io\'.\nIf folder of downloaded comic is found, it will only update (can be disabled with -f/--force).', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('url', metavar='URL/name', type=str, nargs='+',
                    help='URL or URL name to comic\nGo to the comic you want to download (any page)\nRightclick on the comic name in the upper left corner and select "Copy linkaddress" (Or similar) or just use the name behind series in the url\nExamples: https://tapas.io/series/Erma, RavenWolf, ...')
parser.add_argument('-f', '--force', action="store_true", help='Disables updater.')
parser.add_argument('-v', '--verbose', action="store_true", help='Enables verbose mode.')

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
    dataStr = [dataStr for dataStr in page('script') if dataStr.text is not None and dataStr.text.find('var _data = {') != -1][0].text.replace('\n', '')
    data = json.loads(dataStr[dataStr.index('episodeList : ') + 14:dataStr.index('isSeriesView :') - 9])
    name = dataStr[dataStr.index('seriesTitle : \'') + 15:dataStr.index('\',', dataStr.index('seriesTitle : \'') + 15)]

    printLine('{} [{}] ({} pages):'.format(name, urlName, len(data)))

    # Check if folder exsists, if not create it
    printLine('Checking folder...', True)
    dirname = '{} [{}]'.format(name, urlName)
    dirname = "".join(x for x in dirname if (x.isalnum() or x in "._- []"))

    if not os.path.isdir(dirname):
        os.mkdir(dirname)
        printLine('Creating folder...', True)

    pageOffset = 0
    imgOffset = 0

    # Get images from page from JS api
    allImgCount = 0
    for pageCount, pageData in enumerate(data):
        printLine('Downloaded imageData from {} images (pages {}/{})...'.format(allImgCount, pageCount + pageOffset, len(data) + pageOffset), True)

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
            filename = '{} - {} - {} - {} - #{}.{}'.format(lead0(imgCount + imgOffset, allImgCount + imgOffset), lead0(pageCount + pageOffset, len(pageData) + pageOffset), lead0(imgOfPageCount, len(pageData['imgs'])), pageData['title'], pageData['id'], img[img.rindex('.') + 1:])
            filename = "".join(x for x in filename if (x.isalnum() or x in "._- "))
            with open(os.path.join(dirname, filename), 'wb') as f:
                r = requests.get(img)
                f.write(r.content)

            imgCount += 1

            printLine('Downloaded image {}/{} from page {}/{} ({}/{} images)...'.format(imgOfPageCount + 1, len(pageData['imgs']), pageCount + pageOffset, len(data) + pageOffset, imgCount + imgOffset, allImgCount + imgOffset), True)

    if data != []:
        printLine('Downloaded {} images'.format(allImgCount))
    else:
        printLine('Nothing to do')

    if urlCount + 1 != len(args.url):
        printLine()
