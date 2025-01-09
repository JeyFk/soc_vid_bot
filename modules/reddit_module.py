import subprocess
import logging
import json
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def download_and_get_reddit_post(url, logger) -> (str, str, str):
    logger.info("Opening %s", url)
    headers_for_reddit = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        "Cookie": '; token_v2=..; csv=2; edgebucket=XPc8KW9NCptMI78ItA; session=; session_tracker=bjmrgcpejeeemfiflq.0.1682612643323.Z0FBQUFBQmtTcUdqT2FGb1doT1Q3VnlTUXdXNmFEeTRWeUZoSFRxRGdWQV9NLWd5VGpFcGNkUGhGeXNDaFcyTXI2ZTBDSFBuelJ6aC0zbzhRVTVQU0FfZXliUnJjMk5zMGUtTUdBR2RMRDhJa1E4RUdBMUVJbWpXeVlrb2dNaF9zbmRVM1FKOFdKaVY; datadome=7iMYzMVdcbrnGMjeCcvQlLXeeSGAw0_~~ZGUJKPnbzPIxu5EI9N7D'
    }
    response = requests.get(url, headers=headers_for_reddit)
    post_id = url[url.find('comments/') + 9:]
    post_id = f"t3_{post_id[:post_id.find('/')]}"

    if (response.status_code == 200):  # checking if the server responded with OK
        soup = BeautifulSoup(response.text, 'lxml')
        print(soup.text)
        #placeholder to fix cookie
        required_js = soup.find('script', id='data')

        if(required_js == None): return


        json_data = json.loads(
            required_js.text.replace('window.___r = ', '')[:-1])
        # 'window.___r = ' and a semicolon at the end of the text were removed
        # to get the data as json
        title = json_data['posts']['models'][post_id]['title']
        title = title.replace(' ', '_')
        mpd = json_data['posts']['models'][post_id]['media']['dashUrl']
        height = json_data['posts']['models'][post_id]['media']['height']
        width = json_data['posts']['models'][post_id]['media']['width']
        dash_url = mpd[:int(mpd.find('DASH')) + 4]
        # the dash URL is the main URL we need to search for
        # height is used to find the best quality of video available

        # this URL will be used to download the video
        video_url = f'{dash_url}_{height}.mp4'
        # this URL will be used to download the audio part
        audio_url = f'{dash_url}_audio.mp4'
        try:
            logger.info('\rgetting response for MPD url %s', mpd)
            response = requests.get(mpd, headers=headers_for_reddit)
            if response.status_code == 200:
                video_url, audio_url = scrape_video_from_mpd(response.content)

                video_url = f'{dash_url}_{video_url}'
                audio_url = f'{dash_url}_{audio_url}'

                logger.info("video url is %s", video_url)
                logger.info("audio urls is %s", audio_url)
            else:
                logger.info('\rUnable to get response of MPD for %s', post_id)
        except Exception as e:
            logger.error(e)
            return
        with open(f'{post_id}_video.mp4', 'wb') as file:
            logger.info('\rVideo {%s} downloading!', post_id)
            response = requests.get(video_url, headers=headers_for_reddit)
            if response.status_code == 200:
                file.write(response.content)
                logger.info('\rVideo {%s} downloaded!', post_id)
            else:
                logger.info('\rVideo {%s} Download Failed..!', post_id)

            logger.info(" our audio url is %s", audio_url)
            #move logger
            if "audio.mp3" in audio_url or "audio.mp4" in audio_url:
                 with open(f'{post_id}_audio.mp3', 'wb') as file:
                    logger.info('Downloading Audio {%s}', post_id)
                    response = requests.get(
                        audio_url, headers=headers_for_reddit)
                    if response.status_code == 200:
                        file.write(response.content)
                        logger.info('\rAudio {%s} downloaded!', post_id)
                    else:
                        logger.info('\rAudio {%s} Download Failed..!', post_id)
                    subprocess.call(
                    ['ffmpeg', '-i', f'{post_id}_video.mp4', '-i', f'{post_id}_audio.mp3', '-c:v', 'libx264', '-preset',
                    'medium', '-b:v', '1000k', '-vf', 'scale=iw:-2', '-c:a', 'aac', '-b:a', '128k',
                    f'temp/{post_id}_h264.mp4'])
                   
            else:
                 subprocess.call(
                        ['ffmpeg', '-i', f'{post_id}_video.mp4', '-c:v', 'libx264', '-preset',
                        'medium', '-b:v', '1000k', '-vf', 'scale=iw:-2', '-c:a', 'aac', '-b:a', '128k',
                        f'temp/{post_id}_h264.mp4'])
                 
            subprocess.call(['rm', f'{post_id}_video.mp4', f'{post_id}_audio.mp3'])

            return 'temp/' + post_id + '_h264', height, width


def scrape_video_from_mpd(content):
    root = ET.fromstring(content)
    logger.info(content)
   # Define the namespace
    namespace = {"mpd": "urn:mpeg:dash:schema:mpd:2011"}

    # Find all BaseURL elements
    baseurl_elements = root.findall(".//mpd:BaseURL", namespace)

    # Get the last child element, since last one has best quality overall.
    video_url, audio_url = "", ""
    last_one = baseurl_elements[-1]
    if "audio" in last_one.text:
        #Cutting 'DASH_' form video/audio name

        #taking second last element its a best quality video
        video_url = baseurl_elements[-2].text[5:]
        #last one is audio
        audio_url = last_one.text[5:]
    else:
        logger.info("there is only ")
        #there is only video, audio is missing
        video_url = last_one.text[5:]

    logger.info("best quality is %s", video_url)
    logger.info("audio is %s", audio_url)

    return video_url, audio_url


if __name__ == "__main__":
    download_and_get_reddit_post(url="https://www.reddit.com/r/JustGuysBeingDudes/comments/1304hsk/night_with_the_boys/?utm_source=share&utm_medium=android_app&utm_name=androidcss&utm_term=14&utm_content=share_button", logger=logger)