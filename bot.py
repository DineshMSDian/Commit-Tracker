import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load env variables
load_dotenv()

GITHUB_TOKEN=os.getenv('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}