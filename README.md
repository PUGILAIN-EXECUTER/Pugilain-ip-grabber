<p align="center">
  <a href="https://kommodo.ai/i/D8p1OMNIOvPIFm6MoLvC">
    <img src="https://plain-weur-prod-public.komododecks.com/202608/14/D8p1OMNIOvPIFm6MoLvC/image.png" alt="PUGILAIN IP GRB">
  </a>
</p>

<h1 align="center">🐍 PUGILAIN IP GRB</h1>

<p align="center">
  <b>Python Network Diagnostics & Consent-Based Data Collection</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Requests-HTTP-2CA5E0?style=for-the-badge" alt="Requests">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

---

## ⚠️ Disclaimer

**This project is intended for educational, testing and authorized network-diagnostics purposes only.**

Use this software only when you have the appropriate authorization and, where required, the explicit consent of the people whose data is being processed.

The user is solely responsible for their use of this software and for complying with all applicable laws, regulations and privacy requirements.

The author does **not** encourage unauthorized tracking, monitoring, profiling or collection of personal information.


---

## 📖 About

PUGILAIN IP GRB is a Python-based local HTTP server and diagnostics dashboard.

The project demonstrates how a Python application can:

* run a local HTTP server;
* receive JSON data through an API;
* display diagnostic information;
* store test results locally;
* identify basic browser and operating-system information;
* query public IP metadata services;
* display diagnostic results through a web dashboard.

The project is designed primarily for **local laboratories, development and authorized testing environments**.

---

## 🛠️ Technologies

### Python

<p>
  <img src="https://www.python.org/static/community_logos/python-logo.png" width="220" alt="Python">
</p>

The application is written in **Python 3**.

### Requests

Used for HTTP requests to external services.

### HTTP Server

The project uses Python's built-in:

```text
http.server
```

No external web framework is required.

---

## 📋 Requirements

Before starting, install:

* Windows 10/11
* Python 3.x
* Git (optional, if cloning the repository)
* Internet connection for external API requests

Check Python:

```cmd
python --version
```

Check pip:

```cmd
python -m pip --version
```

---

## 📥 Installation

Clone the repository:

```cmd
git clone <REPOSITORY_URL>
```

Enter the project directory:

```cmd
cd Pugilain-ip-grabber
```

Run the automatic setup:

```cmd
setup.bat
```

The setup script will:

1. Check Python
2. Check pip
3. Create `.venv`
4. Activate the virtual environment
5. Update pip
6. Install the required dependencies
7. Start `main.py`

---

## 📦 Dependencies

Create a `requirements.txt` file containing:

```text
requests
```

Install manually with:

```cmd
python -m pip install -r requirements.txt
```

---

## 🚀 Running the project

The easiest method is:

```cmd
setup.bat
```

Or manually:

```cmd
.venv\Scripts\activate
python main.py
```

The local dashboard is available at:

```text
http://localhost:5000
```

---

## 📊 Dashboard

The application provides a local dashboard for viewing authorized diagnostic test results.

The dashboard is available at:

```text
http://localhost:5000/
```

or:

```text
http://localhost:5000/dashboard
```

---

## 🔌 API

The application exposes local API endpoints for the diagnostic workflow.

### Statistics

```text
GET /api/stats
```

Returns basic server statistics.

Example:

```json
{
  "total_visits": 0,
  "status": "online"
}
```

### Data collection

```text
POST /api/collect
```

The endpoint is intended for **authorized diagnostic testing only**.

---

## 📁 Project structure

```text
Pugilain-ip-grabber/
│
├── main.py
├── setup.bat
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
└── .venv/
```

Runtime files are created locally by the application.

These may include:

```text
Desktop/
└── Ipporject/
    ├── datainput.txt
    ├── key.txt
    ├── config.json
    └── system.log
```

These files should **not** be uploaded to a public repository if they contain real diagnostic or personal data.

---

## 🔐 Security & Privacy

Do not commit the following to GitHub:

```text
.venv/
*.log
datainput.txt
key.txt
config.json
```

Add them to `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
*.log
datainput.txt
key.txt
config.json
```

Never publish real user information, IP addresses, GPS coordinates, authentication tokens or other personal data.

---

## 🧪 Recommended Testing

For development, use:

* your own devices;
* a local virtual machine;
* test accounts;
* synthetic data;
* an isolated laboratory network.

Do not test against people or systems without authorization.

---

## 🖥️ Supported Platform

| Platform   | Support |
| ---------- | ------- |
| Windows 10 | ✅       |
| Windows 11 | ✅       |
| Linux      | ⚠️      |
| macOS      | ⚠️      |

The included `setup.bat` is intended for Windows.

---

## 📄 License

This project is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

---

## 👤 Author

### PUGILAIN

Educational Python networking project.

---

<p align="center">
  <img src="https://www.python.org/static/community_logos/python-logo.png" width="180" alt="Python">
</p>

<p align="center">
  Made with 🐍 Python
</p>
