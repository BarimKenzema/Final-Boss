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
    Finds V2Ray links. Crucially, it handles links that are split across
    multiple lines by Telegram.
    """
    # This pattern is designed to find the start of a config and grab everything
    # until the next likely config starts, or until whitespace. It's more greedy.
    pattern = r'\b(vless|vmess|trojan|ss)://[^\s<>"\'`]+'
    
    # First, find all potential matches
    potential_configs = re.findall(pattern, text)
    
    # Now, validate and clean them.
    valid_configs = []
    for config in potential_configs:
        # A simple but effective validation: A real config is usually long.
        if len(config) > 100:
            config = config.strip('.,;!?')
            valid_configs.append(config)
            
    return valid_configs

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def process_message(message, found_configs):
    """
    A dedicated function to process a single message, including its text,
    replies, forwards, and any attached text files.
    """
    if not message:
        return 0

    new_configs_found = 0
    texts_to_scan = []

    # 1. Add the main message text
    if message.text:
        texts_to_scan.append(message.text)
        
    # 2. --- THIS IS THE CORRECTED PART ---
    # Check if this message is a reply to another message
    if message.is_reply:
        try:
            # Fetch the message that was replied to
            replied_message = await message.get_reply_message()
            if replied_message and replied_message.text:
                texts_to_scan.append(replied_message.text)
        except Exception as e:
            # Sometimes the replied-to message is deleted or inaccessible
            print(f"  -> Note: Could not fetch a replied-to message: {e}")
    # --- END OF CORRECTION ---

    # 3. Add text from a forwarded message (with safety checks)
    if message.forward:
        try:
            # We don't need the original message, just the text if it's forwarded with the message itself
            if message.forward.chat and hasattr(message.forward.chat, 'text') and message.forward.chat.text:
                 texts_to_scan.append(message.forward.chat.text)
        except Exception:
            # This part can be complex, so we fail silently if it's an unusual forward
            pass

    # 4. Scan all collected texts
    full_text_to_scan = "\n".join(texts_to_scan)
    configs = find_and_reassemble_configs(full_text_to_scan)
    
    for config in configs:
        renamed = rename_config(config, NEW_NAME)
        if renamed not in found_configs:
            found_configs.add(renamed)
            new_configs_found += 1
            
    # 5. Check for and download text files
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        # Check file size to avoid downloading huge files (e.g., > 1MB)
        if message.document.size < 1024 * 1024:
            print(f"  -> Found a text file, downloading...")
            try:
                file_content_bytes = await message.download_media(bytes)
                file_content = file_content_bytes.decode('utf-8', errors='ignore') # Ignore decoding errors
                
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
    print("--- Telegram Scraper v2.1 (Robust & Corrected) ---")
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
            
            async  
