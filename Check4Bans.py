import requests
import praw
import config  # Your config file with credentials
import logging
from datetime import datetime, timedelta, timezone
import re
import unicodedata
from zoneinfo import ZoneInfo

# Set up logging
logging.basicConfig(
    filename='/home/ubuntu/Reddit-Ban-Checker/error_log.txt',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Reddit API setup
reddit = praw.Reddit(
    client_id=config.destination_client_id,
    client_secret=config.destination_client_secret,
    password=config.destination_password,
    username=config.destination_username,
    user_agent=config.destination_user_agent
)

SUB1 = "UFOs"
SUB2 = "UFOsMeta"

# --- Fetch banned users from subreddit 1 ---
sub1 = reddit.subreddit(SUB1)
banned_sub1 = list(sub1.banned())

# Filter permanent bans correctly (duration == 0 means permanent)
perma_banned = [ban for ban in banned_sub1 if ban.duration == 0]

print(f"Total banned in r/{SUB1}: {len(banned_sub1)}")
print(f"Permanent bans in r/{SUB1}: {len(perma_banned)}")

# --- Fetch banned users from subreddit 2 ---
sub2 = reddit.subreddit(SUB2)
banned_sub2 = {ban.name for ban in sub2.banned()}  # set of usernames

# Build report of users perma-banned in SUB1 but NOT banned in SUB2
report = []
for ban in perma_banned:
    username = ban.name
    note = ban.note or ""
    is_banned_in_sub2 = username in banned_sub2

    # Only include if NOT banned in SUB2
    if not is_banned_in_sub2:
        report.append({
            "username": username,
            "note_sub1": note
        })

# --- Print report ---
print(f"\nUsers permanently banned in r/{SUB1} but NOT banned in r/{SUB2}:\n")
for entry in report:
    print(f"u/{entry['username']} -- note='{entry['note_sub1']}'")

# Save to file
output_file = "/home/ubuntu/Reddit-Ban-Checker/ufos_perma_ban_missing_from_meta.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for entry in report:
        f.write(f"{entry['username']}\t{entry['note_sub1']}\n")

print(f"\nReport written to: {output_file}")
