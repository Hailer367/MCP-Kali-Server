#!/usr/bin/env python3

# This script connect the MCP AI agent to Kali Linux terminal and API Server.

# some of the code here was inspired from https://github.com/whit3rabbit0/project_astro , be sure to check them out

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
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_PORT = int(os.environ.get("API_PORT", 5000))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "y")
API_KEY = os.environ.get("KALI_API_KEY")
COMMAND_TIMEOUT = 180  # 5 minutes default timeout

app = Flask(__name__)

# Global task storage
tasks = {}
task_lock = threading.Lock()

def require_api_key(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEY:
            auth_header = request.headers.get("X-API-Key")
            if not auth_header or auth_header != API_KEY:
                return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401
        return f(*args, **kwargs)
    return decorated_function

class CommandExecutor:
    """Class to handle command execution with better timeout management and background support"""
    
    def __init__(self, command: str, timeout: int = COMMAND_TIMEOUT, task_id: Optional[str] = None):
        self.command = command
        self.timeout = timeout
        self.task_id = task_id
        self.process = None
        self.stdout_data = ""
        self.stderr_data = ""
        self.stdout_thread = None
        self.stderr_thread = None
        self.return_code = None
        self.timed_out = False
        self.is_running = False
        self.start_time = None
        self.end_time = None
    
    def _read_stdout(self):
        """Thread function to continuously read stdout"""
        try:
            for line in iter(self.process.stdout.readline, ''):
                self.stdout_data += line
        except Exception as e:
            logger.error(f"Error reading stdout: {e}")
    
    def _read_stderr(self):
        """Thread function to continuously read stderr"""
        try:
            for line in iter(self.process.stderr.readline, ''):
                self.stderr_data += line
        except Exception as e:
            logger.error(f"Error reading stderr: {e}")
    
    def execute(self, wait: bool = True, use_pty: bool = False) -> Dict[str, Any]:
        """Execute the command"""
        logger.info(f"Executing command: {self.command} (wait={wait}, use_pty={use_pty})")
        self.start_time = time.time()
        self.is_running = True
        self.use_pty = use_pty
        
        try:
            if use_pty:
                master_fd, slave_fd = pty.openpty()
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    stdin=slave_fd,
                    text=True,
                    bufsize=1,
                    preexec_fn=os.setsid
                )
                os.close(slave_fd)
                self.master_fd = master_fd

                def read_pty():
                    try:
                        while True:
                            data = os.read(master_fd, 4096).decode('utf-8', errors='replace')
                            if not data:
                                break
                            self.stdout_data += data
                    except OSError:
                        pass
                    finally:
                        os.close(master_fd)

                self.stdout_thread = threading.Thread(target=read_pty)
                self.stderr_thread = None # Stderr is merged in PTY
            else:
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                    preexec_fn=os.setsid # Create a session leader to allow killing the whole process tree
                )

                # Start threads to read output continuously
                self.stdout_thread = threading.Thread(target=self._read_stdout)
                self.stderr_thread = threading.Thread(target=self._read_stderr)

            self.stdout_thread.daemon = True
            if self.stderr_thread:
                self.stderr_thread.daemon = True

            self.stdout_thread.start()
            if self.stderr_thread:
                self.stderr_thread.start()
            
            if wait:
                return self._wait_for_completion()
            else:
                # Start a thread to wait for completion in background
                threading.Thread(target=self._wait_for_completion).start()
                return {
                    "task_id": self.task_id,
                    "status": "running",
                    "message": "Command started in background"
                }

        except Exception as e:
            self.is_running = False
            self.end_time = time.time()
            logger.error(f"Error executing command: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "stdout": self.stdout_data,
                "stderr": f"Error executing command: {str(e)}\n{self.stderr_data}",
                "return_code": -1,
                "success": False,
                "timed_out": False,
                "partial_results": bool(self.stdout_data or self.stderr_data)
            }

    def _wait_for_completion(self) -> Dict[str, Any]:
        """Wait for the process to complete or timeout"""
        try:
            try:
                self.return_code = self.process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.timed_out = True
                logger.warning(f"Command timed out after {self.timeout} seconds. Terminating process.")
                self.kill()
                self.return_code = -1
            
            # Wait a bit for threads to finish reading
            self.stdout_thread.join(timeout=2)
            if self.stderr_thread:
                self.stderr_thread.join(timeout=2)

            self.is_running = False
            self.end_time = time.time()

            # Always consider it a success if we have output, even with timeout
            success = True if self.timed_out and (self.stdout_data or self.stderr_data) else (self.return_code == 0)
            
            result = {
                "stdout": self.stdout_data,
                "stderr": self.stderr_data,
                "return_code": self.return_code,
                "success": success,
                "timed_out": self.timed_out,
                "partial_results": self.timed_out and (self.stdout_data or self.stderr_data)
            }

            if self.task_id:
                with task_lock:
                    if self.task_id in tasks:
                        tasks[self.task_id]["status"] = "completed"
                        tasks[self.task_id]["result"] = result

            return result
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            self.is_running = False
            return {"error": str(e)}

    def kill(self):
        """Kill the process and its children"""
        if self.process:
            try:
                import signal
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                time.sleep(1)
                if self.process.poll() is None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception as e:
                logger.error(f"Error killing process: {e}")

    def send_input(self, data: str):
        """Send input to the process"""
        if not self.is_running:
            return False

        try:
            if self.use_pty:
                # PTY expects bytes
                encoded_data = data.encode() if isinstance(data, str) else data
                os.write(self.master_fd, encoded_data)
                return True
            else:
                if self.process and self.process.stdin:
                    # Process was opened with text=True, so it expects str
                    self.process.stdin.write(data)
                    self.process.stdin.flush()
                    return True
        except Exception as e:
            logger.error(f"Error sending input: {e}")
        return False


def execute_command(command: str, background: bool = False, use_pty: bool = False) -> Dict[str, Any]:
    """
    Execute a shell command and return the result
    
    Args:
        command: The command to execute
        background: Whether to run in background
        use_pty: Whether to use a PTY
        
    Returns:
        A dictionary containing the results or task ID
    """
    task_id = None
    if background:
        task_id = secrets.token_hex(8)

    executor = CommandExecutor(command, task_id=task_id)

    if background:
        with task_lock:
            tasks[task_id] = {
                "command": command,
                "status": "running",
                "executor": executor,
                "start_time": time.time(),
                "use_pty": use_pty
            }
        return executor.execute(wait=False, use_pty=use_pty)
    else:
        return executor.execute(wait=True, use_pty=use_pty)


@app.route("/api/command", methods=["POST"])
@require_api_key
def generic_command():
    """Execute any command provided in the request."""
    try:
        params = request.json
        command = params.get("command", "")
        background = params.get("background", False)
        use_pty = params.get("use_pty", False)
        
        if not command:
            logger.warning("Command endpoint called without command parameter")
            return jsonify({
                "error": "Command parameter is required"
            }), 400
        
        result = execute_command(command, background=background, use_pty=use_pty)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in command endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/ffuf", methods=["POST"])
@require_api_key
def ffuf():
    """Execute ffuf with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        additional_args = params.get("additional_args", "")

        if not url:
            return jsonify({"error": "URL parameter is required"}), 400

        command = f"ffuf -u {shlex.quote(url)} -w {shlex.quote(wordlist)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in ffuf endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/nuclei", methods=["POST"])
@require_api_key
def nuclei():
    """Execute nuclei with the provided parameters."""
    try:
        params = request.json
        target = params.get("target", "")
        templates = params.get("templates", "")
        additional_args = params.get("additional_args", "")

        if not target:
            return jsonify({"error": "target parameter is required"}), 400

        command = f"nuclei -u {shlex.quote(target)}"

        if templates:
            command += f" -t {shlex.quote(templates)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in nuclei endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/feroxbuster", methods=["POST"])
@require_api_key
def feroxbuster():
    """Execute feroxbuster with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        wordlist = params.get("wordlist", "")
        additional_args = params.get("additional_args", "")

        if not url:
            return jsonify({"error": "url parameter is required"}), 400

        command = f"feroxbuster -u {shlex.quote(url)}"

        if wordlist:
            command += f" -w {shlex.quote(wordlist)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in feroxbuster endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/nxc", methods=["POST"])
@require_api_key
def nxc():
    """Execute NetExec (nxc) with the provided parameters."""
    try:
        params = request.json
        protocol = params.get("protocol", "smb")
        target = params.get("target", "")
        username = params.get("username", "")
        password = params.get("password", "")
        additional_args = params.get("additional_args", "")

        if not target:
            return jsonify({"error": "target parameter is required"}), 400

        command = f"nxc {shlex.quote(protocol)} {shlex.quote(target)}"

        if username:
            command += f" -u {shlex.quote(username)}"
        if password:
            command += f" -p {shlex.quote(password)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in nxc endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/msfvenom", methods=["POST"])
@require_api_key
def msfvenom():
    """Execute msfvenom with the provided parameters."""
    try:
        params = request.json
        payload = params.get("payload", "")
        options = params.get("options", {})
        format_type = params.get("format", "elf")
        output_file = params.get("output", "")

        if not payload:
            return jsonify({"error": "payload parameter is required"}), 400

        command = f"msfvenom -p {shlex.quote(payload)}"

        for key, value in options.items():
            command += f" {shlex.quote(f'{key}={value}')}"

        command += f" -f {shlex.quote(format_type)}"

        if output_file:
            command += f" -o {shlex.quote(output_file)}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in msfvenom endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/searchsploit", methods=["POST"])
@require_api_key
def searchsploit():
    """Execute searchsploit with the provided parameters."""
    try:
        params = request.json
        query = params.get("query", "")
        additional_args = params.get("additional_args", "")

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        command = f"searchsploit {shlex.quote(query)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in searchsploit endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tools/hashcat", methods=["POST"])
@require_api_key
def hashcat():
    """Execute hashcat with the provided parameters."""
    try:
        params = request.json
        hash_file = params.get("hash_file", "")
        mode = params.get("mode", "")
        wordlist = params.get("wordlist", "/usr/share/wordlists/rockyou.txt")
        additional_args = params.get("additional_args", "")

        if not hash_file or not mode:
            return jsonify({"error": "hash_file and mode parameters are required"}), 400

        command = f"hashcat -m {shlex.quote(str(mode))} {shlex.quote(hash_file)} {shlex.quote(wordlist)}"

        if additional_args:
            command += f" {additional_args}"

        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in hashcat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/tools/nmap", methods=["POST"])
@require_api_key
def nmap():
    """Execute nmap scan with the provided parameters."""
    try:
        params = request.json
        target = params.get("target", "")
        scan_type = params.get("scan_type", "-sCV")
        ports = params.get("ports", "")
        additional_args = params.get("additional_args", "-T4 -Pn")
        
        if not target:
            logger.warning("Nmap called without target parameter")
            return jsonify({
                "error": "Target parameter is required"
            }), 400        
        
        command = f"nmap {shlex.quote(scan_type)}"
        
        if ports:
            command += f" -p {shlex.quote(ports)}"
        
        if additional_args:
            # Basic validation for additional args - more sophisticated validation would be better
            command += f" {additional_args}"
        
        command += f" {shlex.quote(target)}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in nmap endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/gobuster", methods=["POST"])
@require_api_key
def gobuster():
    """Execute gobuster with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        mode = params.get("mode", "dir")
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        additional_args = params.get("additional_args", "")
        
        if not url:
            logger.warning("Gobuster called without URL parameter")
            return jsonify({
                "error": "URL parameter is required"
            }), 400
        
        # Validate mode
        if mode not in ["dir", "dns", "fuzz", "vhost"]:
            logger.warning(f"Invalid gobuster mode: {mode}")
            return jsonify({
                "error": f"Invalid mode: {mode}. Must be one of: dir, dns, fuzz, vhost"
            }), 400
        
        command = f"gobuster {shlex.quote(mode)} -u {shlex.quote(url)} -w {shlex.quote(wordlist)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in gobuster endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/dirb", methods=["POST"])
@require_api_key
def dirb():
    """Execute dirb with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        additional_args = params.get("additional_args", "")
        
        if not url:
            logger.warning("Dirb called without URL parameter")
            return jsonify({
                "error": "URL parameter is required"
            }), 400
        
        command = f"dirb {shlex.quote(url)} {shlex.quote(wordlist)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in dirb endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/nikto", methods=["POST"])
@require_api_key
def nikto():
    """Execute nikto with the provided parameters."""
    try:
        params = request.json
        target = params.get("target", "")
        additional_args = params.get("additional_args", "")
        
        if not target:
            logger.warning("Nikto called without target parameter")
            return jsonify({
                "error": "Target parameter is required"
            }), 400
        
        command = f"nikto -h {shlex.quote(target)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in nikto endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/sqlmap", methods=["POST"])
@require_api_key
def sqlmap():
    """Execute sqlmap with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        data = params.get("data", "")
        additional_args = params.get("additional_args", "")
        
        if not url:
            logger.warning("SQLMap called without URL parameter")
            return jsonify({
                "error": "URL parameter is required"
            }), 400
        
        command = f"sqlmap -u {shlex.quote(url)} --batch"
        
        if data:
            command += f" --data={shlex.quote(data)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in sqlmap endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/metasploit", methods=["POST"])
@require_api_key
def metasploit():
    """Execute metasploit module with the provided parameters."""
    try:
        params = request.json
        module = params.get("module", "")
        options = params.get("options", {})
        
        if not module:
            logger.warning("Metasploit called without module parameter")
            return jsonify({
                "error": "Module parameter is required"
            }), 400
        
        # Format options for Metasploit
        options_str = ""
        for key, value in options.items():
            options_str += f" {key}={value}"
        
        # Create an MSF resource script
        resource_content = f"use {module}\n"
        for key, value in options.items():
            resource_content += f"set {key} {value}\n"
        resource_content += "exploit\n"
        
        # Save resource script to a temporary file
        resource_file = "/tmp/mcp_msf_resource.rc"
        with open(resource_file, "w") as f:
            f.write(resource_content)
        
        command = f"msfconsole -q -r {resource_file}"
        result = execute_command(command)
        
        # Clean up the temporary file
        try:
            os.remove(resource_file)
        except Exception as e:
            logger.warning(f"Error removing temporary resource file: {str(e)}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in metasploit endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/hydra", methods=["POST"])
@require_api_key
def hydra():
    """Execute hydra with the provided parameters."""
    try:
        params = request.json
        target = params.get("target", "")
        service = params.get("service", "")
        username = params.get("username", "")
        username_file = params.get("username_file", "")
        password = params.get("password", "")
        password_file = params.get("password_file", "")
        additional_args = params.get("additional_args", "")
        
        if not target or not service:
            logger.warning("Hydra called without target or service parameter")
            return jsonify({
                "error": "Target and service parameters are required"
            }), 400
        
        if not (username or username_file) or not (password or password_file):
            logger.warning("Hydra called without username/password parameters")
            return jsonify({
                "error": "Username/username_file and password/password_file are required"
            }), 400
        
        command = f"hydra -t 4"
        
        if username:
            command += f" -l {shlex.quote(username)}"
        elif username_file:
            command += f" -L {shlex.quote(username_file)}"
        
        if password:
            command += f" -p {shlex.quote(password)}"
        elif password_file:
            command += f" -P {shlex.quote(password_file)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        command += f" {shlex.quote(target)} {shlex.quote(service)}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in hydra endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/john", methods=["POST"])
@require_api_key
def john():
    """Execute john with the provided parameters."""
    try:
        params = request.json
        hash_file = params.get("hash_file", "")
        wordlist = params.get("wordlist", "/usr/share/wordlists/rockyou.txt")
        format_type = params.get("format", "")
        additional_args = params.get("additional_args", "")
        
        if not hash_file:
            logger.warning("John called without hash_file parameter")
            return jsonify({
                "error": "Hash file parameter is required"
            }), 400
        
        command = f"john"
        
        if format_type:
            command += f" --format={shlex.quote(format_type)}"
        
        if wordlist:
            command += f" --wordlist={shlex.quote(wordlist)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        command += f" {shlex.quote(hash_file)}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in john endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/wpscan", methods=["POST"])
@require_api_key
def wpscan():
    """Execute wpscan with the provided parameters."""
    try:
        params = request.json
        url = params.get("url", "")
        additional_args = params.get("additional_args", "")
        
        if not url:
            logger.warning("WPScan called without URL parameter")
            return jsonify({
                "error": "URL parameter is required"
            }), 400
        
        command = f"wpscan --url {shlex.quote(url)}"
        
        if additional_args:
            command += f" {additional_args}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in wpscan endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/tools/enum4linux", methods=["POST"])
@require_api_key
def enum4linux():
    """Execute enum4linux with the provided parameters."""
    try:
        params = request.json
        target = params.get("target", "")
        additional_args = params.get("additional_args", "-a")
        
        if not target:
            logger.warning("Enum4linux called without target parameter")
            return jsonify({
                "error": "Target parameter is required"
            }), 400
        
        command = f"enum4linux {additional_args} {shlex.quote(target)}"
        
        result = execute_command(command)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in enum4linux endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


# File Management Endpoints

@app.route("/api/files/list", methods=["GET"])
@require_api_key
def list_files():
    """List files in a directory."""
    try:
        path = request.args.get("path", ".")
        if not os.path.exists(path):
            return jsonify({"error": f"Path not found: {path}"}), 404

        if not os.path.isdir(path):
            return jsonify({"error": f"Path is not a directory: {path}"}), 400

        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)
            items.append({
                "name": item,
                "path": os.path.abspath(full_path),
                "type": "directory" if is_dir else "file",
                "size": os.path.getsize(full_path) if not is_dir else None
            })

        return jsonify({"path": os.path.abspath(path), "items": items})
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/read", methods=["GET"])
@require_api_key
def read_file():
    """Read content of a file."""
    try:
        path = request.args.get("path")
        if not path:
            return jsonify({"error": "Path parameter is required"}), 400

        if not os.path.exists(path):
            return jsonify({"error": f"File not found: {path}"}), 404

        if not os.path.isfile(path):
            return jsonify({"error": f"Path is not a file: {path}"}), 400

        # Check file size before reading to prevent OOM
        if os.path.getsize(path) > 10 * 1024 * 1024: # 10MB limit
            return jsonify({"error": "File too large to read (10MB limit)"}), 400

        with open(path, "r", errors="replace") as f:
            content = f.read()

        return jsonify({
            "path": os.path.abspath(path),
            "content": content
        })
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/write", methods=["POST"])
@require_api_key
def write_file():
    """Write content to a file."""
    try:
        params = request.json
        path = params.get("path")
        content = params.get("content", "")

        if not path:
            return jsonify({"error": "Path parameter is required"}), 400

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        return jsonify({
            "message": f"Successfully wrote to {path}",
            "path": os.path.abspath(path),
            "bytes": len(content)
        })
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/delete", methods=["POST"])
@require_api_key
def delete_file():
    """Delete a file or directory."""
    try:
        params = request.json
        path = params.get("path")

        if not path:
            return jsonify({"error": "Path parameter is required"}), 400

        if not os.path.exists(path):
            return jsonify({"error": f"Path not found: {path}"}), 404

        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        else:
            os.remove(path)

        return jsonify({"message": f"Successfully deleted {path}"})
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Task Management Endpoints

@app.route("/api/tasks", methods=["GET"])
@require_api_key
def list_tasks():
    """List all background tasks."""
    try:
        result = {}
        with task_lock:
            for tid, tinfo in tasks.items():
                executor = tinfo["executor"]
                result[tid] = {
                    "command": tinfo["command"],
                    "status": tinfo["status"],
                    "start_time": tinfo["start_time"],
                    "is_running": executor.is_running,
                    "return_code": executor.return_code
                }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<task_id>", methods=["GET"])
@require_api_key
def get_task_status(task_id):
    """Get status and output of a background task."""
    try:
        with task_lock:
            if task_id not in tasks:
                return jsonify({"error": "Task not found"}), 404

            tinfo = tasks[task_id]
            executor = tinfo["executor"]

            return jsonify({
                "task_id": task_id,
                "command": tinfo["command"],
                "status": tinfo["status"],
                "stdout": executor.stdout_data,
                "stderr": executor.stderr_data,
                "return_code": executor.return_code,
                "is_running": executor.is_running,
                "timed_out": executor.timed_out
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<task_id>/kill", methods=["POST"])
@require_api_key
def kill_task(task_id):
    """Kill a background task."""
    try:
        with task_lock:
            if task_id not in tasks:
                return jsonify({"error": "Task not found"}), 404

            tinfo = tasks[task_id]
            executor = tinfo["executor"]
            executor.kill()
            tinfo["status"] = "killed"

        return jsonify({"message": f"Task {task_id} killed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<task_id>/input", methods=["POST"])
@require_api_key
def send_task_input(task_id):
    """Send input to a background task."""
    try:
        params = request.json
        input_data = params.get("input", "")

        if not input_data:
            return jsonify({"error": "Input data is required"}), 400

        with task_lock:
            if task_id not in tasks:
                return jsonify({"error": "Task not found"}), 404

            tinfo = tasks[task_id]
            executor = tinfo["executor"]
            success = executor.send_input(input_data)

        if success:
            return jsonify({"message": "Input sent successfully"})
        else:
            return jsonify({"error": "Failed to send input or task not running"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/batch", methods=["POST"])
@require_api_key
def batch_commands():
    """Execute multiple commands in parallel in the background."""
    try:
        params = request.json
        commands = params.get("commands", [])
        use_pty = params.get("use_pty", False)

        if not commands:
            return jsonify({"error": "Commands list is required"}), 400

        batch_results = []

        for cmd in commands:
            res = execute_command(cmd, background=True, use_pty=use_pty)
            batch_results.append({
                "command": cmd,
                "task_id": res.get("task_id")
            })

        return jsonify({
            "message": f"Started {len(commands)} commands in the background",
            "tasks": batch_results
        })
    except Exception as e:
        logger.error(f"Error in batch execution: {str(e)}")
        return jsonify({"error": str(e)}), 500

# System Information Endpoints

@app.route("/api/system/info", methods=["GET"])
@require_api_key
def get_system_info():
    """Get system and network information."""
    try:
        import platform
        import socket
        import getpass

        # Get network interfaces
        interfaces = []
        try:
            import psutil
            addrs = psutil.net_if_addrs()
            for name, info in addrs.items():
                iface_info = {"name": name, "addresses": []}
                for addr in info:
                    iface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                interfaces.append(iface_info)
        except ImportError:
            # Fallback to ip addr command if psutil not available
            result = execute_command("ip addr")
            interfaces = result.get("stdout", "ip addr command failed")

        info = {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "node": platform.node(),
            "python_version": platform.python_version(),
            "interfaces": interfaces,
            "current_user": getpass.getuser()
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    # Check if essential tools are installed
    essential_tools = ["nmap", "gobuster", "dirb", "nikto"]
    tools_status = {}
    
    for tool in essential_tools:
        try:
            result = execute_command(f"which {tool}")
            tools_status[tool] = result["success"]
        except:
            tools_status[tool] = False
    
    all_essential_tools_available = all(tools_status.values())
    
    return jsonify({
        "status": "healthy",
        "message": "Kali Linux Tools API Server is running",
        "tools_status": tools_status,
        "all_essential_tools_available": all_essential_tools_available
    })

@app.route("/mcp/capabilities", methods=["GET"])
def get_capabilities():
    # Return tool capabilities similar to our existing MCP server
    pass

@app.route("/mcp/tools/kali_tools/<tool_name>", methods=["POST"])
@require_api_key
def execute_tool(tool_name):
    # Direct tool execution without going through the API server
    pass

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Kali Linux API Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port for the API server (default: {API_PORT})")
    parser.add_argument("--api-key", type=str, help="API Key for authentication (if not set, a random one will be generated)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Set configuration from command line arguments
    if args.debug:
        DEBUG_MODE = True
        os.environ["DEBUG_MODE"] = "1"
        logger.setLevel(logging.DEBUG)
    
    if args.port != API_PORT:
        API_PORT = args.port

    if args.api_key:
        API_KEY = args.api_key
    elif not API_KEY:
        API_KEY = secrets.token_hex(16)
        logger.info(f"Generated random API Key: {API_KEY}")
    
    logger.info(f"Starting Kali Linux Tools API Server on port {API_PORT}")
    if API_KEY:
        logger.info(f"API Key authentication is ENABLED. Key: {API_KEY}")
    else:
        logger.warning("API Key authentication is DISABLED")

    app.run(host="0.0.0.0", port=API_PORT, debug=DEBUG_MODE)
