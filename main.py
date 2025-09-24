import re, base64, os, asyncio
from telethon.sync import TelegramClient
from urllib.parse import quote

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

TARGET_GROUPS = [ 'letendorproxy' ]
OUTPUT_FILE = 'mobo_net_subs.txt'
NEW_NAME = '@MoboNetPC'

# The maximum number of configs to keep in the subscription file.
MAX_CONFIGS = 444
# --- END OF CONFIGURATION ---

def find_and_reassemble_configs(text):
    """
    Finds V2Ray links with an intelligent filter that understands different
    protocols have different typical lengths.
    """
    if not text:
        return []
    
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
        if is_valid:
            valid_configs.append(config)
    return valid_configs

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def process_message(message, unique_configs, ordered_configs):
    """
    Processes a message and adds new, unique configs to both the
    uniqueness check set and the ordered list.
    """
    if not message:
        return 0

    new_configs_found = 0
    texts_to_scan = []
    if message.text: texts_to_scan.append(message.text)
    if message.is_reply:
        try:
            replied_message = await message.get_reply_message()
            if replied_message and replied_message.text:
                texts_to_scan.append(replied_message.text)
        except Exception: pass

    full_text_to_scan = "\n".join(texts_to_scan)
    for config in find_and_reassemble_configs(full_text_to_scan):
        renamed = rename_config(config, NEW_NAME)
        if renamed not in unique_configs:
            unique_configs.add(renamed)
            ordered_configs.append(renamed) # Add to the end of the list
            new_configs_found += 1
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                content_bytes = await message.download_media(bytes)
                file_content = content_bytes.decode('utf-8', errors='ignore')
                for config in find_and_reassemble_configs(file_content):
                    renamed = rename_config(config, NEW_NAME)
                    if renamed not in unique_configs:
                        unique_configs.add(renamed)
                        ordered_configs.append(renamed) # Add to the end
                        new_configs_found += 1
            except Exception as e:
                print(f"  -> Could not process file: {e}")

    return new_configs_found

async def main():
    print("--- Telegram Scraper v4.0 (Rolling List) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set."); return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    # We use a list to maintain order (oldest first)
    ordered_configs = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                content = f.read()
                if content:
                    # Splitlines preserves the order
                    ordered_configs.extend(base64.b64decode(content).decode('utf-8').splitlines())
            print(f"Loaded {len(ordered_configs)} existing configs.")
        except Exception as e:
            print(f"Warning: Could not read existing file: {e}")
    
    # We use a set for fast, efficient duplicate checking
    unique_configs = set(ordered_configs)
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        total_new_found = 0
        for group in TARGET_GROUPS:
            print(f"\n--- Scraping group: {group} (Limit: 300 messages) ---")
            async for message in client.iter_messages(group, limit=300):
                # Pass both the set and the list to be updated
                total_new_found += await process_message(message, unique_configs, ordered_configs)
        
        print(f"\nFound {total_new_found} new unique configs across all groups.")
            
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    # --- NEW ROLLING LIST LOGIC ---
    print(f"\nTotal unique configs before pruning: {len(ordered_configs)}")
    if len(ordered_configs) > MAX_CONFIGS:
        num_to_remove = len(ordered_configs) - MAX_CONFIGS
        print(f"List exceeds {MAX_CONFIGS}. Removing the {num_to_remove} oldest configs from the beginning.")
        # This slice keeps the last MAX_CONFIGS items
        ordered_configs = ordered_configs[num_to_remove:]
    
    if ordered_configs:
        content = base64.b64encode("\n".join(ordered_configs).encode('utf-8')).decode('utf-8')
        with open(OUTPUT_FILE, 'w') as f: f.write(content)
        print(f"Successfully saved {len(ordered_configs)} configs to {OUTPUT_FILE}")
    else:
        print("No configs found to save.")

if __name__ == "__main__":
    asyncio.run(main())
