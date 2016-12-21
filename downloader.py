import os
import sys
import urllib
from tqdm import tqdm, trange
import requests
from time import sleep
from bs4 import BeautifulSoup
from mimetypes import guess_extension

if len(sys.argv) < 5:
    print "Usage:"
    print "With video ids: python filename email pw v videoId [videoIds]"
    print "With mylist ids: python filename email pw m mylistId"
    sys.exit()
nicoId = sys.argv[1]
nicoPw = sys.argv[2]
mode = sys.argv[3]
args = sys.argv[4:]
# videoIds = sys.argv[4:]

def downloadVideo(sess, url, title):
    # if True:
    #     import time
    #     start = time.time()*1000.0
    #     print len(sess.get(url).content)
    #     end = time.time()*1000.0
    #     print "Time taken: %s" % str(end - start)
    #     return

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
    directoryName = "output"
    filePath = os.path.join(directoryName, fileName)

    if not os.path.exists(directoryName):
        os.makedirs(directoryName)

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

def getVideoIds(sess, mylistId):
    videoIds = args

    if mode == "m":
        mylistUrl = "http://www.nicovideo.jp/mylist/%s" % mylistId
        response = sess.get(mylistUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        print len(soup.find_all("a", class_="watch"))
    return videoIds

with requests.session() as sess:
    if login(sess, nicoId, nicoPw):
        videoIds = getVideoIds(sess, mode, args)
        exit()

        videoPageUrls = ["http://www.nicovideo.jp/watch/%s?watch_harmful=1" % videoId for videoId in videoIds]
        videoApiUrls = ["http://flapi.nicovideo.jp/api/getflv/%s?as3=1" % videoId for videoId in videoIds]
        
        for i in trange(len(videoIds)):
            # Load video page is mandatory for downloading video
            response = sess.get(videoPageUrls[i])
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.select("span.videoHeaderTitle")[0].get_text()
            
            apiResult = sess.get(videoApiUrls[i]).text
            apiResultDict = dict([(pair.split("=")) for pair in apiResult.split("&")])
            videoUrl = urllib.unquote(apiResultDict['url']).decode('utf8')
            
            downloadVideo(sess, videoUrl, title)
            
            # print sess.head(videoUrl).headers
            