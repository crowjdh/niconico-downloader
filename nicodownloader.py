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

# TODO: Handle when id/pw is incorrect
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

        videoIdTitleTuples = [(item.find("link").get_text().split("/")[-1], item.find("title").get_text(), item.find("pubdate").get_text()) for item in soup.find_all("item")]
        if args.sort:
            videoIdTitleTuples.sort(key=lambda tuple: dateparser.parse(tuple[2]))

        videoIdTitlePairs = [(element[0], element[1]) for element in videoIdTitleTuples]
        videoIdTitlePairs = sliceWithRange(videoIdTitlePairs, args.range)
    else:
        videoIdTitlePairs = [(None, arg) for arg in args.videoId]
    return videoIdTitlePairs

def sliceWithRange(arr, sliceRange):
    sliceFrom = int(sliceRange[0])
    sliceCount = int(sliceRange[1])
    sliceTo = sliceFrom + sliceCount
    stride = 1
    return arr[sliceFrom:sliceTo:stride]

def reprint(msg):
    global longestLengthReprinted
    msgLength = len(msg)
    if 'longestLengthReprinted' not in globals():
        longestLengthReprinted = 0
    if msgLength < longestLengthReprinted:
        msg += ' ' * (longestLengthReprinted - msgLength)
    longestLengthReprinted = msgLength
    print msg,
    sys.stdout.flush()
    print "\r",

if __name__ == "__main__":
    args = nicoargparser.parse()

    with requests.session() as sess:
        if login(sess, args.email, args.password):
            videoIdTitlePairs = getVideoIds(sess, args)

            videoPageUrls = ["http://www.nicovideo.jp/watch/%s?watch_harmful=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
            videoApiUrls = ["http://flapi.nicovideo.jp/api/getflv/%s?as3=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
            
            itemsArr = []

            itemCnt = len(videoIdTitlePairs)
            for i in range(itemCnt):
                itemProgressMsg = "{0}/{1}".format(i + 1, itemCnt)
                reprint("Retrieving item {0}".format(itemProgressMsg))

                # Load video page is mandatory for downloading video
                sess.get(videoPageUrls[i])
                
                apiResult = sess.get(videoApiUrls[i]).text
                apiResultDict = dict([(pair.split("=")) for pair in apiResult.split("&")])
                videoUrl = urllib.unquote(apiResultDict['url']).decode('utf8')
                itemsArr.append(Item(videoUrl, title = videoIdTitlePairs[i][1]))

                pullbackInSec = 3
                for pullbackLeft in range(pullbackInSec, 0, -1):
                    reprint("Retrieved item {0}. Pull back left: {1}".format(itemProgressMsg, pullbackLeft))
                    time.sleep(1)

            def beforeRequest(idx):
                sess.get(videoPageUrls[idx])
            
            downloader.batchDownload(itemsArr, args.outputPath, sess = sess, beforeRequest = beforeRequest, processes = args.processes)
