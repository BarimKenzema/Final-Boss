import asyncio
import re
import time
import random
import os
import base64
from datetime import datetime, timezone, timedelta
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty, Channel

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

# Keywords the bot will search for.
SEARCH_KEYWORDS = [
    'бесплатный ВПН', 'конфиги V2Ray', 'VLESS бесплатно', 'обход РКН', 'прокси бесплатно',
    '免费节点', 'V2Ray 机场', '免费梯子', 'SSR 订阅', 'VLESS 节点', '科学上网',
    'v2ray config', 'free vless', 'v2ray subscription', 'shadowsocks free'
]

# The file where promising channel usernames will be saved.
OUTPUT_FILE = 'found_channels.txt'

# How long the script should run in total (in minutes) before stopping.
# Kept short for GitHub Actions to avoid excessive runtime.
RUN_DURATION_MINUTES = 4

# Randomized delays after each search.
SEARCH_DELAYS_SECONDS = [3, 5, 6, 8, 10]

# --- Quality Analysis Configuration ---
ANALYSIS_MESSAGE_LIMIT = 20
MIN_CONFIG_HITS_THRESHOLD = 2
MAX_DAYS_SINCE_LAST_POST = 14 # A bit more lenient
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
# --- END OF CONFIGURATION ---


async def main():
    print("--- Telegram Channel Discovery Bot (GitHub Actions) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets are not set.")
        return

    # Create the session file from the secret
    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f:
            f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file from secret. Error: {e}")
        return

    # Load channels we've already found to avoid re-analyzing.
    already_found = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            already_found.update(line.strip().lower() for line in f)
        print(f"Loaded {len(already_found)} previously discovered channels.")
    
    newly_discovered_channels = []
    start_time = time.time()
    run_duration_seconds = RUN_DURATION_MINUTES * 60
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized. Please generate a new session string.")
            return
        print("Successfully connected to Telegram.")
        
        random.shuffle(SEARCH_KEYWORDS)
        
        for keyword in SEARCH_KEYWORDS:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping discovery.")
                break

            print(f"\nSearching for keyword: '{keyword}'...")
            try:
                result = await client(SearchRequest(
                    peer='me', q=keyword, filter=InputMessagesFilterEmpty(), limit=20,
                    min_date=None, max_date=None, offset_id=0, add_offset=0, max_id=0, min_id=0, from_id=None, hash=0
                ))

                for entity in result.chats:
                    if isinstance(entity, Channel) and hasattr(entity, 'username') and entity.username:
                        username = entity.username.lower()
                        if username not in already_found:
                            print(f"  -> Found potential new channel: @{username}. Analyzing...")
                            already_found.add(username)
                            
                            is_active = False
                            config_hits = 0
                            try:
                                messages = [msg async for msg in client.iter_messages(username, limit=ANALYSIS_MESSAGE_LIMIT)]
                                if messages:
                                    last_post_date = messages[0].date
                                    if datetime.now(timezone.utc) - last_post_date < timedelta(days=MAX_DAYS_SINCE_LAST_POST):
                                        is_active = True
                                    for msg in messages:
                                        if msg.text and VALIDATION_KEYWORDS.search(msg.text):
                                            config_hits += 1
                                
                                if is_active and config_hits >= MIN_CONFIG_HITS_THRESHOLD:
                                    print(f"  -> SUCCESS! @{username} is active and has {config_hits} config posts. Saving.")
                                    newly_discovered_channels.append(entity.username) # Save with original casing
                                else:
                                    print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits}")
                            
                            except Exception:
                                print(f"  -> Could not analyze @{username}. Skipping.")

            except Exception as e:
                print(f"  -> An error occurred during search: {e}")

            delay = random.choice(SEARCH_DELAYS_SECONDS)
            print(f"Waiting for {delay} seconds...")
            await asyncio.sleep(delay)

    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")

    if newly_discovered_channels:
        print(f"\n--- Discovery Complete ---")
        print(f"Found {len(newly_discovered_channels)} new, high-quality channels.")
        with open(OUTPUT_FILE, 'a') as f:
            for username in newly_discovered_channels:
                f.write(f"{username}\n")
        print(f"Usernames have been appended to {OUTPUT_FILE}.")
    else:
        print("\n--- Discovery Complete ---")
        print("No new, high-quality channels were found in this run.")

if __name__ == "__main__":
    asyncio.run(main())
