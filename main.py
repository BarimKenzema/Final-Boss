import re, base64, os, asyncio, json
from telethon.sync import TelegramClient
from urllib.parse import quote

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

TARGET_GROUPS = [ 'letendorproxy' ] # Add more group/channel usernames here
OUTPUT_FILE = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json' # Our new "bookmark" file
NEW_NAME = '@MoboNetPC'
MAX_CONFIGS = 444
# --- END OF CONFIGURATION ---

# All helper functions remain the same
def find_and_reassemble_configs(text):
    if not text: return []
    pattern = r'\b(?:vless|vmess|trojan|ss)://[^\s<>"\'`]+'
    potential_configs = re.findall(pattern, text)
    valid_configs = []
    for config in potential_configs:
        config = config.strip('.,;!?')
        is_valid = False
        if config.startswith('ss://'):
            if len(config) > 60: is_valid = True
        elif config.startswith(('vless://', 'vmess://', 'trojan://')):
            if len(config) > 100: is_valid = True
        if is_valid: valid_configs.append(config)
    return valid_configs

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def process_message(message, unique_configs_set, ordered_configs_list):
    if not message: return 0
    new_found_count = 0
    texts_to_scan = []
    if message.text: texts_to_scan.append(message.text)
    if message.is_reply:
        try:
            replied = await message.get_reply_message()
            if replied and replied.text: texts_to_scan.append(replied.text)
        except Exception: pass
    
    full_text = "\n".join(texts_to_scan)
    for config in find_and_reassemble_configs(full_text):
        renamed = rename_config(config, NEW_NAME)
        if renamed not in unique_configs_set:
            unique_configs_set.add(renamed)
            ordered_configs_list.append(renamed)
            new_found_count += 1
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                content_bytes = await message.download_media(bytes)
                file_content = content_bytes.decode('utf-8', errors='ignore')
                for config in find_and_reassemble_configs(file_content):
                    renamed = rename_config(config, NEW_NAME)
                    if renamed not in unique_configs_set:
                        unique_configs_set.add(renamed)
                        ordered_configs_list.append(renamed)
                        new_found_count += 1
            except Exception as e:
                print(f"  -> Could not process file: {e}")
    return new_found_count

async def main():
    print("--- Telegram Scraper v5.0 (Stateful) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set."); return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    # --- NEW STATEFUL LOGIC ---
    # Load existing configs (ordered)
    ordered_configs = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                content = f.read()
                if content: ordered_configs.extend(base64.b64decode(content).decode('utf-8').splitlines())
            print(f"Loaded {len(ordered_configs)} existing configs.")
        except Exception as e:
            print(f"Warning: Could not read subscription file: {e}")
    
    # Load last message IDs from our "bookmark" file
    last_ids = {}
    try:
        with open(STATE_FILE, 'r') as f:
            last_ids = json.load(f)
        print(f"Loaded last message IDs from {STATE_FILE}.")
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: {STATE_FILE} not found or invalid. Will scrape from scratch.")

    unique_configs = set(ordered_configs)
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        total_new_found = 0
        new_latest_ids = {}

        for group in TARGET_GROUPS:
            group_str = str(group) # Use string for JSON keys
            print(f"\n--- Scraping group: {group_str} ---")
            
            # Get the ID of the last message we processed for this group
            offset_id = last_ids.get(group_str, 0)
            print(f"Starting scrape from message ID after: {offset_id}")

            # Fetch all messages newer than the one we have bookmarked
            messages = await client.get_messages(group, offset_id=offset_id, limit=None)
            
            if messages:
                # The first message in the list is the newest one. This is our new bookmark.
                new_latest_ids[group_str] = messages[0].id
                print(f"Found {len(messages)} new message(s). New latest ID: {messages[0].id}")
                
                for message in messages:
                    total_new_found += await process_message(message, unique_configs, ordered_configs)
            else:
                print("No new messages found.")
                # Keep the old ID if there are no new messages
                if group_str in last_ids:
                    new_latest_ids[group_str] = last_ids[group_str]
        
        print(f"\nFound {total_new_found} new unique configs across all groups.")
            
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    # Prune the list if it's too long
    print(f"\nTotal unique configs before pruning: {len(ordered_configs)}")
    if len(ordered_configs) > MAX_CONFIGS:
        num_to_remove = len(ordered_configs) - MAX_CONFIGS
        print(f"List exceeds {MAX_CONFIGS}. Removing {num_to_remove} oldest configs.")
        ordered_configs = ordered_configs[num_to_remove:]
    
    # Save the updated subscription file
    if ordered_configs:
        content = base64.b64encode("\n".join(ordered_configs).encode('utf-8')).decode('utf-8')
        with open(OUTPUT_FILE, 'w') as f: f.write(content)
        print(f"Successfully saved {len(ordered_configs)} configs to {OUTPUT_FILE}")
    
    # Save the new latest message IDs to our "bookmark" file
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
