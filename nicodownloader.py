import os
import sys
import time
import urllib
from tqdm import tqdm, trange
import requests
from time import sleep
from bs4 import BeautifulSoup
from mimetypes import guess_extension
import unicodedata
from libraries.downloadmanager import downloader
from libraries.downloadmanager.item import Item

def downloadVideo(sess, url, title):
    response = sess.get(url, stream=True)
    total_length = int(response.headers.get('Content-Length', 0))
    
    contentType = response.headers.get('Content-Type')
    extension = guess_extension(contentType)
    if extension is None:
        extensionCandidates = contentType.split("/")
        if len(extensionCandidates) > 1:
            extension = "." + extensionCandidates[1]
        else:
            extension = ""

    fileName = title + extension
    filePath = os.path.join(outputPath, fileName)

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    with open(filePath, "wb") as handle:
        pbar = tqdm(total = total_length)
        for data in response.iter_content(chunk_size=1024):
            handle.write(data)
            pbar.update(len(data))
        # for data in tqdm(response.iter_content(chunk_size=1024), total=total_length):
        #     handle.write(data)

def login(sess, nicoId, nicoPw):
    loginUrl = "https://secure.nicovideo.jp/secure/login?site=niconico&mail=%s&password=%s" % (nicoId, nicoPw)
    response = sess.post(loginUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    return len(soup.select("div.notice.error")) <= 0

def getVideoIds(sess, mode, args):
    videoIdTitlePairs = [(None, arg) for arg in args]

    if mode == "m":
        mylistId = args[0]
        sliceRange = args[1].split(':')

        mylistUrl = "http://www.nicovideo.jp/mylist/%s?rss=2.0" % mylistId
        response = sess.get(mylistUrl)
        soup = BeautifulSoup(response.text, 'html.parser')

        videoIdTitlePairs = [(item.find("link").get_text().split("/")[-1], item.find("title").get_text()) for item in soup.find_all("item")]
        videoIdTitlePairs = sliceWithRange(videoIdTitlePairs, sliceRange)
    return videoIdTitlePairs

def sliceWithRange(arr, sliceRange):
    reverse = True if len(sliceRange) >= 3 and sliceRange[2] == '-1' else False

    sliceFrom = int(sliceRange[0])
    sliceCount = int(sliceRange[1])
    sliceTo = sliceFrom + sliceCount
    stride = 1
    if reverse:
        endIdx = len(arr) - 1
        sliceFrom = endIdx - sliceFrom
        sliceTo = endIdx - sliceTo
        stride = -1
    return arr[sliceFrom:sliceTo:stride]

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print "Usage:"
        print "With video ids: python filename email pw outputPath v videoId [videoIds]"
        print "With mylist ids: python filename email pw outputPath m mylistId [startIdx:count[:sort(-1 for reversed order)]]"
        sys.exit()
        
    nicoId = sys.argv[1]
    nicoPw = sys.argv[2]
    outputPath = sys.argv[3]
    mode = sys.argv[4]
    args = sys.argv[5:]

    with requests.session() as sess:
        if login(sess, nicoId, nicoPw):
            videoIdTitlePairs = getVideoIds(sess, mode, args)

            videoPageUrls = ["http://www.nicovideo.jp/watch/%s?watch_harmful=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
            videoApiUrls = ["http://flapi.nicovideo.jp/api/getflv/%s?as3=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
            
            itemsArr = []

            for i in range(len(videoIdTitlePairs)):
                # Load video page is mandatory for downloading video
                sess.get(videoPageUrls[i])
                
                apiResult = sess.get(videoApiUrls[i]).text
                apiResultDict = dict([(pair.split("=")) for pair in apiResult.split("&")])
                videoUrl = urllib.unquote(apiResultDict['url']).decode('utf8')
                itemsArr.append(Item(videoUrl, title = videoIdTitlePairs[i][1]))

                print "Retrieved item at %d. Pull back for awhile..." % i
                time.sleep(3)
                
                # downloadVideo(sess, videoUrl, title)

            def beforeRequest(idx):
                sess.get(videoPageUrls[idx])
            downloader.batchDownload(itemsArr, outputPath, sess = sess, beforeRequest = beforeRequest)
