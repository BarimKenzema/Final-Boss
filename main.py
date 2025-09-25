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

# Updated with all your provided groups and channels
TARGET_GROUPS = [
    'letendorproxy', 'MuteVpnN', 'ShadowProxy66', 'free_vpn02', 'falcunargo',
    'DirectVPN', 'DailyV2RY', 'daily_configs', 'configpluse', 'ghalagyann',
    'ghalagyann2', 'Leecher56', 'tigervpnorg', 'v2rayng_fars', 'Mrsoulb',
    'vpnplusee_free', 'vpnfail_v2ray', 'vpn_ioss', 'vmessorg', 'vmess_ir',
    'vlessconfig', 'vistav2ray', 'vipv2rayngnp', 'v2rayvpn2', 'v2rayroz',
    'v2rayopen', 'v2rayngvpn', 'v2rayng_matsuri', 'v2rayng_fast',
    'v2ray_official', 'v2pedia', 'toxicvid', 'tehranargo', 'spikevpn',
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net'
]
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@MoboNetPC'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'

# --- NEW: Dictionary for Country Code to Flag Emoji ---
COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲",
    "AO": "🇦🇴", "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼",
    "AX": "🇦🇽", "AZ": "🇦🇿", "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫",
    "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳",
    "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿",
    "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮",
    "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺",
    "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯",
    "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬",
    "EH": "🇪🇭", "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰",
    "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪",
    "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳",
    "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾",
    "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪",
    "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", "IS": "🇮🇸",
    "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬",
    "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼",
    "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰",
    "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦",
    "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱",
    "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸",
    "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾", "MZ": "🇲🇿",
    "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱",
    "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦",
    "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲",
    "PR": "🇵🇷", "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪",
    "RO": "🇷🇴", "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨",
    "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱",
    "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻",
    "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", "TG": "🇹🇬", "TH": "🇹🇭",
    "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷",
    "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸",
    "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮",
    "VN": "🇻🇳", "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦",
    "ZM": "🇿🇲", "ZW": "🇿🇼", "XX": "🌐"
}

# --- Caching & Helpers (No changes to core logic) ---
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
        if security != 'reality' and 'pbk' in params: security = 'reality'
        country = get_country_from_hostname(hostname).upper()
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

def rename_config(link, name, country_code):
    """NEW: Now takes a country code to add the flag."""
    flag = COUNTRY_FLAGS.get(country_code, "🌐")
    new_name_with_flags = f"{flag} {name} {flag}"
    return f"{link.split('#')[0]}#{quote(new_name_with_flags)}"

async def process_message(message, newly_found_configs_set):
    """Processes a message and adds new configs to a temporary set for this run."""
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
        newly_found_configs_set.add(config)
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                content_bytes = await message.download_media(bytes)
                file_content = content_bytes.decode('utf-8', errors='ignore')
                for config in find_and_validate_configs(file_content):
                    newly_found_configs_set.add(config)
            except Exception as e: print(f"  -> Could not process file: {e}")

def load_list_from_file(filepath):
    if not os.path.exists(filepath): return []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if content: return base64.b64decode(content).decode('utf-8').splitlines()
    except Exception: return []
    return []

async def main():
    print(f"--- Telegram Scraper v7.0 (Intelligent Sync) ---")
    global geoip_reader
    if not all([API_ID, API_HASH, SESSION_STRING]): print("FATAL: Required secrets not set."); return

    if not os.path.exists(GEOIP_DB_PATH):
        try:
            r = requests.get("https://git.io/GeoLite2-Country.mmdb", allow_redirects=True)
            with open(GEOIP_DB_PATH, 'wb') as f: f.write(r.content)
        except Exception as e: print(f"ERROR: Could not download GeoIP db. {e}")
    try: geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e: print(f"Warning: Could not load GeoIP db. {e}")

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: print(f"FATAL: Could not write session file. {e}"); return
    
    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: last_ids = json.load(f)
        
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    newly_scraped_configs = set()
    new_latest_ids = last_ids.copy()
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session not authorized."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            group_str = str(group)
            min_id = last_ids.get(group_str, 0)
            
            # --- NEW: Logic for initial scan ---
            is_new_group = min_id == 0
            limit = 44 if is_new_group else None
            scan_type = f"last {limit}" if is_new_group else f"since ID > {min_id}"
            print(f"\n--- Scraping group: {group_str} ({scan_type}) ---")
            
            messages_in_group = [msg async for msg in client.iter_messages(group, min_id=min_id, limit=limit)]
            
            if messages_in_group:
                new_latest_ids[group_str] = messages_in_group[0].id
                print(f"Found {len(messages_in_group)} message(s). New latest ID: {messages_in_group[0].id}")
                for message in messages_in_group:
                    await process_message(message, newly_scraped_configs)
            else:
                print("No new messages found.")
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    # --- Process and save all lists ---
    if newly_scraped_configs:
        print(f"\nFound {len(newly_scraped_configs)} new raw configs. Processing and renaming...")
        # Create a dictionary of all lists to manage
        all_lists = {}
        
        # Load all existing lists from disk
        all_paths = [OUTPUT_FILE_MAIN]
        for cat in ['protocols', 'networks', 'security', 'countries']:
            if os.path.exists(cat):
                all_paths.extend([os.path.join(cat, f) for f in os.listdir(cat) if f.endswith('.txt')])
        for path in all_paths:
            all_lists[path] = load_list_from_file(path)
        
        # Add new configs to the appropriate lists
        for config in newly_scraped_configs:
            attrs = get_config_attributes(config)
            if not attrs: continue
            
            renamed_config = rename_config(config, NEW_NAME, attrs['country'])
            
            # Define paths for this config
            paths = [
                OUTPUT_FILE_MAIN,
                f"protocols/{attrs['protocol']}.txt",
                f"networks/{attrs['network']}.txt",
                f"security/{attrs['security']}.txt",
                f"countries/{attrs['country'].lower()}.txt"
            ]
            for path in paths:
                if path not in all_lists: all_lists[path] = []
                # Add only if it's truly unique to this specific list
                if renamed_config not in set(all_lists[path]):
                    all_lists[path].append(renamed_config)
        
        # Prune and save all lists
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

    # Save the new state
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
