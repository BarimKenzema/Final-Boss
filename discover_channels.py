import asyncio
import re
import time
import random
import os
import base64
from datetime import datetime, timezone, timedelta
from telethon.sync import TelegramClient
from telethon.tl.types import Channel

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

# --- NEW: HASHTAG-FOCUSED KEYWORDS ---
# We are now searching for hashtags that channels use to label their configs.
# This is a much more direct and effective search method.
SEARCH_HASHTAGS = [
    # Russian
    '#vless', '#vmess', '#trojan', '#proxy', '#впн',
    # Chinese (with slang)
    '#V2Ray', '#trojan', '#节点', '#机场', '#订阅',
    # English/General
    '#v2ray', '#vpn', '#outline', '#shadowsocks'
]

OUTPUT_FILE = 'found_channels.txt'
RUN_DURATION_MINUTES = 4
SEARCH_DELAYS_SECONDS = [4, 5, 6, 7]

# --- Quality Analysis Configuration ---
ANALYSIS_MESSAGE_LIMIT = 30
MIN_CONFIG_HITS_THRESHOLD = 3 # Needs to find at least 3 configs in recent posts
MAX_DAYS_SINCE_LAST_POST = 14
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
CHANNEL_LINK_REGEX = re.compile(r't\.me/([a-zA-Z0-9_]{5,})')
# --- END OF CONFIGURATION ---


async def main():
    print("--- Telegram Channel Discoverer v3.0 (Hashtag Hunter) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets are not set.")
        return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            already_processed.update(line.strip().lower() for line in f)
        print(f"Loaded {len(already_processed)} previously discovered channels.")
    
    # Use a set to avoid adding duplicate channels to the queue in the first place
    channels_to_scan_queue = set()
    newly_discovered_channels = []
    start_time = time.time()
    run_duration_seconds = RUN_DURATION_MINUTES * 60
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        # --- Step 1: Seed the queue using hashtag searches ---
        print("\n--- Seeding initial channels from hashtag searches ---")
        random.shuffle(SEARCH_HASHTAGS)
        for hashtag in SEARCH_HASHTAGS:
            if time.time() - start_time > run_duration_seconds: break
            print(f"Searching for hashtag: '{hashtag}'")
            try:
                # Use global message search (iter_messages with None)
                async for message in client.iter_messages(None, search=hashtag, limit=15):
                    if (hasattr(message.peer_id, 'channel_id') and 
                        message.chat and hasattr(message.chat, 'username') and 
                        message.chat.username):
                        
                        username = message.chat.username.lower()
                        if username not in already_processed:
                            channels_to_scan_queue.add(username)
                            
            except Exception as e:
                 print(f"  -> Error during search for '{hashtag}': {e}")
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))
        
        # Convert set to a list to process
        scan_list = list(channels_to_scan_queue)
        print(f"\n--- Found {len(scan_list)} unique seed channels. Starting analysis... ---")
        
        # --- Step 2: The Analysis & Crawling Loop ---
        while scan_list:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping crawler.")
                break
                
            username_to_check = scan_list.pop(0)
            if username_to_check in already_processed:
                continue # Skip if we've already processed it

            print(f"\nAnalyzing @{username_to_check}...")
            already_processed.add(username_to_check) # Mark as processed for this session

            try:
                is_active = False; config_hits = 0; found_links_in_channel = set()
                messages = [msg async for msg in client.iter_messages(username_to_check, limit=ANALYSIS_MESSAGE_LIMIT)]
                if messages:
                    if datetime.now(timezone.utc) - messages[0].date < timedelta(days=MAX_DAYS_SINCE_LAST_POST): is_active = True
                    for msg in messages:
                        if msg.text:
                            if VALIDATION_KEYWORDS.search(msg.text): config_hits += 1
                            for match in CHANNEL_LINK_REGEX.finditer(msg.text):
                                found_links_in_channel.add(match.group(1).lower())
                
                if is_active and config_hits >= MIN_CONFIG_HITS_THRESHOLD:
                    print(f"  -> SUCCESS! @{username_to_check} is a good source. Config Hits: {config_hits}")
                    newly_discovered_channels.append(username_to_check)
                    for link in found_links_in_channel:
                        if link not in already_processed:
                            print(f"    -> Crawled new link to explore: @{link}")
                            scan_list.append(link) # Add to our to-do list
                else:
                    print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits}")
            
            except Exception as e:
                print(f"  -> Could not analyze @{username_to_check}. Skipping. Error: {e}")
            
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))

    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")

    if newly_discovered_channels:
        print(f"\n--- Discovery Complete ---")
        unique_new = sorted(list(set(newly_discovered_channels)))
        print(f"Found {len(unique_new)} new, high-quality channels.")
        with open(OUTPUT_FILE, 'a') as f:
            for username in unique_new:
                f.write(f"{username}\n")
        print(f"Usernames have been appended to {OUTPUT_FILE}.")
    else:
        print("\n--- Discovery Complete ---")
        print("No new, high-quality channels were found.")

if __name__ == "__main__":
    asyncio.run(main())
