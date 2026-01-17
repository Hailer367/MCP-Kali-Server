# MCP Kali Server

**Kali MCP Server** is a lightweight API bridge that connects MCP Clients (e.g: Claude Desktop, [5ire](https://github.com/nanbingxyz/5ire)) to the API server which allows excuting commands on a Linux terminal.

## 🚀 Features

- 🧠 **AI Endpoint Integration**: Connect your kali to any MCP client.
- 🖥️ **Command Execution**: Execute terminal commands safely with `shlex` sanitization.
- 🐚 **Interactive Terminal**: Send input to running background tasks.
- 🌐 **Autonomous Browser**: Headless browser (Playwright) for dynamic analysis and exploit verification.
- 📊 **Persistent Database**: Supabase integration for long-term storage of findings and session data.
- 🛠️ **Git Knowledge Base**: Bind a GitHub repo as a permanent database for tools, research, and exploits.
- 🔍 **White Box Scanning**: Specialized tools (Semgrep, Safety, Regex) for deep source code analysis.

## 🛠️ Installation

```bash
git clone https://github.com/Hailer367/MCP-Kali-Server.git
cd MCP-Kali-Server
pip install flask requests psutil supabase playwright
playwright install chromium
playwright install-deps

# Configuration
export KALI_API_KEY=your_key
export TOKEN=your_github_token
export SUPABASE_URL=your_url
export SUPABASE_KEY=your_key

python3 kali_server.py
```

## 🗄️ Database Setup
Run the `db_init_setup` tool from the AI or manually execute the provided SQL in your Supabase SQL editor.

## ⚠️ Disclaimer:
This project is for educational and ethical testing purposes only.
