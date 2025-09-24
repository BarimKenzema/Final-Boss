import re, base64, os, asyncio
from telethon.sync import TelegramClient
from urllib.parse import quote

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

# Replace with the usernames of the public groups/channels
TARGET_GROUPS = [ 'letendorproxy' ]
OUTPUT_FILE = 'mobo_net_subs.txt'
NEW_NAME = '@MoboNetPC'
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
        config = config.strip('.,;!?') # Clean the link first
        
        # --- THIS IS THE NEW, INTELLIGENT FILTER ---
        is_valid = False
        if config.startswith('ss://'):
            # Shadowsocks configs can be shorter
            if len(config) > 60:
                is_valid = True
        elif config.startswith(('vless://', 'vmess://', 'trojan://')):
            # These are typically much longer
            if len(config) > 100:
                is_valid = True
        
        if is_valid:
            valid_configs.append(config)
            
    return valid_configs

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def process_message(message, found_configs):
    """
    Processes a single message, including text, replies, and files.
    """
    if not message:
        return 0

    new_configs_found = 0
    texts_to_scan = []

    if message.text:
        texts_to_scan.append(message.text)
        
    if message.is_reply:
        try:
            replied_message = await message.get_reply_message()
            if replied_message and replied_message.text:
                texts_to_scan.append(replied_message.text)
        except Exception:
            pass

    full_text_to_scan = "\n".join(texts_to_scan)
    configs = find_and_reassemble_configs(full_text_to_scan)
    
    for config in configs:
        renamed = rename_config(config, NEW_NAME)
        if renamed not in found_configs:
            found_configs.add(renamed)
            new_configs_found += 1
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024: # 1MB limit
            try:
                file_content_bytes = await message.download_media(bytes)
                file_content = file_content_bytes.decode('utf-8', errors='ignore')
                
                configs_in_file = find_and_reassemble_configs(file_content)
                for config in configs_in_file:
                    renamed = rename_config(config, NEW_NAME)
                    if renamed not in found_configs:
                        found_configs.add(renamed)
                        new_configs_found += 1
            except Exception as e:
                print(f"  -> Could not process file: {e}")

    return new_configs_found


async def main():
    print("--- Telegram Scraper v2.4 (Intelligent Filter) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set."); return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    configs = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                content = f.read()
                if content:
                    configs.update(base64.b64decode(content).decode('utf-8').splitlines())
            print(f"Loaded {len(configs)} existing configs.")
        except Exception as e:
            print(f"Warning: Could not read existing file: {e}")
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            print(f"\n--- Scraping group: {group} (Limit: 300 messages) ---")
            total_new_in_group = 0
            
            async for message in client.iter_messages(group, limit=300):
                new_found = await process_message(message, configs)
                total_new_in_group += new_found
            
            print(f"Found {total_new_in_group} new configs in this group.")
            
    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")
    
    if configs:
        content = base64.b64encode("\n".join(sorted(list(configs))).encode('utf-8')).decode('utf-8')
        with open(OUTPUT_FILE, 'w') as f: f.write(content)
        print(f"Successfully saved {len(configs)} total configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main()) 
