import re, base64, os, asyncio, json, socket, ipaddress
from urllib.parse import urlparse, parse_qs, quote, urlencode, urlunparse
from telethon.sync import TelegramClient
import requests
import geoip2.database
from dns import resolver
import hashlib

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
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
ARCHIVE_FILE = 'all_configs_sni_archive.txt'  # NEW: Archive file
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

def country_code_to_flag(iso_code): 
    return COUNTRY_FLAGS.get(iso_code, "🌐")

# --- Domain to IP Resolution ---
def resolve_domain_to_ip(hostname):
    """
    Resolves a domain to IP address with caching.
    Returns the IP or None if resolution fails.
    """
    if not hostname:
        return None
    
    # Check if already an IP
    try:
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass
    
    # Check cache
    if hostname in dns_cache:
        return dns_cache[hostname]
    
    # Resolve
    try:
        ip_addr = resolver.resolve(hostname, 'A')[0].to_text()
        dns_cache[hostname] = ip_addr
        return ip_addr
    except Exception:
        dns_cache[hostname] = None
        return None

# --- FIXED: Completely Silent VMess Parser ---
def parse_vmess_config(config_str):
    """
    Parses a VMess config and returns the decoded JSON object.
    Returns None silently if parsing fails (no error messages).
    """
    try:
        encoded = config_str.replace('vmess://', '').strip()
        encoded = encoded.rstrip('.,;!?')
        
        # Add padding
        missing_padding = len(encoded) % 4
        if missing_padding:
            encoded += '=' * (4 - missing_padding)
        
        # Decode base64
        decoded_bytes = base64.b64decode(encoded, validate=True)
        
        # Try multiple encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                decoded = decoded_bytes.decode(encoding, errors='ignore')
                parsed = json.loads(decoded)
                
                # Validate required fields
                if 'add' in parsed and 'port' in parsed and 'id' in parsed:
                    return parsed
                    
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
        
        return None
        
    except Exception:
        return None  # Silent fail - no print

# --- Config Fingerprinting for Deduplication ---
def get_config_fingerprint(config_str):
    """
    Creates a unique fingerprint for a config based on:
    protocol + IP + port + UUID/password
    This allows detection of semantic duplicates.
    """
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
            port = parsed.port or ''
            return f"{protocol}|{host}|{port}|{uuid}"
        
        elif config_str.startswith('ss://'):
            # Format: ss://base64@server:port
            parts = config_str.split('@')
            if len(parts) == 2:
                server_part = parts[1].split('#')[0]
                method_pass = parts[0].replace('ss://', '')
                return f"ss|{server_part}|{method_pass}"
        
        return None
    except Exception:
        return None

# --- Domain to IP Replacement ---
def replace_domain_with_ip(config_str):
    """
    Replaces domain with IP address in config while preserving SNI/host.
    Returns the modified config or original if resolution fails.
    """
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return config_str
            
            domain = vmess_data.get('add', '')
            ip_addr = resolve_domain_to_ip(domain)
            
            if ip_addr and ip_addr != domain:
                # Preserve original domain in SNI if TLS is used
                if vmess_data.get('tls') == 'tls' and not vmess_data.get('sni'):
                    vmess_data['sni'] = domain
                
                vmess_data['add'] = ip_addr
                
                # Re-encode
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
                
                # Preserve domain in SNI if security is TLS/Reality
                security = params.get('security', [''])[0]
                if security in ['tls', 'reality'] and 'sni' not in params:
                    params['sni'] = [domain]
                
                # Preserve domain in host for HTTP/WS
                network_type = params.get('type', [''])[0]
                if network_type in ['http', 'ws'] and 'host' not in params:
                    params['host'] = [domain]
                
                # Rebuild query string
                new_query = urlencode(params, doseq=True)
                
                # Rebuild netloc with IP
                new_netloc = ip_addr
                if parsed.port:
                    new_netloc = f"{ip_addr}:{parsed.port}"
                if parsed.username:
                    new_netloc = f"{parsed.username}@{new_netloc}"
                
                # Reconstruct URL
                new_parsed = parsed._replace(netloc=new_netloc, query=new_query)
                return new_parsed.geturl()
            
            return config_str
        
        elif config_str.startswith('ss://'):
            # Format: ss://base64@domain:port#name
            parts = config_str.split('@')
            if len(parts) != 2:
                return config_str
            
            prefix = parts[0]
            suffix = parts[1]
            
            # Extract fragment
            fragment = ''
            if '#' in suffix:
                suffix, fragment = suffix.split('#', 1)
                fragment = f'#{fragment}'
            
            # Extract domain and port
            if ':' in suffix:
                domain, port = suffix.rsplit(':', 1)
            else:
                domain, port = suffix, '443'
            
            ip_addr = resolve_domain_to_ip(domain)
            
            if ip_addr and ip_addr != domain:
                return f"{prefix}@{ip_addr}:{port}{fragment}"
            
            return config_str
        
        return config_str
    
    except Exception:
        return config_str

# --- NEW FUNCTION: Address to SNI Replacement ---
def replace_address_with_sni(config_str):
    """
    Replaces the address field with SNI value if the config has SNI.
    If no SNI exists, returns the original config unchanged.
    This is the OPPOSITE of replace_domain_with_ip.
    """
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return config_str
            
            sni = vmess_data.get('sni', '').strip()
            current_add = vmess_data.get('add', '').strip()
            
            # Replace address with SNI if SNI exists and is different
            if sni and sni != current_add:
                vmess_data['add'] = sni
                
                # Re-encode
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
            
            # Replace hostname with SNI if different
            if sni and sni != current_host:
                # Rebuild netloc with SNI
                new_netloc = sni
                if parsed.port:
                    new_netloc = f"{sni}:{parsed.port}"
                if parsed.username:
                    new_netloc = f"{parsed.username}@{new_netloc}"
                
                # Reconstruct URL
                new_parsed = parsed._replace(netloc=new_netloc)
                return new_parsed.geturl()
            
            return config_str
        
        # SS configs don't typically have SNI
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

# --- UPDATED: Config Attributes Parser with Validation ---
def get_config_attributes(config_str):
    """
    Extracts protocol, network, security, and country from config.
    Now properly supports VMess configs and validates all fields.
    """
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
            
            # Reality detection
            if security != 'reality' and 'pbk' in params: 
                security = 'reality'
            
            country = get_country_from_hostname(hostname).upper()
        
        # --- VALIDATION: Ensure all fields are valid ---
        
        # Validate protocol
        valid_protocols = ['vmess', 'vless', 'trojan', 'ss']
        if not protocol or protocol not in valid_protocols:
            return None
        
        # Validate and sanitize network
        valid_networks = ['tcp', 'kcp', 'ws', 'http', 'quic', 'grpc', 'h2', 'httpupgrade', 'splithttp']
        if not network or network not in valid_networks:
            network = 'tcp'  # Default fallback
        
        # Validate and sanitize security
        valid_security = ['none', 'tls', 'reality', 'xtls']
        if not security or security not in valid_security:
            security = 'none'  # Default fallback
        
        # Validate country code (must be 2 letters)
        if not country or len(country) != 2 or not country.isalpha():
            country = 'XX'
        
        return {
            'protocol': protocol, 
            'network': network, 
            'security': security, 
            'country': country
        }
    
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
    print(f"--- Telegram Scraper v11.0 (SNI Archive Added) ---")
    global geoip_reader
    
    if not all([API_ID, API_HASH, SESSION_STRING]): 
        print("FATAL: Required secrets not set.")
        return

    # --- GeoIP Download with Multiple Mirrors ---
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
                print(f"Trying {url}...")
                r = requests.get(url, allow_redirects=True, timeout=30)
                if r.status_code == 200 and len(r.content) > 1000:
                    with open(GEOIP_DB_PATH, 'wb') as f: 
                        f.write(r.content)
                    print(f"✓ GeoIP database downloaded successfully ({len(r.content)} bytes)")
                    downloaded = True
                    break
            except Exception as e:
                print(f"✗ Failed: {e}")
                continue
        
        if not downloaded:
            print("WARNING: Could not download GeoIP database from any mirror.")
    
    try: 
        geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e: 
        print(f"Warning: Could not load GeoIP db. {e}")

    try:
        with open(f"{SESSION_NAME}.session", 'wb') as f: 
            f.write(base64.b64decode(SESSION_STRING))
    except Exception as e: 
        print(f"FATAL: Could not write session file. {e}")
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

    # ============================================================
    # EXISTING LOGIC: IP-based processing (UNCHANGED)
    # ============================================================
    
    # --- UPDATED: Process Configs with Silent Stats Tracking ---
    new_configs_data = []
    seen_fingerprints = set()
    stats = {
        'total_scraped': len(newly_scraped_configs),
        'failed_parse': 0,
        'duplicates': 0,
        'valid_unique': 0
    }
    
    for raw_config in newly_scraped_configs:
        # Replace domain with IP
        ip_config = replace_domain_with_ip(raw_config)
        
        # Get fingerprint for deduplication
        fingerprint = get_config_fingerprint(ip_config)
        
        if fingerprint and fingerprint in seen_fingerprints:
            stats['duplicates'] += 1
            continue
        
        # Get attributes (with validation)
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
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"  PROCESSING SUMMARY (IP-BASED)")
    print(f"{'='*50}")
    print(f"  Total scraped configs    : {stats['total_scraped']}")
    print(f"  ✓ Valid unique configs   : {stats['valid_unique']}")
    print(f"  ⊘ Duplicates skipped     : {stats['duplicates']}")
    print(f"  ✗ Failed/corrupted       : {stats['failed_parse']}")
    print(f"{'='*50}\n")

    # --- Build all possible file paths ---
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
        
        # Special category logic
        if attrs['security'] == 'reality' and attrs['network'] == 'ws': 
            all_possible_paths.add('special/reality_xx.txt')
        if attrs['network'] == 'grpc' and attrs['country'] == 'XX': 
            all_possible_paths.add('special/grpc_xx.txt')
        if attrs['security'] == 'reality' and attrs['network'] == 'tcp': 
            all_possible_paths.add('special/reality_tcp.txt')

    # --- Process files with proper deduplication ---
    print("--- Updating and pruning all subscription files ---")
    final_file_count = 0
    files_cleaned = 0
    total_dupes_removed = 0
    
    for path in sorted(list(all_possible_paths)):
        # Load existing configs
        raw_existing_list = load_list_from_file(path)
        
        # STEP 1: Deduplicate existing configs first (SILENT)
        deduplicated_existing = []
        existing_fingerprints = set()
        
        for existing_config in raw_existing_list:
            fp = get_config_fingerprint(existing_config)
            if fp and fp not in existing_fingerprints:
                deduplicated_existing.append(existing_config)
                existing_fingerprints.add(fp)
            elif not fp:
                # Keep configs without fingerprints
                deduplicated_existing.append(existing_config)
        
        initial_count = len(raw_existing_list)
        after_dedup_count = len(deduplicated_existing)
        
        if initial_count > after_dedup_count:
            dupes_removed = initial_count - after_dedup_count
            total_dupes_removed += dupes_removed
            files_cleaned += 1
            print(f"Cleaned {path}: removed {dupes_removed} internal duplicates")
        
        # STEP 2: Add new configs that belong to this category
        added_count = 0
        for new_config in new_configs_data:
            renamed_config = new_config['renamed']
            attrs = new_config['attrs']
            fingerprint = new_config['fingerprint']
            
            # Check if belongs to this file
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

            # Add if belongs and not duplicate
            if belongs and fingerprint and fingerprint not in existing_fingerprints:
                deduplicated_existing.append(renamed_config)
                existing_fingerprints.add(fingerprint)
                added_count += 1

        # STEP 3: Prune if exceeds max (FIFO - remove oldest)
        final_list = deduplicated_existing
        if len(final_list) > MAX_CONFIGS_PER_FILE:
            num_to_remove = len(final_list) - MAX_CONFIGS_PER_FILE
            final_list = final_list[num_to_remove:]  # Keep newest
            print(f"Pruned {path}: {after_dedup_count} existing + {added_count} new = {len(deduplicated_existing)}, removed {num_to_remove} oldest → {len(final_list)} final")
        elif added_count > 0:
            print(f"Updated {path}: {after_dedup_count} existing + {added_count} new = {len(final_list)} configs")
        
        # STEP 4: Save
        if final_list:
            dir_name = os.path.dirname(path)
            if dir_name: 
                os.makedirs(dir_name, exist_ok=True)
            
            content = base64.b64encode("\n".join(final_list).encode('utf-8')).decode('utf-8')
            with open(path, 'w') as f: 
                f.write(content)
            final_file_count += 1
    
    print(f"\n{'='*50}")
    print(f"  FILE UPDATE SUMMARY (IP-BASED)")
    print(f"{'='*50}")
    print(f"  Files saved/updated      : {final_file_count}")
    print(f"  Files cleaned            : {files_cleaned}")
    print(f"  Total dupes removed      : {total_dupes_removed}")
    print(f"{'='*50}\n")

    # ============================================================
    # NEW LOGIC: SNI-based archiving (ALL configs)
    # ============================================================
    
    print("\n" + "="*60)
    print("  ARCHIVING ALL CONFIGS WITH SNI-BASED ADDRESSING")
    print("="*60)
    
    # Load existing archive
    archive_configs = load_list_from_file(ARCHIVE_FILE)
    archive_fingerprints = set()
    
    # Build fingerprint set from existing archive
    for archived_config in archive_configs:
        fp = get_config_fingerprint(archived_config)
        if fp:
            archive_fingerprints.add(fp)
    
    print(f"Loaded {len(archive_configs)} existing configs from archive")
    
    # Process newly scraped configs for archiving
    new_archived = 0
    archive_stats = {
        'total_scraped': len(newly_scraped_configs),
        'already_archived': 0,
        'newly_added': 0,
        'failed_parse': 0
    }
    
    for raw_config in newly_scraped_configs:
        # Apply SNI-based addressing (NEW LOGIC)
        sni_config = replace_address_with_sni(raw_config)
        
        # Get fingerprint for deduplication
        fingerprint = get_config_fingerprint(sni_config)
        
        # Skip if already in archive
        if fingerprint and fingerprint in archive_fingerprints:
            archive_stats['already_archived'] += 1
            continue
        
        # Validate config
        attrs = get_config_attributes(sni_config)
        
        if attrs:
            # Rename with country flag
            renamed_config = rename_config(sni_config, NEW_NAME, attrs['country'])
            archive_configs.append(renamed_config)
            
            if fingerprint:
                archive_fingerprints.add(fingerprint)
            
            archive_stats['newly_added'] += 1
        else:
            archive_stats['failed_parse'] += 1
    
    # Save archive (NO LIMIT - keeps everything)
    if archive_configs:
        content = base64.b64encode("\n".join(archive_configs).encode('utf-8')).decode('utf-8')
        with open(ARCHIVE_FILE, 'w') as f:
            f.write(content)
    
    print(f"\n{'='*60}")
    print(f"  ARCHIVE SUMMARY (SNI-BASED)")
    print(f"{'='*60}")
    print(f"  Total scraped this run   : {archive_stats['total_scraped']}")
    print(f"  ✓ Newly added to archive : {archive_stats['newly_added']}")
    print(f"  ⊘ Already in archive     : {archive_stats['already_archived']}")
    print(f"  ✗ Failed validation      : {archive_stats['failed_parse']}")
    print(f"  📦 Total archive size     : {len(archive_configs)} configs")
    print(f"  💾 Saved to              : {ARCHIVE_FILE}")
    print(f"{'='*60}\n")
    
    # Save state
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: 
            json.dump(new_latest_ids, f, indent=2)
        print(f"Successfully updated bookmarks in {STATE_FILE}.")

if __name__ == "__main__":
    asyncio.run(main())
