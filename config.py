import os
from dotenv import load_dotenv

load_dotenv()

username = 'YOUR_REDDIT_NAME'
password = 'YOUR_REDDIT_PW'

google_api_key = os.getenv('GOOGLE_API_KEY')

client_id = 'YOUR_REDDIT_APP_ID'
client_secret = 'YOUR_TOP_SECRET_REDDIT_APP_CODE'

show_file = 'shows.csv'
subreddit = 'drumcorps'
