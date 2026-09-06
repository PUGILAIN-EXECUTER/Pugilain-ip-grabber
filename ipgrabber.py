import base64
import hashlib
import html
import ipaddress
import json
import os
import platform
import secrets
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

APP_NAME = "PUGILAIN IP GRB"
APP_VERSION = "3.0"
HOST = "127.0.0.1"
PORT = 5000
PROJECT_NAME = "Ipporject"
GEO_PROVIDER = "https://ipapi.co"
MAX_BODY_SIZE = 16384
GEO_TIMEOUT = 8
CONSENT_VERSION = "1.0"

BANNER = r"""
::::::::::.  ...    :::  .,-:::::/  ::: :::       :::.      ::::::.    :::.   :::     .,-:::::/  
 `;;;```.;;; ;;     ;;;,;;-'````'   ;;; ;;;       ;;`;;     ;;;`;;;;,  `;;;   ;;;   ,;;-'````'   
  `]]nnn]]' [['     [[[[[[   [[[[[[/[[[ [[[      ,[[ '[[,   [[[  [[[[[. '[[   [[[   [[[   [[[[[[/
   $$$""    $$      $$$"$$c.    "$$ $$$ $$'     c$$$cc$$$c  $$$  $$$ "Y$c$$   $$$   "$$c.    "$$ 
   888o     88    .d888 `Y8bo,,,o88o888o88oo,.__ 888   888  888  888    Y88   888d8b `Y8bo,,,o88o
   YMMMb     "YmmMMMM""   `'YMUP"YMMMMM""""YUMMM YMM   \"\"`MMM  MMM     YM   MMMYMP   `'YMUP"YMM
                                      PUGILAIN IP GRABBER
                                                                                                 
                                                                                      
"""

START_TIME = time.time()
SERVER = None
SERVER_THREAD = None
SERVER_LOCK = threading.RLock()
STATE_LOCK = threading.RLock()
RATE_LOCK = threading.RLock()

RUNTIME = {
    "requests": 0,
    "consented": 0,
    "successful": 0,
    "failed": 0,
    "last_result": None,
    "started": False,
    "stopped": False
}

RATE_STATE = {
    "started": time.monotonic(),
    "count": 0
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def terminal(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()


def slow_print(text, delay=0.003):
    for char in str(text):
        terminal(char)
        time.sleep(delay)
    print()


def loading_animation(duration, message):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + duration
    while time.time() < end:
        for char in chars:
            if time.time() >= end:
                break
            terminal(f"\r\033[96m{char} {message}\033[0m")
            time.sleep(0.07)
    terminal("\r" + " " * 90 + "\r")


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_iso_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def get_unix_timestamp():
    return int(time.time())


def format_uptime(seconds):
    value = max(0, int(seconds))
    days, value = divmod(value, 86400)
    hours, value = divmod(value, 3600)
    minutes, seconds = divmod(value, 60)

    if days:
        return f"{days}d {hours}h {minutes}m {seconds}s"

    if hours:
        return f"{hours}h {minutes}m {seconds}s"

    if minutes:
        return f"{minutes}m {seconds}s"

    return f"{seconds}s"


def format_bytes(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "0.00 B"

    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if number < 1024:
            return f"{number:.2f} {unit}"
        number /= 1024

    return f"{number:.2f} PB"


def encode_base64(data):
    raw = json.dumps(
        data,
        ensure_ascii=False
    ).encode("utf-8")

    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_base64(data):
    raw = base64.urlsafe_b64decode(
        data.encode("ascii")
    )

    return json.loads(
        raw.decode("utf-8")
    )


def generate_device_id():
    material = "|".join(
        [
            platform.system(),
            platform.release(),
            platform.machine(),
            platform.python_version()
        ]
    )

    digest = hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()

    return digest[:16]


def generate_token():
    return secrets.token_urlsafe(48)


def safe_text(value, default="N/A"):
    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def html_text(value, default="N/A"):
    return html.escape(
        safe_text(value, default)
    )


def desktop_path():
    return os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )


def get_project_folder():
    preferred = os.path.join(
        desktop_path(),
        PROJECT_NAME
    )

    try:
        os.makedirs(
            preferred,
            exist_ok=True
        )
        return preferred
    except OSError:
        fallback = os.path.join(
            os.path.expanduser("~"),
            "." + PROJECT_NAME.lower()
        )

        os.makedirs(
            fallback,
            exist_ok=True
        )

        return fallback


PROJECT_FOLDER = get_project_folder()

INSTANCE_FILE = os.path.join(
    PROJECT_FOLDER,
    ".instance.json"
)

KEY_FILE = os.path.join(
    PROJECT_FOLDER,
    "key.txt"
)

CONFIG_FILE = os.path.join(
    PROJECT_FOLDER,
    "config.json"
)

LOG_FILE = os.path.join(
    PROJECT_FOLDER,
    "system.log"
)


def read_text(path, default=""):
    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()
    except (OSError, UnicodeError):
        return default


def write_text(path, value):
    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(value)


def load_json(path, default=None):
    if default is None:
        default = {}

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return default

    except (
        OSError,
        ValueError,
        TypeError,
        UnicodeError
    ):
        return default


def save_json(path, data):
    temporary = path + ".tmp"

    with open(
        temporary,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    os.replace(
        temporary,
        path
    )


def log_message(message):
    timestamp = get_timestamp()

    line = (
        f"[{timestamp}] "
        f"{safe_text(message, '')}\n"
    )

    try:
        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:
            file.write(line)
    except OSError:
        pass

    print(
        f"\033[90m[{timestamp}] "
        f"{safe_text(message, '')}\033[0m"
    )


def validate_ip(value):
    try:
        ipaddress.ip_address(
            str(value)
        )
        return True
    except ValueError:
        return False


def normalize_ip(value):
    value = safe_text(
        value,
        ""
    )

    if not validate_ip(value):
        return ""

    return value


def is_private_ip(value):
    try:
        address = ipaddress.ip_address(
            str(value)
        )
    except ValueError:
        return True

    return any(
        [
            address.is_private,
            address.is_loopback,
            address.is_link_local,
            address.is_reserved,
            address.is_multicast,
            address.is_unspecified
        ]
    )


def get_local_ip():
    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        ) as sock:
            sock.connect(
                ("1.1.1.1", 80)
            )

            return sock.getsockname()[0]

    except OSError:
        return "127.0.0.1"


def get_hostname():
    try:
        return socket.gethostname()
    except OSError:
        return "unknown"


def get_server_url():
    return f"http://{HOST}:{PORT}"


def get_lan_url():
    return f"http://{get_local_ip()}:{PORT}"


def port_available(host, port):
    try:
        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as sock:
            sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            sock.bind(
                (host, port)
            )

            return True

    except OSError:
        return False


def create_instance_state():
    return {
        "instance_key": generate_token(),
        "device_id": generate_device_id(),
        "created_at": get_iso_timestamp(),
        "version": APP_VERSION,
        "application": APP_NAME,
        "privacy_mode": "consent_required",
        "gps": False,
        "fingerprinting": False,
        "visitor_storage": False,
        "visitor_history": False
    }


def load_instance():
    with STATE_LOCK:
        state = load_json(
            INSTANCE_FILE,
            {}
        )

        if not state.get("instance_key"):
            state = create_instance_state()
            save_json(
                INSTANCE_FILE,
                state
            )

        if not state.get("device_id"):
            state["device_id"] = generate_device_id()

            save_json(
                INSTANCE_FILE,
                state
            )

        return state


INSTANCE = load_instance()

SECRET_KEY = INSTANCE["instance_key"]
DEVICE_ID = INSTANCE["device_id"]


def save_instance():
    with STATE_LOCK:
        save_json(
            INSTANCE_FILE,
            INSTANCE
        )


def write_key():
    write_text(
        KEY_FILE,
        SECRET_KEY
    )


def build_config():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "host": HOST,
        "port": PORT,
        "device_id": DEVICE_ID,
        "created_at": INSTANCE.get("created_at"),
        "updated_at": get_iso_timestamp(),
        "privacy": {
            "consent_required": True,
            "gps": False,
            "fingerprinting": False,
            "visitor_storage": False,
            "visitor_history": False
        },
        "geolocation": {
            "provider": GEO_PROVIDER,
            "approximate": True
        }
    }


def save_config():
    save_json(
        CONFIG_FILE,
        build_config()
    )


def initialize_files():
    os.makedirs(
        PROJECT_FOLDER,
        exist_ok=True
    )

    write_key()
    save_config()

    log_message(
        "Configuration initialized"
    )

    log_message(
        "Consent mode enabled"
    )

    log_message(
        "Visitor storage disabled"
    )


def rotate_key():
    global SECRET_KEY

    new_key = generate_token()

    with STATE_LOCK:
        INSTANCE["instance_key"] = new_key
        INSTANCE["rotated_at"] = get_iso_timestamp()

        SECRET_KEY = new_key

        save_instance()

    write_key()
    save_config()

    log_message(
        "Instance key rotated"
    )

    return new_key


def reset_key():
    print()
    print(
        "\033[93mRESET INSTANCE KEY\033[0m"
    )
    print(
        "La chiave precedente verrà invalidata."
    )

    answer = input(
        "Scrivi YES per confermare: "
    ).strip()

    if answer != "YES":
        print(
            "\033[90mOperazione annullata.\033[0m"
        )
        return

    new_key = rotate_key()

    print(
        "\033[92m[✓] Nuova chiave:\033[0m"
    )

    print(new_key)


def register_request():
    with STATE_LOCK:
        RUNTIME["requests"] += 1


def register_consent():
    with STATE_LOCK:
        RUNTIME["consented"] += 1


def register_success(data):
    with STATE_LOCK:
        RUNTIME["successful"] += 1
        RUNTIME["last_result"] = dict(data)


def register_failure():
    with STATE_LOCK:
        RUNTIME["failed"] += 1


def clear_result():
    with STATE_LOCK:
        RUNTIME["last_result"] = None


def get_runtime():
    with STATE_LOCK:
        return {
            "requests": RUNTIME["requests"],
            "consented": RUNTIME["consented"],
            "successful": RUNTIME["successful"],
            "failed": RUNTIME["failed"],
            "uptime": format_uptime(
                time.time() - START_TIME
            ),
            "running": (
                RUNTIME["started"]
                and not RUNTIME["stopped"]
            )
        }


def get_last_result():
    with STATE_LOCK:
        value = RUNTIME["last_result"]

        if value is None:
            return None

        return dict(value)


def allow_request():
    with RATE_LOCK:
        now = time.monotonic()

        if now - RATE_STATE["started"] >= 1:
            RATE_STATE["started"] = now
            RATE_STATE["count"] = 0

        if RATE_STATE["count"] >= 20:
            return False

        RATE_STATE["count"] += 1

        return True


def parse_content_length(handler):
    raw = handler.headers.get(
        "Content-Length",
        "0"
    )

    try:
        value = int(raw)
    except ValueError:
        return 0

    return max(
        0,
        value
    )


def read_body(handler):
    length = parse_content_length(
        handler
    )

    if length > MAX_BODY_SIZE:
        raise ValueError(
            "Request body too large"
        )

    return handler.rfile.read(
        length
    )


def parse_json_body(handler):
    raw = read_body(
        handler
    )

    if not raw:
        return {}

    try:
        data = json.loads(
            raw.decode("utf-8")
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError
    ):
        raise ValueError(
            "Invalid JSON"
        )

    if not isinstance(data, dict):
        raise ValueError(
            "JSON object required"
        )

    return data


def valid_consent(data):
    return (
        data.get("consent") is True
        and data.get("purpose")
        == "approximate_ip_geolocation"
        and data.get("consent_version")
        == CONSENT_VERSION
    )


def get_requester_ip(handler):
    address = handler.client_address

    if not address:
        return ""

    return normalize_ip(
        address[0]
    )


def external_get(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "PUGILAIN-IP-GRB/3.0"
        },
        method="GET"
    )

    with urllib.request.urlopen(
        request,
        timeout=GEO_TIMEOUT
    ) as response:
        raw = response.read(
            MAX_BODY_SIZE
        )

        return json.loads(
            raw.decode("utf-8")
        )


def clean_geo_data(data, ip):
    if not isinstance(data, dict):
        return None

    return {
        "ip": ip,
        "country": safe_text(
            data.get("country_name")
        ),
        "country_code": safe_text(
            data.get("country_code")
        ),
        "region": safe_text(
            data.get("region")
        ),
        "city": safe_text(
            data.get("city")
        ),
        "postal_code": safe_text(
            data.get("postal")
        ),
        "timezone": safe_text(
            data.get("timezone")
        ),
        "latitude": data.get(
            "latitude"
        ),
        "longitude": data.get(
            "longitude"
        ),
        "approximate": True,
        "provider": GEO_PROVIDER
    }


def get_client_info(ip):
    return get_ip_location(
        ip
    )


def get_ip_location(ip):
    ip = normalize_ip(ip)

    if not ip:
        register_failure()

        return {
            "success": False,
            "error": "Invalid IP address"
        }

    if is_private_ip(ip):
        return {
            "success": False,
            "error": "Private or local address"
        }

    encoded = urllib.parse.quote(
        ip,
        safe=""
    )

    url = (
        f"{GEO_PROVIDER}/"
        f"{encoded}/json/"
    )

    try:
        data = external_get(
            url
        )

    except urllib.error.HTTPError as error:
        register_failure()

        return {
            "success": False,
            "error":
                f"Provider HTTP {error.code}"
        }

    except urllib.error.URLError:
        register_failure()

        return {
            "success": False,
            "error":
                "Geolocation provider unavailable"
        }

    except (
        TimeoutError,
        json.JSONDecodeError,
        UnicodeDecodeError
    ):
        register_failure()

        return {
            "success": False,
            "error":
                "Invalid provider response"
        }

    except Exception:
        register_failure()

        return {
            "success": False,
            "error":
                "Geolocation lookup failed"
        }

    if data.get("error") is True:
        register_failure()

        return {
            "success": False,
            "error": safe_text(
                data.get("reason"),
                "Lookup failed"
            )
        }

    result = clean_geo_data(
        data,
        ip
    )

    if result is None:
        register_failure()

        return {
            "success": False,
            "error":
                "No geolocation data"
        }

    register_success(
        result
    )

    return {
        "success": True,
        "data": result
    }


def get_additional_geo(lat, lng):
    try:
        latitude = float(lat)
        longitude = float(lng)
    except (TypeError, ValueError):
        return None

    if not -90 <= latitude <= 90:
        return None

    if not -180 <= longitude <= 180:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
        "precision": "approximate"
    }


def make_map_link(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return ""

    if not -90 <= latitude <= 90:
        return ""

    if not -180 <= longitude <= 180:
        return ""

    return (
        "https://www.openstreetmap.org/"
        f"?mlat={latitude}"
        f"&mlon={longitude}"
        f"&zoom=10"
    )


def security_headers(handler):
    handler.send_header(
        "Cache-Control",
        "no-store, max-age=0"
    )

    handler.send_header(
        "Pragma",
        "no-cache"
    )

    handler.send_header(
        "X-Content-Type-Options",
        "nosniff"
    )

    handler.send_header(
        "X-Frame-Options",
        "DENY"
    )

    handler.send_header(
        "Referrer-Policy",
        "no-referrer"
    )

    handler.send_header(
        "Permissions-Policy",
        "geolocation=(), camera=(), microphone=()"
    )

    handler.send_header(
        "Content-Security-Policy",
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self'"
    )


def send_json(handler, status, data):
    body = json.dumps(
        data,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(
        status
    )

    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )

    handler.send_header(
        "Content-Length",
        str(len(body))
    )

    security_headers(
        handler
    )

    handler.end_headers()

    handler.wfile.write(
        body
    )


def send_html(handler, body, status=200):
    payload = body.encode(
        "utf-8"
    )

    handler.send_response(
        status
    )

    handler.send_header(
        "Content-Type",
        "text/html; charset=utf-8"
    )

    handler.send_header(
        "Content-Length",
        str(len(payload))
    )

    security_headers(
        handler
    )

    handler.end_headers()

    handler.wfile.write(
        payload
    )


def public_info():
    stats = get_runtime()

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status":
            "online"
            if stats["running"]
            else "offline",
        "privacy": {
            "consent_required": True,
            "gps": False,
            "fingerprinting": False,
            "visitor_storage": False,
            "visitor_history": False,
            "approximate_geolocation": True
        }
    }


def public_stats():
    stats = get_runtime()

    return {
        "status":
            "online"
            if stats["running"]
            else "offline",
        "requests":
            stats["requests"],
        "consented_requests":
            stats["consented"],
        "successful_lookups":
            stats["successful"],
        "failed_lookups":
            stats["failed"],
        "uptime":
            stats["uptime"]
    }


def admin_info():
    stats = get_runtime()

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "device_id": DEVICE_ID,
        "hostname": get_hostname(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "host": HOST,
        "port": PORT,
        "local_url": get_server_url(),
        "lan_url": get_lan_url(),
        "uptime": stats["uptime"],
        "requests": stats["requests"],
        "consented": stats["consented"],
        "successful": stats["successful"],
        "failed": stats["failed"],
        "gps": False,
        "fingerprinting": False,
        "visitor_storage": False
    }


def render_result(data):
    if not data:
        return """
        <div class="empty">
            <div class="empty-icon">◎</div>
            <div>Nessun risultato disponibile.</div>
        </div>
        """

    if not data.get("success"):
        return f"""
        <div class="result error">
            <div class="eyebrow">ERRORE</div>
            <h2>{html_text(data.get("error"))}</h2>
        </div>
        """

    geo = data.get(
        "data",
        {}
    )

    rows = [
        ("IP", geo.get("ip")),
        ("Paese", geo.get("country")),
        ("Codice", geo.get("country_code")),
        ("Regione", geo.get("region")),
        ("Città", geo.get("city")),
        ("CAP", geo.get("postal_code")),
        ("Fuso orario", geo.get("timezone")),
        ("Latitudine", geo.get("latitude")),
        ("Longitudine", geo.get("longitude")),
        ("Precisione", "Approssimativa")
    ]

    cells = []

    for label, value in rows:
        cells.append(
            f"""
            <div class="data-row">
                <span>{html_text(label)}</span>
                <strong>{html_text(value)}</strong>
            </div>
            """
        )

    map_link = make_map_link(
        geo.get("latitude"),
        geo.get("longitude")
    )

    map_button = ""

    if map_link:
        map_button = (
            '<a class="map-button" '
            f'href="{html.escape(map_link, quote=True)}" '
            'target="_blank" '
            'rel="noreferrer">Apri mappa</a>'
        )

    return f"""
    <div class="result">
        <div class="result-head">
            <div>
                <div class="eyebrow">RISULTATO</div>
                <h2>Geolocalizzazione IP</h2>
            </div>
            <div class="pill">CONSENSO</div>
        </div>
        <div class="grid">
            {''.join(cells)}
        </div>
        {map_button}
        <div class="notice">
            Il risultato è temporaneo e non viene salvato nello storico.
        </div>
    </div>
    """


def dashboard_html():
    return DASHBOARD_HTML.replace(
        "{{APP_NAME}}",
        html_text(APP_NAME)
    ).replace(
        "{{VERSION}}",
        html_text(APP_VERSION)
    )


class Handler(BaseHTTPRequestHandler):

    server_version = "PUGILAIN/3.0"

    def do_GET(self):
        register_request()

        if not allow_request():
            send_json(
                self,
                429,
                {
                    "success": False,
                    "error": "Rate limit"
                }
            )
            return

        path = urllib.parse.urlparse(
            self.path
        ).path

        if path in (
            "/",
            "/dashboard"
        ):
            send_html(
                self,
                dashboard_html()
            )
            return

        if path == "/health":
            send_json(
                self,
                200,
                {
                    "success": True,
                    "status": "online",
                    "uptime":
                        get_runtime()["uptime"]
                }
            )
            return

        if path == "/api/info":
            send_json(
                self,
                200,
                public_info()
            )
            return

        if path == "/api/stats":
            send_json(
                self,
                200,
                public_stats()
            )
            return

        if path == "/api/result":
            send_json(
                self,
                200,
                {
                    "success": True,
                    "data": get_last_result(),
                    "persistent": False
                }
            )
            return

        if path == "/api/admin":
            send_json(
                self,
                200,
                admin_info()
            )
            return

        send_json(
            self,
            404,
            {
                "success": False,
                "error": "Not found"
            }
        )

    def do_POST(self):
        register_request()

        if not allow_request():
            send_json(
                self,
                429,
                {
                    "success": False,
                    "error": "Rate limit"
                }
            )
            return

        path = urllib.parse.urlparse(
            self.path
        ).path

        if path != "/api/location":
            send_json(
                self,
                404,
                {
                    "success": False,
                    "error": "Not found"
                }
            )
            return

        try:
            data = parse_json_body(
                self
            )
        except ValueError as error:
            send_json(
                self,
                400,
                {
                    "success": False,
                    "error": str(error)
                }
            )
            return

        if not valid_consent(data):
            send_json(
                self,
                403,
                {
                    "success": False,
                    "error":
                        "Explicit consent required",
                    "required": {
                        "consent": True,
                        "purpose":
                            "approximate_ip_geolocation",
                        "consent_version":
                            CONSENT_VERSION
                    }
                }
            )
            return

        register_consent()

        requester_ip = get_requester_ip(
            self
        )

        if not requester_ip:
            send_json(
                self,
                400,
                {
                    "success": False,
                    "error":
                        "Unable to determine requester address"
                }
            )
            return

        result = get_ip_location(
            requester_ip
        )

        payload = {
            "success":
                result.get(
                    "success",
                    False
                ),
            "data":
                result.get("data"),
            "error":
                result.get("error"),
            "stored": False,
            "gps": False,
            "fingerprinting": False,
            "approximate": True
        }

        print_result(
            result
        )

        status = (
            200
            if result.get("success")
            else 502
        )

        send_json(
            self,
            status,
            payload
        )

    def do_OPTIONS(self):
        self.send_response(
            204
        )

        security_headers(
            self
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Access-Control-Max-Age",
            "600"
        )

        self.end_headers()

    def log_message(self, format_string, *args):
        return


def print_result(result):
    print()

    print(
        "\033[92m"
        + "╔"
        + "═" * 76
        + "╗"
        + "\033[0m"
    )

    print(
        "\033[92m║"
        + " " * 20
        + "CONSENTED REQUEST"
        + " " * 39
        + "║"
        + "\033[0m"
    )

    print(
        "\033[92m"
        + "╚"
        + "═" * 76
        + "╝"
        + "\033[0m"
    )

    if result.get("success"):
        data = result.get(
            "data",
            {}
        )

        print(
            f"\033[96mCountry:\033[0m "
            f"{safe_text(data.get('country'))}"
        )

        print(
            f"\033[96mRegion:\033[0m "
            f"{safe_text(data.get('region'))}"
        )

        print(
            f"\033[96mCity:\033[0m "
            f"{safe_text(data.get('city'))}"
        )

        print(
            f"\033[96mTimezone:\033[0m "
            f"{safe_text(data.get('timezone'))}"
        )

        print(
            f"\033[96mLatitude:\033[0m "
            f"{safe_text(data.get('latitude'))}"
        )

        print(
            f"\033[96mLongitude:\033[0m "
            f"{safe_text(data.get('longitude'))}"
        )

        print(
            "\033[90m"
            "Requester IP non salvato su disco."
            "\033[0m"
        )

    else:
        print(
            f"\033[91mLookup failed:\033[0m "
            f"{safe_text(result.get('error'))}"
        )

    print()


def self_test():
    results = []

    results.append(
        (
            "IPv4 validation",
            validate_ip("127.0.0.1")
        )
    )

    results.append(
        (
            "IPv6 validation",
            validate_ip("::1")
        )
    )

    results.append(
        (
            "Invalid IP rejection",
            not validate_ip(
                "999.999.999.999"
            )
        )
    )

    results.append(
        (
            "Private IP detection",
            is_private_ip(
                "127.0.0.1"
            )
        )
    )

    token = generate_token()

    results.append(
        (
            "Token generation",
            len(token) > 30
        )
    )

    sample = {
        "status": "ok",
        "value": 42
    }

    encoded = encode_base64(
        sample
    )

    results.append(
        (
            "Base64 roundtrip",
            decode_base64(encoded)
            == sample
        )
    )

    results.append(
        (
            "Project directory",
            os.path.isdir(
                PROJECT_FOLDER
            )
        )
    )

    results.append(
        (
            "Config file",
            os.path.isfile(
                CONFIG_FILE
            )
        )
    )

    results.append(
        (
            "Key file",
            os.path.isfile(
                KEY_FILE
            )
        )
    )

    return results


def run_self_test():
    print()
    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )

    print(
        "\033[97mSELF TEST\033[0m"
    )

    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )

    results = self_test()

    passed = 0

    for name, status in results:
        if status:
            marker = (
                "\033[92mPASS\033[0m"
            )
            passed += 1
        else:
            marker = (
                "\033[91mFAIL\033[0m"
            )

        print(
            f"{marker}  {name}"
        )

    print()

    print(
        f"Result: "
        f"{passed}/{len(results)}"
    )


def print_privacy():
    print()
    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )

    print(
        "\033[97mPRIVACY MODEL\033[0m"
    )

    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )

    lines = [
        "Consenso esplicito richiesto.",
        "Geolocalizzazione tramite IP approssimativa.",
        "GPS del browser disabilitato.",
        "Fingerprinting disabilitato.",
        "User-Agent del visitatore non analizzato.",
        "IP del visitatore non scritto su disco.",
        "Nessuno storico visite persistente.",
        "Risultato corrente conservato solo temporaneamente.",
        "Server locale per impostazione predefinita."
    ]

    for line in lines:
        print(
            f"\033[97m•\033[0m {line}"
        )


def print_section(title):
    print()
    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )

    print(
        f"\033[97m{title}\033[0m"
    )

    print(
        "\033[96m"
        + "═" * 78
        + "\033[0m"
    )


def print_summary():
    print_section(
        "SYSTEM READY"
    )

    values = [
        (
            "Project",
            PROJECT_FOLDER
        ),
        (
            "Key",
            KEY_FILE
        ),
        (
            "Config",
            CONFIG_FILE
        ),
        (
            "Log",
            LOG_FILE
        ),
        (
            "Dashboard",
            get_server_url()
        ),
        (
            "LAN",
            get_lan_url()
        ),
        (
            "Host",
            HOST
        ),
        (
            "Port",
            PORT
        ),
        (
            "Version",
            APP_VERSION
        )
    ]

    for label, value in values:
        print(
            f"\033[97m{label:<12}\033[0m "
            f"{value}"
        )


def show_key():
    print_section(
        "INSTANCE KEY"
    )

    print(
        "\033[96m"
        + SECRET_KEY
        + "\033[0m"
    )

    print()
    print(
        "La chiave resta invariata "
        "tra gli avvii."
    )


def show_config():
    print_section(
        "CONFIGURATION"
    )

    print(
        json.dumps(
            build_config(),
            ensure_ascii=False,
            indent=4
        )
    )


def show_diagnostics():
    print_section(
        "DIAGNOSTICS"
    )

    diagnostics = [
        (
            "Python",
            platform.python_version()
        ),
        (
            "Platform",
            platform.platform()
        ),
        (
            "Machine",
            platform.machine()
        ),
        (
            "Processor",
            platform.processor()
            or "Unknown"
        ),
        (
            "Hostname",
            get_hostname()
        ),
        (
            "Local IP",
            get_local_ip()
        ),
        (
            "Project",
            PROJECT_FOLDER
        ),
        (
            "Port available",
            port_available(
                HOST,
                PORT
            )
        ),
        (
            "Server URL",
            get_server_url()
        )
    ]

    for label, value in diagnostics:
        print(
            f"\033[97m"
            f"{label:<18}"
            f"\033[0m {value}"
        )


def show_runtime():
    print_section(
        "RUNTIME"
    )

    stats = get_runtime()

    values = [
        (
            "Requests",
            stats["requests"]
        ),
        (
            "Consent",
            stats["consented"]
        ),
        (
            "Success",
            stats["successful"]
        ),
        (
            "Failed",
            stats["failed"]
        ),
        (
            "Uptime",
            stats["uptime"]
        ),
        (
            "Running",
            stats["running"]
        )
    ]

    for label, value in values:
        print(
            f"\033[97m"
            f"{label:<18}"
            f"\033[0m {value}"
        )


def server_running():
    with SERVER_LOCK:
        return (
            SERVER is not None
            and RUNTIME["started"]
            and not RUNTIME["stopped"]
        )


def serve():
    try:
        SERVER.serve_forever(
            poll_interval=0.25
        )
    except Exception as error:
        log_message(
            f"Server loop error: {error}"
        )


def start_server():
    global SERVER
    global SERVER_THREAD

    with SERVER_LOCK:
        if server_running():
            print(
                "\033[93mServer già attivo.\033[0m"
            )
            return False

        if not port_available(
            HOST,
            PORT
        ):
            print(
                f"\033[91mPorta {PORT} non disponibile.\033[0m"
            )
            return False

        try:
            SERVER = ThreadingHTTPServer(
                (
                    HOST,
                    PORT
                ),
                Handler
            )

            SERVER.daemon_threads = True

            RUNTIME["started"] = True
            RUNTIME["stopped"] = False

            SERVER_THREAD = threading.Thread(
                target=serve,
                name="PUGILAIN-HTTP",
                daemon=True
            )

            SERVER_THREAD.start()

        except OSError as error:
            SERVER = None

            print(
                f"\033[91mErrore server: "
                f"{error}\033[0m"
            )

            return False

    log_message(
        f"Server started on "
        f"{get_server_url()}"
    )

    return True


def stop_server():
    global SERVER

    with SERVER_LOCK:
        current = SERVER
        SERVER = None

        RUNTIME["stopped"] = True

    if current is None:
        return

    try:
        current.shutdown()
    except Exception:
        pass

    try:
        current.server_close()
    except Exception:
        pass

    log_message(
        "Server stopped"
    )


def restart_server():
    stop_server()

    time.sleep(
        0.4
    )

    return start_server()


def open_dashboard():
    if not server_running():
        print(
            "\033[93m"
            "Server non attivo."
            "\033[0m"
        )
        return

    try:
        webbrowser.open(
            get_server_url(),
            new=2
        )
    except Exception:
        print(
            get_server_url()
        )


def menu():
    print_section(
        "MAIN MENU"
    )

    print(
        "\033[97m[1]\033[0m "
        "Avvia server"
    )

    print(
        "\033[97m[2]\033[0m "
        "Ferma server"
    )

    print(
        "\033[97m[3]\033[0m "
        "Riavvia server"
    )

    print(
        "\033[97m[4]\033[0m "
        "Apri dashboard"
    )

    print(
        "\033[97m[5]\033[0m "
        "Mostra chiave"
    )

    print(
        "\033[97m[6]\033[0m "
        "Reset chiave"
    )

    print(
        "\033[97m[7]\033[0m "
        "Configurazione"
    )

    print(
        "\033[97m[8]\033[0m "
        "Diagnostica"
    )

    print(
        "\033[97m[9]\033[0m "
        "Runtime"
    )

    print(
        "\033[97m[10]\033[0m "
        "Cancella risultato"
    )

    print(
        "\033[97m[11]\033[0m "
        "Self test"
    )

    print(
        "\033[97m[0]\033[0m "
        "Esci"
    )

    return input(
        "\n\033[96mPUGILAIN > \033[0m"
    ).strip()


def menu_loop():
    while True:
        choice = menu()

        if choice == "1":
            if start_server():
                print(
                    "\033[92m"
                    "[✓] Server avviato"
                    "\033[0m"
                )
                open_dashboard()

        elif choice == "2":
            stop_server()

            print(
                "\033[92m"
                "[✓] Server fermato"
                "\033[0m"
            )

        elif choice == "3":
            if restart_server():
                print(
                    "\033[92m"
                    "[✓] Server riavviato"
                    "\033[0m"
                )

        elif choice == "4":
            open_dashboard()

        elif choice == "5":
            show_key()

        elif choice == "6":
            reset_key()

        elif choice == "7":
            show_config()

        elif choice == "8":
            show_diagnostics()

        elif choice == "9":
            show_runtime()

        elif choice == "10":
            clear_result()

            print(
                "\033[92m"
                "[✓] Risultato cancellato"
                "\033[0m"
            )

        elif choice == "11":
            run_self_test()

        elif choice == "0":
            break

        else:
            print(
                "\033[91m"
                "Scelta non valida."
                "\033[0m"
            )


def shutdown():
    stop_server()

    log_message(
        "Application shutdown"
    )


def initialize():
    initialize_files()

    log_message(
        f"{APP_NAME} {APP_VERSION}"
    )

    log_message(
        f"Device ID: {DEVICE_ID}"
    )


def startup():
    clear()

    print(
        "\033[92m"
        + BANNER
        + "\033[0m"
    )

    time.sleep(
        0.5
    )

    loading_animation(
        0.7,
        "Initializing core modules..."
    )

    print(
        "\033[92m"
        "[✓] Core modules initialized"
        "\033[0m"
    )

    loading_animation(
        0.7,
        "Loading persistent instance..."
    )

    print(
        "\033[92m"
        "[✓] Instance loaded"
        "\033[0m"
    )

    loading_animation(
        0.7,
        "Preparing environment..."
    )

    initialize()

    print(
        "\033[92m"
        "[✓] Environment ready"
        "\033[0m"
    )

    loading_animation(
        0.7,
        "Running diagnostics..."
    )

    run_self_test()

    print(
        f"\033[97m"
        f"Device ID: "
        f"{DEVICE_ID}"
        f"\033[0m"
    )

    print(
        f"\033[97m"
        f"Key preview: "
        f"{SECRET_KEY[:16]}..."
        f"\033[0m"
    )

    print_privacy()

    print_summary()

    if start_server():
        print(
            "\033[92m"
            "[✓] Local server started"
            "\033[0m"
        )

        open_dashboard()

    else:
        print(
            "\033[91m"
            "[!] Server not started"
            "\033[0m"
        )


DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="robots" content="noindex,nofollow">
<title>{{APP_NAME}} · {{VERSION}}</title>
<style>

* {
    box-sizing: border-box;
}

html {
    min-height: 100%;
}

body {
    margin: 0;
    min-height: 100vh;
    background: rgb(6, 8, 11);
    color: rgb(238, 242, 247);
    font-family: Inter, Segoe UI, Arial, sans-serif;
}

.page {
    width: min(980px, calc(100% - 30px));
    margin: 0 auto;
    padding: 28px 0 70px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 17px 20px;
    border: 1px solid rgb(37, 44, 53);
    border-radius: 18px;
    background: rgb(12, 15, 20);
}

.brand {
    display: flex;
    align-items: center;
    gap: 13px;
}

.logo {
    width: 44px;
    height: 44px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    background: rgb(235, 239, 244);
    color: rgb(5, 7, 9);
    font-weight: 900;
    font-size: 20px;
}

.brand-title {
    font-size: 16px;
    font-weight: 900;
    letter-spacing: .12em;
}

.brand-subtitle {
    margin-top: 4px;
    color: rgb(122, 134, 149);
    font-size: 11px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid rgb(36, 83, 56);
    background: rgb(10, 28, 18);
    color: rgb(131, 235, 167);
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 10px;
    font-weight: 900;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: rgb(82, 220, 125);
}

.hero {
    padding: 70px 0 35px;
}

.eyebrow {
    color: rgb(105, 224, 150);
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .2em;
}

h1 {
    margin: 13px 0 17px;
    max-width: 820px;
    font-size: clamp(38px, 8vw, 72px);
    line-height: .97;
    letter-spacing: -.06em;
}

.hero-text {
    max-width: 720px;
    color: rgb(153, 165, 179);
    font-size: 16px;
    line-height: 1.75;
}

.panel {
    padding: 28px;
    border: 1px solid rgb(37, 44, 53);
    border-radius: 22px;
    background: rgb(12, 15, 20);
    box-shadow: 0 30px 90px rgba(0,0,0,.28);
}

.panel-title {
    font-size: 21px;
    font-weight: 900;
}

.panel-subtitle {
    margin: 8px 0 23px;
    color: rgb(135, 147, 161);
    line-height: 1.65;
}

.consent {
    display: flex;
    align-items: flex-start;
    gap: 13px;
    padding: 17px;
    border: 1px solid rgb(43, 51, 61);
    border-radius: 15px;
    background: rgb(16, 20, 26);
}

.consent input {
    width: 20px;
    height: 20px;
    margin-top: 2px;
    accent-color: rgb(228, 233, 239);
}

.consent-text {
    color: rgb(190, 199, 210);
    font-size: 13px;
    line-height: 1.65;
}

.consent-text strong {
    color: rgb(241, 244, 248);
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 17px;
}

button {
    border: 0;
    border-radius: 12px;
    padding: 13px 18px;
    font-size: 13px;
    font-weight: 900;
    cursor: pointer;
    transition: transform .16s ease, opacity .16s ease;
}

button:hover {
    transform: translateY(-1px);
}

button:disabled {
    opacity: .4;
    cursor: not-allowed;
    transform: none;
}

.primary {
    background: rgb(235, 239, 244);
    color: rgb(6, 8, 11);
}

.secondary {
    background: rgb(29, 35, 43);
    color: rgb(222, 228, 235);
}

.result-wrap {
    margin-top: 20px;
}

.result {
    padding: 21px;
    border: 1px solid rgb(42, 52, 63);
    border-radius: 17px;
    background: rgb(9, 13, 18);
}

.result.error {
    border-color: rgb(92, 43, 49);
}

.result-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    margin-bottom: 20px;
}

.result h2 {
    margin: 6px 0 0;
    font-size: 24px;
}

.pill {
    padding: 7px 10px;
    border-radius: 999px;
    border: 1px solid rgb(42, 86, 59);
    color: rgb(131, 235, 167);
    background: rgb(11, 29, 19);
    font-size: 9px;
    font-weight: 900;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
}

.data-row {
    padding: 13px;
    border: 1px solid rgb(31, 39, 48);
    border-radius: 12px;
    background: rgb(15, 19, 25);
}

.data-row span {
    display: block;
    margin-bottom: 6px;
    color: rgb(118, 130, 145);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.data-row strong {
    display: block;
    color: rgb(232, 237, 242);
    font-size: 14px;
    word-break: break-word;
}

.map-button {
    display: inline-block;
    margin-top: 17px;
    padding: 12px 16px;
    border-radius: 11px;
    background: rgb(222, 227, 234);
    color: rgb(6, 8, 11);
    text-decoration: none;
    font-size: 12px;
    font-weight: 900;
}

.notice {
    margin-top: 16px;
    padding: 13px;
    border-radius: 11px;
    background: rgb(17, 22, 29);
    color: rgb(127, 140, 154);
    font-size: 11px;
    line-height: 1.65;
}

.empty {
    padding: 35px;
    border: 1px dashed rgb(43, 51, 61);
    border-radius: 17px;
    color: rgb(124, 137, 151);
    text-align: center;
}

.empty-icon {
    margin-bottom: 9px;
    font-size: 29px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 11px;
    margin-top: 20px;
}

.card {
    padding: 18px;
    border: 1px solid rgb(36, 43, 52);
    border-radius: 16px;
    background: rgb(12, 15, 20);
}

.card strong {
    display: block;
    margin-bottom: 6px;
    font-size: 16px;
}

.card span {
    color: rgb(126, 139, 153);
    font-size: 11px;
    line-height: 1.55;
}

.footer {
    padding-top: 25px;
    color: rgb(84, 97, 112);
    font-size: 10px;
    line-height: 1.7;
    text-align: center;
}

.loading {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.spinner {
    width: 13px;
    height: 13px;
    border: 2px solid rgb(58, 67, 78);
    border-top-color: rgb(236, 240, 244);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 720px) {

    .page {
        width: min(100% - 18px, 980px);
        padding-top: 12px;
    }

    .topbar {
        align-items: flex-start;
    }

    .hero {
        padding: 48px 0 28px;
    }

    .panel {
        padding: 20px;
    }

    .grid {
        grid-template-columns: 1fr;
    }

    .cards {
        grid-template-columns: 1fr;
    }
}

</style>
</head>
<body>

<div class="page">

<header class="topbar">

<div class="brand">

<div class="logo">
P
</div>

<div>

<div class="brand-title">
{{APP_NAME}}
</div>

<div class="brand-subtitle">
Approximate IP Geolocation
</div>

</div>

</div>

<div class="status">

<span class="status-dot"></span>

ONLINE

</div>

</header>

<section class="hero">

<div class="eyebrow">
CONSENSO ESPLICITO
</div>

<h1>
Geolocalizzazione approssimativa tramite IP.
</h1>

<p class="hero-text">
Questa pagina esegue un lookup geografico approssimativo
solo dopo un consenso esplicito. Non utilizza il GPS del browser,
non effettua fingerprinting e non crea uno storico degli IP.
</p>

</section>

<section class="panel">

<div class="panel-title">
Prima di continuare
</div>

<div class="panel-subtitle">
Il lookup viene eseguito solamente dopo aver selezionato
la casella di consenso. La posizione ottenuta dall'IP è
approssimativa e non deve essere interpretata come posizione GPS.
</div>

<label class="consent">

<input
id="consent"
type="checkbox"
>

<span class="consent-text">

<strong>
Acconsento al lookup dell'IP per ottenere una posizione geografica approssimativa.
</strong>

<br>

Comprendo che il servizio di geolocalizzazione può fornire
un risultato impreciso e che l'indirizzo IP necessario al
lookup viene trasmesso al provider geografico.

</span>

</label>

<div class="actions">

<button
id="lookup"
class="primary"
disabled
>
Ottieni posizione approssimativa
</button>

<button
id="clear"
class="secondary"
>
Pulisci risultato
</button>

</div>

<div
id="result"
class="result-wrap"
>

<div class="empty">

<div class="empty-icon">
◎
</div>

<div>
Seleziona il consenso per abilitare il lookup.
</div>

</div>

</div>

</section>

<div class="cards">

<div class="card">

<strong>
GPS disattivato
</strong>

<span>
La pagina non richiede permessi di posizione al browser.
</span>

</div>

<div class="card">

<strong>
Fingerprinting disattivato
</strong>

<span>
Nessuna analisi delle caratteristiche hardware o browser del visitatore.
</span>

</div>

<div class="card">

<strong>
Storico disattivato
</strong>

<span>
Gli IP non vengono scritti su file e non viene creato uno storico visite.
</span>

</div>

</div>

<footer class="footer">

{{APP_NAME}}
·
{{VERSION}}
·
consenso obbligatorio
·
server locale

</footer>

</div>

<script>

const consent =
document.getElementById("consent");

const lookup =
document.getElementById("lookup");

const clearButton =
document.getElementById("clear");

const result =
document.getElementById("result");


function escapeValue(value) {

    const node =
        document.createElement("div");

    node.textContent =
        value === null ||
        value === undefined
            ? "N/A"
            : String(value);

    return node.innerHTML;
}


function empty(message) {

    result.innerHTML =
        '<div class="empty">' +
        '<div class="empty-icon">◎</div>' +
        '<div>' +
        escapeValue(message) +
        '</div>' +
        '</div>';

}


function loading(value) {

    if (value) {

        lookup.disabled = true;

        lookup.innerHTML =
            '<span class="loading">' +
            '<span class="spinner"></span>' +
            'Lookup in corso' +
            '</span>';

    } else {

        lookup.disabled =
            !consent.checked;

        lookup.textContent =
            "Ottieni posizione approssimativa";

    }

}


function render(payload) {

    if (
        !payload ||
        payload.success !== true
    ) {

        const message =
            payload &&
            payload.error
                ? payload.error
                : "Lookup non riuscito.";

        result.innerHTML =
            '<div class="result error">' +
            '<div class="eyebrow">ERRORE</div>' +
            '<h2>' +
            escapeValue(message) +
            '</h2>' +
            '</div>';

        return;
    }


    const data =
        payload.data || {};


    const rows = [

        ["IP", data.ip],

        ["Paese", data.country],

        ["Codice", data.country_code],

        ["Regione", data.region],

        ["Città", data.city],

        ["CAP", data.postal_code],

        ["Fuso orario", data.timezone],

        ["Latitudine", data.latitude],

        ["Longitudine", data.longitude],

        ["Precisione", "Approssimativa"]

    ];


    let cells = "";


    for (
        const row of rows
    ) {

        cells +=
            '<div class="data-row">' +
            '<span>' +
            escapeValue(row[0]) +
            '</span>' +
            '<strong>' +
            escapeValue(row[1]) +
            '</strong>' +
            '</div>';

    }


    let map = "";


    if (
        data.latitude !== null &&
        data.latitude !== undefined &&
        data.longitude !== null &&
        data.longitude !== undefined
    ) {

        const link =
            "https://www.openstreetmap.org/" +
            "?mlat=" +
            encodeURIComponent(data.latitude) +
            "&mlon=" +
            encodeURIComponent(data.longitude) +
            "&zoom=10";


        map =
            '<a class="map-button" href="' +
            link +
            '" target="_blank" rel="noreferrer">' +
            'Apri mappa' +
            '</a>';

    }


    result.innerHTML =
        '<div class="result">' +

        '<div class="result-head">' +

        '<div>' +

        '<div class="eyebrow">' +
        'RISULTATO' +
        '</div>' +

        '<h2>' +
        'Geolocalizzazione IP' +
        '</h2>' +

        '</div>' +

        '<div class="pill">' +
        'CONSENSO' +
        '</div>' +

        '</div>' +

        '<div class="grid">' +
        cells +
        '</div>' +

        map +

        '<div class="notice">' +
        'Il risultato è temporaneo e non viene salvato nello storico.' +
        '</div>' +

        '</div>';

}


consent.addEventListener(
    "change",
    function() {

        lookup.disabled =
            !consent.checked;

        if (!consent.checked) {

            empty(
                "Seleziona il consenso per abilitare il lookup."
            );

        }

    }
);


clearButton.addEventListener(
    "click",
    function() {

        empty(
            "Risultato cancellato dalla pagina."
        );

    }
);


lookup.addEventListener(
    "click",
    async function() {

        if (!consent.checked) {
            return;
        }

        loading(true);

        try {

            const response =
                await fetch(
                    "/api/location",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json"
                        },
                        body:
                            JSON.stringify(
                                {
                                    consent: true,
                                    purpose:
                                        "approximate_ip_geolocation",
                                    consent_version:
                                        "1.0"
                                }
                            )
                    }
                );


            const payload =
                await response.json();


            render(payload);

        } catch (error) {

            result.innerHTML =
                '<div class="result error">' +
                '<div class="eyebrow">' +
                'ERRORE' +
                '</div>' +
                '<h2>' +
                'Impossibile contattare il server.' +
                '</h2>' +
                '</div>';

        } finally {

            loading(false);

        }

    }
);

</script>

</body>
</html>
"""


def main():
    try:
        startup()
        menu_loop()
    except KeyboardInterrupt:
        print()
        print(
            "\033[93m"
            "Interruzione ricevuta."
            "\033[0m"
        )
    finally:
        shutdown()
        print(
            "\033[92m"
            "[✓] PUGILAIN chiuso correttamente."
            "\033[0m"
        )


if __name__ == "__main__":
    main()
