# config.py
import logging

# Bot Configuration
API_ID = 29620980
API_HASH = "f1f5b9e6ef7d4d3c6d13d526d8a4f9ff"
BOT_TOKEN = "8450523795:AAHt8Ywfis8R6TSw06qIteibXWC7Z7jI3EM"
MONGO_URI = "mongodb+srv://shopgenzar:kXfZ3Dx8GFAqxAoW@cluster0.h3ffnb6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "telegram_stars_db"
ADMIN_ID = 7438550943
BOT_USERNAME = "RajXStarsBot"

# Database Collections
USERS_COLLECTION = "users"
CHANNELS_COLLECTION = "channels"
WITHDRAWALS_COLLECTION = "withdrawals"

# Bot Settings
MIN_WITHDRAWAL = 15
DAILY_BONUS = 1
REFERRAL_BONUS = 2

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)