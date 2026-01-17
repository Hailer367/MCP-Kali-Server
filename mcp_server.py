#!/usr/bin/env python3

import sys
import os
import argparse
import logging
from typing import Dict, Any, Optional
import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

DEFAULT_KALI_SERVER = "http://localhost:5000"
DEFAULT_REQUEST_TIMEOUT = 300

class KaliToolsClient:
    def __init__(self, server_url, api_key=None, timeout=DEFAULT_REQUEST_TIMEOUT):
        self.server_url = server_url.rstrip("/")
        self.headers = {"X-API-Key": api_key} if api_key else {}
        self.timeout = timeout
        
    def safe_get(self, endpoint, params=None):
        try:
            res = requests.get(f"{self.server_url}/{endpoint}", params=params, headers=self.headers, timeout=self.timeout)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def safe_post(self, endpoint, json_data):
        try:
            res = requests.post(f"{self.server_url}/{endpoint}", json=json_data, headers=self.headers, timeout=self.timeout)
            return res.json()
        except Exception as e: return {"error": str(e)}

def setup_mcp_server(kali_client):
    mcp = FastMCP("kali-mcp")
    
    @mcp.tool()
    def nmap_scan(target: str, scan_type: str = "-sCV", ports: str = "", additional_args: str = ""):
        return kali_client.safe_post("api/tools/nmap", {"target": target, "scan_type": scan_type, "ports": ports, "additional_args": additional_args})

    @mcp.tool()
    def nuclei_scan(target: str, templates: str = "", additional_args: str = ""):
        return kali_client.safe_post("api/tools/nuclei", {"target": target, "templates": templates, "additional_args": additional_args})

    @mcp.tool()
    def browser_action(action: str, url: str = "", selector: str = "", data: str = "", wait_for: str = ""):
        return kali_client.safe_post("api/browser/action", {"action": action, "url": url, "selector": selector, "data": data, "wait_for": wait_for})

    @mcp.tool()
    def git_bind_repository(repo_url: str):
        return kali_client.safe_post("api/git/bind", {"repo_url": repo_url})

    @mcp.tool()
    def git_store_data(category: str, filename: str, content: str):
        return kali_client.safe_post("api/git/store", {"category": category, "filename": filename, "content": content})

    @mcp.tool()
    def whitebox_scan(path: str = "."):
        return kali_client.safe_post("api/tools/whitebox/scan", {"path": path})

    @mcp.tool()
    def db_init_setup():
        return kali_client.safe_post("api/db/init", {})

    @mcp.tool()
    def execute_command(command: str, background: bool = False, use_pty: bool = False):
        return kali_client.safe_post("api/command", {"command": command, "background": background, "use_pty": use_pty})

    @mcp.tool()
    def send_task_input(task_id: str, input_data: str):
        return kali_client.safe_post(f"api/tasks/{task_id}/input", {"input": input_data})

    @mcp.tool()
    def list_files(path: str = "."): return kali_client.safe_get("api/files/list", {"path": path})
    @mcp.tool()
    def read_file(path: str): return kali_client.safe_get("api/files/read", {"path": path})
    @mcp.tool()
    def write_file(path: str, content: str): return kali_client.safe_post("api/files/write", {"path": path, "content": content})

    return mcp

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default=DEFAULT_KALI_SERVER)
    parser.add_argument("--api-key", default=os.environ.get("KALI_API_KEY"))
    args = parser.parse_args()
    kali_client = KaliToolsClient(args.server, args.api_key)
    mcp = setup_mcp_server(kali_client)
    mcp.run()

if __name__ == "__main__":
    main()
