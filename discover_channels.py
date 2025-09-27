import asyncio
import re
import time
import random
import os
import base64
from datetime import datetime, timezone, timedelta
from telethon.sync import TelegramClient
from telethon.tl.types import Channel

# --- CONFIGURATION (Unchanged) ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

SEED_CHANNELS = [
    'letendorproxy', 'MuteVpnN', 'ShadowProxy66',
    'v2rayng_news', 'PrivateConfig', 'v2ray_official'
]
OUTPUT_FILE = 'found_channels.txt'
RUN_DURATION_MINUTES = 5 
SEARCH_DELAYS_SECONDS = [2, 3, 4, 5]

ANALYSIS_MESSAGE_LIMIT = 50
MIN_CONFIG_HITS_THRESHOLD = 3
MAX_DAYS_SINCE_LAST_POST = 14
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
CHANNEL_LINK_REGEX = re.compile(r't\.me/([a-zA-Z0-9_]{5,})')
# --- END OF CONFIGURATION ---


async def main():
    print("--- Telegram Channel Crawler v8.1 (Corrected Logic) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets are not set.")
        return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    # This is our long-term memory.
    already_found_in_file = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            already_found_in_file.update(line.strip().lower() for line in f)
        print(f"Loaded {len(already_found_in_file)} previously discovered channels from file.")
    
    # --- THIS IS THE CORRECTED LOGIC ---
    # The queue ALWAYS starts with the seeds.
    channels_to_scan_queue = [seed.lower() for seed in SEED_CHANNELS]
    # The "processed" set for THIS RUN starts with the seeds to avoid re-analyzing them if found via crawl.
    processed_this_run = set(channels_to_scan_queue)
    # --- END OF CORRECTION ---

    newly_discovered_channels = []
    start_time = time.time()
    run_duration_seconds = RUN_DURATION_MINUTES * 60
        
    print(f"\n--- Starting crawl with {len(channels_to_scan_queue)} seed channels... ---")
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        while channels_to_scan_queue:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping crawler."); break
                
            username_to_check = channels_to_scan_queue.pop(0)
            print(f"\nAnalyzing @{username_to_check}...")

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
                
                # We only save channels that are not already in our long-term file.
                if is_active and config_hits >= MIN_CONFIG_HITS_THRESHOLD and username_to_check not in already_found_in_file:
                    print(f"  -> SUCCESS! @{username_to_check} is a new good source. Config Hits: {config_hits}")
                    newly_discovered_channels.append(username_to_check)
                elif not is_active or config_hits < MIN_CONFIG_HITS_THRESHOLD:
                     print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits} (Threshold: {MIN_CONFIG_HITS_THRESHOLD})")
                
                # Crawl for new links regardless of whether the current channel is "good" or not.
                for link in found_links_in_channel:
                    if link not in processed_this_run:
                        print(f"    -> Crawled new link to explore: @{link}")
                        channels_to_scan_queue.append(link)
                        processed_this_run.add(link)
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
        print(f"Usernames appended to {OUTPUT_FILE}.")
    else:
        print("\n--- Discovery Complete ---")
        print("No new, high-quality channels were found in this run.")

if __name__ == "__main__":
    asyncio.run(main())
