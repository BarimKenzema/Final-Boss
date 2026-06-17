import re, base64, os, asyncio, json, socket, ipaddress, random
from urllib.parse import urlparse, parse_qs, quote, urlencode
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError
import requests
import geoip2.database
from dns import resolver

print("--- Telegram Scraper v16.0 (Unified Database + Simplified) START ---")

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')

TARGET_GROUPS = [
    'letsproxys', 'fastkanfig', 'MuteVpnN', 'ShadowProxy66', 'free_vpn02', 'falcunargo', 'FreakConfig', 'tazaxy', 'frekansmeli', 
    'DirectVPN', 'DailyV2RY', 'daily_configs', 'configpluse', 'ghalagyann', 'meli_proxyy', 'fixeror', 'FergalVpnMod', 
    'ghalagyann2', 'Leecher56', 'tigervpnorg', 'v2rayng_fars', 'Mrsoulb', 'mtproxy_lists', 'shankamil', 'prrofile_purple',
    'vpnplusee_free', 'GetConfigIR', 'Pro_v2rayShop', 'surfboardv2ray', 'V2rayBaaz', 'proxymtprotoir', 'V2ray_Alpha', 
    'v2ray_official', 'horn_proxy', 'ocean_peace_mind', 'safavpnn', 'vless_config', 'AR14N24b', 'anotherme_night', 'knightshield', 
    'vpn_tehran', 'vpnz4', 'customv2ray', 'vpnfail_v2ray', 'vpn_ioss', 'vmessorg', 'entryNET', 'OnlineForevers',
    'vmess_ir', 'vlessconfig', 'vistav2ray', 'vipv2rayngnp', 'v2rayvpn2', 'sinavm', 'xpnteam', 'proxymthub', 
    'v2rayroz', 'v2rayopen', 'v2rayngvpn', 'v2rayng_matsuri', 'v2rayng_fast', 'V2All', 'proxy_v2ray_meli',
    'v2pedia', 'sadoshockss', 'toxicvid', 'tehranargo', 'spikevpn', 'FG_Link', 'FreeNetAndProxy', 
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net', 'zhicroid', 'saghi_proxy1'
]

# Anti-rate-limit settings
MIN_CHANNEL_DELAY = 8
MAX_CHANNEL_DELAY = 15
MAX_FLOOD_WAIT_TOLERATE = 600
BATCH_SIZE = 5
BATCH_PAUSE = 30

# Database configuration
DATABASE_DIR = './database'
DATABASE_BASE_NAME = 'Database'
MAX_DB_SIZE_MB = 44
MAX_DB_FILES = 7

# Active file
ACTIVE_FILE = 'latest_configs.txt'
MAX_ACTIVE_CONFIGS = 4444

# Categorized files (444 cap)
STATE_FILE = 'last_ids.json'
NEW_NAME = '@VPNProxyTest'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'

# Download settings
TEMP_DOWNLOAD_FOLDER = './temp_downloads'
MAX_FILE_SIZE_MB = 10

# Subscription link settings
SUBSCRIPTION_FETCH_TIMEOUT = 10
MAX_SUBSCRIPTION_SIZE_MB = 3

COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", 
    "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿", 
    "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫", "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", 
    "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", 
    "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", 
    "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", 
    "CU": "🇨🇺", "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯", 
    "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭", 
    "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰", "FM": "🇫🇲", "FO": "🇫🇴", 
    "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", 
    "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", 
    "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾", "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", 
    "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", 
    "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", 
    "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KY": "🇰🇾", 
    "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", 
    "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", 
    "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", 
    "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", 
    "MY": "🇲🇾", "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", 
    "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦", 
    "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲", "PR": "🇵🇷", 
    "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴", "RS": "🇷🇸", 
    "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", 
    "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", 
    "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", 
    "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", 
    "TR": "🇹🇷", "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸", 
    "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳", 
    "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼", 
    "XX": "🔓"
}

# --- Caching & Global Variables ---
dns_cache = {}
geoip_reader = None
stats_npvt_files_found = 0
stats_subscriptions_processed = 0
stats_subscription_configs = 0
stats_subscription_skipped = 0

# =========================
# Database Management (Unified)
# =========================

def ensure_database_dir():
    """Ensure database directory exists."""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print(f"📁 Created database directory: {DATABASE_DIR}")

def get_database_files():
    """Get all database files sorted by number."""
    ensure_database_dir()
    files = []
    for i in range(1, MAX_DB_FILES + 1):
        filepath = os.path.join(DATABASE_DIR, f"{DATABASE_BASE_NAME}_{i}.txt")
        if os.path.exists(filepath):
            files.append(filepath)
    return files

def get_current_database_file():
    """Get the current active database file (last one or create first)."""
    files = get_database_files()
    if not files:
        return os.path.join(DATABASE_DIR, f"{DATABASE_BASE_NAME}_1.txt")
    return files[-1]

def get_next_database_file(current_file):
    """Get next database file in rotation."""
    current_name = os.path.basename(current_file)
    match = re.search(r'_(\d+)\.txt$', current_name)
    if match:
        current_num = int(match.group(1))
        next_num = (current_num % MAX_DB_FILES) + 1
        return os.path.join(DATABASE_DIR, f"{DATABASE_BASE_NAME}_{next_num}.txt")
    return os.path.join(DATABASE_DIR, f"{DATABASE_BASE_NAME}_1.txt")

def load_database_file(filepath):
    """Load a single database file (base64 encoded)."""
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return set()
            decoded = base64.b64decode(content).decode('utf-8')
            return set(decoded.splitlines())
    except Exception as e:
        print(f"Warning: Could not load {filepath}: {e}")
        return set()

def load_all_databases():
    """Load configs from ALL database files."""
    all_configs = set()
    files = get_database_files()
    
    if not files:
        print(f"  No database files found in {DATABASE_DIR}")
        return all_configs
    
    print(f"  Loading from {len(files)} database file(s):")
    for db_file in files:
        configs = load_database_file(db_file)
        all_configs.update(configs)
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print(f"    • {os.path.basename(db_file)}: {len(configs)} configs ({size_mb:.2f} MB)")
    
    return all_configs

def save_database(new_configs_list):
    """Save new configs to database with rotation."""
    if not new_configs_list:
        return None
    
    ensure_database_dir()
    current_file = get_current_database_file()
    
    # Load existing from current file only
    existing = load_database_file(current_file)
    combined = existing.union(set(new_configs_list))
    
    # Prepare content
    content = "\n".join(sorted(combined))
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    size_mb = len(encoded.encode('utf-8')) / (1024 * 1024)
    
    # Check if rotation needed
    if size_mb > MAX_DB_SIZE_MB and existing:
        next_file = get_next_database_file(current_file)
        print(f"  ⚠️  {os.path.basename(current_file)} would be {size_mb:.2f}MB (limit: {MAX_DB_SIZE_MB}MB)")
        print(f"  🔄 Rotating to: {os.path.basename(next_file)}")
        
        # Save only new configs to next file
        new_content = "\n".join(sorted(new_configs_list))
        new_encoded = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        
        with open(next_file, 'w', encoding='utf-8') as f:
            f.write(new_encoded)
        
        new_size_mb = len(new_encoded.encode('utf-8')) / (1024 * 1024)
        print(f"  ✅ Saved {len(new_configs_list)} configs to {os.path.basename(next_file)} ({new_size_mb:.2f}MB)")
        return next_file
    else:
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        print(f"  ✅ Updated {os.path.basename(current_file)} ({size_mb:.2f}MB, {len(combined)} total configs)")
        return current_file

# =========================
# Active File Management
# =========================

def save_active_file(configs_list):
    """Save active file (base64 encoded, capped)."""
    try:
        configs_to_save = configs_list[-MAX_ACTIVE_CONFIGS:] if len(configs_list) > MAX_ACTIVE_CONFIGS else configs_list
        content = "\n".join(configs_to_save)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(ACTIVE_FILE, 'w', encoding='utf-8') as f:
            f.write(encoded)
        return len(configs_to_save)
    except Exception as e:
        print(f"Error saving {ACTIVE_FILE}: {e}")
        return 0

def load_active_file():
    """Load active file."""
    if not os.path.exists(ACTIVE_FILE):
        return []
    try:
        with open(ACTIVE_FILE, 'r') as f:
            content = f.read()
            if content:
                return base64.b64decode(content).decode('utf-8').splitlines()
    except Exception as e:
        print(f"Error loading {ACTIVE_FILE}: {e}")
    return []

def get_config_fingerprint(config_str):
    """Get unique fingerprint for deduplication."""
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return None
            return f"vmess|{vmess_data.get('add', '')}|{vmess_data.get('port', '')}|{vmess_data.get('id', '')}"
        elif config_str.startswith(('vless://', 'trojan://')):
            parsed = urlparse(config_str)
            try:
                port = parsed.port or ''
            except:
                port = ''
            return f"{parsed.scheme}|{parsed.hostname}|{port}|{parsed.username}"
        elif config_str.startswith('ss://'):
            parts = config_str.split('@')
            if len(parts) == 2:
                return f"ss|{parts[1].split('#')[0]}|{parts[0].replace('ss://', '')}"
        return None
    except Exception:
        return None

def merge_configs_by_fingerprint(existing_list, new_list):
    """Merge existing + new, deduplicate, cap to newest."""
    combined = existing_list + new_list
    seen = set()
    dedup_rev = []
    for cfg in reversed(combined):
        fp = get_config_fingerprint(cfg)
        key = fp if fp else f"RAW::{cfg}"
        if key not in seen:
            dedup_rev.append(cfg)
            seen.add(key)
    dedup = list(reversed(dedup_rev))
    if len(dedup) > MAX_ACTIVE_CONFIGS:
        dedup = dedup[-MAX_ACTIVE_CONFIGS:]
    return dedup

# =========================
# Subscription Link Helpers
# =========================

SUBSCRIPTION_BLACKLIST = [
    't.me/proxy', 't.me/socks', 'telegram.me/proxy', 'telegram.me/socks',
    'telegram.org', 'telegram.dog', 'telesco.pe', 'twitter.com', 'x.com',
    'facebook.com', 'fb.com', 'instagram.com', 'youtube.com', 'youtu.be',
    'tiktok.com', 'reddit.com', 'discord.gg', 'discord.com', 'wa.me',
    'whatsapp.com', 'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
]

SUBSCRIPTION_WHITELIST_PATTERNS = [
    r'\.workers\.dev/', r'/sub/', r'/api/v\d+/', r'/link/', r'/profile/',
    r'\.txt$', r'\.json$', r'/raw/', r'/v2ray', r'/clash', r'/shadowrocket',
]

def is_valid_subscription_url(url):
    """Check if URL is likely a real subscription link."""
    if not url:
        return False
    
    url_lower = url.lower()
    
    for blocked in SUBSCRIPTION_BLACKLIST:
        if blocked in url_lower:
            return False
    
    if not url_lower.startswith(('http://', 'https://')):
        return False
    
    if 't.me/' in url_lower or 'telegram.me/' in url_lower or 'telegram.dog/' in url_lower:
        return False
    
    for pattern in SUBSCRIPTION_WHITELIST_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    parsed = urlparse(url)
    if not parsed.path or len(parsed.path) < 3:
        return False
    
    spam_patterns = [r'tag=d_\d+', r'click\d+', r'redirect', r'goto', r'track', r'adv\d+', r'/ad/', r'utm_', r'affiliate']
    for spam in spam_patterns:
        if re.search(spam, url, re.IGNORECASE):
            return False
    
    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
    long_hash_pattern = r'[a-zA-Z0-9_-]{20,}'
    
    if re.search(uuid_pattern, url) or re.search(long_hash_pattern, parsed.path):
        return True
    
    return False

def find_subscription_urls(text):
    """Extract subscription URLs from text."""
    if not text:
        return []
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:/[^\s<>"{}|\\^`\[\]]*)?'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    subscription_urls = []
    for url in urls:
        url = url.rstrip('.,;:!?)\]*')
        if is_valid_subscription_url(url):
            subscription_urls.append(url)
    
    return list(set(subscription_urls))

def fetch_subscription_content(url):
    """Fetch content from subscription URL."""
    try:
        headers = {
            'User-Agent': 'clash-verge/v1.3.8',
            'Accept': 'text/html,application/json,text/plain,*/*',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        response = requests.get(url, headers=headers, timeout=SUBSCRIPTION_FETCH_TIMEOUT, allow_redirects=True, stream=True)
        
        if response.status_code == 200:
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_SUBSCRIPTION_SIZE_MB * 1024 * 1024:
                return None
            
            content = b''
            max_size = MAX_SUBSCRIPTION_SIZE_MB * 1024 * 1024
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > max_size:
                    return None
            
            return content.decode('utf-8', errors='ignore')
    except:
        pass
    return None

def extract_configs_from_subscription(content):
    """Extract configs from subscription content."""
    if not content:
        return []
    
    configs = set()
    
    # Try plaintext
    configs.update(find_and_validate_configs(content))
    
    # Try base64
    if not configs:
        try:
            decoded = base64.b64decode(content.strip()).decode('utf-8', errors='ignore')
            configs.update(find_and_validate_configs(decoded))
        except:
            pass
    
    # Try JSON
    if not configs:
        try:
            json_data = json.loads(content)
            
            def extract_from_json(obj):
                found = set()
                if isinstance(obj, str):
                    found.update(find_and_validate_configs(obj))
                elif isinstance(obj, list):
                    for item in obj:
                        found.update(extract_from_json(item))
                elif isinstance(obj, dict):
                    for value in obj.values():
                        found.update(extract_from_json(value))
                return found
            
            configs.update(extract_from_json(json_data))
        except:
            pass
    
    return list(configs)

async def process_subscription_links(text):
    """Find and process all subscription URLs in text."""
    global stats_subscriptions_processed, stats_subscription_configs, stats_subscription_skipped
    
    urls = find_subscription_urls(text)
    if not urls:
        return []
    
    all_configs = []
    
    for url in urls:
        display_url = url[:70] + "..." if len(url) > 70 else url
        print(f"  🔗 Fetching: {display_url}")
        
        content = fetch_subscription_content(url)
        
        if content:
            configs = extract_configs_from_subscription(content)
            if configs:
                print(f"     ✅ Extracted {len(configs)} configs")
                all_configs.extend(configs)
                stats_subscriptions_processed += 1
                stats_subscription_configs += len(configs)
            else:
                stats_subscription_skipped += 1
        else:
            stats_subscription_skipped += 1
    
    return all_configs

# =========================
# DNS Resolution & Parsing
# =========================

def country_code_to_flag(iso_code):
    return COUNTRY_FLAGS.get(iso_code, "🌐")

def is_ip_address(hostname):
    """Check if hostname is an IP address."""
    if not hostname:
        return False
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False

def resolve_domain_to_ip(hostname):
    """Resolve domain to IP, return None if already IP or resolution fails."""
    if not hostname:
        return None
    
    if is_ip_address(hostname):
        return hostname
    
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
    """Parse VMess config from base64."""
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
            except:
                continue
        return None
    except Exception:
        return None

def replace_domain_with_ip(config_str):
    """
    Replace domain with IP address if the address is a domain.
    Preserves original domain in SNI/host parameters.
    If already IP, returns unchanged.
    """
    try:
        if config_str.startswith('vmess://'):
            vmess_data = parse_vmess_config(config_str)
            if not vmess_data:
                return config_str
            
            address = vmess_data.get('add', '')
            
            if is_ip_address(address):
                return config_str
            
            ip_addr = resolve_domain_to_ip(address)
            if not ip_addr or ip_addr == address:
                return config_str
            
            if vmess_data.get('tls') == 'tls' and not vmess_data.get('sni'):
                vmess_data['sni'] = address
            
            net = vmess_data.get('net', '').lower()
            if net in ['ws', 'http', 'h2'] and not vmess_data.get('host'):
                vmess_data['host'] = address
            
            vmess_data['add'] = ip_addr
            new_json = json.dumps(vmess_data, separators=(',', ':'))
            return f"vmess://{base64.b64encode(new_json.encode('utf-8')).decode('utf-8')}"
        
        elif config_str.startswith(('vless://', 'trojan://')):
            parsed = urlparse(config_str)
            hostname = parsed.hostname
            
            if is_ip_address(hostname):
                return config_str
            
            ip_addr = resolve_domain_to_ip(hostname)
            if not ip_addr or ip_addr == hostname:
                return config_str
            
            params = parse_qs(parsed.query)
            security = params.get('security', [''])[0]
            network_type = params.get('type', [''])[0]
            
            if security in ['tls', 'reality'] and 'sni' not in params:
                params['sni'] = [hostname]
            
            if network_type in ['ws', 'http', 'h2'] and 'host' not in params:
                params['host'] = [hostname]
            
            new_query = urlencode(params, doseq=True)
            new_netloc = ip_addr
            try:
                if parsed.port:
                    new_netloc = f"{ip_addr}:{parsed.port}"
            except:
                pass
            if parsed.username:
                new_netloc = f"{parsed.username}@{new_netloc}"
            
            return parsed._replace(netloc=new_netloc, query=new_query).geturl()
        
        elif config_str.startswith('ss://'):
            parts = config_str.split('@')
            if len(parts) != 2:
                return config_str
            
            prefix, suffix = parts[0], parts[1]
            fragment = ''
            if '#' in suffix:
                suffix, fragment = suffix.split('#', 1)
                fragment = f'#{fragment}'
            
            if ':' in suffix:
                hostname, port = suffix.rsplit(':', 1)
            else:
                hostname, port = suffix, '443'
            
            if is_ip_address(hostname):
                return config_str
            
            ip_addr = resolve_domain_to_ip(hostname)
            if ip_addr and ip_addr != hostname:
                return f"{prefix}@{ip_addr}:{port}{fragment}"
            return config_str
        
        return config_str
    except Exception:
        return config_str

def get_country_from_hostname(hostname):
    """Get country code from hostname."""
    if not hostname:
        return "XX"
    
    if not is_ip_address(hostname):
        ip_addr = resolve_domain_to_ip(hostname)
    else:
        ip_addr = hostname
    
    if not ip_addr or not geoip_reader:
        return "XX"
    
    try:
        return geoip_reader.country(ip_addr).country.iso_code or "XX"
    except Exception:
        return "XX"

def get_config_attributes(config_str):
    """Extract config attributes for categorization."""
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
        
        valid_networks = ['tcp', 'kcp', 'ws', 'http', 'quic', 'grpc', 'h2', 'httpupgrade', 'splithttp', 'xhttp']
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
    """Find and validate config strings in text."""
    global stats_npvt_files_found
    
    if not text:
        return []
    
    if '.npvt' in text.lower():
        stats_npvt_files_found += text.lower().count('.npvt')
    
    normalized_text = text
    quote_chars = ['"', '"', ''', ''', '«', '»', '‹', '›', '「', '」', '『', '』']
    for qc in quote_chars:
        normalized_text = normalized_text.replace(qc, ' ')
    
    zw_chars = ['\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\ufeff']
    for zw in zw_chars:
        normalized_text = normalized_text.replace(zw, '')
    
    pattern = r'((?:vless|vmess|trojan|ss)://[^\s\u0600-\u06FF\u200b-\u200f\ufeff]+)'
    simple_pattern = r'((?:vless|vmess|trojan|ss)://\S+)'
    
    valid_configs = []
    seen = set()
    
    for config in re.findall(pattern, normalized_text, re.IGNORECASE):
        config = clean_config(config)
        if config and config not in seen and validate_config_length(config):
            valid_configs.append(config)
            seen.add(config)
    
    for config in re.findall(simple_pattern, text, re.IGNORECASE):
        config = clean_config(config)
        if config and config not in seen and validate_config_length(config):
            valid_configs.append(config)
            seen.add(config)
    
    return valid_configs

def clean_config(config):
    """Clean config string."""
    if not config:
        return None
    config = config.strip()
    while config and config[-1] in '.,;!?:\'"`""''«»‹›':
        config = config[:-1]
    return config.strip() if config else None

def validate_config_length(config):
    """Validate config has minimum required length."""
    if not config:
        return False
    if config.startswith('ss://'):
        return len(config) > 40
    elif config.startswith('vmess://'):
        return len(config) > 50
    elif config.startswith(('vless://', 'trojan://')):
        return len(config) > 60
    return False

def rename_config(link, name, country_code):
    """Rename config with country flag."""
    flag = country_code_to_flag(country_code)
    new_name = f"{flag} {name} {flag}"
    return f"{link.split('#')[0]}#{quote(new_name)}"

# =========================
# File Download & Parsing
# =========================

async def process_txt_file(client, message):
    """Process text file attachments."""
    configs_found = []
    
    if not message.document:
        return configs_found
    
    filename = message.file.name or ""
    mime_type = message.file.mime_type or ""
    
    if filename.lower().endswith('.npvt'):
        global stats_npvt_files_found
        stats_npvt_files_found += 1
        return configs_found
    
    is_txt_file = filename.lower().endswith('.txt') or mime_type == 'text/plain'
    if not is_txt_file:
        return configs_found
    
    file_size_mb = message.file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(f"  ⚠️ Skipping large file: {filename} ({file_size_mb:.2f}MB)")
        return configs_found
    
    try:
        os.makedirs(TEMP_DOWNLOAD_FOLDER, exist_ok=True)
        file_path = await client.download_media(message, file=TEMP_DOWNLOAD_FOLDER)
        
        if not file_path:
            return configs_found
        
        print(f"  📄 Downloaded: {filename} ({file_size_mb:.2f}MB)")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                content = ""
        
        if content and re.match(r'^[A-Za-z0-9+/=\s]+$', content.strip()):
            try:
                decoded = base64.b64decode(content.strip()).decode('utf-8')
                content = decoded
            except:
                pass
        
        configs_found = find_and_validate_configs(content)
        
        if configs_found:
            print(f"  ✅ Found {len(configs_found)} configs in {filename}")
        
        try:
            os.remove(file_path)
        except:
            pass
        
    except Exception as e:
        print(f"  ❌ Error processing file {filename}: {e}")
    
    return configs_found

async def scrape_new_configs(client, groups, last_ids):
    """Scrape new configs from Telegram groups."""
    scraped_configs = set()
    new_latest_ids = last_ids.copy()
    
    total_files_processed = 0
    total_configs_from_files = 0
    channels_skipped = 0
    channels_succeeded = 0
    
    shuffled_groups = list(groups)
    random.shuffle(shuffled_groups)
    
    for idx, group in enumerate(shuffled_groups, 1):
        group_str = str(group)
        min_id = last_ids.get(group_str, 0)
        is_new_group = min_id == 0
        limit = 11 if is_new_group else None
        scan_type = f"last {limit}" if is_new_group else f"since ID > {min_id}"
        print(f"\n--- Scraping group {idx}/{len(shuffled_groups)}: {group_str} ({scan_type}) ---")
        
        if idx > 1:
            delay = random.uniform(MIN_CHANNEL_DELAY, MAX_CHANNEL_DELAY)
            print(f"  ⏱️  Waiting {delay:.1f}s before next channel...")
            await asyncio.sleep(delay)
        
        if idx % BATCH_SIZE == 0:
            print(f"  ⏸️  Batch {idx//BATCH_SIZE} complete. Pausing {BATCH_PAUSE}s...")
            await asyncio.sleep(BATCH_PAUSE)
        
        messages = []
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                messages = [msg async for msg in client.iter_messages(group, min_id=min_id, limit=limit)]
                channels_succeeded += 1
                break
            except FloodWaitError as e:
                wait_time = e.seconds
                print(f"  ⚠️  FloodWait: {wait_time}s required for {group_str}")
                if wait_time > MAX_FLOOD_WAIT_TOLERATE:
                    print(f"  ❌ Skipping {group_str} (wait too long)")
                    channels_skipped += 1
                    break
                else:
                    await asyncio.sleep(wait_time + 5)
            except (ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError) as e:
                print(f"  ❌ Channel access error for {group_str}: {type(e).__name__}")
                channels_skipped += 1
                break
            except Exception as e:
                print(f"  ❌ Error scraping {group_str}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(10)
                else:
                    channels_skipped += 1
                break
        
        if not messages:
            continue
        
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
                except:
                    pass
            
            if message.document:
                file_configs = await process_txt_file(client, message)
                if file_configs:
                    scraped_configs.update(file_configs)
                    total_files_processed += 1
                    total_configs_from_files += len(file_configs)
            
            combined_text = "\n".join(texts_to_scan)
            for config in find_and_validate_configs(combined_text):
                scraped_configs.add(config)
            
            subscription_configs = await process_subscription_links(combined_text)
            if subscription_configs:
                scraped_configs.update(subscription_configs)
    
    # Cleanup temp folder
    try:
        if os.path.exists(TEMP_DOWNLOAD_FOLDER):
            import shutil
            shutil.rmtree(TEMP_DOWNLOAD_FOLDER)
    except:
        pass
    
    print(f"\n{'='*70}")
    print(f"  SCRAPING SUMMARY")
    print(f"{'='*70}")
    print(f"  Channels succeeded     : {channels_succeeded}")
    print(f"  Channels skipped       : {channels_skipped}")
    print(f"  Files processed        : {total_files_processed}")
    print(f"  Configs from files     : {total_configs_from_files}")
    print(f"  Subscriptions fetched  : {stats_subscriptions_processed}")
    print(f"  Subscriptions skipped  : {stats_subscription_skipped}")
    print(f"  Configs from subs      : {stats_subscription_configs}")
    print(f"  Total configs          : {len(scraped_configs)}")
    if stats_npvt_files_found > 0:
        print(f"  .npvt files found      : {stats_npvt_files_found} (skipped)")
    print(f"{'='*70}")
    
    return scraped_configs, new_latest_ids

# =========================
# Categorized Files (444 cap)
# =========================

def load_categorized_file(path):
    """Load categorized file (base64 encoded)."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as f:
            content = f.read()
            if content:
                return base64.b64decode(content).decode('utf-8').splitlines()
    except:
        pass
    return []

def save_categorized_file(path, configs_list):
    """Save categorized file with 444 cap."""
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    if len(configs_list) > MAX_CONFIGS_PER_FILE:
        configs_list = configs_list[-MAX_CONFIGS_PER_FILE:]
    
    content = base64.b64encode("\n".join(configs_list).encode('utf-8')).decode('utf-8')
    with open(path, 'w') as f:
        f.write(content)

def update_categorized_files(new_configs_data):
    """Update all categorized files with new configs."""
    all_paths = set()
    
    for cat_dir in ['protocols', 'networks', 'security', 'countries', 'special']:
        if os.path.exists(cat_dir):
            all_paths.update([os.path.join(cat_dir, f) for f in os.listdir(cat_dir) if f.endswith('.txt')])
    
    for item in new_configs_data:
        attrs = item['attrs']
        all_paths.add(f"protocols/{attrs['protocol']}.txt")
        all_paths.add(f"networks/{attrs['network']}.txt")
        all_paths.add(f"security/{attrs['security']}.txt")
        all_paths.add(f"countries/{attrs['country'].lower()}.txt")
        if attrs['security'] == 'reality' and attrs['country'] == 'XX':
            all_paths.add('special/reality_xx.txt')
        if attrs['network'] == 'grpc' and attrs['country'] == 'XX':
            all_paths.add('special/grpc_xx.txt')
        if attrs['security'] == 'reality' and attrs['network'] == 'tcp':
            all_paths.add('special/reality_tcp.txt')
    
    files_updated = 0
    
    for path in sorted(list(all_paths)):
        existing = load_categorized_file(path)
        existing_fps = set()
        deduped = []
        
        for cfg in existing:
            fp = get_config_fingerprint(cfg)
            if fp and fp not in existing_fps:
                deduped.append(cfg)
                existing_fps.add(fp)
            elif not fp:
                deduped.append(cfg)
        
        added = 0
        for item in new_configs_data:
            config, attrs = item['config'], item['attrs']
            fp = item.get('fingerprint')
            
            belongs = False
            if f"protocols/{attrs['protocol']}.txt" == path:
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
            
            if belongs and fp and fp not in existing_fps:
                deduped.append(config)
                existing_fps.add(fp)
                added += 1
        
        if deduped:
            save_categorized_file(path, deduped)
            if added > 0:
                print(f"  Updated {path}: +{added} → {len(deduped)} total")
                files_updated += 1
    
    return files_updated

# =========================
# Main Function
# =========================

async def main():
    global geoip_reader
    
    if not all([API_ID, API_HASH, SESSION_STRING]):
        print("FATAL: Required secrets not set.")
        return
    
    # Ensure database directory exists
    ensure_database_dir()
    
    # GeoIP download
    if not os.path.exists(GEOIP_DB_PATH):
        print("Downloading GeoIP database...")
        urls = [
            "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb",
            "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb",
        ]
        for url in urls:
            try:
                r = requests.get(url, allow_redirects=True, timeout=30)
                if r.status_code == 200 and len(r.content) > 1000:
                    with open(GEOIP_DB_PATH, 'wb') as f:
                        f.write(r.content)
                    print(f"✓ GeoIP downloaded")
                    break
            except:
                continue
    
    try:
        geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)
    except Exception as e:
        print(f"Warning: Could not load GeoIP: {e}")
    
    # Load last message IDs
    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            last_ids = json.load(f)
    
    # Connect to Telegram
    client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
    newly_scraped_configs = set()
    new_latest_ids = {}
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("FATAL: Session not authorized.")
            return
        print("Successfully connected to Telegram.")
        newly_scraped_configs, new_latest_ids = await scrape_new_configs(client, TARGET_GROUPS, last_ids)
    except Exception as e:
        print(f"FATAL ERROR during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()
        print("Disconnected from Telegram.")
    
    print(f"\nFound {len(newly_scraped_configs)} raw configs this run.")
    
    if not newly_scraped_configs:
        print("No new configs found. Saving bookmarks and exiting.")
        if new_latest_ids:
            with open(STATE_FILE, 'w') as f:
                json.dump(new_latest_ids, f, indent=2)
        return
    
    # === DATABASE PROCESSING ===
    print(f"\n{'='*70}")
    print(f"  DATABASE PROCESSING")
    print(f"{'='*70}")
    
    db_all = load_all_databases()
    print(f"Total historical configs across all databases: {len(db_all)}")
    
    # Process configs
    new_configs_data = []
    seen_fingerprints = set()
    stats = {'total': len(newly_scraped_configs), 'failed': 0, 'dupes': 0, 'valid': 0, 'converted': 0}
    
    for raw_config in newly_scraped_configs:
        # Convert domain to IP if needed
        ip_config = replace_domain_with_ip(raw_config)
        if ip_config != raw_config:
            stats['converted'] += 1
        
        fingerprint = get_config_fingerprint(ip_config)
        if fingerprint and fingerprint in seen_fingerprints:
            stats['dupes'] += 1
            continue
        
        attrs = get_config_attributes(ip_config)
        if attrs:
            if fingerprint:
                seen_fingerprints.add(fingerprint)
            renamed = rename_config(ip_config, NEW_NAME, attrs['country'])
            new_configs_data.append({'config': renamed, 'attrs': attrs, 'fingerprint': fingerprint})
            stats['valid'] += 1
        else:
            stats['failed'] += 1
    
    print(f"Processed: {stats['valid']} valid, {stats['dupes']} dupes, {stats['failed']} failed, {stats['converted']} converted")
    
    configs_in_order = [item['config'] for item in new_configs_data]
    new_configs = [c for c in configs_in_order if c not in db_all]
    print(f"Found {len(new_configs)} NEW configs")
    
    if new_configs:
        save_database(new_configs)
        
        existing_active = load_active_file()
        merged_active = merge_configs_by_fingerprint(existing_active, new_configs)
        saved_count = save_active_file(merged_active)
        print(f"  ✅ Saved {saved_count} to {ACTIVE_FILE}")
    else:
        print("  ℹ️  No new configs this run")
    
    # === CATEGORIZED FILES ===
    print(f"\n{'='*70}")
    print(f"  UPDATING CATEGORIZED FILES (444 limit)")
    print(f"{'='*70}")
    
    files_updated = update_categorized_files(new_configs_data)
    print(f"✓ Updated {files_updated} categorized files")
    
    # === FINAL SUMMARY ===
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Raw scraped            : {len(newly_scraped_configs)}")
    print(f"  Processed valid        : {stats['valid']}")
    print(f"  Domains converted      : {stats['converted']}")
    print(f"  New configs            : {len(new_configs)}")
    print(f"  Database files         : {len(get_database_files())}")
    print(f"  Active configs         : {len(load_active_file())}")
    print(f"  DNS cache entries      : {len(dns_cache)}")
    if stats_subscriptions_processed > 0:
        print(f"  Valid subscriptions    : {stats_subscriptions_processed}")
        print(f"  Configs from subs      : {stats_subscription_configs}")
    print(f"{'='*70}")
    
    # Save bookmarks
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_latest_ids, f, indent=2)
        print(f"\n✓ Bookmarks saved to {STATE_FILE}")
    
    print("\n✓ COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())
