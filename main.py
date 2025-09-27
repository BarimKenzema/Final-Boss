import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver

# --- CONFIGURATION (Unchanged) ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

TARGET_GROUPS = [
    'letendorproxy', 'MuteVpnN', 'ShadowProxy66', 'free_vpn02', 'falcunargo',
    'DirectVPN', 'DailyV2RY', 'daily_configs', 'configpluse', 'ghalagyann',
    'ghalagyann2', 'Leecher56', 'tigervpnorg', 'v2rayng_fars', 'Mrsoulb',
    'vpnplusee_free', 'GetConfigIR', 'Pro_v2rayShop', 'surfboardv2ray', 
    'v2ray_official', 'horn_proxy', 'ocean_peace_mind', 'safavpnn', 'vless_config', 
    'vpn_tehran', 'vpnz4', 'customv2ray', 'vpnfail_v2ray', 'vpn_ioss', 'vmessorg', 
    'vmess_ir', 'vlessconfig', 'vistav2ray', 'vipv2rayngnp', 'v2rayvpn2', 
    'v2rayroz', 'v2rayopen', 'v2rayngvpn', 'v2rayng_matsuri', 'v2rayng_fast',
    'v2pedia', 'sadoshockss', 'toxicvid', 'tehranargo', 'spikevpn',
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net'
]
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@MoboNetPC'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿", "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫", "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺", "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭", "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰", "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾", "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾", "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦", "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲", "PR": "🇵🇷", "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴", "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷", "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳", "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼", "XX": "🔓"
}

dns_cache = {}
geoip_reader = None

def country_code_to_flag(iso_code): return COUNTRY_FLAGS.get(iso_code, "🔓")

# --- THIS FUNCTION IS THE ONLY PART THAT HAS CHANGED ---
def get_country_from_hostname(hostname):
    """Performs DNS and GeoIP lookup with enhanced logging for failures."""
    if not hostname: return "XX"
    ip_addr = dns_cache.get(hostname)
    if not ip_addr:
        try:
            if ipaddress.ip_address(hostname): ip_addr = hostname
            else: ip_addr = resolver.resolve(hostname, 'A')[0].to_text()
            dns_cache[hostname] = ip_addr
        except Exception as e:
            # NEW: Log the DNS failure
            print(f"  -> DNS lookup failed for '{hostname}': {e}")
            dns_cache[hostname] = None
            return "XX"
    if not ip_addr: return "XX"

    if not geoip_reader: return "XX"
    try:
        return geoip_reader.country(ip_addr).country.iso_code or "XX"
    except geoip2.errors.AddressNotFoundError:
        # NEW: Log the "not found" error
        print(f"  -> GeoIP lookup failed: IP '{ip_addr}' not found in the database.")
        return "XX"
    except Exception as e:
        # NEW: Log any other GeoIP errors
        print(f"  -> GeoIP lookup failed for '{ip_addr}': {e}")
        return "XX"

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
    flag = country_code_to_flag(country_code)
    new_name_with_flags = f"{flag} {name} {flag}"
    return f"{link.split('#')[0]}#{quote(new_name_with_flags)}"

async def process_message(message, newly_found_configs_map, all_known_configs_set):
    texts_to_scan = []
    if message.text: texts_to_scan.append(message.text)
    if message.is_reply:
        try:
            replied = await message.get_reply_message()
            if replied and replied.text: texts_to_scan.append(replied.text)
        except Exception: pass
    
    full_text = "\n".join(texts_to_scan)
    for config in find_and_validate_configs(full_text):
        base_config = config.split('#')[0]
        if base_config not in all_known_configs_set:
            all_known_configs_set.add(base_config)
            attrs = get_config_attributes(config)
            if attrs: newly_found_configs_map[base_config] = attrs
            
    if message.document and hasattr(message.document, 'mime_type') and message.document.mime_type == 'text/plain':
        if message.document.size < 1024 * 1024:
            try:
                content_bytes = await message.download_media(bytes)
                file_content = content_bytes.decode('utf-8', errors='ignore')
                for config in find_and_validate_configs(file_content):
                    base_config = config.split('#')[0]
                    if base_config not in all_known_configs_set:
                        all_known_configs_set.add(base_config)
                        attrs = get_config_attributes(config)
                        if attrs: newly_found_configs_map[base_config] = attrs
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
    print(f"--- Telegram Scraper v7.0 (with Enhanced Logging) ---")
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
    
    # The rest of the main function remains exactly the same as v7.0
    all_lists = {}
    all_paths = [OUTPUT_FILE_MAIN]
    for cat_dir in ['protocols', 'networks', 'security', 'countries']:
        if os.path.exists(cat_dir):
            all_paths.extend([os.path.join(cat_dir, f) for f in os.listdir(cat_dir) if f.endswith('.txt')])
    for path in all_paths:
        all_lists[path] = load_list_from_file(path)
    all_known_configs_set = set(c.split('#')[0] for lst in all_lists.values() for c in lst)
    print(f"Loaded {len(all_lists)} existing files containing {len(all_known_configs_set)} unique base configs.")

    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: last_ids = json.load(f)
        
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    newly_found_configs_map = {}
    new_latest_ids = last_ids.copy()
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session not authorized."); return
        print("Successfully connected to Telegram.")
        
        for group in TARGET_GROUPS:
            group_str = str(group)
            min_id = last_ids.get(group_str, 0)
            is_new_group = min_id == 0
            limit = 11 if is_new_group else None
            scan_type = f"last {limit}" if is_new_group else f"since ID > {min_id}"
            print(f"\n--- Scraping group: {group_str} ({scan_type}) ---")
            messages = [msg async for msg in client.iter_messages(group, min_id=min_id, limit=limit)]
            if messages:
                new_latest_ids[group_str] = messages[0].id
                print(f"Found {len(messages)} new message(s). New latest ID: {messages[0].id}")
                for message in messages:
                    await process_message(message, newly_found_configs_map, all_known_configs_set)
            else:
                print("No new messages found.")
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")

    print(f"\nFound {len(newly_found_configs_map)} new unique configs in this run.")

    if newly_found_configs_map:
        for base_config, attrs in newly_found_configs_map.items():
            renamed_config = rename_config(base_config, NEW_NAME, attrs['country'])
            
            paths = [
                OUTPUT_FILE_MAIN,
                f"protocols/{attrs['protocol']}.txt",
                f"networks/{attrs['network']}.txt",
                f"security/{attrs['security']}.txt",
                f"countries/{attrs['country'].lower()}.txt"
            ]
            for path in paths:
                if path not in all_lists: all_lists[path] = []
                if renamed_config not in set(all_lists[path]):
                    all_lists[path].append(renamed_config)

    # Special Category: reality_grpc
            if attrs['security'] == 'reality' and attrs['network'] == 'grpc':
                special_path = 'special/reality_grpc.txt'
                if special_path not in all_lists: all_lists[special_path] = []
                all_lists[special_path].append(renamed_config)
            
            # Special Category: grpc_xx
            if attrs['network'] == 'grpc' and attrs['country'] == 'XX':
                special_path_grpc_xx = 'special/grpc_xx.txt'
                if special_path_grpc_xx not in all_lists: all_lists[special_path_grpc_xx] = []
                all_lists[special_path_grpc_xx].append(renamed_config)
            # --- END OF NEW CODE BLOCK ---
    
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
    
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
