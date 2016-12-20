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

# for it in trange(3):
#     for jt in trange(100):
#         sleep(0.01)

def downloadVideo(sess, url, title):
    response = sess.get(url, stream=True)
    total_length = int(response.headers.get('Content-Length', 0))
    
    extension = guess_extension(response.headers.get('Content-Type'))
    fileName = title + extension
    
    with open(fileName, "wb") as handle:
        for data in tqdm(response.iter_content(), total=total_length):
            handle.write(data)
            
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
            