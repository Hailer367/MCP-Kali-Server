#!/usr/bin/env python3

import argparse
import functools
import json
import logging
import os
import pty
import shlex
import secrets
import subprocess
import sys
import time
import traceback
import threading
import asyncio
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

API_PORT = int(os.environ.get("API_PORT", 5000))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "y")
API_KEY = os.environ.get("KALI_API_KEY")
COMMAND_TIMEOUT = 180

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

KB_REPO_LOCAL_PATH = os.environ.get("KB_REPO_LOCAL_PATH", os.path.abspath("data/kali_mcp_kb"))
GITHUB_TOKEN = os.environ.get("TOKEN")

app = Flask(__name__)
tasks = {}
task_lock = threading.Lock()

def sanitize_args(args_string: str) -> str:
    if not args_string: return ""
    try:
        return " ".join(shlex.quote(arg) for arg in shlex.split(args_string))
    except Exception:
        return shlex.quote(args_string)

def require_api_key(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEY:
            auth_header = request.headers.get("X-API-Key")
            if not auth_header or auth_header != API_KEY:
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

class CommandExecutor:
    def __init__(self, command: str, timeout: int = COMMAND_TIMEOUT, task_id: Optional[str] = None):
        self.command = command
        self.timeout = timeout
        self.task_id = task_id
        self.process = None
        self.stdout_data = ""
        self.stderr_data = ""
        self.return_code = None
        self.timed_out = False
        self.is_running = False
        self.use_pty = False

    def execute(self, wait: bool = True, use_pty: bool = False):
        self.is_running = True
        self.use_pty = use_pty
        try:
            if use_pty:
                master_fd, slave_fd = pty.openpty()
                self.process = subprocess.Popen(self.command, shell=True, stdout=slave_fd, stderr=slave_fd, stdin=slave_fd, text=True, preexec_fn=os.setsid)
                os.close(slave_fd)
                self.master_fd = master_fd
                def read_pty():
                    try:
                        while True:
                            data = os.read(master_fd, 4096).decode('utf-8', errors='replace')
                            if not data: break
                            self.stdout_data += data
                    except OSError: pass
                self.stdout_thread = threading.Thread(target=read_pty)
                self.stderr_thread = None
            else:
                self.process = subprocess.Popen(self.command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setsid)
                def read_out():
                    for line in iter(self.process.stdout.readline, ''): self.stdout_data += line
                def read_err():
                    for line in iter(self.process.stderr.readline, ''): self.stderr_data += line
                self.stdout_thread = threading.Thread(target=read_out)
                self.stderr_thread = threading.Thread(target=read_err)
            self.stdout_thread.daemon = True
            self.stdout_thread.start()
            if self.stderr_thread:
                self.stderr_thread.daemon = True
                self.stderr_thread.start()
            if wait: return self._wait()
            threading.Thread(target=self._wait).start()
            return {"task_id": self.task_id, "status": "running"}
        except Exception as e:
            self.is_running = False
            return {"error": str(e)}

    def _wait(self):
        try:
            self.return_code = self.process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.timed_out = True
            self.kill()
        self.is_running = False
        res = {"stdout": self.stdout_data, "stderr": self.stderr_data, "success": self.return_code == 0}
        if self.task_id:
            with task_lock:
                if self.task_id in tasks: tasks[self.task_id]["status"] = "completed"; tasks[self.task_id]["result"] = res
        return res

    def kill(self):
        if self.process:
            try: os.killpg(os.getpgid(self.process.pid), 9)
            except: pass

    def send_input(self, data: str):
        if not self.is_running: return False
        try:
            if self.use_pty: os.write(self.master_fd, data.encode()); return True
            elif self.process.stdin: self.process.stdin.write(data); self.process.stdin.flush(); return True
        except: pass
        return False

def execute_command(cmd, background=False, use_pty=False):
    task_id = secrets.token_hex(8) if background else None
    executor = CommandExecutor(cmd, task_id=task_id)
    if background:
        with task_lock: tasks[task_id] = {"command": cmd, "status": "running", "executor": executor}
    return executor.execute(wait=not background, use_pty=use_pty)

@app.route("/api/command", methods=["POST"])
@require_api_key
def generic_command():
    p = request.json
    return jsonify(execute_command(p.get("command"), p.get("background"), p.get("use_pty")))

@app.route("/api/tools/ffuf", methods=["POST"])
@require_api_key
def ffuf():
    p = request.json
    cmd = f"ffuf -u {shlex.quote(p.get('url'))} -w {shlex.quote(p.get('wordlist', '/usr/share/wordlists/dirb/common.txt'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/nuclei", methods=["POST"])
@require_api_key
def nuclei():
    p = request.json
    cmd = f"nuclei -u {shlex.quote(p.get('target'))}"
    if p.get("templates"): cmd += f" -t {shlex.quote(p.get('templates'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/feroxbuster", methods=["POST"])
@require_api_key
def feroxbuster():
    p = request.json
    cmd = f"feroxbuster -u {shlex.quote(p.get('url'))}"
    if p.get("wordlist"): cmd += f" -w {shlex.quote(p.get('wordlist'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/nxc", methods=["POST"])
@require_api_key
def nxc():
    p = request.json
    cmd = f"nxc {shlex.quote(p.get('protocol', 'smb'))} {shlex.quote(p.get('target'))}"
    if p.get("username"): cmd += f" -u {shlex.quote(p.get('username'))}"
    if p.get("password"): cmd += f" -p {shlex.quote(p.get('password'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/msfvenom", methods=["POST"])
@require_api_key
def msfvenom():
    p = request.json
    cmd = f"msfvenom -p {shlex.quote(p.get('payload'))}"
    for k, v in p.get("options", {}).items(): cmd += f" {shlex.quote(f'{k}={v}')}"
    cmd += f" -f {shlex.quote(p.get('format', 'elf'))}"
    if p.get("output"): cmd += f" -o {shlex.quote(p.get('output'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/nmap", methods=["POST"])
@require_api_key
def nmap():
    p = request.json
    cmd = f"nmap {shlex.quote(p.get('scan_type', '-sCV'))}"
    if p.get("ports"): cmd += f" -p {shlex.quote(p.get('ports'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    cmd += f" {shlex.quote(p.get('target'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/semgrep", methods=["POST"])
@require_api_key
def semgrep():
    p = request.json
    cmd = f"semgrep scan --json --config {shlex.quote(p.get('config', 'p/default'))} {shlex.quote(p.get('path', '.'))}"
    if p.get("additional_args"): cmd += f" {sanitize_args(p.get('additional_args'))}"
    return jsonify(execute_command(cmd))

@app.route("/api/tools/whitebox/scan", methods=["POST"])
@require_api_key
def whitebox_scan():
    p = request.json
    path = p.get("path", ".")
    patterns = {
        "SQLi": r"(?i)(select|insert|update|delete|drop).*where.*=.*['\"]\\s*\\+|f['\"].*\\{.*\\}",
        "CmdInj": r"(os\.system|subprocess\.|exec|eval|system)\(",
        "SSRF": r"(requests\.(get|post)|urllib\.request\.urlopen|aiohttp\.ClientSession)\(",
        "Traversal": r"(open|os\.path\.|pathlib\.Path)\(",
        "Secrets": r"(?i)(api_key|password|secret|token).*=.*['\"][a-zA-Z0-9\-_]{10,}['\"]"
    }
    results = {}
    for name, pattern in patterns.items():
        res = execute_command(f"rg --json -e {shlex.quote(pattern)} {shlex.quote(path)}")
        results[name] = res.get("stdout", "")
    return jsonify(results)

@app.route("/api/browser/action", methods=["POST"])
@require_api_key
def browser_action():
    p = request.json
    async def run():
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                if p.get("url"): await page.goto(p.get("url"))
                if p.get("action") == "click": await page.click(p.get("selector"))
                if p.get("action") == "fill": await page.fill(p.get("selector"), p.get("data"))
                if p.get("wait_for"): await page.wait_for_selector(p.get("wait_for"), timeout=5000)
                shot = f"screenshots/browser_{int(time.time())}.png"
                os.makedirs("screenshots", exist_ok=True)
                await page.screenshot(path=shot)
                res = {"url": page.url, "title": await page.title(), "screenshot": os.path.abspath(shot)}
            finally: await browser.close()
            return res
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run())
    if supabase:
        try: supabase.table("browser_history").insert({"url": result["url"], "action": p.get("action"), "screenshot_path": result["screenshot"], "metadata": result}).execute()
        except: pass
    return jsonify(result)

@app.route("/api/git/bind", methods=["POST"])
@require_api_key
def git_bind():
    p = request.json
    url = p.get("repo_url")
    if not url or not GITHUB_TOKEN: return jsonify({"error": "Missing url or TOKEN"}), 400
    if "github.com" in url: url = url.replace("://", f"://{GITHUB_TOKEN}@")
    if os.path.exists(KB_REPO_LOCAL_PATH): import shutil; shutil.rmtree(KB_REPO_LOCAL_PATH)
    os.makedirs(os.path.dirname(KB_REPO_LOCAL_PATH), exist_ok=True)
    res = execute_command(f"git clone {shlex.quote(url)} {shlex.quote(KB_REPO_LOCAL_PATH)}")
    if res["success"]:
        execute_command(f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} config user.email 'mcp@kali'")
        execute_command(f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} config user.name 'MCP'")
    return jsonify(res)

@app.route("/api/git/store", methods=["POST"])
@require_api_key
def git_store():
    p = request.json
    path = os.path.join(KB_REPO_LOCAL_PATH, p.get("category", "general"), p.get("filename", "info.txt"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: f.write(p.get("content", ""))
    res = execute_command(f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} add {shlex.quote(path)} && git -C {shlex.quote(KB_REPO_LOCAL_PATH)} commit -m 'Update' && git -C {shlex.quote(KB_REPO_LOCAL_PATH)} push")
    return jsonify(res)

@app.route("/api/db/init", methods=["POST"])
@require_api_key
def db_init():
    sql = "CREATE TABLE IF NOT EXISTS targets (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY, host TEXT NOT NULL); CREATE TABLE IF NOT EXISTS vulnerabilities (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY, target_id UUID REFERENCES targets(id), tool TEXT, vuln_type TEXT, severity TEXT, description TEXT); CREATE TABLE IF NOT EXISTS exploits (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY, vulnerability_id UUID REFERENCES vulnerabilities(id), poc_content TEXT); CREATE TABLE IF NOT EXISTS browser_history (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY, url TEXT, action TEXT, screenshot_path TEXT);"
    if not supabase: return jsonify({"error": "No Supabase", "sql": sql}), 400
    try: supabase.rpc("exec_sql", {"query": sql}).execute(); success = True
    except: success = False
    return jsonify({"rpc_success": success, "sql": sql})

@app.route("/api/tasks/<task_id>/input", methods=["POST"])
@require_api_key
def task_input(task_id):
    with task_lock:
        if task_id in tasks: return jsonify({"success": tasks[task_id]["executor"].send_input(request.json.get("input", ""))})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/system/info", methods=["GET"])
@require_api_key
def get_system_info():
    import platform
    return jsonify({"os": platform.system(), "version": platform.version(), "machine": platform.machine()})

@app.route("/api/files/list", methods=["GET"])
@require_api_key
def list_files():
    try:
        path = request.args.get("path", ".")
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({"name": item, "path": os.path.abspath(full_path), "type": "directory" if os.path.isdir(full_path) else "file"})
        return jsonify({"path": os.path.abspath(path), "items": items})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/api/files/read", methods=["GET"])
@require_api_key
def read_file():
    try:
        path = request.args.get("path")
        with open(path, "r", errors="replace") as f: content = f.read()
        return jsonify({"path": os.path.abspath(path), "content": content})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/api/files/write", methods=["POST"])
@require_api_key
def write_file_endpoint():
    try:
        p = request.json
        path = p.get("path")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f: f.write(p.get("content", ""))
        return jsonify({"message": f"Wrote to {path}"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/health")
def health(): return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=API_PORT, debug=DEBUG_MODE)
