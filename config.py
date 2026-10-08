import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')
ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'Admin')
OWNER_ID = 1234567890  # سيتم تحديثه لاحقاً
OWNER_USERNAME = 'g_8ia'  # صاحب البوت

# Giveaway Settings
GIVEAWAY_SETTINGS = {
    'min_duration_seconds': 60,
    'max_participants': 1000,
}
