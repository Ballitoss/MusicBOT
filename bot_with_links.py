#!/usr/bin/env python3
"""
Telegram Music Bot met support voor Telegram link downloads
"""
import asyncio
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from pathlib import Path

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuratie
BOT_TOKEN = "8316998623:AAFW4D85_UIdi1hHSrit7xOku1chW_5dv3g"
API_ID = 27851448
API_HASH = "cd623b07974e42767cb8e9ed61a6a20d"

# Telethon client (voor downloaden van Telegram links)
telethon_client = None

def parse_telegram_link(text):
    """Parse Telegram link uit tekst"""
    # Pattern voor topic/thread links: t.me/c/CHANNEL_ID/TOPIC_ID/MESSAGE_ID
    pattern_topic = r't\.me/c/(\d+)/(\d+)/(\d+)'
    match = re.search(pattern_topic, text)
    if match:
        channel_id = int(match.group(1))
        topic_id = int(match.group(2))  # We negeren deze voor nu
        message_id = int(match.group(3))
        full_channel_id = int(f"-100{channel_id}")
        return full_channel_id, message_id
    
    # Pattern voor normale links: t.me/c/CHANNEL_ID/MESSAGE_ID
    pattern_normal = r't\.me/c/(\d+)/(\d+)'
    match = re.search(pattern_normal, text)
    if match:
        channel_id = int(match.group(1))
        message_id = int(match.group(2))
        full_channel_id = int(f"-100{channel_id}")
        return full_channel_id, message_id
    
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "🎵 Welkom bij BBB Media Bot!\n\n"
        "Stuur me een Telegram link (t.me/c/...) en ik download de media voor je!\n"
        "Ondersteunt: audio, foto's, video's en andere bestanden\n\n"
        "Commando's:\n"
        "/start - Start de bot\n"
        "/help - Toon help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📖 Help:\n\n"
        "Stuur gewoon een Telegram link:\n"
        "bijvoorbeeld: https://t.me/c/3342923502/616\n\n"
        "Ondersteunt:\n"
        "• 🎵 Audio (mp3, wav, ogg, etc.)\n"
        "• 🖼️ Foto's (jpg, png, gif, etc.)\n"
        "• 🎥 Video's (mp4, mov, mkv, etc.)\n"
        "• 📄 Andere bestanden\n\n"
        "De bot zal het downloaden en naar je terugsturen!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle alle berichten"""
    text = update.message.text
    
    # Check of het een Telegram link is
    channel_id, message_id = parse_telegram_link(text)
    
    if channel_id and message_id:
        await handle_telegram_link(update, channel_id, message_id)
    else:
        await update.message.reply_text(
            "❌ Geen geldige Telegram link gevonden.\n"
            "Stuur een link in het formaat: https://t.me/c/XXXXXX/XXX"
        )

async def handle_telegram_link(update: Update, channel_id: int, message_id: int):
    """Download en stuur media van Telegram link"""
    status_msg = await update.message.reply_text("🔄 Bezig met downloaden...")
    
    try:
        # Haal bericht op via Telethon
        message = await telethon_client.get_messages(channel_id, ids=message_id)
        
        logger.info(f"Message: {message}")
        logger.info(f"Has media: {message.media if message else 'No message'}")
        logger.info(f"Has text: {message.text if message else 'No message'}")
        
        if not message:
            await status_msg.edit_text("❌ Bericht niet gevonden. Zorg dat je account toegang heeft tot dit kanaal.")
            return
        
        # Als het bericht alleen tekst heeft (geen media)
        if not message.media:
            if message.text:
                await status_msg.delete()
                await update.message.reply_text(f"📝 Tekst:\n{message.text}")
                return
            else:
                await status_msg.edit_text("❌ Dit bericht bevat geen media of tekst.")
                return
        
        await status_msg.edit_text("📥 Downloaden...")
        
        # Download
        Path("downloads").mkdir(parents=True, exist_ok=True)
        file_path = await telethon_client.download_media(message, file="downloads")
        
        if not file_path:
            await status_msg.edit_text("❌ Kon bestand niet downloaden.")
            return
        
        await status_msg.edit_text("📤 Versturen...")
        
        # Stuur eerst de tekst (indien aanwezig)
        if message.text:
            await update.message.reply_text(f"📝 Tekst:\n{message.text}")
        
        # Bepaal media type en stuur het juiste type terug
        file_path_lower = file_path.lower()
        with open(file_path, 'rb') as media_file:
            if file_path_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                # Foto
                await update.message.reply_photo(photo=media_file)
            elif file_path_lower.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                # Video
                await update.message.reply_video(video=media_file)
            elif file_path_lower.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac')):
                # Audio
                await update.message.reply_audio(audio=media_file)
            else:
                # Anders als document
                await update.message.reply_document(document=media_file)
        
        await status_msg.delete()
        
        # Ruim op
        import os
        os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Fout bij downloaden: {e}")
        await status_msg.edit_text(f"❌ Fout: {str(e)}")

async def post_init(application: Application):
    """Initialize Telethon client na bot start"""
    global telethon_client
    logger.info("🔌 Verbinden met Telethon...")
    telethon_client = TelegramClient('user_session', API_ID, API_HASH)
    await telethon_client.start()
    logger.info("✅ Telethon verbonden!")

async def post_shutdown(application: Application):
    """Cleanup bij afsluiten"""
    if telethon_client:
        logger.info("🔌 Telethon afsluiten...")
        await telethon_client.disconnect()

def main():
    """Start de bot"""
    logger.info("🤖 Starting BBB Music Bot...")
    
    # Maak applicatie
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("✅ Bot gestart!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
