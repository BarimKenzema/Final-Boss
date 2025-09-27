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

# Initial keywords to "seed" the discovery process.
SEARCH_KEYWORDS = [
    'бесплатный ВПН', 'конфиги V2Ray', 'VLESS бесплатно', 'обход РКН', 'прокси бесплатно',
    '免费节点', 'V2Ray 机场', '免费梯子', 'SSR 订阅', 'VLESS 节点', '科学上网',
    'v2ray config', 'free vless', 'v2ray subscription', 'shadowsocks free'
]

OUTPUT_FILE = 'found_channels.txt'
# Increased runtime to give the crawler more time to explore.
RUN_DURATION_MINUTES = 5 
SEARCH_DELAYS_SECONDS = [3, 4, 5, 6, 7]

# --- Quality Analysis Configuration ---
ANALYSIS_MESSAGE_LIMIT = 50 # Scan a few more messages for better accuracy
MIN_CONFIG_HITS_THRESHOLD = 3 # A slightly higher bar for quality
MAX_DAYS_SINCE_LAST_POST = 14
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
# Regex to find t.me links to other channels
CHANNEL_LINK_REGEX = re.compile(r't\.me/([a-zA-Z0-9_]{5,})')
# --- END OF CONFIGURATION ---


async def main():
    print("--- Telegram Channel Crawler v2.0 ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets are not set.")
        return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file from secret. Error: {e}"); return

    # This set is our master memory of every channel ever processed to prevent loops.
    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            already_processed.update(line.strip().lower() for line in f)
        print(f"Loaded {len(already_processed)} previously discovered channels.")
    
    # This list is our "to-do list" for the current run.
    channels_to_scan_queue = []
    newly_discovered_channels = []
    start_time = time.time()
    run_duration_seconds = RUN_DURATION_MINUTES * 60
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        # --- Step 1: Seed the queue with initial keyword searches ---
        print("\n--- Seeding initial channels from keywords ---")
        random.shuffle(SEARCH_KEYWORDS)
        for keyword in SEARCH_KEYWORDS:
            if time.time() - start_time > run_duration_seconds: break
            print(f"Searching for: '{keyword}'")
            try:
                result = await client(SearchRequest(peer='me', q=keyword, filter=InputMessagesFilterEmpty(), limit=10))
                for entity in result.chats:
                    if isinstance(entity, Channel) and hasattr(entity, 'username') and entity.username:
                        username = entity.username.lower()
                        if username not in already_processed:
                            print(f"  -> Found seed channel: @{username}")
                            channels_to_scan_queue.append(username)
                            already_processed.add(username) # Mark as "seen"
            except Exception: pass
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))
        
        print(f"\n--- Starting to crawl {len(channels_to_scan_queue)} seed channels ---")
        
        # --- Step 2: The Crawling Loop ---
        while channels_to_scan_queue:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping crawler.")
                break
                
            username_to_check = channels_to_scan_queue.pop(0) # Get the next channel from the to-do list
            print(f"\nAnalyzing @{username_to_check}...")

            is_active = False
            config_hits = 0
            found_links_in_channel = set()
            try:
                messages = [msg async for msg in client.iter_messages(username_to_check, limit=ANALYSIS_MESSAGE_LIMIT)]
                if messages:
                    if datetime.now(timezone.utc) - messages[0].date < timedelta(days=MAX_DAYS_SINCE_LAST_POST):
                        is_active = True
                    for msg in messages:
                        if msg.text:
                            if VALIDATION_KEYWORDS.search(msg.text):
                                config_hits += 1
                            # Find t.me links to other channels
                            for match in CHANNEL_LINK_REGEX.finditer(msg.text):
                                found_links_in_channel.add(match.group(1).lower())
                
                # Decision Logic
                if is_active and config_hits >= MIN_CONFIG_HITS_THRESHOLD:
                    print(f"  -> SUCCESS! @{username_to_check} is a good source. Config Hits: {config_hits}")
                    newly_discovered_channels.append(username_to_check)
                    # Now add the links it mentioned to our to-do list
                    for link in found_links_in_channel:
                        if link not in already_processed:
                            print(f"    -> Found new link to explore: @{link}")
                            channels_to_scan_queue.append(link)
                            already_processed.add(link) # Mark as "seen"
                else:
                    print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits} (Threshold: {MIN_CONFIG_HITS_THRESHOLD})")
            
            except Exception:
                print(f"  -> Could not analyze @{username_to_check}. Skipping.")
            
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))

    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")

    # --- Step 3: Save the results ---
    if newly_discovered_channels:
        print(f"\n--- Discovery Complete ---")
        print(f"Found {len(newly_discovered_channels)} new, high-quality channels in this run.")
        with open(OUTPUT_FILE, 'a') as f:
            for username in newly_discovered_channels:
                f.write(f"{username}\n")
        print(f"Usernames have been appended to {OUTPUT_FILE}.")
    else:
        print("\n--- Discovery Complete ---")
        print("No new, high-quality channels were found.")

if __name__ == "__main__":
    asyncio.run(main())
