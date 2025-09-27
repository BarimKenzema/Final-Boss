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

# Keywords to "seed" the discovery process.
SEARCH_KEYWORDS = [
    'бесплатный ВПН', 'конфиги V2Ray', 'VLESS бесплатно', 'обход РКН', 'прокси бесплатно',
    '免费节点', 'V2Ray 机场', '免费梯子', 'SSR 订阅', 'VLESS 节点', '科学上网',
    'v2ray config', 'free vless', 'v2ray subscription', 'shadowsocks free'
]

OUTPUT_FILE = 'found_channels.txt'
RUN_DURATION_MINUTES = 5 
SEARCH_DELAYS_SECONDS = [5, 6, 7, 8] # Slightly longer delays to be safer

# --- Quality Analysis Configuration ---
ANALYSIS_MESSAGE_LIMIT = 50
MIN_CONFIG_HITS_THRESHOLD = 3
MAX_DAYS_SINCE_LAST_POST = 14
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
CHANNEL_LINK_REGEX = re.compile(r't\.me/([a-zA-Z0-9_]{5,})')
# --- END OF CONFIGURATION ---


async def main():
    print("--- Telegram Channel Crawler v2.1 (Robust Search) ---")
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
        
        # --- Step 1: Seed the queue with a more robust search method ---
        print("\n--- Seeding initial channels from keywords ---")
        random.shuffle(SEARCH_KEYWORDS)
        for keyword in SEARCH_KEYWORDS:
            if time.time() - start_time > run_duration_seconds: break
            print(f"Searching for: '{keyword}'")
            try:
                # --- NEW, MORE RELIABLE SEARCH LOGIC ---
                # We search the global index for messages containing the keyword.
                async for message in client.iter_messages(None, search=keyword, limit=10):
                    # Check if the message is from a public channel with a username
                    if hasattr(message.peer_id, 'channel_id') and message.chat and hasattr(message.chat, 'username') and message.chat.username:
                        username = message.chat.username.lower()
                        if username not in already_processed:
                            print(f"  -> Found seed channel via message: @{username}")
                            channels_to_scan_queue.append(username)
                            already_processed.add(username)
                # --- END OF NEW LOGIC ---
            except Exception as e:
                 print(f"  -> Error during search for '{keyword}': {e}")
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))
        
        print(f"\n--- Starting to crawl {len(set(channels_to_scan_queue))} unique seed channels ---")
        
        # --- Step 2: The Crawling Loop (no changes needed here) ---
        while channels_to_scan_queue:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping crawler.")
                break
                
            username_to_check = channels_to_scan_queue.pop(0)
            print(f"\nAnalyzing @{username_to_check}...")

            is_active = False; config_hits = 0; found_links_in_channel = set()
            try:
                messages = [msg async for msg in client.iter_messages(username_to_check, limit=ANALYSIS_MESSAGE_LIMIT)]
                if messages:
                    if datetime.now(timezone.utc) - messages[0].date < timedelta(days=MAX_DAYS_SINCE_LAST_POST):
                        is_active = True
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
                            print(f"    -> Found new link to explore: @{link}")
                            channels_to_scan_queue.append(link)
                            already_processed.add(link)
                else:
                    print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits}")
            
            except Exception:
                print(f"  -> Could not analyze @{username_to_check}. Skipping.")
            
            await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))

    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")

    # --- Step 3: Save the results (no changes) ---
    if newly_discovered_channels:
        print(f"\n--- Discovery Complete ---")
        print(f"Found {len(newly_discovered_channels)} new, high-quality channels.")
        # We use a set to ensure the final written list is unique
        unique_new_channels = sorted(list(set(newly_discovered_channels)))
        with open(OUTPUT_FILE, 'a') as f:
            for username in unique_new_channels:
                f.write(f"{username}\n")
        print(f"Usernames have been appended to {OUTPUT_FILE}.")
    else:
        print("\n--- Discovery Complete ---")
        print("No new, high-quality channels were found.")

if __name__ == "__main__":
    asyncio.run(main())
