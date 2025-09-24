import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver

# --- CONFIGURATION (No changes needed) ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'
TARGET_GROUPS = [ 'letendorproxy', 'MuteVpnN', 'ShadowProxy66' ] # Assuming you added these
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@MoboNetPC'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
# --- END OF CONFIGURATION ---

# --- Caching for performance ---
dns_cache = {}
geoip_reader = None

def get_country_from_hostname(hostname):
    if not hostname: return "XX"
    ip_addr = dns_cache.get(hostname)
    if not ip_addr:
        try:
            if ipaddress.ip_address(hostname): ip_addr = hostname
            else: ip_addr = resolver.resolve(hostname, 'A')[0].to_text()
            dns_cache[hostname] = ip_addr
        except Exception:
            dns_cache[hostname] = None; return "XX"
    if not ip_addr or not geoip_reader: return "XX"
    try:
        return geoip_reader.country(ip_addr).country.iso_code or "XX"
    except Exception: return "XX"

def get_config_attributes(config_str):
    """
    Parses a config string to extract its attributes with corrected REALITY detection.
    """
    try:
        parsed = urlparse(config_str)
        params = parse_qs(parsed.query)
        
        protocol = parsed.scheme
        hostname = parsed.hostname
        network = params.get('type', ['tcp'])[0].lower()
        
        # --- CORRECTED REALITY DETECTION ---
        # A config is REALITY if security is explicitly set, OR if it has a public key (pbk).
        security = params.get('security', ['none'])[0].lower()
        if security != 'reality' and 'pbk' in params:
            security = 'reality'
        # --- END OF CORRECTION ---

        country = get_country_from_hostname(hostname)

        return {'protocol': protocol, 'network': network, 'security': security, 'country': country}
    except Exception: return None

# Helper functions (no changes)
def find_and_validate_configs(text):
    if not text: return []
    pattern = r'\b(?:vless|vmess|trojan|ss)://[^\s<>"\'`]+'
    valid_configs = []
    for config in re.findall(pattern, text):
        config = config.strip('.,;!?')
        is_valid = False
        if config.startswith('ss://') and len(config) > 60: is_valid = True
        elif config.startswith(('vless://', 'vmess://', 'trojan://')) and len(config) > 100: is_valid = True
        if is_valid: valid_configs.append(config)
    return valid_configs

def rename_config(link, name):
    return f"{link.split('#')[0]}#{quote(name)}"

async def process_message(message, all_configs_set, new_configs_list):
    if not message: return
    texts_to_scan = []
    if message.text: texts_to_scan.append(message.text)
    if message.is_reply:
        try:
            replied = await message.get_reply_message()
            if replied and replied.text: texts_to_scan.append(replied.text)
        except Exception: pass
    
    full_text = "\n".join(texts_to_scan)
    for config in find_and_validate_configs(full_text):
        renamed = rename_config(config, NEW_NAME)
        if renamed not in all_configs_set:
            all_configs_set.add(renamed)
            new_configs_list.append(renamed)
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                content_bytes = await message.download_media(bytes)
                file_content = content_bytes.decode('utf-8', errors='ignore')
                for config in find_and_validate_configs(file_content):
                    renamed = rename_config(config, NEW_NAME)
                    if renamed not in all_configs_set:
                        all_configs_set.add(renamed)
                        new_configs_list.append(renamed)
            except Exception as e: print(f"  -> Could not process file: {e}")

def load_all_lists():
    all_lists = {}
    dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d in ['protocols', 'networks', 'security', 'countries']]
    dirs.append('.') # Also scan the root directory for the main file
    for d in dirs:
        for filename in os.listdir(d):
            if filename.endswith('.txt'):
                filepath = os.path.join(d, filename)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if content: all_lists[filepath] = base64.b64decode(content).decode('utf-8').splitlines()
                except Exception: continue
    return all_lists

async def main():
    print(f"--- Telegram Scraper v6.1 (Corrected Sync & REALITY) ---")
    global geoip_reader
    if not all([API_ID, API_HASH, SESSION_STRING]): print("FATAL: Required secrets not set."); return

    if not os.path.exists(GEOIP_DB_PATH):
        print("GeoIP database not found. Downloading...")
        try:
            r = requests.get("https://git.io/GeoLite2-Country.mmdb", allow_redirects=True)
            with open(GEOIP_DB_PATH, 'wb') as f: f.write(r.content)
        except Exception as e: print(f"ERROR: Could not download GeoIP db. {e}")
    try: geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e: print(f"Warning: Could not load GeoIP db. {e}")

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: print(f"FATAL: Could not write session file. {e}"); return

    all_lists = load_all_lists()
    all_configs_set = set(c for lst in all_lists.values() for c in lst)
    print(f"Loaded {len(all_lists)} existing files containing {len(all_configs_set)} unique configs.")
    
    last_ids = {}
    try:
        with open(STATE_FILE, 'r') as f: last_ids = json.load(f)
    except Exception: pass
    
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    newly_found_configs = []
    new_latest_ids = {}
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            group_str = str(group)
            min_id_to_fetch = last_ids.get(group_str, 0)
            print(f"\n--- Scraping group: {group_str} (since message ID > {min_id_to_fetch}) ---")
            
            # --- CORRECTED SCRAPING LOGIC ---
            # Using iter_messages with min_id correctly fetches only new messages.
            messages_in_group = []
            async for message in client.iter_messages(group, min_id=min_id_to_fetch):
                messages_in_group.append(message)
                await process_message(message, all_configs_set, newly_found_configs)

            if messages_in_group:
                new_latest_ids[group_str] = messages_in_group[0].id
                print(f"Found {len(messages_in_group)} new message(s). New latest ID: {messages_in_group[0].id}")
            else:
                print("No new messages found.")
                if group_str in last_ids: new_latest_ids[group_str] = last_ids[group_str]
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")

    print(f"\nFound {len(newly_found_configs)} new unique configs across all groups.")

    if newly_found_configs:
        if OUTPUT_FILE_MAIN not in all_lists: all_lists[OUTPUT_FILE_MAIN] = []
        all_lists[OUTPUT_FILE_MAIN].extend(newly_found_configs)
        for config in newly_found_configs:
            attrs = get_config_attributes(config)
            if not attrs: continue
            paths = [
                f"protocols/{attrs['protocol']}.txt", f"networks/{attrs['network']}.txt",
                f"security/{attrs['security']}.txt", f"countries/{attrs['country'].lower()}.txt"
            ]
            for path in paths:
                if path not in all_lists: all_lists[path] = []
                all_lists[path].append(config)

    print("\n--- Pruning and saving all subscription files ---")
    for filepath, config_list in all_lists.items():
        if len(config_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(config_list) - MAX_CONFIGS_PER_FILE
            all_lists[filepath] = config_list[num_to_remove:]
            print(f"Pruned {filepath}: removed {num_to_remove} old configs.")
        dir_name = os.path.dirname(filepath)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        content = base64.b64encode("\n".join(all_lists[filepath]).encode('utf-8')).decode('utf-8')
        with open(filepath, 'w') as f: f.write(content)
    print(f"Successfully saved/updated {len(all_lists)} subscription files.")

    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
