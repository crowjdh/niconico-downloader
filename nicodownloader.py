import os
import sys
import time
import urllib
import requests
from time import sleep
from bs4 import BeautifulSoup
from mimetypes import guess_extension
import unicodedata
from dateutil import parser as dateparser
import nicoargparser
from libraries.downloadmanager import downloader
from libraries.downloadmanager.item import Item

encoding = 'UTF-8'
FORMAT_URL_VIDEO_PAGE = "http://www.nicovideo.jp/watch/{0}?watch_harmful=1"
FORMAT_URL_API_GETFLV = "http://flapi.nicovideo.jp/api/getflv/{0}?as3=1"

def login(sess, nicoId, nicoPw):
    loginUrl = "https://secure.nicovideo.jp/secure/login?site=niconico&mail=%s&password=%s" % (nicoId, nicoPw)
    response = sess.post(loginUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    return len(soup.select("div.notice.error")) <= 0

def getVideoIds(sess, args):
    if args.mode == "m":
        mylistUrl = "http://www.nicovideo.jp/mylist/%s?rss=2.0" % args.mylistId
        response = sess.get(mylistUrl)
        soup = BeautifulSoup(response.text, 'html.parser')

        videoIdTitleTuples = [(item.find("link").get_text().split("/")[-1], item.find("title").get_text().encode(encoding), item.find("pubdate").get_text())
        				for item in soup.find_all("item")]
        if args.sort:
            videoIdTitleTuples.sort(key=lambda tuple: dateparser.parse(tuple[2]))

        videoIdTitlePairs = [(element[0], element[1]) for element in videoIdTitleTuples]
        videoIdTitlePairs = sliceWithRange(videoIdTitlePairs, args.range)
    else:
        videoIdTitlePairs = [(arg, None) for arg in args.videoId]
    return videoIdTitlePairs

def sliceWithRange(arr, sliceRange):
    if sliceRange is None:
        return arr
    sliceFrom = int(sliceRange[0])
    sliceCount = int(sliceRange[1])
    sliceTo = sliceFrom + sliceCount
    stride = 1
    return arr[sliceFrom:sliceTo:stride]

def overprint(msg, addNewLine = False):
    global longestLengthReprinted
    msgLength = len(msg)
    if 'longestLengthReprinted' not in globals():
        longestLengthReprinted = 0
    if msgLength < longestLengthReprinted:
        msg += ' ' * (longestLengthReprinted - msgLength)
    longestLengthReprinted = msgLength
    print msg,
    sys.stdout.flush()
    if not addNewLine:
        print "\r",
    else:
        print ""

def createDummyItems(count):
    items = []
    for i in range(count):
        items.append(Item("http://download.thinkbroadband.com/5MB.zip"))
        items.append(Item("http://download.thinkbroadband.com/10MB.zip"))
        items.append(Item("http://download.thinkbroadband.com/20MB.zip"))
    return items

def getItems(videoIdTitlePairs):
    videoPageUrls = [FORMAT_URL_VIDEO_PAGE.format(videoIdTitlePair[0]) for videoIdTitlePair in videoIdTitlePairs]
    videoApiUrls = [FORMAT_URL_API_GETFLV.format(videoIdTitlePair[0]) for videoIdTitlePair in videoIdTitlePairs]
    items = []

    itemCnt = len(videoIdTitlePairs)
    for i in range(itemCnt):
        itemProgressMsg = "{0}/{1}".format(i + 1, itemCnt)
        overprint("Retrieving item {0}".format(itemProgressMsg))

        # Load video page is mandatory for downloading video
        sess.get(videoPageUrls[i])
        
        apiResult = sess.get(videoApiUrls[i]).text
        apiResultDict = dict([(pair.split("=")) for pair in apiResult.split("&")])
        videoUrl = urllib.unquote(apiResultDict['url']).decode(encoding)
        items.append(Item(videoUrl, title = videoIdTitlePairs[i][1]))

        pullbackInSec = 3
        for pullbackLeft in range(pullbackInSec, 0, -1):
            overprint("Retrieved item {0}. Pull back left: {1}".format(itemProgressMsg, pullbackLeft))
            time.sleep(1)
    return items

if __name__ == "__main__":
    args = nicoargparser.parse()

    if args.debug:
        downloader.batchDownload(createDummyItems(14), args.outputPath, processes = args.processes)

    else:
        with requests.session() as sess:
            overprint("Logging in...")
            if login(sess, args.email, args.password):
                overprint("Logged in.", addNewLine = True)
                videoIdTitlePairs = getVideoIds(sess, args)
                items = getItems(videoIdTitlePairs)

                def beforeRequest(idx):
                    videoPageUrl = FORMAT_URL_VIDEO_PAGE.format(videoIdTitlePairs[idx][0])
                    sess.get(videoPageUrl)

                downloader.batchDownload(items, args.outputPath, sess = sess, beforeRequest = beforeRequest,
                	processes = args.processes, printEncoding = encoding)
            else:
                print "Login failed. Check your ID or password again."
