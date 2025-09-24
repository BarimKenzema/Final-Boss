import re, base64, os, asyncio
from telethon.sync import TelegramClient
from urllib.parse import quote

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

TARGET_GROUPS = [ 'letendorproxy' ] # Add your public group/channel usernames here
OUTPUT_FILE = 'mobo_net_subs.txt'
NEW_NAME = '@MoboNetPC'
# --- END OF CONFIGURATION ---

def find_configs(text):
    if not text: return []
    return re.findall(r'(vless|vmess|trojan|ss)://[^\s<>"\'`]+', text)

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def main():
    print("--- Telegram Scraper (User Account Mode on GitHub) ---")
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set.")
        return

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f:
            f.write(base64.b64decode(SESSION_STRING))
        print("Session file created from secret.")
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    configs = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                configs.update(base64.b64decode(f.read()).decode('utf-8').splitlines())
            print(f"Loaded {len(configs)} existing configs.")
        except Exception as e:
            print(f"Warning: Could not read existing file: {e}")
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized. Please generate a new session file."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            print(f"\n--- Scraping group: {group} ---")
            new = 0
            async for msg in client.iter_messages(group, limit=200):
                if msg and msg.text:
                    for cfg in find_configs(msg.text):
                        renamed = rename_config(cfg, NEW_NAME)
                        if renamed not in configs:
                            configs.add(renamed)
                            new += 1
            print(f"Found {new} new configs.")
    finally:
        await client.disconnect()
        print("\nDisconnected from Telegram.")
    
    if configs:
        content = base64.b64encode("\n".join(sorted(list(configs))).encode('utf-8')).decode('utf-8')
        with open(OUTPUT_FILE, 'w') as f:
            f.write(content)
        print(f"Successfully saved {len(configs)} total configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
