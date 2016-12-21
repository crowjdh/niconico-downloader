import os
import sys
import urllib
from tqdm import tqdm, trange
import requests
from time import sleep
from bs4 import BeautifulSoup
from mimetypes import guess_extension
import unicodedata

if len(sys.argv) < 6:
    print "Usage:"
    print "With video ids: python filename email pw outputPath v videoId [videoIds]"
    print "With mylist ids: python filename email pw outputPath m mylistId"
    sys.exit()
nicoId = sys.argv[1]
nicoPw = sys.argv[2]
outputPath = sys.argv[3]
mode = sys.argv[4]
args = sys.argv[5:]

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
        mylistUrl = "http://www.nicovideo.jp/mylist/%s?rss=2.0" % mylistId
        response = sess.get(mylistUrl)
        soup = BeautifulSoup(response.text, 'html.parser')

        videoIdTitlePairs = [(item.find("link").get_text().split("/")[-1], item.find("title").get_text()) for item in soup.find_all("item")]
    return videoIdTitlePairs

with requests.session() as sess:
    if login(sess, nicoId, nicoPw):
        videoIdTitlePairs = getVideoIds(sess, mode, args)

        videoPageUrls = ["http://www.nicovideo.jp/watch/%s?watch_harmful=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
        videoApiUrls = ["http://flapi.nicovideo.jp/api/getflv/%s?as3=1" % videoIdTitlePair[0] for videoIdTitlePair in videoIdTitlePairs]
        
        for i in trange(len(videoIdTitlePairs)):
            # Load video page is mandatory for downloading video
            response = sess.get(videoPageUrls[i])
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.select("span.videoHeaderTitle")[0].get_text()
            
            apiResult = sess.get(videoApiUrls[i]).text
            apiResultDict = dict([(pair.split("=")) for pair in apiResult.split("&")])
            videoUrl = urllib.unquote(apiResultDict['url']).decode('utf8')
            
            downloadVideo(sess, videoUrl, title)
            