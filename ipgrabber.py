import os
import json
import secrets
from datetime import datetime, timezone

BASE_DIR = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "PugilainNetlify"
)

FUNCTION_DIR = os.path.join(
    BASE_DIR,
    "netlify",
    "functions"
)

os.makedirs(FUNCTION_DIR, exist_ok=True)

TOKEN = secrets.token_urlsafe(32)

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
TOML_FILE = os.path.join(BASE_DIR, "netlify.toml")
FUNCTION_FILE = os.path.join(FUNCTION_DIR, "event.js")


def save(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


config = {
    "project": "PugilainNetlify",
    "token": TOKEN,
    "created": datetime.now(timezone.utc).isoformat()
}

save(
    CONFIG_FILE,
    json.dumps(config, indent=2, ensure_ascii=False)
)

save(
    HISTORY_FILE,
    "[]"
)


index_html = r'''<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1.0"
>

<meta
name="description"
content="Pugilain consent session"
>

<title>Pugilain</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    width: 100%;
    min-height: 100%;
}

body {
    min-height: 100vh;
    background:
        radial-gradient(
            circle at 50% 0%,
            #25252b 0%,
            #111113 35%,
            #080809 75%
        );
    color: #f4f4f5;
    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 22px;
    overflow-x: hidden;
}

.background {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
}

.glow {
    position: absolute;
    width: 420px;
    height: 420px;
    border-radius: 50%;
    filter: blur(100px);
    opacity: .18;
    background: #6366f1;
    left: 50%;
    top: -220px;
    transform: translateX(-50%);
}

.container {
    position: relative;
    width: 100%;
    max-width: 680px;
}

.card {
    width: 100%;
    padding: 34px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,.09);
    background: rgba(17,17,19,.88);
    backdrop-filter: blur(20px);
    box-shadow:
        0 35px 100px rgba(0,0,0,.55),
        inset 0 1px 0 rgba(255,255,255,.04);
    animation:
        cardIn .7s ease both;
}

@keyframes cardIn {
    from {
        opacity: 0;
        transform:
            translateY(20px)
            scale(.98);
    }

    to {
        opacity: 1;
        transform:
            translateY(0)
            scale(1);
    }
}

.logo {
    width: 58px;
    height: 58px;
    border-radius: 17px;
    display: flex;
    justify-content: center;
    align-items: center;
    background:
        linear-gradient(
            135deg,
            #3f3f46,
            #18181b
        );
    border: 1px solid #3f3f46;
    font-weight: 900;
    font-size: 18px;
    letter-spacing: -1px;
    box-shadow:
        0 12px 30px rgba(0,0,0,.35);
    margin-bottom: 24px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.07);
    color: #a1a1aa;
    font-size: 12px;
    margin-bottom: 16px;
}

.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 12px #22c55e;
}

h1 {
    margin: 0;
    font-size: 34px;
    line-height: 1.1;
    letter-spacing: -1.5px;
}

.subtitle {
    margin-top: 13px;
    color: #a1a1aa;
    line-height: 1.65;
    font-size: 15px;
}

.banner {
    margin-top: 25px;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #27272a;
    background: rgba(24,24,27,.85);
}

.banner-title {
    font-weight: 800;
    margin-bottom: 7px;
}

.banner-text {
    color: #a1a1aa;
    font-size: 13px;
    line-height: 1.6;
}

.consent {
    margin-top: 18px;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #27272a;
    background: #0d0d0f;
}

.consent label {
    display: flex;
    align-items: flex-start;
    gap: 13px;
    cursor: pointer;
}

.consent input {
    appearance: none;
    width: 21px;
    height: 21px;
    min-width: 21px;
    border-radius: 6px;
    border: 1px solid #52525b;
    background: #18181b;
    cursor: pointer;
    position: relative;
    margin: 0;
}

.consent input:checked {
    background: #f4f4f5;
    border-color: #f4f4f5;
}

.consent input:checked::after {
    content: "";
    position: absolute;
    width: 5px;
    height: 10px;
    border-right: 2px solid #09090b;
    border-bottom: 2px solid #09090b;
    transform: rotate(45deg);
    left: 7px;
    top: 3px;
}

.consent-text {
    color: #d4d4d8;
    font-size: 13px;
    line-height: 1.55;
}

.button {
    position: relative;
    width: 100%;
    height: 54px;
    margin-top: 18px;
    border: 0;
    border-radius: 14px;
    background: #f4f4f5;
    color: #09090b;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: .4px;
    cursor: pointer;
    overflow: hidden;
    transition:
        transform .2s,
        opacity .2s;
}

.button:hover:not(:disabled) {
    transform: translateY(-2px);
}

.button:active:not(:disabled) {
    transform: translateY(0);
}

.button:disabled {
    opacity: .35;
    cursor: not-allowed;
}

.button.loading {
    pointer-events: none;
}

.button.loading .button-text {
    opacity: 0;
}

.loader {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 22px;
    height: 22px;
    transform:
        translate(-50%,-50%);
    border-radius: 50%;
    border: 3px solid #d4d4d8;
    border-top-color: #09090b;
    animation:
        spin .7s linear infinite;
    display: none;
}

.button.loading .loader {
    display: block;
}

@keyframes spin {
    to {
        transform:
            translate(-50%,-50%)
            rotate(360deg);
    }
}

.status {
    display: none;
    margin-top: 18px;
    padding: 15px;
    border-radius: 13px;
    background: #18181b;
    border: 1px solid #27272a;
    color: #d4d4d8;
    font-size: 13px;
    line-height: 1.5;
}

.status.show {
    display: block;
    animation:
        statusIn .3s ease both;
}

@keyframes statusIn {
    from {
        opacity: 0;
        transform: translateY(5px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.session {
    display: none;
    margin-top: 14px;
    padding: 14px;
    border-radius: 13px;
    background: #09090b;
    border: 1px solid #27272a;
}

.session-title {
    color: #71717a;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .8px;
    margin-bottom: 7px;
}

.session-id {
    color: #d4d4d8;
    font-family: monospace;
    font-size: 12px;
    word-break: break-all;
}

.footer {
    margin-top: 18px;
    color: #52525b;
    font-size: 11px;
    text-align: center;
}

.hidden {
    display: none !important;
}

</style>

</head>

<body>

<div class="background">
    <div class="glow"></div>
</div>

<div class="container">

<div class="card">

<div class="logo">
PG
</div>

<div class="badge">
<span class="dot"></span>
SESSION SYSTEM
</div>

<h1>
Benvenuto
</h1>

<div class="subtitle">
Prima di continuare, consulta l'informativa
e scegli esplicitamente se autorizzare
la registrazione della sessione.
</div>

<div class="banner">

<div class="banner-title">
Informativa sulla sessione
</div>

<div class="banner-text">
La registrazione viene effettuata solo dopo
il consenso esplicito. La sessione utilizza
un identificatore casuale separato.
</div>

</div>

<div class="consent">

<label>

<input
id="consent"
type="checkbox"
>

<span class="consent-text">
Ho letto l'informativa e acconsento
alla registrazione degli eventi della
mia sessione per lo scopo dichiarato.
</span>

</label>

</div>

<button
id="continueButton"
class="button"
disabled
>

<span class="button-text">
CONSENTI E CONTINUA
</span>

<span class="loader"></span>

</button>

<div
id="status"
class="status"
></div>

<div
id="sessionBox"
class="session"
>

<div class="session-title">
Session ID
</div>

<div
id="sessionId"
class="session-id"
></div>

</div>

<div class="footer">
Pugilain Session System
</div>

</div>

</div>

<script>

const PROJECT_TOKEN = "__TOKEN__";

const consent =
    document.getElementById(
        "consent"
    );

const button =
    document.getElementById(
        "continueButton"
    );

const statusBox =
    document.getElementById(
        "status"
    );

const sessionBox =
    document.getElementById(
        "sessionBox"
    );

const sessionIdBox =
    document.getElementById(
        "sessionId"
    );

const sessionId =
    crypto.randomUUID();

sessionIdBox.textContent =
    sessionId;

function showStatus(message) {

    statusBox.textContent =
        message;

    statusBox.classList.add(
        "show"
    );
}

async function sendEvent(type) {

    const response =
        await fetch(
            "/.netlify/functions/event",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    token:
                        PROJECT_TOKEN,

                    session:
                        sessionId,

                    type:
                        type,

                    consent:
                        true,

                    timestamp:
                        new Date()
                            .toISOString()
                })
            }
        );

    if (!response.ok) {
        throw new Error(
            "Request failed"
        );
    }

    return response.json();
}

consent.addEventListener(
    "change",
    function() {

        button.disabled =
            !consent.checked;

    }
);

button.addEventListener(
    "click",
    async function() {

        if (!consent.checked) {
            return;
        }

        button.classList.add(
            "loading"
        );

        showStatus(
            "Verifica del consenso..."
        );

        try {

            await sendEvent(
                "consent"
            );

            showStatus(
                "Sessione autorizzata. Avvio..."
            );

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        600
                    )
            );

            await sendEvent(
                "session_started"
            );

            sessionBox.style.display =
                "block";

            showStatus(
                "Sessione avviata correttamente."
            );

            button.classList.remove(
                "loading"
            );

            button.querySelector(
                ".button-text"
            ).textContent =
                "SESSIONE ATTIVA";

        } catch(error) {

            button.classList.remove(
                "loading"
            );

            showStatus(
                "Impossibile contattare il servizio."
            );

            button.disabled = false;

        }

    }
);

</script>

</body>

</html>
'''

index_html = index_html.replace(
    "__TOKEN__",
    TOKEN
)

save(
    INDEX_FILE,
    index_html
)


netlify_toml = r'''[build]
publish = "."
functions = "netlify/functions"

[functions]
node_bundler = "esbuild"
'''

save(
    TOML_FILE,
    netlify_toml
)


event_js = r'''exports.handler = async function(event) {

    if (event.httpMethod !== "POST") {

        return {
            statusCode: 405,
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                ok: false,
                error:
                    "Method not allowed"
            })
        };

    }

    let data;

    try {

        data = JSON.parse(
            event.body || "{}"
        );

    } catch(error) {

        return {
            statusCode: 400,
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                ok: false,
                error:
                    "Invalid JSON"
            })
        };

    }

    if (
        typeof data.token !== "string" ||
        typeof data.session !== "string" ||
        typeof data.type !== "string" ||
        data.consent !== true
    ) {

        return {
            statusCode: 400,
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                ok: false,
                error:
                    "Invalid event"
            })
        };

    }

    console.log(
        JSON.stringify({
            token:
                data.token,

            session:
                data.session,

            type:
                data.type,

            timestamp:
                data.timestamp
        })
    );

    return {
        statusCode: 200,
        headers: {
            "Content-Type":
                "application/json"
        },
        body: JSON.stringify({
            ok: true,
            saved: true,
            session:
                data.session
        })
    };

};
'''

save(
    FUNCTION_FILE,
    event_js
)


readme = """PUGILAIN NETLIFY

1. Esegui pugilain.py.

2. Troverai questa cartella sul Desktop:

PugilainNetlify

3. Dentro troverai:

index.html
netlify.toml
config.json
history.json
netlify/functions/event.js

4. Su Netlify importa l'intera cartella PugilainNetlify.

5. NON caricare soltanto index.html.

6. Dopo il deploy apri il dominio Netlify.

7. Il token del progetto è già incorporato
nell'index.html.

8. Ogni apertura della pagina genera
un session ID separato.

9. Gli eventi vengono gestiti dalla
Netlify Function.

Endpoint:

/.netlify/functions/event
"""

save(
    os.path.join(BASE_DIR, "README.txt"),
    readme
)


print()
print("==============================================")
print("          PUGILAIN NETLIFY GENERATOR")
print("==============================================")
print()
print("PROGETTO CREATO:")
print(BASE_DIR)
print()
print("INDEX:")
print(INDEX_FILE)
print()
print("FUNCTION:")
print(FUNCTION_FILE)
print()
print("TOKEN:")
print(TOKEN)
print()
print("IMPORTA SU NETLIFY L'INTERA CARTELLA:")
print(BASE_DIR)
print()
print("NON SOLO index.html")
print()
print("==============================================")
print("               COMPLETATO")
print("==============================================")
print()
