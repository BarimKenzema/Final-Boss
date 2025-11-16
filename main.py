import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote, urlencode, urlunparse
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver
import hashlib

print("--- Telegram Scraper v12.0 (Historical Databases) START ---")

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')
SESSION_NAME = 'my_telegram_session'

TARGET_GROUPS = [
    'letendorproxy', 'MuteVpnN', 'ShadowProxy66', 'free_vpn02', 'falcunargo', 'FreakConfig',
    'DirectVPN', 'DailyV2RY', 'daily_configs', 'configpluse', 'ghalagyann', 'meli_proxyy',
    'ghalagyann2', 'Leecher56', 'tigervpnorg', 'v2rayng_fars', 'Mrsoulb', 'mtproxy_lists',
    'vpnplusee_free', 'GetConfigIR', 'Pro_v2rayShop', 'surfboardv2ray', 'V2rayBaaz', 
    'v2ray_official', 'horn_proxy', 'ocean_peace_mind', 'safavpnn', 'vless_config', 
    'vpn_tehran', 'vpnz4', 'customv2ray', 'vpnfail_v2ray', 'vpn_ioss', 'vmessorg', 
    'vmess_ir', 'vlessconfig', 'vistav2ray', 'vipv2rayngnp', 'v2rayvpn2', 
    'v2rayroz', 'v2rayopen', 'v2rayngvpn', 'v2rayng_matsuri', 'v2rayng_fast',
    'v2pedia', 'sadoshockss', 'toxicvid', 'tehranargo', 'spikevpn', 'FG_Link',
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net'
]

# NEW: Database files
DATABASE_SNI = 'database_sni.txt'
DATABASE_IP = 'database_ip.txt'
ACTIVE_FILE_SNI = 'active_sni_configs.txt'
ACTIVE_FILE_IP = 'active_ip_configs.txt'
MAX_ACTIVE_CONFIGS = 1111

# Categorized files (stay at 444)
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@VPNProxyTest'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'

COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿", "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫", "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺", "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭", "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰", "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾", "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾", "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦", "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲", "PR": "🇵🇷", "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴", "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷", "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳", "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼", "XX": "🔓"
}

# --- Caching & Global Variables ---
dns_cache = {}
geoip_reader = None

# --- DATABASE FUNCTIONS (NEW) ---

def load_database(db_file):
    """Load historical database and return set of config strings."""
    if not os.path.exists(db_file):
        return set()
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return set()
            decoded = base64.b64decode(content).decode('utf-8')
            return set(decoded.splitlines())
    except Exception as e:
        print(f"Warning: Could not load {db_file}: {e}")
        return set()

def save_database(db_file, configs_set):
    """Save configs to database (base64 encoded)."""
    try:
        content = "\n".join(sorted(configs_set))
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(db_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
    except Exception as e:
        print(f"Error saving {db_file}: {e}")

def save_active_file(filepath, configs_list):
    """Save active subscription file (base64 encoded, max 1111 configs)."""
    try:
        configs_to_save = configs_list[-MAX_ACTIVE_CONFIGS:] if len(configs_list) > MAX_ACTIVE_CONFIGS else configs_list
        content = "\n".join(configs_to_save)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(encoded)
        return len(configs_to_save)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return 0

# --- HELPER FUNCTIONS ---

def country_code_to_flag(iso_code): 
    return COUNTRY_FLAGS.get(iso_code, "🌐")

def resolve_domain_to_ip(hostname):
    if not hostname:
        return None
    try:
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass
    if hostname in dns_cache:
        return dns_cache[hostname]
    try:
        ip_addr = resolver.resolve(hostname, 'A')[0].to_text()
        dns_cache[hostname] = ip_addr
        return ip_addr
    except Exception:
        dns_cache[hostname] = None
        return None

def parse_vmess_config(config_str):
    try:
        encoded = config_str.replace('vmess://', '').strip().rstrip('.,;!?')
        missing_padding = len(encoded) % 4
        if missing_padding:
            encoded += '=' * (4 - missing_padding)
        decoded_bytes = base64.b64decode(encoded, validate=True)
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                decoded = decoded_bytes.decode(encoding, errors='ignore')
                parsed = json.loads(decoded)
                if 'add' in parsed and 'port' in parsed and 'id' in parsed:
                    return parsed
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        return None
    except Exception:
        return None

def get_config_fingerprint(config_str):
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return None
            addr = vmess_data.get('add', '')
            port = vmess_data.get('port', '')
            uuid = vmess_data.get('id', '')
            return f"vmess|{addr}|{port}|{uuid}"
        elif config_str.startswith(('vless://', 'trojan://')):
            parsed = urlparse(config_str)
            protocol = parsed.scheme
            uuid = parsed.username or ''
            host = parsed.hostname or ''
            try:
                port = parsed.port or ''
            except:
                port = ''
            return f"{protocol}|{host}|{port}|{uuid}"
        elif config_str.startswith('ss://'):
            parts = config_str.split('@')
            if len(parts) == 2:
                server_part = parts[1].split('#')[0]
                method_pass = parts[0].replace('ss://', '')
                return f"ss|{server_part}|{method_pass}"
        return None
    except Exception:
        return None

def replace_address_with_sni(config_str):
    """Replace address with SNI if available."""
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return config_str
            sni = vmess_data.get('sni', '').strip()
            host = vmess_data.get('host', '').strip()
            current_add = vmess_data.get('add', '').strip()
            new_addr = sni or host
            if new_addr and new_addr != current_add:
                vmess_data['add'] = new_addr
                new_json = json.dumps(vmess_data, separators=(',', ':'))
                new_encoded = base64.b64encode(new_json.encode('utf-8')).decode('utf-8')
                return f"vmess://{new_encoded}"
            return config_str
        elif config_str.startswith(('vless://', 'trojan://')):
            parsed = urlparse(config_str)
            params = parse_qs(parsed.query)
            sni_list = params.get('sni', [])
            if not sni_list or not sni_list[0]:
                return config_str
            sni = sni_list[0].strip()
            current_host = parsed.hostname
            if sni and sni != current_host:
                new_netloc = sni
                try:
                    if parsed.port:
                        new_netloc = f"{sni}:{parsed.port}"
                except:
                    pass
                if parsed.username:
                    new_netloc = f"{parsed.username}@{new_netloc}"
                new_parsed = parsed._replace(netloc=new_netloc)
                return new_parsed.geturl()
            return config_str
        return config_str
    except Exception:
        return config_str

def replace_domain_with_ip(config_str):
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return config_str
            domain = vmess_data.get('add', '')
            ip_addr = resolve_domain_to_ip(domain)
            if ip_addr and ip_addr != domain:
                if vmess_data.get('tls') == 'tls' and not vmess_data.get('sni'):
                    vmess_data['sni'] = domain
                vmess_data['add'] = ip_addr
                new_json = json.dumps(vmess_data, separators=(',', ':'))
                new_encoded = base64.b64encode(new_json.encode('utf-8')).decode('utf-8')
                return f"vmess://{new_encoded}"
            return config_str
        elif config_str.startswith(('vless://', 'trojan://')):
            parsed = urlparse(config_str)
            domain = parsed.hostname
            if not domain:
                return config_str
            ip_addr = resolve_domain_to_ip(domain)
            if ip_addr and ip_addr != domain:
                params = parse_qs(parsed.query)
                security = params.get('security', [''])[0]
                if security in ['tls', 'reality'] and 'sni' not in params:
                    params['sni'] = [domain]
                network_type = params.get('type', [''])[0]
                if network_type in ['http', 'ws'] and 'host' not in params:
                    params['host'] = [domain]
                new_query = urlencode(params, doseq=True)
                new_netloc = ip_addr
                try:
                    if parsed.port:
                        new_netloc = f"{ip_addr}:{parsed.port}"
                except:
                    pass
                if parsed.username:
                    new_netloc = f"{parsed.username}@{new_netloc}"
                new_parsed = parsed._replace(netloc=new_netloc, query=new_query)
                return new_parsed.geturl()
            return config_str
        elif config_str.startswith('ss://'):
            parts = config_str.split('@')
            if len(parts) != 2:
                return config_str
            prefix, suffix = parts[0], parts[1]
            fragment = ''
            if '#' in suffix:
                suffix, fragment = suffix.split('#', 1)
                fragment = f'#{fragment}'
            domain, port = suffix.rsplit(':', 1) if ':' in suffix else (suffix, '443')
            ip_addr = resolve_domain_to_ip(domain)
            if ip_addr and ip_addr != domain:
                return f"{prefix}@{ip_addr}:{port}{fragment}"
            return config_str
        return config_str
    except Exception:
        return config_str

def get_country_from_hostname(hostname):
    if not hostname: 
        return "XX"
    ip_addr = resolve_domain_to_ip(hostname)
    if not ip_addr or not geoip_reader: 
        return "XX"
    try: 
        return geoip_reader.country(ip_addr).country.iso_code or "XX"
    except Exception: 
        return "XX"

def get_config_attributes(config_str):
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return None
            protocol = 'vmess'
            network = vmess_data.get('net', 'tcp').lower().strip()
            security = vmess_data.get('tls', 'none').lower().strip()
            country = get_country_from_hostname(vmess_data.get('add', '')).upper()
        else:
            parsed = urlparse(config_str)
            params = parse_qs(parsed.query)
            protocol = parsed.scheme.lower().strip()
            hostname = parsed.hostname
            network = params.get('type', ['tcp'])[0].lower().strip()
            security = params.get('security', ['none'])[0].lower().strip()
            if security != 'reality' and 'pbk' in params: 
                security = 'reality'
            country = get_country_from_hostname(hostname).upper()
        
        valid_protocols = ['vmess', 'vless', 'trojan', 'ss']
        if not protocol or protocol not in valid_protocols:
            return None
        valid_networks = ['tcp', 'kcp', 'ws', 'http', 'quic', 'grpc', 'h2', 'httpupgrade', 'splithttp']
        if not network or network not in valid_networks:
            network = 'tcp'
        valid_security = ['none', 'tls', 'reality', 'xtls']
        if not security or security not in valid_security:
            security = 'none'
        if not country or len(country) != 2 or not country.isalpha():
            country = 'XX'
        
        return {'protocol': protocol, 'network': network, 'security': security, 'country': country}
    except Exception:
        return None

def find_and_validate_configs(text):
    if not text: 
        return []
    pattern = r'\b(?:vless|vmess|trojan|ss)://[^\s<>"\'`]+'
    valid_configs = []
    for config in re.findall(pattern, text):
        config = config.strip('.,;!?')
        is_valid = False
        if config.startswith('ss://') and len(config) > 60: 
            is_valid = True
        elif config.startswith(('vless://', 'vmess://', 'trojan://')) and len(config) > 100: 
            is_valid = True
        if is_valid: 
            valid_configs.append(config)
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
                if message.text: 
                    texts_to_scan.append(message.text)
                if message.is_reply:
                    try:
                        replied = await message.get_reply_message()
                        if replied and replied.text: 
                            texts_to_scan.append(replied.text)
                    except Exception: 
                        pass
                for config in find_and_validate_configs("\n".join(texts_to_scan)):
                    scraped_configs.add(config)
        else:
            print("No new messages found.")
    return scraped_configs, new_latest_ids

def load_list_from_file(filepath):
    if not os.path.exists(filepath): 
        return []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if content: 
                return base64.b64decode(content).decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []
    return []

# --- MAIN FUNCTION ---
async def main():
    global geoip_reader
    
    if not all([API_ID, API_HASH, SESSION_STRING]): 
        print("FATAL: Required secrets not set.")
        return

    # GeoIP Download
    if not os.path.exists(GEOIP_DB_PATH):
        print("Downloading GeoIP database...")
        urls = [
            "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb",
            "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb",
            "https://git.io/GeoLite2-Country.mmdb"
        ]
        downloaded = False
        for url in urls:
            try:
                r = requests.get(url, allow_redirects=True, timeout=30)
                if r.status_code == 200 and len(r.content) > 1000:
                    with open(GEOIP_DB_PATH, 'wb') as f: 
                        f.write(r.content)
                    print(f"✓ GeoIP downloaded")
                    downloaded = True
                    break
            except:
                continue
        if not downloaded:
            print("WARNING: Could not download GeoIP database.")
    
    try: 
        geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e: 
        print(f"Warning: Could not load GeoIP: {e}")

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: 
            f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: 
        print(f"FATAL: Could not write session file: {e}")
        return
    
    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: 
            last_ids = json.load(f)
        
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    newly_scraped_configs = set()
    new_latest_ids = {}
    
    try:
        await client.connect()
        if not await client.is_user_authorized(): 
            print("FATAL: Session not authorized.")
            return
        print("Successfully connected to Telegram.")
        newly_scraped_configs, new_latest_ids = await scrape_new_configs(client, TARGET_GROUPS, last_ids)
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    print(f"\nFound {len(newly_scraped_configs)} raw configs this run.")

    # ========== SNI DATABASE PROCESSING ==========
    print(f"\n{'='*70}")
    print(f"  SNI DATABASE PROCESSING")
    print(f"{'='*70}")
    
    db_sni = load_database(DATABASE_SNI)
    print(f"Loaded {len(db_sni)} historical SNI configs from database")
    
    sni_configs_list = []
    for config in newly_scraped_configs:
        sni_config = replace_address_with_sni(config)
        attrs = get_config_attributes(sni_config)
        if attrs:
            renamed = rename_config(sni_config, NEW_NAME, attrs['country'])
            sni_configs_list.append(renamed)
        else:
            sni_configs_list.append(sni_config)
    
    sni_configs_set = set(sni_configs_list)
    new_sni_configs = sni_configs_set - db_sni
    print(f"Found {len(new_sni_configs)} NEW SNI configs")
    
    if new_sni_configs:
        db_sni.update(new_sni_configs)
        save_database(DATABASE_SNI, db_sni)
        print(f"✓ Updated {DATABASE_SNI} (now {len(db_sni)} total)")
        new_sni_list = list(new_sni_configs)
        saved_count = save_active_file(ACTIVE_FILE_SNI, new_sni_list)
        print(f"✓ Saved {saved_count} newest to {ACTIVE_FILE_SNI}")
    else:
        print(f"No new SNI configs to add")
        save_active_file(ACTIVE_FILE_SNI, [])

    # ========== IP DATABASE PROCESSING ==========
    print(f"\n{'='*70}")
    print(f"  IP DATABASE PROCESSING")
    print(f"{'='*70}")
    
    db_ip = load_database(DATABASE_IP)
    print(f"Loaded {len(db_ip)} historical IP configs from database")
    
    new_configs_data = []
    seen_fingerprints = set()
    stats = {
        'total_scraped': len(newly_scraped_configs),
        'failed_parse': 0,
        'duplicates': 0,
        'valid_unique': 0
    }
    
    for raw_config in newly_scraped_configs:
        ip_config = replace_domain_with_ip(raw_config)
        fingerprint = get_config_fingerprint(ip_config)
        if fingerprint and fingerprint in seen_fingerprints:
            stats['duplicates'] += 1
            continue
        attrs = get_config_attributes(ip_config)
        if attrs:
            if fingerprint:
                seen_fingerprints.add(fingerprint)
            renamed_config = rename_config(ip_config, NEW_NAME, attrs['country'])
            new_configs_data.append({
                'renamed': renamed_config, 
                'attrs': attrs,
                'fingerprint': fingerprint
            })
            stats['valid_unique'] += 1
        else:
            stats['failed_parse'] += 1
    
    print(f"Processed: {stats['valid_unique']} valid, {stats['duplicates']} duplicates, {stats['failed_parse']} failed")
    
    ip_configs_list = [item['renamed'] for item in new_configs_data]
    ip_configs_set = set(ip_configs_list)
    new_ip_configs = ip_configs_set - db_ip
    print(f"Found {len(new_ip_configs)} NEW IP configs")
    
    if new_ip_configs:
        db_ip.update(new_ip_configs)
        save_database(DATABASE_IP, db_ip)
        print(f"✓ Updated {DATABASE_IP} (now {len(db_ip)} total)")
        new_ip_list = list(new_ip_configs)
        saved_count = save_active_file(ACTIVE_FILE_IP, new_ip_list)
        print(f"✓ Saved {saved_count} newest to {ACTIVE_FILE_IP}")
    else:
        print(f"No new IP configs to add")
        save_active_file(ACTIVE_FILE_IP, [])

    # ========== CATEGORIZED FILES (444 limit) ==========
    print(f"\n{'='*70}")
    print(f"  UPDATING CATEGORIZED FILES (444 limit)")
    print(f"{'='*70}")
    
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
        if attrs['security'] == 'reality' and attrs['country'] == 'XX': 
            all_possible_paths.add('special/reality_xx.txt')
        if attrs['network'] == 'grpc' and attrs['country'] == 'XX': 
            all_possible_paths.add('special/grpc_xx.txt')
        if attrs['security'] == 'reality' and attrs['network'] == 'tcp': 
            all_possible_paths.add('special/reality_tcp.txt')

    final_file_count = 0
    files_cleaned = 0
    total_dupes_removed = 0
    
    for path in sorted(list(all_possible_paths)):
        raw_existing_list = load_list_from_file(path)
        deduplicated_existing = []
        existing_fingerprints = set()
        
        for existing_config in raw_existing_list:
            fp = get_config_fingerprint(existing_config)
            if fp and fp not in existing_fingerprints:
                deduplicated_existing.append(existing_config)
                existing_fingerprints.add(fp)
            elif not fp:
                deduplicated_existing.append(existing_config)
        
        initial_count = len(raw_existing_list)
        after_dedup_count = len(deduplicated_existing)
        
        if initial_count > after_dedup_count:
            dupes_removed = initial_count - after_dedup_count
            total_dupes_removed += dupes_removed
            files_cleaned += 1
            print(f"Cleaned {path}: removed {dupes_removed} duplicates")
        
        added_count = 0
        for new_config in new_configs_data:
            renamed_config = new_config['renamed']
            attrs = new_config['attrs']
            fingerprint = new_config['fingerprint']
            
            belongs = False
            if path == OUTPUT_FILE_MAIN: 
                belongs = True
            elif f"protocols/{attrs['protocol']}.txt" == path: 
                belongs = True
            elif f"networks/{attrs['network']}.txt" == path: 
                belongs = True
            elif f"security/{attrs['security']}.txt" == path: 
                belongs = True
            elif f"countries/{attrs['country'].lower()}.txt" == path: 
                belongs = True
            elif path == 'special/reality_xx.txt' and attrs['security'] == 'reality' and attrs['country'] == 'XX': 
                belongs = True
            elif path == 'special/grpc_xx.txt' and attrs['network'] == 'grpc' and attrs['country'] == 'XX': 
                belongs = True
            elif path == 'special/reality_tcp.txt' and attrs['security'] == 'reality' and attrs['network'] == 'tcp': 
                belongs = True

            if belongs and fingerprint and fingerprint not in existing_fingerprints:
                deduplicated_existing.append(renamed_config)
                existing_fingerprints.add(fingerprint)
                added_count += 1

        final_list = deduplicated_existing
        if len(final_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(final_list) - MAX_CONFIGS_PER_FILE
            final_list = final_list[num_to_remove:]
            print(f"Pruned {path}: {after_dedup_count}+{added_count}→{len(final_list)}")
        elif added_count > 0:
            print(f"Updated {path}: +{added_count} → {len(final_list)} total")
        
        if final_list:
            dir_name = os.path.dirname(path)
            if dir_name: 
                os.makedirs(dir_name, exist_ok=True)
            content = base64.b64encode("\n".join(final_list).encode('utf-8')).decode('utf-8')
            with open(path, 'w') as f: 
                f.write(content)
            final_file_count += 1
    
    print(f"\n✓ Updated {final_file_count} categorized files (cleaned {files_cleaned}, removed {total_dupes_removed} dupes)")

    # ========== FINAL SUMMARY ==========
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Raw scraped            : {len(newly_scraped_configs)}")
    print(f"  ")
    print(f"  SNI Database total     : {len(db_sni)}")
    print(f"  SNI new this run       : {len(new_sni_configs)}")
    print(f"  SNI active file        : {min(len(new_sni_configs), MAX_ACTIVE_CONFIGS)}")
    print(f"  ")
    print(f"  IP Database total      : {len(db_ip)}")
    print(f"  IP new this run        : {len(new_ip_configs)}")
    print(f"  IP active file         : {min(len(new_ip_configs), MAX_ACTIVE_CONFIGS)}")
    print(f"  ")
    print(f"  Categorized files      : {final_file_count} (444 limit)")
    print(f"  DNS cache entries      : {len(dns_cache)}")
    print(f"{'='*70}")
    
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: 
            json.dump(new_latest_ids, f, indent=2)
        print(f"\n✓ Bookmarks saved to {STATE_FILE}")
    
    print("\n✓ COMPLETE - Databases Updated!")

if __name__ == "__main__":
    asyncio.run(main())
