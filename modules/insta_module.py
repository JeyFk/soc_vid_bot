import subprocess
import logging
import json
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
from jsonpath_ng import jsonpath, parse

logger = logging.getLogger(__name__)


def download_and_get_reel(url, logger) -> (str, str, str):
    logger.info("Opening %s", url)
    headers_for_reddit = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        "Cookie": ''
    }
    response = requests.get(url)
    print(response)
    if (response.status_code == 200):  # checking if the server responded with OK
            soup = BeautifulSoup(response.text, 'lxml')
            # reel_json = soup.find('script', type="application/ld+json")
            # json_data = json.loads(reel_json.text)\
            script_tags = soup.find_all('script')
            
            # Loop through script tags and extract video_versions
            for script_tag in script_tags:
                script_text = script_tag.string
                
                # Check if the script text contains "video_versions"
                if script_text and "video_versions" in script_text:
                    try:
                        data = json.loads(script_text)
                        video_versions = data.get('require', {}).get('0', [])[3].get('__bbox', {}).get('result', {}).get('data', {}).get('xdt_api__v1__media__shortcode__web_info', {}).get('items', [])[0].get('video_versions', [])
                        
                        if video_versions:
                            first_video_url = video_versions[0].get('url')
                            print("Extracted URL from the first video_versions:", first_video_url)
                            break  # Exit the loop once the first occurrence is found
                        
                    except json.JSONDecodeError:
                        print("Failed to decode JSON content")
                        continue

                    if not first_video_url:
                        print("No video_versions found in the provided script tags")



          

if __name__ == "__main__":
    download_and_get_reel(url="https://www.instagram.com/reel/CsmIhVQqsur/", logger=logger)