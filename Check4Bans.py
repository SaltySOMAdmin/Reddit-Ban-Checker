import praw
import config
import logging

logging.basicConfig(
    filename='/home/ubuntu/Reddit-Ban-Checker/error_log.txt',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Reddit API setup
reddit = praw.Reddit(
    client_id=config.source_client_id,
    client_secret=config.source_client_secret,
    password=config.source_password,
    username=config.source_username,
    user_agent=config.source_user_agent
)

SUB1 = "UFOs"
SUB2 = "UFOsMeta"

sub1 = reddit.subreddit(SUB1)
sub2 = reddit.subreddit(SUB2)

# --- Get permanently banned users from modlog ---
perma_banned_candidates = set()

print("Scanning modlog for permanent bans in r/UFOs...")

for log in sub1.mod.log(action="banuser", limit=None):
    # log.details examples: "permanent", "Permanent", "None"
    if log.details and ("permanent" in log.details.lower() or log.details.lower() == "none"):
        perma_banned_candidates.add(log.target_author.lower())

print(f"Found {len(perma_banned_candidates)} permanent-ban candidates in modlog.")

# --- Get currently banned users in r/UFOs ---
current_banned = {ban.name.lower() for ban in sub1.banned()}

# --- Filter only users who are still banned ---
perma_banned = perma_banned_candidates.intersection(current_banned)
print(f"{len(perma_banned)} permanent bans are still active.")

# --- Get currently banned users in r/UFOsMeta ---
meta_banned = {ban.name.lower() for ban in sub2.banned()}

# --- Users permanently banned in SUB1 but NOT banned in SUB2 ---
missing_users = sorted([u for u in perma_banned if u not in meta_banned])

print("\nUsers permanently banned in r/UFOs but NOT banned in r/UFOsMeta:\n")
for user in missing_users:
    print("u/" + user)

# --- Save results ---
output_file = "/home/ubuntu/Reddit-Ban-Checker/ufos_perma_ban_missing_from_meta.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for user in missing_users:
        f.write(user + "\n")

print(f"\nReport saved to {output_file}")
