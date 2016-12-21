import os
import sys
import urllib
from tqdm import tqdm, trange
import requests
from time import sleep
from bs4 import BeautifulSoup
from mimetypes import guess_extension

if len(sys.argv) < 4:
    print "Usage: python filename email pw videoId [videoIds]"
    sys.exit()
nicoId = sys.argv[1]
nicoPw = sys.argv[2]
videoIds = sys.argv[3:]

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
            
with requests.session() as sess:
    loginUrl = "https://secure.nicovideo.jp/secure/login?site=niconico&mail=%s&password=%s" % (nicoId, nicoPw)
    response = sess.post(loginUrl)
    soup = BeautifulSoup(response.text, 'html.parser')
    loginSuccessful = len(soup.select("div.notice.error")) <= 0
    if loginSuccessful:
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
            