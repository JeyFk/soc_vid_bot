#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple bot that enables viewing of twitter videos in telegram channels
"""


import logging
import re
from datetime import datetime
import instaloader
import shutil
import json

from telegram import __version__ as TG_VER
TELEGRAM_BOT_TOKEN = 'X'

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ChatMemberHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.text("Bot started, you can send you links")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just sent twitter link into the channel, so I can adjust it with")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def handle_soc_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """EDIT TWITTER TO DISPLAY VIDEO"""
    message = update.message.text
    #Handle twitter
    if 'twitter.com/' in message and not "vstwitter.com" in message:
        logger.info("editing %s" , message)
        try:
            modified_message = re.sub(r'(https?://www\.)?twitter\.com/', 'vstwitter.com/', message)
           # await update.message.reply_text(modified_message)
            await context.bot.send_message(context._chat_id, modified_message + "\n\nSent by @" + str(update.message.from_user.username)) 

            await update.message.delete()
        except Exception as e:
            await update.message.reply_text(f'Error: {str(e)}')
    
    #Handle instagram reels
    if 'instagram.com/reel' in message:
        logger.info("it's instagram link " + message)
        shortcode = re.search(r"instagram.com/(reel|reels)/([\w-]+)", message)
        if not shortcode:
            logger.info("Invalid URL")
            return

        shortcode = shortcode.group(2)
        timeCode = str(datetime.now().timestamp()) + update.message.from_user.name;
        #Build instaloader
        L = instaloader.Instaloader(filename_pattern="{target}",save_metadata=True,
                                    download_pictures=False, download_geotags=False, download_comments=False,
                                    download_video_thumbnails=False, compress_json=False)
        
        try:
            logger.info("downloading from shortcode:{%s}", shortcode)
            reel = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(reel, target=timeCode)
            path = timeCode + "/" + timeCode + ".mp4"
            #extract heigh width
            height, width = extract_height_width(file_path=path, reel_id=shortcode)
            logger.info("height:{%s}, width:{%s}", height, width)
        
            await context.bot.send_video(context._chat_id, path , height=1919, width=1080, caption="Sent by @" + str(update.message.from_user.username)) 
            await update.message.delete()
            delete_temp(file_path=timeCode)
        except Exception as e:
            logger.error(f"Error downloading reel: {e}")
            await update.message.reply_text("Unable to parse url or video is private, maybe API changed as well?")
    
    
    
def extract_height_width(file_path, reel_id):
    file_path = file_path[:-4] + ".json" 

    logger.info("extacting metadta for reel %s", reel_id)
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    # Extract the "height" and "width" from the JSON
    try:
        height = json_data["node"]["dimensions"]["height"]
        width = json_data["node"]["dimensions"]["width"]
    except Exception as e:
        #handle exception if no metadata about heigh witdth present
        logger.warn("unable to parse metadata for reel %s")
        return(1919, 1080)
    
    return (height, width)
     
def delete_temp(file_path):     
    #maybe add cash for reel files?
    logger.info("deleting temp files")
    shutil.rmtree(file_path)  

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # on twitter message - echo twitter message with fixed url for video
    # on instagram messages - extact video
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_soc_videos))
    application.add_handler(ChatMemberHandler(handle_soc_videos, ChatMemberHandler.CHAT_MEMBER))
    #handle instagram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, instagram))
    # application.add_handler(ChatMemberHandler(instagram, ChatMemberHandler.CHAT_MEMBER))

    #echo
    application.add_handler(ChatMemberHandler(echo, ChatMemberHandler.CHAT_MEMBER))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()