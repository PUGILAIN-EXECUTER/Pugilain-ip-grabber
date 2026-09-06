import os
import sys
import json
import time
import uuid
import socket
import secrets
import hashlib
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

APP_NAME = "PUGILAIN LOCAL GEO"
VERSION = "4.0"
HOST = "127.0.0.1"
PORT = 5000

BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "PugilainLocalGeo")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
INSTANCE_FILE = os.path.join(BASE_DIR, "instance.json")
KEY_FILE = os.path.join(BASE_DIR, "key.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

LOCK = threading.RLock()

STATE = {
    "started": time.time(),
    "requests": 0,
    "accepted": 0,
    "rejected": 0,
    "errors": 0,
    "last_activity": None
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def slow_print(text, delay=0.008):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def loading(text, duration=1.0):
    sequence = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    end = time.time() + duration
    index = 0

    while time.time() < end:
        print("\r" + text + " " + sequence[index % len(sequence)], end="", flush=True)
        index += 1
        time.sleep(0.07)

    print("\r" + text + " ✓")


def banner():
    print()
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                              ║")
    print("║   ██████╗ ██╗   ██╗  ██████╗  ██╗ ██╗       █████╗  ██╗ ███╗   ██╗        ║")
    print("║   ██╔══██╗██║   ██║ ██╔════╝  ██║ ██║      ██╔══██╗ ██║ ████╗  ██║        ║")
    print("║   ██████╔╝██║   ██║ ██║  ███╗ ██║ ██║      ███████║ ██║ ██╔██╗ ██║        ║")
    print("║   ██╔═══╝ ██║   ██║ ██║   ██║ ██║ ██║      ██╔══██║ ██║ ██║╚██╗██║        ║")
    print("║   ██║     ╚██████╔╝ ╚██████╔╝ ██║ ███████╗ ██║  ██║ ██║ ██║ ╚████║        ║")
    print("║   ╚═╝      ╚═════╝   ╚═════╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝ ╚═╝  ╚═══╝        ║")
    print("║                                                                              ║")
    print("║                       ◈  LOCAL GEO CONSOLE  ◈                             ║")
    print("║                                                                              ║")
    print("║                    CONSENSO • HISTORY • DASHBOARD                          ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()


def ensure_directory():
    os.makedirs(BASE_DIR, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def generate_instance_id():
    seed = "|".join([
        socket.gethostname(),
        sys.platform,
        str(uuid.getnode()),
        os.path.abspath(BASE_DIR)
    ])

    return hashlib.sha256(seed.encode()).hexdigest()[:32]


def generate_key():
    return secrets.token_urlsafe(32)


def initialize_instance():
    ensure_directory()

    if os.path.exists(INSTANCE_FILE):
        try:
            with open(INSTANCE_FILE, "r", encoding="utf-8") as file:
                instance = json.load(file)

            if instance.get("instance_id"):
                return instance

        except Exception:
            pass

    instance = {
        "instance_id": generate_instance_id(),
        "created_at": now_iso()
    }

    with open(INSTANCE_FILE, "w", encoding="utf-8") as file:
        json.dump(instance, file, indent=2, ensure_ascii=False)

    return instance


def initialize_key():
    ensure_directory()

    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as file:
                key = file.read().strip()

            if key:
                return key

        except Exception:
            pass

    key = generate_key()

    with open(KEY_FILE, "w", encoding="utf-8") as file:
        file.write(key)

    return key


def initialize_config():
    ensure_directory()

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = json.load(file)

            if isinstance(config, dict):
                return config

        except Exception:
            pass

    config = {
        "app_name": APP_NAME,
        "version": VERSION,
        "host": HOST,
        "port": PORT,
        "history_enabled": True,
        "consent_required": True,
        "local_only": True
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)

    return config


def initialize_history():
    ensure_directory()

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False)

        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception:
        pass

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump([], file)

    return []


def load_history():
    with LOCK:
        return initialize_history()


def save_history(history):
    with LOCK:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=2, ensure_ascii=False)


def append_history(entry):
    history = load_history()
    history.append(entry)
    save_history(history)


def delete_history():
    save_history([])


def reset_instance():
    ensure_directory()

    instance = {
        "instance_id": generate_instance_id(),
        "created_at": now_iso(),
        "reset_at": now_iso()
    }

    with open(INSTANCE_FILE, "w", encoding="utf-8") as file:
        json.dump(instance, file, indent=2, ensure_ascii=False)

    key = generate_key()

    with open(KEY_FILE, "w", encoding="utf-8") as file:
        file.write(key)

    return instance, key


def escape_html(value):
    if value is None:
        return ""

    value = str(value)

    replacements = [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&#39;")
    ]

    for source, target in replacements:
        value = value.replace(source, target)

    return value


def format_time(value):
    if not value:
        return "—"

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return value


def format_number(value):
    if value is None:
        return "—"

    try:
        return f"{float(value):.6f}"
    except Exception:
        return str(value)


def is_valid_coordinate(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except Exception:
        return False

    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def get_ip_from_request(handler):
    address = handler.client_address

    if not address:
        return ""

    return address[0]


def get_ip_information(ip):
    if not ip:
        return {
            "success": False,
            "error": "IP non disponibile."
        }

    try:
        request = Request(
            "https://ipwho.is/" + ip,
            headers={
                "User-Agent": "PugilainLocalGeo/4.0"
            }
        )

        with urlopen(request, timeout=8) as response:
            raw = response.read().decode("utf-8", errors="replace")

        data = json.loads(raw)

        if not data.get("success"):
            return {
                "success": False,
                "error": data.get("message", "Informazioni IP non disponibili.")
            }

        timezone_data = data.get("timezone") or {}

        return {
            "success": True,
            "country": data.get("country", ""),
            "country_code": data.get("country_code", ""),
            "region": data.get("region", ""),
            "city": data.get("city", ""),
            "postal": data.get("postal", ""),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": timezone_data.get("id", "")
        }

    except HTTPError:
        return {
            "success": False,
            "error": "Servizio IP non disponibile."
        }

    except URLError:
        return {
            "success": False,
            "error": "Connessione al servizio IP non riuscita."
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def update_state(field):
    with LOCK:
        STATE[field] += 1
        STATE["last_activity"] = now_iso()


def statistics():
    with LOCK:
        history = load_history()

        return {
            "requests": STATE["requests"],
            "accepted": STATE["accepted"],
            "rejected": STATE["rejected"],
            "errors": STATE["errors"],
            "history": len(history),
            "uptime": int(time.time() - STATE["started"]),
            "last_activity": STATE["last_activity"]
        }


def make_entry(ip, latitude, longitude, accuracy, ip_info):
    return {
        "id": uuid.uuid4().hex,
        "timestamp": now_iso(),
        "ip": ip,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "accuracy": float(accuracy) if accuracy is not None else None,
        "country": ip_info.get("country", ""),
        "country_code": ip_info.get("country_code", ""),
        "region": ip_info.get("region", ""),
        "city": ip_info.get("city", ""),
        "postal": ip_info.get("postal", ""),
        "timezone": ip_info.get("timezone", "")
    }


def json_send(handler, payload, status=200):
    raw = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5000")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(raw)


def html_send(handler, content, status=200):
    raw = content.encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)


def read_json(handler):
    try:
        length = int(handler.headers.get("Content-Length", "0"))

        if length <= 0:
            return {}

        if length > 1024 * 64:
            return {}

        body = handler.rfile.read(length).decode("utf-8", errors="replace")

        return json.loads(body)

    except Exception:
        return {}


def map_link(latitude, longitude):
    if not is_valid_coordinate(latitude, longitude):
        return ""

    return (
        "https://www.openstreetmap.org/"
        "?mlat=" + str(latitude) +
        "&mlon=" + str(longitude)
    )


def render_history_rows(history):
    if not history:
        return """
        <div class="empty">
            <div class="empty-symbol">◎</div>
            <div class="empty-title">Nessun dato nello storico</div>
            <div class="empty-text">Le richieste autorizzate appariranno qui.</div>
        </div>
        """

    rows = []

    for item in reversed(history):
        map_url = map_link(
            item.get("latitude"),
            item.get("longitude")
        )

        map_button = ""

        if map_url:
            map_button = (
                '<a class="small-button" href="' +
                escape_html(map_url) +
                '" target="_blank" rel="noreferrer">MAPPA</a>'
            )

        rows.append(
            f"""
            <div class="history-item">
                <div class="history-main">
                    <div class="history-date">
                        {escape_html(format_time(item.get("timestamp")))}
                    </div>

                    <div class="history-ip">
                        {escape_html(item.get("ip", "—"))}
                    </div>

                    <div class="history-location">
                        {escape_html(item.get("city") or "Posizione GPS")}
                        <span>•</span>
                        {escape_html(item.get("country") or "—")}
                    </div>
                </div>

                <div class="history-coordinates">
                    <div>
                        <span>LAT</span>
                        <strong>{escape_html(format_number(item.get("latitude")))}</strong>
                    </div>

                    <div>
                        <span>LON</span>
                        <strong>{escape_html(format_number(item.get("longitude")))}</strong>
                    </div>

                    <div>
                        <span>ACC</span>
                        <strong>{escape_html(item.get("accuracy") or "—")} m</strong>
                    </div>

                    {map_button}
                </div>
            </div>
            """
        )

    return "".join(rows)


def render_dashboard():
    return """
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PUGILAIN LOCAL GEO</title>
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
    color: #f7f8ff;
    background:
        radial-gradient(circle at 15% 10%, rgba(104,91,255,.16), transparent 30%),
        radial-gradient(circle at 85% 20%, rgba(40,205,255,.11), transparent 28%),
        #070a10;
    font-family: Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}

body:before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: .5;
    background-image:
        linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
    background-size: 36px 36px;
}

.container {
    width: min(1200px,calc(100% - 32px));
    margin: auto;
}

nav {
    height: 84px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,.07);
}

.logo {
    display: flex;
    align-items: center;
    gap: 13px;
    font-weight: 900;
    letter-spacing: 3px;
}

.logo-mark {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg,#765cff,#26d5ef);
    box-shadow: 0 0 35px rgba(93,92,255,.3);
}

.nav-info {
    display: flex;
    gap: 9px;
}

.badge {
    padding: 9px 13px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(255,255,255,.035);
    color: #929cb5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.online {
    color: #a9f8c3;
    border-color: rgba(95,235,140,.2);
}

main {
    padding: 68px 0 90px;
}

.hero {
    max-width: 850px;
    margin-bottom: 38px;
}

.kicker {
    color: #8f8cff;
    font-size: 11px;
    letter-spacing: 4px;
    font-weight: 900;
    margin-bottom: 17px;
}

h1 {
    margin: 0;
    font-size: clamp(44px,7vw,82px);
    line-height: .94;
    letter-spacing: -4px;
}

.gradient {
    background: linear-gradient(90deg,#fff,#a6a4ff,#65e5ff);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
}

.subtitle {
    color: #858fa8;
    line-height: 1.7;
    font-size: 17px;
    max-width: 700px;
    margin-top: 24px;
}

.panel {
    padding: 27px;
    border-radius: 27px;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(14,18,28,.78);
    box-shadow: 0 30px 100px rgba(0,0,0,.35);
    backdrop-filter: blur(20px);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: center;
    margin-bottom: 22px;
}

.panel-title {
    font-weight: 900;
    font-size: 18px;
}

.panel-description {
    color: #68738b;
    font-size: 12px;
    margin-top: 5px;
}

.consent-box {
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,.07);
    background: rgba(0,0,0,.18);
    line-height: 1.7;
    color: #8791a8;
    font-size: 13px;
}

.consent-title {
    color: #f2f4ff;
    font-weight: 800;
    margin-bottom: 7px;
}

.consent-actions {
    display: flex;
    gap: 11px;
    margin-top: 20px;
}

button {
    border: 0;
    cursor: pointer;
    color: white;
    padding: 14px 20px;
    border-radius: 14px;
    font-weight: 900;
    letter-spacing: 1px;
    background: linear-gradient(135deg,#765cff,#28cbea);
    box-shadow: 0 14px 35px rgba(72,80,255,.2);
}

button.secondary {
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: none;
}

button.danger {
    background: rgba(255,70,100,.1);
    border: 1px solid rgba(255,70,100,.2);
    box-shadow: none;
}

.status-box {
    margin-top: 18px;
    display: none;
    padding: 15px;
    border-radius: 15px;
    background: rgba(255,255,255,.035);
    color: #9ca6bc;
    font-size: 12px;
}

.status-box.visible {
    display: block;
}

.stats {
    margin-top: 18px;
    display: grid;
    grid-template-columns: repeat(5,1fr);
    gap: 11px;
}

.stat {
    border-radius: 19px;
    border: 1px solid rgba(255,255,255,.07);
    background: rgba(255,255,255,.025);
    padding: 18px;
}

.stat-label {
    color: #69748d;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 2px;
}

.stat-value {
    margin-top: 9px;
    font-size: 25px;
    font-weight: 900;
}

.history-panel {
    margin-top: 18px;
}

.history-tools {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.search {
    min-width: 230px;
    flex: 1;
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(0,0,0,.2);
    color: white;
    padding: 13px 15px;
    border-radius: 13px;
    outline: none;
}

.history-list {
    margin-top: 20px;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 18px 0;
    border-bottom: 1px solid rgba(255,255,255,.055);
}

.history-item:last-child {
    border-bottom: 0;
}

.history-date {
    color: #68738d;
    font-size: 10px;
    letter-spacing: 1px;
}

.history-ip {
    margin-top: 7px;
    font-size: 17px;
    font-weight: 900;
}

.history-location {
    margin-top: 6px;
    color: #7e89a2;
    font-size: 12px;
}

.history-location span {
    padding: 0 6px;
    color: #515c74;
}

.history-coordinates {
    display: flex;
    gap: 9px;
    align-items: center;
}

.history-coordinates > div {
    min-width: 88px;
    padding: 9px 11px;
    border-radius: 11px;
    background: rgba(255,255,255,.025);
}

.history-coordinates span {
    display: block;
    color: #59647b;
    font-size: 8px;
    letter-spacing: 1px;
    font-weight: 900;
}

.history-coordinates strong {
    display: block;
    margin-top: 4px;
    font-size: 10px;
}

.small-button {
    display: inline-flex;
    align-items: center;
    text-decoration: none;
    color: white;
    padding: 10px 12px;
    border-radius: 11px;
    background: rgba(115,92,255,.14);
    border: 1px solid rgba(115,92,255,.2);
    font-size: 9px;
    font-weight: 900;
}

.empty {
    text-align: center;
    padding: 60px 20px;
    border: 1px dashed rgba(255,255,255,.08);
    border-radius: 20px;
}

.empty-symbol {
    font-size: 35px;
    color: #6873ff;
}

.empty-title {
    margin-top: 13px;
    font-weight: 900;
}

.empty-text {
    color: #69748d;
    margin-top: 6px;
    font-size: 12px;
}

footer {
    border-top: 1px solid rgba(255,255,255,.06);
    padding: 28px 0;
    text-align: center;
    color: #555f76;
    font-size: 10px;
}

@media(max-width:850px) {
    .stats {
        grid-template-columns: repeat(2,1fr);
    }

    .history-item {
        align-items: flex-start;
        flex-direction: column;
    }

    .history-coordinates {
        width: 100%;
        flex-wrap: wrap;
    }
}

@media(max-width:600px) {
    .container {
        width: min(100% - 20px,1200px);
    }

    nav {
        height: 70px;
    }

    .nav-info .badge:first-child {
        display: none;
    }

    main {
        padding-top: 42px;
    }

    h1 {
        letter-spacing: -2px;
    }

    .panel {
        padding: 19px;
    }

    .panel-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .consent-actions {
        flex-direction: column;
    }

    button {
        width: 100%;
    }
}
</style>
</head>

<body>

<div class="container">

<nav>
    <div class="logo">
        <div class="logo-mark">◈</div>
        <span>PUGILAIN</span>
    </div>

    <div class="nav-info">
        <div class="badge">LOCAL GEO</div>
        <div class="badge online">● ONLINE</div>
    </div>
</nav>

<main>

<section class="hero">
    <div class="kicker">LOCAL PRIVACY CONSOLE</div>
    <h1>
        <span class="gradient">Geolocation</span><br>
        con consenso.
    </h1>
    <div class="subtitle">
        Console locale per richieste di geolocalizzazione autorizzate,
        con dashboard, statistiche e storico persistente sul computer.
    </div>
</section>

<section class="panel">

<div class="panel-header">
    <div>
        <div class="panel-title">Richiesta posizione</div>
        <div class="panel-description">
            Il browser mostrerà la propria finestra di autorizzazione.
        </div>
    </div>

    <div class="badge">CONSENSO OBBLIGATORIO</div>
</div>

<div class="consent-box">
    <div class="consent-title">Prima di continuare</div>

    La posizione del dispositivo verrà richiesta tramite la normale
    autorizzazione del browser. Se l'utente rifiuta, nessuna posizione
    GPS viene inviata. Se accetta, i dati della richiesta vengono mostrati
    nella console locale e possono essere mantenuti nello storico locale.
</div>

<div class="consent-actions">
    <button onclick="requestLocation()">CONSENTI E CONTINUA</button>
    <button class="secondary" onclick="loadHistory()">AGGIORNA STORICO</button>
</div>

<div id="status" class="status-box"></div>

</section>

<section class="stats">

<div class="stat">
    <div class="stat-label">RICHIESTE</div>
    <div class="stat-value" id="requests">0</div>
</div>

<div class="stat">
    <div class="stat-label">CONSENSI</div>
    <div class="stat-value" id="accepted">0</div>
</div>

<div class="stat">
    <div class="stat-label">RIFIUTI</div>
    <div class="stat-value" id="rejected">0</div>
</div>

<div class="stat">
    <div class="stat-label">STORICO</div>
    <div class="stat-value" id="historyCount">0</div>
</div>

<div class="stat">
    <div class="stat-label">UPTIME</div>
    <div class="stat-value" id="uptime">0s</div>
</div>

</section>

<section class="panel history-panel">

<div class="panel-header">

<div>
    <div class="panel-title">History</div>
    <div class="panel-description">
        Storico salvato esclusivamente nella directory locale dell'applicazione.
    </div>
</div>

<div class="history-tools">
    <input
        id="search"
        class="search"
        type="text"
        placeholder="Cerca IP, città o paese..."
        oninput="filterHistory()"
    >

    <button class="secondary" onclick="exportHistory()">ESPORTA</button>

    <button class="danger" onclick="clearHistory()">SVUOTA</button>
</div>

</div>

<div id="history" class="history-list"></div>

</section>

</main>

<footer>
    PUGILAIN LOCAL GEO · VERSION 4.0 · LOCALHOST ONLY
</footer>

</div>

<script>
let historyData = [];

function showStatus(message) {
    const element = document.getElementById("status");
    element.textContent = message;
    element.classList.add("visible");
}

function requestLocation() {
    if (!navigator.geolocation) {
        showStatus("Questo browser non supporta la geolocalizzazione.");
        return;
    }

    showStatus("Richiesta del consenso in corso...");

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            showStatus("Consenso ricevuto. Invio della posizione al server locale...");

            fetch("/api/collect", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    consent: true,
                    latitude: latitude,
                    longitude: longitude,
                    accuracy: accuracy
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (!data.success) {
                    showStatus(data.error || "Errore durante la richiesta.");
                    return;
                }

                showStatus(
                    "Posizione ricevuta. Record aggiunto allo storico locale."
                );

                loadHistory();
            })
            .catch(function() {
                showStatus("Impossibile comunicare con il server locale.");
            });
        },
        function(error) {
            if (error.code === 1) {
                showStatus("Posizione rifiutata dall'utente.");
            } else if (error.code === 2) {
                showStatus("Posizione non disponibile.");
            } else if (error.code === 3) {
                showStatus("Richiesta di posizione scaduta.");
            } else {
                showStatus("Richiesta di posizione non riuscita.");
            }

            fetch("/api/rejected", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    consent: false
                })
            })
            .then(function() {
                loadHistory();
            })
            .catch(function() {});
        },
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}

function loadHistory() {
    fetch("/api/history")
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            historyData = data.history || [];
            renderHistory(historyData);
            updateStats();
        })
        .catch(function() {
            showStatus("Impossibile caricare lo storico.");
        });
}

function updateStats() {
    fetch("/api/stats")
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            document.getElementById("requests").textContent = data.requests;
            document.getElementById("accepted").textContent = data.accepted;
            document.getElementById("rejected").textContent = data.rejected;
            document.getElementById("historyCount").textContent = data.history;
            document.getElementById("uptime").textContent = formatUptime(data.uptime);
        })
        .catch(function() {});
}

function formatUptime(seconds) {
    seconds = Number(seconds) || 0;

    const days = Math.floor(seconds / 86400);
    seconds %= 86400;

    const hours = Math.floor(seconds / 3600);
    seconds %= 3600;

    const minutes = Math.floor(seconds / 60);
    seconds %= 60;

    let output = "";

    if (days) {
        output += days + "d ";
    }

    if (hours) {
        output += hours + "h ";
    }

    if (minutes) {
        output += minutes + "m ";
    }

    output += seconds + "s";

    return output;
}

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value == null ? "" : String(value);
    return element.innerHTML;
}

function renderHistory(items) {
    const container = document.getElementById("history");

    if (!items.length) {
        container.innerHTML = `
            <div class="empty">
                <div class="empty-symbol">◎</div>
                <div class="empty-title">Nessun dato nello storico</div>
                <div class="empty-text">
                    Le richieste autorizzate appariranno qui.
                </div>
            </div>
        `;

        return;
    }

    container.innerHTML = items.map(function(item) {
        const date = new Date(item.timestamp).toLocaleString();

        const latitude = Number(item.latitude).toFixed(6);
        const longitude = Number(item.longitude).toFixed(6);

        const map =
            "https://www.openstreetmap.org/?mlat=" +
            encodeURIComponent(item.latitude) +
            "&mlon=" +
            encodeURIComponent(item.longitude);

        return `
            <div class="history-item">
                <div class="history-main">
                    <div class="history-date">
                        ${escapeHtml(date)}
                    </div>

                    <div class="history-ip">
                        ${escapeHtml(item.ip)}
                    </div>

                    <div class="history-location">
                        ${escapeHtml(item.city || "Posizione GPS")}
                        <span>•</span>
                        ${escapeHtml(item.country || "—")}
                    </div>
                </div>

                <div class="history-coordinates">
                    <div>
                        <span>LAT</span>
                        <strong>${escapeHtml(latitude)}</strong>
                    </div>

                    <div>
                        <span>LON</span>
                        <strong>${escapeHtml(longitude)}</strong>
                    </div>

                    <div>
                        <span>ACC</span>
                        <strong>${escapeHtml(item.accuracy || "—")} m</strong>
                    </div>

                    <a
                        class="small-button"
                        href="${escapeHtml(map)}"
                        target="_blank"
                        rel="noreferrer"
                    >
                        MAPPA
                    </a>
                </div>
            </div>
        `;
    }).join("");
}

function filterHistory() {
    const query =
        document.getElementById("search").value
        .toLowerCase()
        .trim();

    if (!query) {
        renderHistory(historyData);
        return;
    }

    const filtered = historyData.filter(function(item) {
        const values = [
            item.ip,
            item.city,
            item.country,
            item.country_code,
            item.region,
            item.postal,
            item.latitude,
            item.longitude
        ];

        return values.some(function(value) {
            return String(value || "")
                .toLowerCase()
                .includes(query);
        });
    });

    renderHistory(filtered);
}

function exportHistory() {
    fetch("/api/export")
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            const blob = new Blob(
                [JSON.stringify(data, null, 2)],
                {
                    type: "application/json"
                }
            );

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "pugilain-history.json";
            link.click();

            URL.revokeObjectURL(url);
        })
        .catch(function() {
            showStatus("Esportazione non riuscita.");
        });
}

function clearHistory() {
    const confirmed = confirm(
        "Vuoi eliminare definitivamente lo storico locale?"
    );

    if (!confirmed) {
        return;
    }

    fetch("/api/history", {
        method: "DELETE"
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            historyData = [];
            renderHistory([]);
            loadHistory();
            showStatus("Storico eliminato.");
        }
    })
    .catch(function() {
        showStatus("Impossibile eliminare lo storico.");
    });
}

loadHistory();

setInterval(function() {
    loadHistory();
}, 5000);
</script>

</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):

    def log_message(self, format_string, *args):
        return

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            html_send(self, render_dashboard())
            return

        if path == "/api/stats":
            json_send(self, statistics())
            return

        if path == "/api/history":
            history = load_history()
            json_send(self, {
                "success": True,
                "history": history
            })
            return

        if path == "/api/export":
            history = load_history()

            json_send(self, {
                "success": True,
                "exported_at": now_iso(),
                "count": len(history),
                "history": history
            })

            return

        if path == "/api/instance":
            instance = initialize_instance()

            json_send(self, {
                "success": True,
                "instance": instance
            })

            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        json_send(
            self,
            {
                "success": False,
                "error": "Endpoint non trovato."
            },
            404
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/rejected":
            update_state("rejected")
            json_send(self, {
                "success": True
            })
            return

        if path != "/api/collect":
            json_send(
                self,
                {
                    "success": False,
                    "error": "Endpoint non trovato."
                },
                404
            )
            return

        update_state("requests")

        payload = read_json(self)

        if not payload.get("consent"):
            update_state("rejected")

            json_send(
                self,
                {
                    "success": False,
                    "error": "Consenso richiesto."
                },
                403
            )

            return

        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        accuracy = payload.get("accuracy")

        if not is_valid_coordinate(latitude, longitude):
            update_state("errors")

            json_send(
                self,
                {
                    "success": False,
                    "error": "Coordinate non valide."
                },
                400
            )

            return

        ip = get_ip_from_request(self)

        ip_info = get_ip_information(ip)

        if not ip_info.get("success"):
            ip_info = {
                "country": "",
                "country_code": "",
                "region": "",
                "city": "",
                "postal": "",
                "timezone": ""
            }

        entry = make_entry(
            ip,
            latitude,
            longitude,
            accuracy,
            ip_info
        )

        append_history(entry)
        update_state("accepted")

        json_send(
            self,
            {
                "success": True,
                "entry": entry
            }
        )

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path != "/api/history":
            json_send(
                self,
                {
                    "success": False,
                    "error": "Endpoint non trovato."
                },
                404
            )

            return

        delete_history()

        json_send(
            self,
            {
                "success": True,
                "message": "Storico eliminato."
            }
        )


def start_server():
    server = HTTPServer(
        (HOST, PORT),
        Handler
    )

    print()
    print("╭──────────────────────────────────────────────────────────────╮")
    print("│ SERVER                                                        │")
    print("├──────────────────────────────────────────────────────────────┤")
    print("│ Host        127.0.0.1                                        │")
    print("│ Port        5000                                             │")
    print("│ Mode        LOCAL                                            │")
    print("│ History     ENABLED                                          │")
    print("╰──────────────────────────────────────────────────────────────╯")
    print()

    return server


def open_browser():
    url = f"http://{HOST}:{PORT}/"

    try:
        webbrowser.open(url)
    except Exception:
        pass


def show_console_info(instance, key):
    print()
    print("┌──────────────────────────────────────────────────────────────┐")
    print("│ INSTANCE                                                     │")
    print("├──────────────────────────────────────────────────────────────┤")
    print("│ ID                                                           │")
    print("│ " + instance["instance_id"])
    print("│                                                              │")
    print("│ KEY                                                          │")
    print("│ " + key)
    print("│                                                              │")
    print("│ HISTORY                                                      │")
    print("│ " + HISTORY_FILE)
    print("└──────────────────────────────────────────────────────────────┘")
    print()


def run_server():
    instance = initialize_instance()
    key = initialize_key()
    initialize_config()
    initialize_history()

    clear()
    banner()

    loading("Inizializzazione", 1.0)
    loading("Caricamento configurazione", 0.8)
    loading("Preparazione storico locale", 0.8)

    show_console_info(instance, key)

    server = start_server()

    open_browser()

    print("Dashboard aperta.")
    print("Premi CTRL+C per arrestare il server.")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print()
        print("Arresto del server...")

    finally:
        server.server_close()
        print("Server arrestato.")


def main():
    ensure_directory()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "reset":
            instance, key = reset_instance()

            print()
            print("Istanza resettata.")
            print("Instance ID:", instance["instance_id"])
            print("Nuova key:", key)
            print()

            return

        if command == "clear":
            delete_history()

            print()
            print("Storico eliminato.")
            print()

            return

        if command == "info":
            instance = initialize_instance()
            key = initialize_key()
            config = initialize_config()
            history = initialize_history()

            print()
            print("APP:", APP_NAME)
            print("VERSION:", VERSION)
            print("HOST:", HOST)
            print("PORT:", PORT)
            print("INSTANCE:", instance["instance_id"])
            print("HISTORY:", len(history))
            print("DIRECTORY:", BASE_DIR)
            print("KEY:", key)
            print()

            return

    run_server()


if __name__ == "__main__":
    main()
