from seleniumwire import webdriver 
from seleniumwire.utils import decode
import re
import json
import time
from selenium.webdriver.chrome.options import Options

def scrape_tweet_and_get_latest_response(url):


    firefox_options = webdriver.FirefoxOptions()
    firefox_options.binary_location = "/Users/vdaninwork/Projects/soc_vid_bot/modules/geckodriver"

    driver = webdriver.Chrome()
    
    # driver.get('https://twitter.com/jffkey/status/1652037315890388996')


    driver.get("https://vstwitter.com/GirkinGirkin/status/1653267315847311360?s=20")
    time.sleep(3)

    byte_body = None;
    for r in driver.requests:
        if 'TweetDetail?variables' in r.url:
            print(r.path)
            byte_body = decode(r.response.body, r.response.headers.get('Content-Encoding', 'identity'))
            break

    string_body = str(byte_body)

    string_body =  string_body.replace("b'", "")[:-1]
    mah_new_body = re.sub('\\\\\\\\\"', '\\\"', string_body)
    return retrieve_highest_res_video(mah_new_body)

def retrieve_highest_res_video(string_body):
    # Regex pattern
    pattern = r'"url":"https:\/\/video\.twimg\.com\/(?:ext_tw_video|amplify_video)\/(\d+)\/(?:pu\/vid|vid)\/(\d+x\d+)\/[^"]+"'

    matches = re.finditer(pattern, string_body)

    # Store information in a dictionary (resolution as key, link as value)
    video_info = {}
    iter = 0
    #store matches with main_post and answers.
    for match in matches:
        iter = iter + 1

        unique_id = match.group(1)

        if iter == 1:
            unique_id = "main_post"

        resolution = match.group(2)
        link = match.group(0)[7:-1]

        if unique_id not in video_info:
            video_info[unique_id] = []

        video_info[unique_id].append((resolution, link))

    #sort by highest to lowest reso
    for unique_id in video_info:
        video_info[unique_id].sort(key=lambda x: (int(x[0].split("x")[0]), int(x[0].split("x")[1])), reverse=True)
    ids = list(video_info.keys())

    main_post = video_info.get("main_post")
    #return highest resolution object

    return main_post[0][1]

if __name__ == "__main__":
    scrape_tweet_and_get_latest_response(url="")