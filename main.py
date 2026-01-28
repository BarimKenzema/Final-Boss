import re, base64, os, asyncio, json, socket, ipaddress, random
from urllib.parse import urlparse, parse_qs, quote, urlencode, urlunparse
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError
import requests
import geoip2.database
from dns import resolver

print("--- Telegram Scraper v15.1 (Smart Subscription Filtering + Database Rotation) START ---")

# --- CONFIGURATION ---
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')

TARGET_GROUPS = [
    'letsproxys', 'MuteVpnN', 'ShadowProxy66', 'free_vpn02', 'falcunargo', 'FreakConfig', 'tazaxy', 'frekansmeli', 
    'DirectVPN', 'DailyV2RY', 'daily_configs', 'configpluse', 'ghalagyann', 'meli_proxyy', 'fixeror', 'FergalVpnMod', 
    'ghalagyann2', 'Leecher56', 'tigervpnorg', 'v2rayng_fars', 'Mrsoulb', 'mtproxy_lists', 'shankamil', 'prrofile_purple',
    'vpnplusee_free', 'GetConfigIR', 'Pro_v2rayShop', 'surfboardv2ray', 'V2rayBaaz', 'proxymtprotoir', 
    'v2ray_official', 'horn_proxy', 'ocean_peace_mind', 'safavpnn', 'vless_config', 'AR14N24b', 'anotherme_night', 'knightshield', 
    'vpn_tehran', 'vpnz4', 'customv2ray', 'vpnfail_v2ray', 'vpn_ioss', 'vmessorg', 'entryNET', 'OnlineForevers',
    'vmess_ir', 'vlessconfig', 'vistav2ray', 'vipv2rayngnp', 'v2rayvpn2', 'sinavm', 'xpnteam', 'proxymthub', 
    'v2rayroz', 'v2rayopen', 'v2rayngvpn', 'v2rayng_matsuri', 'v2rayng_fast', 'V2All', 'proxy_v2ray_meli',
    'v2pedia', 'sadoshockss', 'toxicvid', 'tehranargo', 'spikevpn', 'FG_Link', 'FreeNetAndProxy', 
    'privatevpns', 'outline_ir', 'mehrosaboran', 'marambashi', 'hope_net', 'zhicroid', 'saghi_proxy1'
]

# Anti-rate-limit settings (CONSERVATIVE)
MIN_CHANNEL_DELAY = 8
MAX_CHANNEL_DELAY = 15
MAX_FLOOD_WAIT_TOLERATE = 600
BATCH_SIZE = 5
BATCH_PAUSE = 30

# Database rotation settings
MAX_DB_SIZE_MB = 44
MAX_DB_SIZE_BYTES = MAX_DB_SIZE_MB * 1024 * 1024
MAX_DB_COUNT = 4
DB_STATE_FILE = 'db_rotation_state.json'

# Databases and Active Files
DATABASE_SNI = 'database_sni.txt'
DATABASE_IP = 'database_ip.txt'
ACTIVE_FILE_SNI = 'active_sni_configs.txt'
ACTIVE_FILE_IP = 'active_ip_configs.txt'
MAX_ACTIVE_CONFIGS = 1111

# Categorized files (444 cap)
OUTPUT_FILE_MAIN = 'mobo_net_subs.txt'
STATE_FILE = 'last_ids.json'
NEW_NAME = '@VPNProxyTest'
MAX_CONFIGS_PER_FILE = 444
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'

# Download settings
TEMP_DOWNLOAD_FOLDER = './temp_downloads'
MAX_FILE_SIZE_MB = 10

# Subscription link settings
SUBSCRIPTION_FETCH_TIMEOUT = 10  # Reduced from 20
MAX_SUBSCRIPTION_SIZE_MB = 3     # Reduced from 5

COUNTRY_FLAGS = {
    "AD": "🇦🇩", "AE": "🇦🇪", "AF": "🇦🇫", "AG": "🇦🇬", "AI": "🇦🇮", "AL": "🇦🇱", "AM": "🇦🇲", "AO": "🇦🇴", "AQ": "🇦🇶", "AR": "🇦🇷", "AS": "🇦🇸", "AT": "🇦🇹", "AU": "🇦🇺", "AW": "🇦🇼", "AX": "🇦🇽", "AZ": "🇦🇿", "BA": "🇧🇦", "BB": "🇧🇧", "BD": "🇧🇩", "BE": "🇧🇪", "BF": "🇧🇫", "BG": "🇧🇬", "BH": "🇧🇭", "BI": "🇧🇮", "BJ": "🇧🇯", "BL": "🇧🇱", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴", "BR": "🇧🇷", "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿", "CA": "🇨🇦", "CC": "🇨🇨", "CD": "🇨🇩", "CF": "🇨🇫", "CG": "🇨🇬", "CH": "🇨🇭", "CI": "🇨🇮", "CK": "🇨🇰", "CL": "🇨🇱", "CM": "🇨🇲", "CN": "🇨🇳", "CO": "🇨🇴", "CR": "🇨🇷", "CU": "🇨🇺", "CV": "🇨🇻", "CW": "🇨🇼", "CX": "🇨🇽", "CY": "🇨🇾", "CZ": "🇨🇿", "DE": "🇩🇪", "DJ": "🇩🇯", "DK": "🇩🇰", "DM": "🇩🇲", "DO": "🇩🇴", "DZ": "🇩🇿", "EC": "🇪🇨", "EE": "🇪🇪", "EG": "🇪🇬", "EH": "🇪🇭", "ER": "🇪🇷", "ES": "🇪🇸", "ET": "🇪🇹", "FI": "🇫🇮", "FJ": "🇫🇯", "FK": "🇫🇰", "FM": "🇫🇲", "FO": "🇫🇴", "FR": "🇫🇷", "GA": "🇬🇦", "GB": "🇬🇧", "GD": "🇬🇩", "GE": "🇬🇪", "GF": "🇬🇫", "GG": "🇬🇬", "GH": "🇬🇭", "GI": "🇬🇮", "GL": "🇬🇱", "GM": "🇬🇲", "GN": "🇬🇳", "GP": "🇬🇵", "GQ": "🇬🇶", "GR": "🇬🇷", "GT": "🇬🇹", "GU": "🇬🇺", "GW": "🇬🇼", "GY": "🇬🇾", "HK": "🇭🇰", "HN": "🇭🇳", "HR": "🇭🇷", "HT": "🇭🇹", "HU": "🇭🇺", "ID": "🇮🇩", "IE": "🇮🇪", "IL": "🇮🇱", "IM": "🇮🇲", "IN": "🇮🇳", "IO": "🇮🇴", "IQ": "🇮🇶", "IR": "🇮🇷", "IS": "🇮🇸", "IT": "🇮🇹", "JE": "🇯🇪", "JM": "🇯🇲", "JO": "🇯🇴", "JP": "🇯🇵", "KE": "🇰🇪", "KG": "🇰🇬", "KH": "🇰🇭", "KI": "🇰🇮", "KM": "🇰🇲", "KN": "🇰🇳", "KP": "🇰🇵", "KR": "🇰🇷", "KW": "🇰🇼", "KY": "🇰🇾", "KZ": "🇰🇿", "LA": "🇱🇦", "LB": "🇱🇧", "LC": "🇱🇨", "LI": "🇱🇮", "LK": "🇱🇰", "LR": "🇱🇷", "LS": "🇱🇸", "LT": "🇱🇹", "LU": "🇱🇺", "LV": "🇱🇻", "LY": "🇱🇾", "MA": "🇲🇦", "MC": "🇲🇨", "MD": "🇲🇩", "ME": "🇲🇪", "MG": "🇲🇬", "MH": "🇲🇭", "MK": "🇲🇰", "ML": "🇲🇱", "MM": "🇲🇲", "MN": "🇲🇳", "MO": "🇲🇴", "MP": "🇲🇵", "MQ": "🇲🇶", "MR": "🇲🇷", "MS": "🇲🇸", "MT": "🇲🇹", "MU": "🇲🇺", "MV": "🇲🇻", "MW": "🇲🇼", "MX": "🇲🇽", "MY": "🇲🇾", "MZ": "🇲🇿", "NA": "🇳🇦", "NC": "🇳🇨", "NE": "🇳🇪", "NF": "🇳🇫", "NG": "🇳🇬", "NI": "🇳🇮", "NL": "🇳🇱", "NO": "🇳🇴", "NP": "🇳🇵", "NR": "🇳🇷", "NU": "🇳🇺", "NZ": "🇳🇿", "OM": "🇴🇲", "PA": "🇵🇦", "PE": "🇵🇪", "PF": "🇵🇫", "PG": "🇵🇬", "PH": "🇵🇭", "PK": "🇵🇰", "PL": "🇵🇱", "PM": "🇵🇲", "PR": "🇵🇷", "PS": "🇵🇸", "PT": "🇵🇹", "PW": "🇵🇼", "PY": "🇵🇾", "QA": "🇶🇦", "RE": "🇷🇪", "RO": "🇷🇴", "RS": "🇷🇸", "RU": "🇷🇺", "RW": "🇷🇼", "SA": "🇸🇦", "SB": "🇸🇧", "SC": "🇸🇨", "SD": "🇸🇩", "SE": "🇸🇪", "SG": "🇸🇬", "SH": "🇸🇭", "SI": "🇸🇮", "SK": "🇸🇰", "SL": "🇸🇱", "SM": "🇸🇲", "SN": "🇸🇳", "SO": "🇸🇴", "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SV": "🇸🇻", "SX": "🇸🇽", "SY": "🇸🇾", "SZ": "🇸🇿", "TC": "🇹🇨", "TD": "🇹🇩", "TG": "🇹🇬", "TH": "🇹🇭", "TJ": "🇹🇯", "TK": "🇹🇰", "TL": "🇹🇱", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TR": "🇹🇷", "TT": "🇹🇹", "TV": "🇹🇻", "TW": "🇹🇼", "TZ": "🇹🇿", "UA": "🇺🇦", "UG": "🇺🇬", "US": "🇺🇸", "UY": "🇺🇾", "UZ": "🇺🇿", "VA": "🇻🇦", "VC": "🇻🇨", "VE": "🇻🇪", "VG": "🇻🇬", "VI": "🇻🇮", "VN": "🇻🇳", "VU": "🇻🇺", "WF": "🇼🇫", "WS": "🇼🇸", "YE": "🇾🇪", "YT": "🇾🇹", "ZA": "🇿🇦", "ZM": "🇿🇲", "ZW": "🇿🇼", "XX": "🔓"
}

# --- Caching & Global Variables ---
dns_cache = {}
geoip_reader = None
stats_npvt_files_found = 0
stats_subscriptions_processed = 0
stats_subscription_configs = 0
stats_subscription_skipped = 0

# =========================
# Database Rotation Helpers
# =========================
def get_current_db_index(db_type):
    """Get current database index (1-4) for SNI or IP"""
    state = {}
    if os.path.exists(DB_STATE_FILE):
        try:
            with open(DB_STATE_FILE, 'r') as f:
                state = json.load(f)
        except:
            pass
    return state.get(db_type, 1)

def set_current_db_index(db_type, index):
    """Set current database index"""
    state = {}
    if os.path.exists(DB_STATE_FILE):
        try:
            with open(DB_STATE_FILE, 'r') as f:
                state = json.load(f)
        except:
            pass
    state[db_type] = index
    with open(DB_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_db_filename(base_name, index):
    """Get database filename with rotation index (e.g., database_sni_1.txt)"""
    name, ext = os.path.splitext(base_name)
    return f"{name}_{index}{ext}"

def load_database(db_file):
    """Load configs from ALL rotated database files"""
    all_configs = set()
    
    # Try loading from rotated files (database_X_1.txt, database_X_2.txt, etc.)
    for i in range(1, MAX_DB_COUNT + 1):
        filename = get_db_filename(db_file, i)
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        decoded = base64.b64decode(content).decode('utf-8')
                        all_configs.update(decoded.splitlines())
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    # Also try loading from legacy single file (for backwards compatibility)
    if os.path.exists(db_file) and not any(os.path.exists(get_db_filename(db_file, i)) for i in range(1, MAX_DB_COUNT + 1)):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    decoded = base64.b64decode(content).decode('utf-8')
                    all_configs.update(decoded.splitlines())
        except Exception as e:
            print(f"Warning: Could not load {db_file}: {e}")
    
    return all_configs

def save_database(db_file, configs_set):
    """Save database with automatic rotation when size exceeds limit"""
    # Determine database type for rotation tracking
    if 'sni' in db_file.lower():
        db_type = 'sni'
    elif 'ip' in db_file.lower():
        db_type = 'ip'
    else:
        db_type = 'other'
    
    current_idx = get_current_db_index(db_type)
    current_file = get_db_filename(db_file, current_idx)
    
    # Prepare content
    content = "\n".join(sorted(configs_set))
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    estimated_size = len(encoded.encode('utf-8'))
    size_mb = estimated_size / (1024 * 1024)
    
    # Check if we need to rotate
    if estimated_size > MAX_DB_SIZE_BYTES:
        next_idx = (current_idx % MAX_DB_COUNT) + 1
        current_file = get_db_filename(db_file, next_idx)
        set_current_db_index(db_type, next_idx)
        print(f"🔄 Database rotation: {db_type.upper()} -> file #{next_idx} (exceeded {MAX_DB_SIZE_MB}MB limit)")
    
    # Save to current file
    try:
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write(encoded)
        print(f"💾 Saved {current_file} ({size_mb:.2f} MB, {len(configs_set)} configs)")
    except Exception as e:
        print(f"Error saving {current_file}: {e}")

# =========================
# Subscription Link Helpers
# =========================

# Blacklisted domains that are NOT subscription services
SUBSCRIPTION_BLACKLIST = [
    't.me/proxy',           # Telegram MTProxy
    't.me/socks',           # Telegram SOCKS proxy
    'telegram.me/proxy',
    'telegram.me/socks',
    'telegram.org',
    'telegram.dog',
    'telesco.pe',
    'twitter.com',
    'x.com',
    'facebook.com',
    'fb.com',
    'instagram.com',
    'youtube.com',
    'youtu.be',
    'tiktok.com',
    'reddit.com',
    'discord.gg',
    'discord.com',
    'wa.me',                # WhatsApp
    'whatsapp.com',
    'bit.ly',               # URL shorteners (usually spam)
    'tinyurl.com',
    'goo.gl',
    't.co',
    'ow.ly',
    'is.gd',
    'buff.ly',
]

# Whitelist patterns for known subscription services
SUBSCRIPTION_WHITELIST_PATTERNS = [
    r'\.workers\.dev/',      # Cloudflare Workers (common for subs)
    r'/sub/',                # Common subscription path
    r'/api/v\d+/',           # API endpoints
    r'/link/',               # Link endpoints
    r'/profile/',            # Profile links
    r'\.txt$',               # Direct text files
    r'\.json$',              # JSON files
    r'/raw/',                # Raw paste services
    r'/v2ray',               # V2Ray endpoints
    r'/clash',               # Clash endpoints
    r'/shadowrocket',        # Shadowrocket
]

def is_valid_subscription_url(url):
    """Check if URL is likely a real subscription link"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Check blacklist first (fast rejection)
    for blocked in SUBSCRIPTION_BLACKLIST:
        if blocked in url_lower:
            return False
    
    # Must be http/https
    if not url_lower.startswith(('http://', 'https://')):
        return False
    
    # Reject t.me links entirely (they're never subscription services)
    if 't.me/' in url_lower or 'telegram.me/' in url_lower or 'telegram.dog/' in url_lower:
        return False
    
    # Check whitelist patterns (strong indicators)
    for pattern in SUBSCRIPTION_WHITELIST_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    # Additional heuristics
    parsed = urlparse(url)
    
    # Reject if no path or very short path (likely spam)
    if not parsed.path or len(parsed.path) < 3:
        return False
    
    # Reject common spam patterns
    spam_patterns = [
        r'tag=d_\d+',          # Ad tracking
        r'click\d+',           # Click trackers
        r'redirect',           # Redirects
        r'goto',
        r'track',
        r'adv\d+',
        r'/ad/',
        r'utm_',               # UTM tracking parameters
        r'affiliate',
    ]
    for spam in spam_patterns:
        if re.search(spam, url, re.IGNORECASE):
            return False
    
    # If URL has UUID/hash-like patterns, it's likely legitimate
    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
    long_hash_pattern = r'[a-zA-Z0-9_-]{20,}'
    
    if re.search(uuid_pattern, url) or re.search(long_hash_pattern, parsed.path):
        return True
    
    # Default: reject (conservative approach)
    return False

def find_subscription_urls(text):
    """Extract subscription URLs from text with smart filtering"""
    if not text:
        return []
    
    # Pattern for HTTP/HTTPS URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:/[^\s<>"{}|\\^`\[\]]*)?'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    # Filter and validate
    subscription_urls = []
    
    for url in urls:
        # Clean URL (remove trailing punctuation)
        url = url.rstrip('.,;:!?)\]*')
        
        # Validate
        if is_valid_subscription_url(url):
            subscription_urls.append(url)
    
    return list(set(subscription_urls))

def fetch_subscription_content(url):
    """Fetch content from subscription URL"""
    try:
        headers = {
            'User-Agent': 'clash-verge/v1.3.8',  # Mimic VPN client
            'Accept': 'text/html,application/json,text/plain,*/*',
            'Accept-Encoding': 'gzip, deflate',
        }
        
        response = requests.get(
            url, 
            headers=headers, 
            timeout=SUBSCRIPTION_FETCH_TIMEOUT,
            allow_redirects=True,
            stream=True
        )
        
        if response.status_code == 200:
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_SUBSCRIPTION_SIZE_MB * 1024 * 1024:
                return None
            
            # Read content with size limit
            content = b''
            max_size = MAX_SUBSCRIPTION_SIZE_MB * 1024 * 1024
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > max_size:
                    return None
            
            return content.decode('utf-8', errors='ignore')
        else:
            return None
            
    except requests.exceptions.Timeout:
        pass  # Silent fail for timeouts
    except requests.exceptions.ConnectionError:
        pass  # Silent fail for connection errors
    except Exception:
        pass  # Silent fail for all other errors
    
    return None

def extract_configs_from_subscription(content):
    """Extract configs from subscription content (handles text, base64, JSON)"""
    if not content:
        return []
    
    configs = set()
    
    # Strategy 1: Try as plaintext first
    configs.update(find_and_validate_configs(content))
    
    # Strategy 2: Try base64 decode (common for subscription links)
    if not configs:  # Only try if plaintext found nothing
        try:
            clean_content = content.strip()
            decoded = base64.b64decode(clean_content).decode('utf-8', errors='ignore')
            configs.update(find_and_validate_configs(decoded))
        except:
            pass
    
    # Strategy 3: Try as JSON
    if not configs:  # Only try if previous methods found nothing
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
    """Find and process all subscription URLs in text"""
    global stats_subscriptions_processed, stats_subscription_configs, stats_subscription_skipped
    
    urls = find_subscription_urls(text)
    if not urls:
        return []
    
    all_configs = []
    
    for url in urls:
        # Truncate long URLs for display
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
# Active File Helpers
# =========================
def save_active_file(filepath, configs_list):
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

def merge_active_by_fingerprint(existing_list, new_list):
    combined = existing_list + new_list
    seen = set()
    dedup_reversed = []
    for cfg in reversed(combined):
        fp = get_config_fingerprint(cfg)
        key = fp if fp else f"RAW::{cfg}"
        if key not in seen:
            dedup_reversed.append(cfg)
            seen.add(key)
    dedup = list(reversed(dedup_reversed))
    if len(dedup) > MAX_ACTIVE_CONFIGS:
        dedup = dedup[-MAX_ACTIVE_CONFIGS:]
    return dedup

# =========================
# Resolution & parsing
# =========================
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

def replace_address_with_sni(config_str):
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
    if not config:
        return None
    config = config.strip()
    while config and config[-1] in '.,;!?:\'"`""''«»‹›':
        config = config[:-1]
    config = config.strip()
    return config if config else None

def validate_config_length(config):
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
    flag = country_code_to_flag(country_code)
    new_name_with_flags = f"{flag} {name} {flag}"
    return f"{link.split('#')[0]}#{quote(new_name_with_flags)}"

# =========================
# File download & parsing
# =========================
async def process_txt_file(client, message):
    configs_found = []
    
    if not message.document:
        return configs_found
    
    filename = message.file.name or ""
    mime_type = message.file.mime_type or ""
    
    if filename.lower().endswith('.npvt'):
        print(f"  ⚠️ Skipping .npvt file (not supported): {filename}")
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
                print(f"  ❌ Could not read file: {filename}")
                content = ""
        
        if content and re.match(r'^[A-Za-z0-9+/=\s]+$', content.strip()):
            try:
                decoded = base64.b64decode(content.strip()).decode('utf-8')
                content = decoded
                print(f"  ℹ️  Decoded base64 content")
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
                    print(f"  ❌ Skipping {group_str} (wait too long: {wait_time/60:.1f} min)")
                    channels_skipped += 1
                    break
                else:
                    print(f"  ⏳ Waiting {wait_time}s + 5s buffer...")
                    await asyncio.sleep(wait_time + 5)
                    
            except (ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError) as e:
                print(f"  ❌ Channel access error for {group_str}: {type(e).__name__}")
                channels_skipped += 1
                break
                
            except Exception as e:
                print(f"  ❌ Error scraping {group_str}: {e}")
                if attempt < max_retries - 1:
                    print(f"  🔄 Retrying in 10s...")
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
                except Exception: 
                    pass
            
            # Process .txt file attachments
            if message.document:
                file_configs = await process_txt_file(client, message)
                if file_configs:
                    scraped_configs.update(file_configs)
                    total_files_processed += 1
                    total_configs_from_files += len(file_configs)
            
            # Process text configs
            combined_text = "\n".join(texts_to_scan)
            for config in find_and_validate_configs(combined_text):
                scraped_configs.add(config)
            
            # Process subscription links
            subscription_configs = await process_subscription_links(combined_text)
            if subscription_configs:
                scraped_configs.update(subscription_configs)
    
    # Clean up temp folder
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

# --- MAIN FUNCTION ---
async def main():
    global geoip_reader
    
    if not all([API_ID, API_HASH, SESSION_STRING]): 
        print("FATAL: Required secrets not set.")
        return

    # GeoIP download
    if not os.path.exists(GEOIP_DB_PATH):
        print("Downloading GeoIP database...")
        urls = [
            "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb",
            "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb",
            "https://git.io/GeoLite2-Country.mmdb"
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

    last_ids = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f: 
            last_ids = json.load(f)
    
    # Use StringSession directly
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

    # ========== SNI DATABASE PROCESSING ==========
    print(f"\n{'='*70}")
    print(f"  SNI DATABASE PROCESSING")
    print(f"{'='*70}")
    
    db_sni = load_database(DATABASE_SNI)
    print(f"Loaded {len(db_sni)} historical SNI configs from all databases")
    
    sni_configs_in_order = []
    for cfg in newly_scraped_configs:
        sni_cfg = replace_address_with_sni(cfg)
        attrs = get_config_attributes(sni_cfg)
        if attrs:
            renamed = rename_config(sni_cfg, NEW_NAME, attrs['country'])
            sni_configs_in_order.append(renamed)
        else:
            sni_configs_in_order.append(sni_cfg)
    
    sni_new = [c for c in sni_configs_in_order if c not in db_sni]
    print(f"Found {len(sni_new)} NEW SNI configs")
    if sni_new:
        db_sni.update(sni_new)
        save_database(DATABASE_SNI, db_sni)
        existing_active_sni = load_list_from_file(ACTIVE_FILE_SNI) or []
        active_sni_merged = merge_active_by_fingerprint(existing_active_sni, sni_new)
        saved_count = save_active_file(ACTIVE_FILE_SNI, active_sni_merged)
        print(f"✓ Saved {saved_count} to {ACTIVE_FILE_SNI} (accumulated)")
    else:
        print(f"No new SNI configs to add this run (active file left unchanged)")

    # ========== IP DATABASE PROCESSING ==========
    print(f"\n{'='*70}")
    print(f"  IP DATABASE PROCESSING")
    print(f"{'='*70}")
    
    db_ip = load_database(DATABASE_IP)
    print(f"Loaded {len(db_ip)} historical IP configs from all databases")
    
    new_configs_data = []
    seen_fingerprints = set()
    stats = {'total_scraped': len(newly_scraped_configs), 'failed_parse': 0, 'duplicates': 0, 'valid_unique': 0}
    
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
            new_configs_data.append({'renamed': renamed_config, 'attrs': attrs, 'fingerprint': fingerprint})
            stats['valid_unique'] += 1
        else:
            stats['failed_parse'] += 1
    
    print(f"Processed: {stats['valid_unique']} valid, {stats['duplicates']} duplicates, {stats['failed_parse']} failed")
    
    ip_configs_in_order = [item['renamed'] for item in new_configs_data]
    ip_new = [c for c in ip_configs_in_order if c not in db_ip]
    print(f"Found {len(ip_new)} NEW IP configs")
    if ip_new:
        db_ip.update(ip_new)
        save_database(DATABASE_IP, db_ip)
        existing_active_ip = load_list_from_file(ACTIVE_FILE_IP) or []
        active_ip_merged = merge_active_by_fingerprint(existing_active_ip, ip_new)
        saved_count = save_active_file(ACTIVE_FILE_IP, active_ip_merged)
        print(f"✓ Saved {saved_count} to {ACTIVE_FILE_IP} (accumulated)")
    else:
        print(f"No new IP configs to add this run (active file left unchanged)")

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
    
    def load_file_decoded(path):
        return load_list_from_file(path)

    for path in sorted(list(all_possible_paths)):
        raw_existing_list = load_file_decoded(path)
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

    # FINAL SUMMARY
    print(f"\n{'='*70}")
    print(f"  FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Raw scraped            : {len(newly_scraped_configs)}")
    print(f"  SNI Database total     : {len(load_database(DATABASE_SNI))}")
    print(f"  IP Database total      : {len(load_database(DATABASE_IP))}")
    print(f"  Active SNI (current)   : {len(load_list_from_file(ACTIVE_FILE_SNI))}")
    print(f"  Active IP (current)    : {len(load_list_from_file(ACTIVE_FILE_IP))}")
    print(f"  Categorized files      : {final_file_count} (444 limit)")
    print(f"  DNS cache entries      : {len(dns_cache)}")
    if stats_subscriptions_processed > 0:
        print(f"  Valid subscriptions    : {stats_subscriptions_processed}")
        print(f"  Configs from subs      : {stats_subscription_configs}")
    print(f"{'='*70}")
    
    if new_latest_ids:
        with open(STATE_FILE, 'w') as f: 
            json.dump(new_latest_ids, f, indent=2)
        print(f"\n✓ Bookmarks saved to {STATE_FILE}")
    
    print("\n✓ COMPLETE - Databases & Active Files Updated!")

if __name__ == "__main__":
    asyncio.run(main())
