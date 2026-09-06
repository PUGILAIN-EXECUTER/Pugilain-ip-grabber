import os
import json
import uuid
import time
import secrets
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 5000

BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "PugilainGeo")
PUBLIC_DIR = os.path.join(BASE_DIR, "netlify")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    temp = path + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    os.replace(temp, path)


history = load_json(HISTORY_FILE, [])
tokens = load_json(TOKENS_FILE, {})

config = load_json(
    CONFIG_FILE,
    {
        "name": "Pugilain Geo",
        "version": "1.0",
        "port": PORT,
        "created": datetime.now(timezone.utc).isoformat()
    }
)

save_json(CONFIG_FILE, config)


def create_token():
    token = secrets.token_urlsafe(32)

    tokens[token] = {
        "created": datetime.now(timezone.utc).isoformat(),
        "events": 0,
        "active": True
    }

    save_json(TOKENS_FILE, tokens)

    return token


def add_event(token, event):
    if token not in tokens:
        return False

    record = {
        "id": uuid.uuid4().hex,
        "token": token,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event
    }

    history.append(record)

    tokens[token]["events"] = tokens[token].get("events", 0) + 1

    save_json(HISTORY_FILE, history)
    save_json(TOKENS_FILE, tokens)

    return True


def json_response(handler, data, status=200):
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()

    handler.wfile.write(raw)


class LocalHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print("[LOCAL]", format % args)

    def do_OPTIONS(self):
        json_response(self, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            html = DASHBOARD_HTML.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()

            self.wfile.write(html)
            return

        if parsed.path == "/api/history":
            json_response(
                self,
                {
                    "ok": True,
                    "count": len(history),
                    "history": history
                }
            )
            return

        if parsed.path == "/api/tokens":
            safe_tokens = {}

            for token, data in tokens.items():
                safe_tokens[token] = {
                    "created": data.get("created"),
                    "events": data.get("events", 0),
                    "active": data.get("active", True)
                }

            json_response(
                self,
                {
                    "ok": True,
                    "tokens": safe_tokens
                }
            )
            return

        if parsed.path == "/api/stats":
            json_response(
                self,
                {
                    "ok": True,
                    "sessions": len(tokens),
                    "events": len(history),
                    "active_sessions": sum(
                        1
                        for value in tokens.values()
                        if value.get("active", True)
                    )
                }
            )
            return

        if parsed.path == "/api/health":
            json_response(
                self,
                {
                    "ok": True,
                    "server": "Pugilain Geo",
                    "time": datetime.now(timezone.utc).isoformat()
                }
            )
            return

        json_response(self, {"ok": False, "error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/event":
            json_response(self, {"ok": False, "error": "Not found"}, 404)
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))

            if size <= 0 or size > 10000:
                json_response(
                    self,
                    {
                        "ok": False,
                        "error": "Invalid request size"
                    },
                    400
                )
                return

            body = self.rfile.read(size)
            data = json.loads(body.decode("utf-8"))

        except Exception:
            json_response(
                self,
                {
                    "ok": False,
                    "error": "Invalid JSON"
                },
                400
            )
            return

        token = str(data.get("token", "")).strip()
        event = data.get("event")

        if not token or token not in tokens:
            json_response(
                self,
                {
                    "ok": False,
                    "error": "Invalid session token"
                },
                403
            )
            return

        if not isinstance(event, dict):
            json_response(
                self,
                {
                    "ok": False,
                    "error": "Invalid event"
                },
                400
            )
            return

        event_type = str(event.get("type", "")).strip()

        if event_type not in {
            "consent",
            "session_started",
            "page_opened",
            "location_available"
        }:
            json_response(
                self,
                {
                    "ok": False,
                    "error": "Unsupported event"
                },
                400
            )
            return

        if not add_event(token, event):
            json_response(
                self,
                {
                    "ok": False,
                    "error": "Unable to save event"
                },
                500
            )
            return

        print()
        print("========================================")
        print("NUOVO EVENTO")
        print("TOKEN:", token)
        print("TIPO:", event_type)
        print("ORA:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("========================================")
        print()

        json_response(
            self,
            {
                "ok": True,
                "saved": True,
                "token": token
            }
        )


def create_netlify_index():
    html = r'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Pugilain Geo</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background: #09090b;
    color: #f4f4f5;
    font-family: Arial, Helvetica, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 24px;
}

.container {
    width: 100%;
    max-width: 680px;
}

.card {
    background: #111113;
    border: 1px solid #27272a;
    border-radius: 18px;
    padding: 32px;
    box-shadow: 0 20px 70px rgba(0,0,0,.4);
}

.logo {
    width: 54px;
    height: 54px;
    border-radius: 15px;
    background: #27272a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 20px;
    margin-bottom: 22px;
}

h1 {
    margin: 0 0 10px;
    font-size: 30px;
}

p {
    color: #a1a1aa;
    line-height: 1.6;
}

.notice {
    margin-top: 22px;
    padding: 18px;
    border: 1px solid #3f3f46;
    border-radius: 13px;
    background: #18181b;
}

.checkbox {
    display: flex;
    gap: 12px;
    align-items: flex-start;
}

.checkbox input {
    width: 20px;
    height: 20px;
    margin-top: 2px;
}

button {
    width: 100%;
    margin-top: 22px;
    padding: 15px;
    border: 0;
    border-radius: 12px;
    background: #f4f4f5;
    color: #09090b;
    font-weight: bold;
    cursor: pointer;
    font-size: 15px;
}

button:disabled {
    opacity: .4;
    cursor: not-allowed;
}

.status {
    margin-top: 20px;
    padding: 15px;
    border-radius: 12px;
    background: #18181b;
    color: #a1a1aa;
    display: none;
}

.data {
    margin-top: 18px;
    display: none;
}

.row {
    padding: 12px 0;
    border-bottom: 1px solid #27272a;
}

.label {
    color: #71717a;
    font-size: 12px;
    text-transform: uppercase;
}

.value {
    margin-top: 4px;
    word-break: break-all;
}

.small {
    font-size: 12px;
    color: #71717a;
    margin-top: 18px;
}
</style>
</head>

<body>

<div class="container">

<div class="card">

<div class="logo">PG</div>

<h1>Accesso</h1>

<p>
Prima di continuare, leggi l'informativa e scegli esplicitamente
se vuoi autorizzare la sessione.
</p>

<div class="notice">

<label class="checkbox">

<input type="checkbox" id="consent">

<span>
Acconsento alla registrazione di questa sessione per lo scopo
dichiarato nella pagina.
</span>

</label>

</div>

<button id="continue" disabled>
CONSENTI E CONTINUA
</button>

<div class="status" id="status"></div>

<div class="data" id="data">

<div class="row">
<div class="label">Sessione</div>
<div class="value" id="session"></div>
</div>

<div class="row">
<div class="label">Stato</div>
<div class="value" id="state"></div>
</div>

<div class="row">
<div class="label">Precisione posizione</div>
<div class="value" id="accuracy"></div>
</div>

</div>

<div class="small">
La sessione utilizza un identificatore casuale separato.
</div>

</div>

</div>

<script>

const params = new URLSearchParams(window.location.search);

let token = params.get("token");

if (!token) {
    token = crypto.randomUUID();
}

const consent = document.getElementById("consent");
const button = document.getElementById("continue");
const statusBox = document.getElementById("status");
const dataBox = document.getElementById("data");

document.getElementById("session").textContent = token;

consent.addEventListener("change", function() {
    button.disabled = !consent.checked;
});

function showStatus(text) {
    statusBox.style.display = "block";
    statusBox.textContent = text;
}

async function sendEvent(type, extra = {}) {

    const endpoint = "/api/event";

    const payload = {
        token: token,
        event: {
            type: type,
            ...extra
        }
    };

    try {

        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        return await response.json();

    } catch (error) {

        return {
            ok: false,
            error: "backend_unavailable"
        };

    }
}

button.addEventListener("click", async function() {

    if (!consent.checked) {
        return;
    }

    button.disabled = true;

    showStatus("Registrazione del consenso...");

    await sendEvent("consent", {
        consent: true
    });

    await sendEvent("session_started");

    dataBox.style.display = "block";

    document.getElementById("state").textContent =
        "Sessione autorizzata";

    if (!navigator.geolocation) {

        showStatus(
            "La geolocalizzazione non è disponibile in questo browser."
        );

        return;
    }

    showStatus(
        "Sessione autorizzata. Se richiesto, puoi concedere la posizione al browser."
    );

    navigator.geolocation.getCurrentPosition(

        async function(position) {

            const accuracy = Math.round(
                position.coords.accuracy
            );

            document.getElementById("accuracy").textContent =
                accuracy + " metri";

            await sendEvent("location_available", {
                location_available: true,
                accuracy_meters: accuracy
            });

            showStatus(
                "Sessione completata."
            );

        },

        async function() {

            document.getElementById("state").textContent =
                "Sessione autorizzata senza posizione";

            await sendEvent("location_available", {
                location_available: false
            });

            showStatus(
                "Hai autorizzato la sessione, ma la posizione non è stata fornita."
            );

        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }

    );

});

sendEvent("page_opened");

</script>

</body>
</html>
'''

    path = os.path.join(PUBLIC_DIR, "index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return path


DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Pugilain Geo Local</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #09090b;
    color: #f4f4f5;
    font-family: Arial, Helvetica, sans-serif;
}

header {
    padding: 25px;
    border-bottom: 1px solid #27272a;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

h1 {
    margin: 0;
    font-size: 22px;
}

main {
    padding: 25px;
    max-width: 1200px;
    margin: auto;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}

.stat {
    padding: 20px;
    background: #111113;
    border: 1px solid #27272a;
    border-radius: 14px;
}

.stat-number {
    font-size: 28px;
    font-weight: bold;
}

.stat-label {
    color: #71717a;
    margin-top: 5px;
}

.panel {
    background: #111113;
    border: 1px solid #27272a;
    border-radius: 14px;
    overflow: hidden;
}

.panel-head {
    padding: 18px;
    border-bottom: 1px solid #27272a;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

button {
    border: 0;
    border-radius: 9px;
    padding: 9px 13px;
    cursor: pointer;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    text-align: left;
    padding: 14px;
    border-bottom: 1px solid #27272a;
}

th {
    color: #71717a;
    font-size: 12px;
    text-transform: uppercase;
}

code {
    color: #d4d4d8;
    word-break: break-all;
}

@media(max-width:700px) {
    .stats {
        grid-template-columns: 1fr;
    }

    table {
        font-size: 12px;
    }

    th:nth-child(3),
    td:nth-child(3) {
        display: none;
    }
}
</style>
</head>

<body>

<header>
<h1>Pugilain Geo · Local</h1>
<div id="connection">ONLINE</div>
</header>

<main>

<div class="stats">

<div class="stat">
<div class="stat-number" id="sessions">0</div>
<div class="stat-label">Sessioni</div>
</div>

<div class="stat">
<div class="stat-number" id="events">0</div>
<div class="stat-label">Eventi</div>
</div>

<div class="stat">
<div class="stat-number" id="active">0</div>
<div class="stat-label">Sessioni attive</div>
</div>

</div>

<div class="panel">

<div class="panel-head">
<strong>Eventi recenti</strong>
<button onclick="loadData()">Aggiorna</button>
</div>

<table>

<thead>

<tr>
<th>Ora</th>
<th>Token</th>
<th>Evento</th>
<th>Dati</th>
</tr>

</thead>

<tbody id="rows"></tbody>

</table>

</div>

</main>

<script>

async function loadData() {

    try {

        const stats = await fetch(
            "/api/stats",
            {cache: "no-store"}
        ).then(r => r.json());

        document.getElementById("sessions").textContent =
            stats.sessions;

        document.getElementById("events").textContent =
            stats.events;

        document.getElementById("active").textContent =
            stats.active_sessions;

        const data = await fetch(
            "/api/history",
            {cache: "no-store"}
        ).then(r => r.json());

        const rows = document.getElementById("rows");

        rows.innerHTML = "";

        const list = [...data.history].reverse();

        for (const item of list) {

            const tr = document.createElement("tr");

            const date = new Date(
                item.timestamp
            ).toLocaleString();

            const details =
                JSON.stringify(item.event);

            tr.innerHTML =
                "<td>" + date + "</td>" +
                "<td><code>" +
                escapeHtml(item.token) +
                "</code></td>" +
                "<td>" +
                escapeHtml(item.event.type || "") +
                "</td>" +
                "<td><code>" +
                escapeHtml(details) +
                "</code></td>";

            rows.appendChild(tr);
        }

    } catch(error) {

        document.getElementById(
            "connection"
        ).textContent = "OFFLINE";

    }

}

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}

loadData();

setInterval(
    loadData,
    3000
);

</script>

</body>
</html>
'''


def print_banner():

    print()
    print("==============================================")
    print("          PUGILAIN GEO LOCAL")
    print("==============================================")
    print()
    print("Cartella:")
    print(BASE_DIR)
    print()
    print("Cartella Netlify:")
    print(PUBLIC_DIR)
    print()
    print("Index:")
    print(os.path.join(PUBLIC_DIR, "index.html"))
    print()
    print("Pannello locale:")
    print("http://127.0.0.1:5000")
    print()
    print("Cronologia:")
    print(HISTORY_FILE)
    print()
    print("Token:")
    print(TOKENS_FILE)
    print()
    print("==============================================")
    print()


def run_server():

    server = ThreadingHTTPServer(
        (HOST, PORT),
        LocalHandler
    )

    print_banner()

    try:
        webbrowser.open(
            "http://127.0.0.1:5000"
        )
    except Exception:
        pass

    print(
        "Server avviato su "
        + HOST
        + ":"
        + str(PORT)
    )

    print(
        "CTRL+C per terminare."
    )

    server.serve_forever()


if __name__ == "__main__":

    index_path = create_netlify_index()

    print()
    print("FILE NETLIFY CREATO:")
    print(index_path)
    print()

    run_server()
