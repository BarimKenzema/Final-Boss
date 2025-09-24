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

# --- Caching for performance ---
dns_cache = {}
geoip_reader = None

def get_country_from_hostname(hostname):
    """Performs DNS and GeoIP lookup to find the country of a hostname."""
    if not hostname: return "XX"
    
    ip_addr = dns_cache.get(hostname)
    if not ip_addr:
        try:
            if ipaddress.ip_address(hostname):
                ip_addr = hostname
            else:
                res = resolver.Resolver(); res.nameservers = ["8.8.8.8", "1.1.1.1"]
                answer = res.resolve(hostname, 'A')
                ip_addr = answer[0].to_text()
            dns_cache[hostname] = ip_addr
        except Exception:
            dns_cache[hostname] = None
            return "XX"

    if not ip_addr or not geoip_reader: return "XX"
    
    try:
        return geoip_reader.country(ip_addr).country.iso_code or "XX"
    except geoip2.errors.AddressNotFoundError:
        return "XX"
    except Exception:
        return "XX"

def get_config_attributes(config_str):
    """Parses a config string to extract its attributes."""
    try:
        parsed = urlparse(config_str)
        params = parse_qs(parsed.query)
        
        protocol = parsed.scheme
        hostname = parsed.hostname
        network = params.get('type', ['tcp'])[0].lower()
        security = params.get('security', ['none'])[0].lower()
        country = get_country_from_hostname(hostname)

        return {
            'protocol': protocol,
            'network': network,
            'security': security,
            'country': country
        }
    except Exception:
        return None

def find_and_validate_configs(text):
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
            new_configs_list.append(renamed) # Add to the list of newly found configs
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                file_bytes = await message.download_media(bytes)
                file_content = file_bytes.decode('utf-8', errors='ignore')
                for config in find_and_validate_configs(file_content):
                    renamed = rename_config(config, NEW_NAME)
                    if renamed not in all_configs_set:
                        all_configs_set.add(renamed)
                        new_configs_list.append(renamed)
            except Exception as e: print(f"  -> Could not process file: {e}")

def load_all_lists():
    """Loads all existing subscription files into a dictionary."""
    all_lists = {}
    dirs_to_scan = [os.path.dirname(OUTPUT_FILE_MAIN)] + [d for d in os.listdir() if os.path.isdir(d) and d in ['protocols', 'networks', 'security', 'countries']]
    for d in dirs_to_scan:
        if not os.path.exists(d): continue
        for filename in os.listdir(d):
            if filename.endswith('.txt'):
                filepath = os.path.join(d, filename)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if content:
                            decoded = base64.b64decode(content).decode('utf-8').splitlines()
                            all_lists[filepath] = decoded
                except Exception: continue
    return all_lists

async def main():
    print(f"--- Telegram Scraper v6.0 (Categorizer & Rolling Lists) ---")
    global geoip_reader
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set."); return

    if not os.path.exists(GEOIP_DB_PATH):
        print("GeoIP database not found. Downloading...")
        try:
            r = requests.get("https://git.io/GeoLite2-Country.mmdb", allow_redirects=True)
            with open(GEOIP_DB_PATH, 'wb') as f: f.write(r.content)
            print("GeoIP database downloaded successfully.")
        except Exception as e:
            print(f"ERROR: Could not download GeoIP database. Error: {e}")

    try:
        geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e:
        print(f"Warning: Could not load GeoIP database. Country categorization will be limited. Error: {e}")

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e:
        print(f"FATAL: Could not write session file. Error: {e}"); return

    # --- Load all existing data ---
    all_lists = load_all_lists()
    all_configs_set = set(c for lst in all_lists.values() for c in lst)
    print(f"Loaded {len(all_lists)} existing subscription files containing {len(all_configs_set)} unique configs.")
    
    last_ids = {}
    try:
        with open(STATE_FILE, 'r') as f: last_ids = json.load(f)
    except Exception: pass
    
    # --- Scrape for new data ---
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    newly_found_configs = []
    new_latest_ids = {}
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session is not authorized."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            group_str = str(group)
            offset_id = last_ids.get(group_str, 0)
            print(f"\n--- Scraping group: {group_str} (since message ID: {offset_id}) ---")
            
            messages = await client.get_messages(group, offset_id=offset_id, limit=None)
            if messages:
                new_latest_ids[group_str] = messages[0].id
                print(f"Found {len(messages)} new message(s). New latest ID: {messages[0].id}")
                for message in messages:
                    await process_message(message, all_configs_set, newly_found_configs)
            else:
                if group_str in last_ids: new_latest_ids[group_str] = last_ids[group_str]
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")

    print(f"\nFound {len(newly_found_configs)} new unique configs across all groups.")

    # --- Add new configs to categories ---
    if newly_found_configs:
        # Add to main list first
        if OUTPUT_FILE_MAIN not in all_lists: all_lists[OUTPUT_FILE_MAIN] = []
        all_lists[OUTPUT_FILE_MAIN].extend(newly_found_configs)

        for config in newly_found_configs:
            attributes = get_config_attributes(config)
            if not attributes: continue

            # Create file paths and add to respective lists
            paths = [
                f"protocols/{attributes['protocol']}.txt",
                f"networks/{attributes['network']}.txt",
                f"security/{attributes['security']}.txt",
                f"countries/{attributes['country'].lower()}.txt"
            ]
            for path in paths:
                if path not in all_lists: all_lists[path] = []
                all_lists[path].append(config)

    # --- Prune all lists and save ---
    print("\n--- Pruning and saving all subscription files ---")
    for filepath, config_list in all_lists.items():
        if len(config_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(config_list) - MAX_CONFIGS_PER_FILE
            all_lists[filepath] = config_list[num_to_remove:]
            print(f"Pruned {filepath}: removed {num_to_remove} old configs.")
        
        # Ensure directory exists and save the file
        dir_name = os.path.dirname(filepath)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        content = base64.b64encode("\n".join(all_lists[filepath]).encode('utf-8')).decode('utf-8')
        with open(filepath, 'w') as f: f.write(content)
    
    print(f"Successfully saved/updated {len(all_lists)} subscription files.")

    # --- Save state for next run ---
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
