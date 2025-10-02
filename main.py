import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver

# --- CONFIGURATION (Your latest version) ---
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
    'v2pedia', 'sadoshockss', 'toxicvid', 'tehranargo', 'spikevpn', 'FG_Link',
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net'
]
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@VPNProxyTest'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿", "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫", "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺", "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭", "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰", "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾", "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾", "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦", "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲", "PR": "🇵🇷", "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴", "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷", "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳", "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼", "XX": "🔓"
}

# --- Caching & Helpers (Unchanged from your version) ---
dns_cache = {}
geoip_reader = None
def country_code_to_flag(iso_code): return COUNTRY_FLAGS.get(iso_code, "🌐")
def get_country_from_hostname(hostname):
    if not hostname: return "XX"
    ip_addr = dns_cache.get(hostname)
    if not ip_addr:
        try:
            if ipaddress.ip_address(hostname): ip_addr = hostname
            else: ip_addr = resolver.resolve(hostname, 'A')[0].to_text()
            dns_cache[hostname] = ip_addr
        except Exception: dns_cache[hostname] = None; return "XX"
    if not ip_addr or not geoip_reader: return "XX"
    try: return geoip_reader.country(ip_addr).country.iso_code or "XX"
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
    flag = country_code_to_flag(country_code)
    new_name_with_flags = f"{flag} {name} {flag}"
    return f"{link.split('#')[0]}#{quote(new_name_with_flags)}"
async def scrape_new_configs(client, groups, last_ids):
    scraped_configs = set()
    new_latest_ids = last_ids.copy()
    for group in groups:
        group_str = str(group)
        min_id = last_ids.get(group_str, 0)
        is_new_group = min_id == 0
        limit = 44 if is_new_group else None
        scan_type = f"last {limit}" if is_new_group else f"since ID > {min_id}"
        print(f"\n--- Scraping group: {group_str} ({scan_type}) ---")
        messages = [msg async for msg in client.iter_messages(group, min_id=min_id, limit=limit)]
        if messages:
            new_latest_ids[group_str] = messages[0].id
            print(f"Found {len(messages)} new message(s). New latest ID: {messages[0].id}")
            for message in messages:
                texts_to_scan = []
                if message.text: texts_to_scan.append(message.text)
                if message.is_reply:
                    try:
                        replied = await message.get_reply_message()
                        if replied and replied.text: texts_to_scan.append(replied.text)
                    except Exception: pass
                for config in find_and_validate_configs("\n".join(texts_to_scan)):
                    scraped_configs.add(config)
        else:
            print("No new messages found.")
    return scraped_configs, new_latest_ids
def load_list_from_file(filepath):
    if not os.path.exists(filepath): return []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if content: return base64.b64decode(content).decode('utf-8').splitlines()
    except Exception: return []
    return []

# --- MAIN FUNCTION ---
async def main():
    print(f"--- Telegram Scraper v9.0 (Corrected Independent Logic) ---")
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
    new_latest_ids = {}
    try:
        await client.connect()
        if not await client.is_user_authorized(): print("FATAL: Session not authorized."); return
        print("Successfully connected to Telegram.")
        newly_scraped_configs, new_latest_ids = await scrape_new_configs(client, TARGET_GROUPS, last_ids)
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    print(f"\nFound {len(newly_scraped_configs)} raw configs this run.")

    # --- THIS IS THE NEW, CORRECTED LIST PROCESSING LOGIC ---
    
    # 1. Prepare newly found configs with their attributes
    new_configs_data = []
    for raw_config in newly_scraped_configs:
        attrs = get_config_attributes(raw_config)
        if attrs:
            renamed_config = rename_config(raw_config, NEW_NAME, attrs['country'])
            new_configs_data.append({'renamed': renamed_config, 'attrs': attrs})

    # 2. Define all possible file paths we might need to update
    all_possible_paths = {OUTPUT_FILE_MAIN}
    for cat_dir in ['protocols', 'networks', 'security', 'countries', 'special']:
        if os.path.exists(cat_dir):
            all_possible_paths.update([os.path.join(cat_dir, f) for f in os.listdir(cat_dir) if f.endswith('.txt')])
    for item in new_configs_data:
        attrs = item['attrs']
        all_possible_paths.add(f"protocols/{attrs['protocol']}.txt")
        all_possible_paths.add(f"networks/{attrs['network']}.txt")
        all_possible_paths.add(f"security/{attrs['security']}.txt")
        all_possible_paths.add(f"countries/{attrs['country'].lower()}.txt")
        if attrs['network'] == 'ws' and attrs['country'] == 'XX': all_possible_paths.add('special/reality_xx.txt')
        if attrs['network'] == 'grpc' and attrs['country'] == 'XX': all_possible_paths.add('special/grpc_xx.txt')
        if attrs['security'] == 'reality' and attrs['network'] == 'tcp': all_possible_paths.add('special/reality_tcp.txt')

    # 3. Process each file independently
    print("\n--- Updating and pruning all subscription files ---")
    final_file_count = 0
    for path in sorted(list(all_possible_paths)):
        # Load the specific list for this file
        current_list = load_list_from_file(path)
        current_set = set(current_list)
        initial_count = len(current_list)
        
        # Add new configs that belong to this category and are not duplicates
        for new_config in new_configs_data:
            renamed_config = new_config['renamed']
            attrs = new_config['attrs']
            
            # Check if this config belongs in this file
            belongs = False
            if path == OUTPUT_FILE_MAIN: belongs = True
            elif f"protocols/{attrs['protocol']}.txt" == path: belongs = True
            elif f"networks/{attrs['network']}.txt" == path: belongs = True
            elif f"security/{attrs['security']}.txt" == path: belongs = True
            elif f"countries/{attrs['country'].lower()}.txt" == path: belongs = True
            elif path == 'special/reality_xx.txt' and attrs['network'] == 'ws' and attrs['country'] == 'XX': belongs = True
            elif path == 'special/grpc_xx.txt' and attrs['network'] == 'grpc' and attrs['country'] == 'XX': belongs = True
            elif path == 'special/reality_tcp.txt' and attrs['security'] == 'reality' and attrs['network'] == 'tcp': belongs = True

            if belongs and renamed_config not in current_set:
                current_list.append(renamed_config)
                current_set.add(renamed_config) # Update the set for this list

        # Prune this specific list if it exceeds the max
        if len(current_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(current_list) - MAX_CONFIGS_PER_FILE
            current_list = current_list[num_to_remove:]
            print(f"Pruned {path}: had {initial_count} + new, removed {num_to_remove} oldest.")
        
        # Save this specific list back to its file
        if current_list:
            dir_name = os.path.dirname(path)
            if dir_name: os.makedirs(dir_name, exist_ok=True)
            content = base64.b64encode("\n".join(current_list).encode('utf-8')).decode('utf-8')
            with open(path, 'w') as f: f.write(content)
            final_file_count += 1
    
    print(f"\nSuccessfully saved/updated {final_file_count} subscription files.")
    
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
