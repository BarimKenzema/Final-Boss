import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'
TARGET_GROUPS = [ 'letendorproxy', 'MuteVpnN', 'ShadowProxy66' ]
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@MoboNetPC'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
# --- END OF CONFIGURATION ---

# --- Caching & Helpers ---
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
    try:
        parsed = urlparse(config_str)
        params = parse_qs(parsed.query)
        protocol = parsed.scheme
        hostname = parsed.hostname
        network = params.get('type', ['tcp'])[0].lower()
        security = params.get('security', ['none'])[0].lower()
        if security != 'reality' and 'pbk' in params:
            security = 'reality'
        country = get_country_from_hostname(hostname)
        return {'protocol': protocol, 'network': network, 'security': security, 'country': country}
    except Exception: return None

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

async def scrape_new_configs(client, groups, last_ids):
    """Scrapes all groups and returns a set of new, unique configs."""
    freshly_scraped_set = set()
    new_latest_ids = last_ids.copy() # Start with old IDs

    for group in groups:
        group_str = str(group)
        min_id = last_ids.get(group_str, 0)
        print(f"\n--- Scraping group: {group_str} (since message ID > {min_id}) ---")
        
        messages_in_group = [msg async for msg in client.iter_messages(group, min_id=min_id)]
        
        if messages_in_group:
            new_latest_ids[group_str] = messages_in_group[0].id
            print(f"Found {len(messages_in_group)} new message(s). New latest ID: {messages_in_group[0].id}")
            for message in messages_in_group:
                texts_to_scan = []
                if message.text: texts_to_scan.append(message.text)
                if message.is_reply:
                    try:
                        replied = await message.get_reply_message()
                        if replied and replied.text: texts_to_scan.append(replied.text)
                    except Exception: pass
                
                full_text = "\n".join(texts_to_scan)
                for config in find_and_validate_configs(full_text):
                    freshly_scraped_set.add(rename_config(config, NEW_NAME))
        else:
            print("No new messages found.")
            
    return freshly_scraped_set, new_latest_ids

def load_list_from_file(filepath):
    """Loads a single subscription list from a file."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if content: return base64.b64decode(content).decode('utf-8').splitlines()
    except Exception:
        return []
    return []

async def main():
    print(f"--- Telegram Scraper v6.2 (Independent List Logic) ---")
    global geoip_reader
    if not all([API_ID, API_HASH, SESSION_STRING]): print("FATAL: Required secrets not set."); return

    # Setup GeoIP
    if not os.path.exists(GEOIP_DB_PATH):
        try:
            r = requests.get("https://git.io/GeoLite2-Country.mmdb", allow_redirects=True)
            with open(GEOIP_DB_PATH, 'wb') as f: f.write(r.content)
        except Exception as e: print(f"ERROR: Could not download GeoIP db. {e}")
    try: geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e: print(f"Warning: Could not load GeoIP db. {e}")

    # Connect to Telegram
    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: print(f"FATAL: Could not write session file. {e}"); return
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    # --- Scrape first to get a list of new configs ---
    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: last_ids = json.load(f)
        
    newly_found_configs = set()
    new_latest_ids = {}
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session not authorized."); return
        print("Successfully connected to Telegram.")
        newly_found_configs, new_latest_ids = await scrape_new_configs(client, TARGET_GROUPS, last_ids)
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    print(f"\nFound {len(newly_found_configs)} new unique configs in this run.")

    # --- Now, process all lists independently ---
    # Create a dictionary to hold all file paths and their desired contents
    all_lists = {}

    # 1. Process the main list
    main_list = load_list_from_file(OUTPUT_FILE_MAIN)
    main_list_set = set(main_list)
    added_to_main = 0
    for config in newly_found_configs:
        if config not in main_list_set:
            main_list.append(config)
            added_to_main += 1
    all_lists[OUTPUT_FILE_MAIN] = main_list
    print(f"Added {added_to_main} new configs to the main list.")

    # 2. Process all category lists
    for config in newly_found_configs:
        attrs = get_config_attributes(config)
        if not attrs: continue
        
        paths = {
            f"protocols/{attrs['protocol']}.txt": 'protocol',
            f"networks/{attrs['network']}.txt": 'network',
            f"security/{attrs['security']}.txt": 'security',
            f"countries/{attrs['country'].lower()}.txt": 'country'
        }
        for path in paths:
            if path not in all_lists:
                all_lists[path] = load_list_from_file(path)
            
            # Check for duplicates before adding
            if config not in set(all_lists[path]):
                all_lists[path].append(config)
    
    # 3. Prune and save all lists
    print("\n--- Pruning and saving all subscription files ---")
    for filepath, config_list in all_lists.items():
        if len(config_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(config_list) - MAX_CONFIGS_PER_FILE
            config_list = config_list[num_to_remove:]
            print(f"Pruned {filepath}: removed {num_to_remove} old configs.")
        
        dir_name = os.path.dirname(filepath)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        content = base64.b64encode("\n".join(config_list).encode('utf-8')).decode('utf-8')
        with open(filepath, 'w') as f: f.write(content)
        
    print(f"\nSuccessfully saved/updated {len(all_lists)} subscription files.")
    
    # 4. Save the new state
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
