import asyncio
import re
import time
import random
import os
import base64
import requests
from datetime import datetime, timezone, timedelta
from telethon.sync import TelegramClient

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

# --- NEW: Using SearXNG Public Instances for stable API access ---
SEARXNG_INSTANCES = [
    "https://searx.be",
    "https://searx.work",
    "https://searx.info",
    "https://searx.tiekoetter.com",
    "https://searx.bacardi.cat"
]

SEARCH_QUERIES = [
    'site:t.me "v2ray" "config"', 'site:t.me "vless" "бесплатно"',
    'site:t.me "vmess" "免费节点"', 'inurl:t.me "shadowsocks" "proxy"',
    'inurl:t.me "trojan" "梯子"', 'site:t.me "v2ray" "subscription"',
    'site:t.me "обход блокировок" "РКН"', 'site:t.me "V2Ray 机场" "订阅"'
]

OUTPUT_FILE = 'found_channels.txt'
RUN_DURATION_MINUTES = 4
SEARCH_DELAYS_SECONDS = [5, 7, 10]

# --- Quality Analysis Configuration (Unchanged) ---
ANALYSIS_MESSAGE_LIMIT = 30
MIN_CONFIG_HITS_THRESHOLD = 2
MAX_DAYS_SINCE_LAST_POST = 14
VALIDATION_KEYWORDS = re.compile(r'vless://|vmess://|ss://|trojan://', re.IGNORECASE)
CHANNEL_LINK_REGEX = re.compile(r't\.me/([a-zA-Z0-9_]{5,})')
# --- END OF CONFIGURATION ---


async def search_searxng_for_telegram_links(query, instances):
    """Searches a SearXNG instance using its JSON API."""
    print(f"  -> Searching SearXNG for: '{query}'")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Try each instance until one works
    for instance in instances:
        try:
            url = f"{instance}/?q={requests.utils.quote(query)}&format=json"
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            found_channels = set()
            for result in data.get('results', []):
                url = result.get('url')
                if url:
                    match = CHANNEL_LINK_REGEX.search(url)
                    if match:
                        found_channels.add(match.group(1).lower())
            
            print(f"  -> Found {len(found_channels)} potential channels via {instance}.")
            return list(found_channels) # Return on first success
        except Exception as e:
            print(f"  -> Instance {instance} failed: {e}. Trying next...")
            continue
    
    print(f"  -> All SearXNG instances failed for this query.")
    return []


async def main():
    print("--- Telegram Channel Discoverer v5.0 (SearXNG API) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]): print("FATAL: Required secrets not set."); return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: print(f"FATAL: Could not write session file. Error: {e}"); return

    already_processed = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            already_processed.update(line.strip().lower() for line in f)
        print(f"Loaded {len(already_processed)} previously discovered channels.")
    
    channels_to_scan_queue = set()
    newly_discovered_channels = []
    start_time = time.time()
    run_duration_seconds = RUN_DURATION_MINUTES * 60
    
    # --- Step 1: Seed the queue from SearXNG ---
    print("\n--- Seeding initial channels from SearXNG API searches ---")
    random.shuffle(SEARCH_QUERIES)
    shuffled_instances = random.sample(SEARXNG_INSTANCES, len(SEARXNG_INSTANCES))
    for query in SEARCH_QUERIES:
        if time.time() - start_time > run_duration_seconds: break
        
        search_results = await search_searxng_for_telegram_links(query, shuffled_instances)
        for username in search_results:
            if username not in already_processed:
                channels_to_scan_queue.add(username)
        
        await asyncio.sleep(random.choice(SEARCH_DELAYS_SECONDS))
    
    if not channels_to_scan_queue:
        print("\nSearXNG search did not yield any new channels to analyze. Exiting.")
        return
        
    scan_list = list(channels_to_scan_queue)
    print(f"\n--- Found {len(scan_list)} unique seed channels from SearXNG. Starting analysis... ---")
    
    # --- Step 2: Analyze the channels ---
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram for analysis.")
        
        while scan_list:
            if time.time() - start_time > run_duration_seconds:
                print("\nTime limit reached. Stopping analysis."); break
                
            username_to_check = scan_list.pop(0)
            if username_to_check in already_processed: continue
            
            print(f"\nAnalyzing @{username_to_check}...")
            already_processed.add(username_to_check)

            try:
                is_active = False; config_hits = 0
                messages = [msg async for msg in client.iter_messages(username_to_check, limit=ANALYSIS_MESSAGE_LIMIT)]
                if messages:
                    if datetime.now(timezone.utc) - messages[0].date < timedelta(days=MAX_DAYS_SINCE_LAST_POST): is_active = True
                    for msg in messages:
                        if msg.text and VALIDATION_KEYWORDS.search(msg.text): config_hits += 1
                
                if is_active and config_hits >= MIN_CONFIG_HITS_THRESHOLD:
                    print(f"  -> SUCCESS! @{username_to_check} is a good source. Config Hits: {config_hits}")
                    newly_discovered_channels.append(username_to_check)
                else:
                    print(f"  -> REJECTED. Active: {is_active}, Config Hits: {config_hits}")
            except Exception as e:
                print(f"  -> Could not analyze @{username_to_check}. Skipping. Error: {e}")
            
            await asyncio.sleep(2)
            
    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")

    # --- Step 3: Save results ---
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
        print("No new, high-quality channels were found.")

if __name__ == "__main__":
    asyncio.run(main())
