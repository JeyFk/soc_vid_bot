from download_reels import download
import logging
 
logger = logging.getLogger(__name__)

def download_and_get_reel(url, logger) -> (str, str, str):
    logger.info("Opening %s", url)
    path = download(url, "name.mp4")
    return path;


if __name__ == "__main__":
    download_and_get_reel(url="https://www.instagram.com/reel/CsmIhVQqsur/", logger=logger)