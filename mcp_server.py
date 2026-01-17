#!/usr/bin/env python3
"""
MCP Kali Server - MCP Client Interface
Enhanced with 150+ Security Tools and 12+ AI Agents

Version: 2.0.0
Provides MCP tools for AI agents to interact with Kali Linux security tools
"""

import sys
import os
import argparse
import logging
import time
from typing import Dict, Any, Optional
import requests
from mcp.server.fastmcp import FastMCP

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class Colors:
    """Terminal colors for enhanced logging"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    HACKER_RED = '\033[38;5;196m'
    CRIMSON = '\033[38;5;160m'
    SUCCESS = '\033[38;5;46m'
    WARNING = '\033[38;5;208m'
    ERROR = '\033[38;5;196m'

class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    COLORS = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.HACKER_RED
    }
    
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥'
    }
    
    def format(self, record):
        emoji = self.EMOJIS.get(record.levelname, '📝')
        color = self.COLORS.get(record.levelname, Colors.WHITE)
        record.msg = f"{color}{emoji} {record.msg}{Colors.RESET}"
        return super().format(record)

logging.basicConfig(
    level=logging.INFO,
    format="[🔥 MCP-Kali] %(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(ColoredFormatter(
        "[🔥 MCP-Kali] %(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_KALI_SERVER = "http://localhost:5000"
DEFAULT_REQUEST_TIMEOUT = 300
MAX_RETRIES = 3

# ============================================================================
# KALI TOOLS CLIENT
# ============================================================================

class KaliToolsClient:
    """Client for communicating with MCP Kali Server"""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None, timeout: int = DEFAULT_REQUEST_TIMEOUT):
        self.server_url = server_url.rstrip("/")
        self.headers = {"X-API-Key": api_key} if api_key else {}
        self.timeout = timeout
        self.session = requests.Session()
        
        # Test connection
        connected = False
        for i in range(MAX_RETRIES):
            try:
                logger.info(f"🔗 Connecting to MCP Kali Server at {server_url} (attempt {i+1}/{MAX_RETRIES})")
                response = self.session.get(f"{self.server_url}/health", timeout=5)
                response.raise_for_status()
                health = response.json()
                connected = True
                logger.info(f"🎯 Connected to MCP Kali Server v{health.get('version', 'unknown')}")
                logger.info(f"📊 Active tasks: {health.get('active_tasks', 0)}")
                break
            except Exception as e:
                logger.warning(f"⚠️ Connection attempt {i+1} failed: {e}")
                time.sleep(2)
        
        if not connected:
            logger.error(f"❌ Failed to connect to MCP Kali Server at {server_url}")
    
    def safe_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Safe GET request"""
        try:
            response = self.session.get(
                f"{self.server_url}/{endpoint}",
                params=params or {},
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def safe_post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Safe POST request"""
        try:
            response = self.session.post(
                f"{self.server_url}/{endpoint}",
                json=json_data,
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

def setup_mcp_server(kali_client: KaliToolsClient) -> FastMCP:
    """Setup MCP server with all tools"""
    mcp = FastMCP("mcp-kali-server")
    
    # ========================================================================
    # CORE TOOLS
    # ========================================================================
    
    @mcp.tool()
    def execute_command(command: str, background: bool = False, use_pty: bool = False) -> Dict[str, Any]:
        """
        Execute any shell command on the Kali system.
        
        Args:
            command: Shell command to execute
            background: Run in background (returns task_id)
            use_pty: Use pseudo-terminal for interactive commands
        
        Returns:
            Command output or task_id if background
        """
        logger.info(f"⚡ Executing: {command[:50]}...")
        return kali_client.safe_post("api/command", {
            "command": command,
            "background": background,
            "use_pty": use_pty
        })
    
    @mcp.tool()
    def get_system_info() -> Dict[str, Any]:
        """Get system information and performance metrics."""
        return kali_client.safe_get("api/system/info")
    
    @mcp.tool()
    def get_telemetry() -> Dict[str, Any]:
        """Get server telemetry including active tasks and agents."""
        return kali_client.safe_get("api/telemetry")
    
    # ========================================================================
    # INTELLIGENCE & AGENTS
    # ========================================================================
    
    @mcp.tool()
    def analyze_target(target: str) -> Dict[str, Any]:
        """
        Analyze a target and create a comprehensive profile.
        Uses AI decision engine to determine target type, technologies, and risk.
        
        Args:
            target: URL, IP address, domain, or file path to analyze
        
        Returns:
            Target profile with risk assessment and recommended tools
        """
        logger.info(f"🎯 Analyzing target: {target}")
        return kali_client.safe_post("api/intelligence/analyze-target", {"target": target})
    
    @mcp.tool()
    def select_optimal_tools(target: str, objective: str = "comprehensive") -> Dict[str, Any]:
        """
        Select optimal security tools for a target.
        
        Args:
            target: Target to test
            objective: Testing objective (quick, comprehensive, stealth)
        
        Returns:
            List of recommended tools and rationale
        """
        logger.info(f"🔧 Selecting tools for {target} ({objective})")
        return kali_client.safe_post("api/intelligence/select-tools", {
            "target": target,
            "objective": objective
        })
    
    @mcp.tool()
    def get_attack_pattern(pattern: str = "web_reconnaissance") -> Dict[str, Any]:
        """
        Get predefined attack pattern with tool sequence.
        
        Args:
            pattern: Pattern name (web_reconnaissance, api_testing, network_discovery, 
                    bug_bounty_recon, whitebox_analysis)
        
        Returns:
            Attack pattern with ordered tool steps
        """
        return kali_client.safe_post("api/intelligence/attack-pattern", {"pattern": pattern})
    
    @mcp.tool()
    def bugbounty_recon(target: str) -> Dict[str, Any]:
        """
        Run bug bounty reconnaissance workflow on a target.
        
        Args:
            target: Target domain or URL
        
        Returns:
            Reconnaissance results with recommended next steps
        """
        logger.info(f"🐛 Bug bounty recon: {target}")
        return kali_client.safe_post("api/agents/bugbounty/recon", {"target": target})
    
    @mcp.tool()
    def bugbounty_analyze_scope(domains: list) -> Dict[str, Any]:
        """
        Analyze multiple domains for bug bounty scope assessment.
        
        Args:
            domains: List of domains to analyze
        
        Returns:
            Scope analysis with high-value targets
        """
        return kali_client.safe_post("api/agents/bugbounty/scope", {"domains": domains})
    
    @mcp.tool()
    def ctf_analyze_challenge(challenge_type: str, target: str = "") -> Dict[str, Any]:
        """
        Analyze a CTF challenge and get recommended approach.
        
        Args:
            challenge_type: Type (web, pwn, crypto, forensics, reverse, misc)
            target: Challenge target or file
        
        Returns:
            Recommended tools and approach
        """
        logger.info(f"🏆 CTF analysis: {challenge_type}")
        return kali_client.safe_post("api/agents/ctf/analyze", {
            "type": challenge_type,
            "target": target
        })
    
    @mcp.tool()
    def cve_search(product: str, version: str = "") -> Dict[str, Any]:
        """
        Search for CVEs affecting a product.
        
        Args:
            product: Product name
            version: Product version (optional)
        
        Returns:
            CVE search guidance
        """
        logger.info(f"🔍 CVE search: {product} {version}")
        return kali_client.safe_post("api/agents/cve/search", {
            "product": product,
            "version": version
        })
    
    @mcp.tool()
    def cve_exploit_info(cve_id: str) -> Dict[str, Any]:
        """
        Get exploit information for a CVE.
        
        Args:
            cve_id: CVE identifier (e.g., CVE-2021-44228)
        
        Returns:
            Exploit search guidance
        """
        return kali_client.safe_post("api/agents/cve/exploit-info", {"cve_id": cve_id})
    
    @mcp.tool()
    def generate_exploit_payload(vuln_type: str, target_os: str = "linux") -> Dict[str, Any]:
        """
        Generate exploit payloads for testing.
        
        Args:
            vuln_type: Vulnerability type (sqli, xss, cmd_injection, lfi, ssti)
            target_os: Target OS (linux, windows)
        
        Returns:
            Payload templates
        """
        logger.info(f"🎯 Generating {vuln_type} payloads")
        return kali_client.safe_post("api/agents/exploit/generate", {
            "type": vuln_type,
            "os": target_os
        })
    
    @mcp.tool()
    def build_attack_chain(vulnerabilities: list) -> Dict[str, Any]:
        """
        Build attack chain from discovered vulnerabilities.
        
        Args:
            vulnerabilities: List of vulnerability dicts with name, severity, type
        
        Returns:
            Attack chain with exploitation path
        """
        return kali_client.safe_post("api/agents/correlator/chain", {
            "vulnerabilities": vulnerabilities
        })
    
    @mcp.tool()
    def detect_technology(target: str, headers: dict = None, content: str = "") -> Dict[str, Any]:
        """
        Detect technology stack of a target.
        
        Args:
            target: Target URL
            headers: Response headers (optional)
            content: Page content (optional)
        
        Returns:
            Detected technologies
        """
        return kali_client.safe_post("api/agents/tech/detect", {
            "target": target,
            "headers": headers or {},
            "content": content
        })
    
    # ========================================================================
    # NETWORK SCANNING TOOLS
    # ========================================================================
    
    @mcp.tool()
    def nmap_scan(target: str, scan_type: str = "-sCV", ports: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Nmap port scan and service detection.
        
        Args:
            target: Target IP or hostname
            scan_type: Scan type (-sS, -sV, -sCV, -A, etc.)
            ports: Ports to scan (e.g., "22,80,443" or "1-1000")
            additional_args: Extra Nmap arguments
        
        Returns:
            Scan results
        """
        logger.info(f"🔍 Nmap scan: {target}")
        return kali_client.safe_post("api/tools/nmap", {
            "target": target,
            "scan_type": scan_type,
            "ports": ports,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def rustscan(target: str, ports: str = "", ulimit: int = 5000, scripts: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute ultra-fast Rustscan port scanner.
        
        Args:
            target: Target IP or hostname
            ports: Specific ports to scan
            ulimit: File descriptor limit
            scripts: Run Nmap scripts on found ports
            additional_args: Extra arguments
        
        Returns:
            Scan results
        """
        logger.info(f"⚡ Rustscan: {target}")
        return kali_client.safe_post("api/tools/rustscan", {
            "target": target,
            "ports": ports,
            "ulimit": ulimit,
            "scripts": scripts,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def masscan(target: str, ports: str = "1-65535", rate: int = 1000, banners: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute high-speed Masscan port scanner.
        
        Args:
            target: Target IP or CIDR range
            ports: Port range to scan
            rate: Packets per second
            banners: Enable banner grabbing
            additional_args: Extra arguments
        
        Returns:
            Scan results
        """
        logger.info(f"🚀 Masscan: {target}")
        return kali_client.safe_post("api/tools/masscan", {
            "target": target,
            "ports": ports,
            "rate": rate,
            "banners": banners,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def autorecon(target: str, output_dir: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute comprehensive AutoRecon scan (runs in background).
        
        Args:
            target: Target IP or hostname
            output_dir: Output directory
            additional_args: Extra arguments
        
        Returns:
            Task ID for background task
        """
        logger.info(f"🤖 AutoRecon: {target}")
        return kali_client.safe_post("api/tools/autorecon", {
            "target": target,
            "output_dir": output_dir,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # WEB APPLICATION TOOLS
    # ========================================================================
    
    @mcp.tool()
    def ffuf_scan(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", match_codes: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute FFuf web fuzzer.
        
        Args:
            url: Target URL with FUZZ keyword
            wordlist: Wordlist path
            match_codes: HTTP status codes to match
            additional_args: Extra arguments
        
        Returns:
            Fuzzing results
        """
        logger.info(f"🔍 FFuf: {url}")
        return kali_client.safe_post("api/tools/ffuf", {
            "url": url,
            "wordlist": wordlist,
            "match_codes": match_codes,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def gobuster_scan(url: str, mode: str = "dir", wordlist: str = "/usr/share/wordlists/dirb/common.txt", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Gobuster directory/DNS enumeration.
        
        Args:
            url: Target URL
            mode: Scan mode (dir, dns, vhost, fuzz)
            wordlist: Wordlist path
            additional_args: Extra arguments
        
        Returns:
            Enumeration results
        """
        logger.info(f"📁 Gobuster {mode}: {url}")
        return kali_client.safe_post("api/tools/gobuster", {
            "url": url,
            "mode": mode,
            "wordlist": wordlist,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def feroxbuster_scan(url: str, wordlist: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Feroxbuster recursive content discovery.
        
        Args:
            url: Target URL
            wordlist: Wordlist path
            additional_args: Extra arguments
        
        Returns:
            Discovery results
        """
        logger.info(f"🦀 Feroxbuster: {url}")
        return kali_client.safe_post("api/tools/feroxbuster", {
            "url": url,
            "wordlist": wordlist,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def dirsearch_scan(url: str, extensions: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Dirsearch directory scanner.
        
        Args:
            url: Target URL
            extensions: File extensions to search
            additional_args: Extra arguments
        
        Returns:
            Scan results
        """
        logger.info(f"📂 Dirsearch: {url}")
        return kali_client.safe_post("api/tools/dirsearch", {
            "url": url,
            "extensions": extensions,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def nuclei_scan(target: str, templates: str = "", severity: str = "", tags: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Nuclei vulnerability scanner.
        
        Args:
            target: Target URL
            templates: Template path or name
            severity: Filter by severity (critical,high,medium,low,info)
            tags: Filter by tags (cve,rce,lfi,xss,sqli)
            additional_args: Extra arguments
        
        Returns:
            Vulnerability findings
        """
        logger.info(f"🔬 Nuclei: {target}")
        return kali_client.safe_post("api/tools/nuclei", {
            "target": target,
            "templates": templates,
            "severity": severity,
            "tags": tags,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def nikto_scan(target: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Nikto web vulnerability scanner.
        
        Args:
            target: Target URL
            additional_args: Extra arguments
        
        Returns:
            Vulnerability findings
        """
        logger.info(f"🕷️ Nikto: {target}")
        return kali_client.safe_post("api/tools/nikto", {
            "target": target,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def sqlmap_scan(url: str, data: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute SQLMap SQL injection tester.
        
        Args:
            url: Target URL with parameter
            data: POST data
            additional_args: Extra arguments
        
        Returns:
            SQL injection test results
        """
        logger.info(f"💉 SQLMap: {url}")
        return kali_client.safe_post("api/tools/sqlmap", {
            "url": url,
            "data": data,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def wpscan(url: str, api_token: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute WPScan WordPress security scanner.
        
        Args:
            url: WordPress site URL
            api_token: WPScan API token for vulnerability data
            additional_args: Extra arguments
        
        Returns:
            WordPress vulnerabilities
        """
        logger.info(f"📰 WPScan: {url}")
        return kali_client.safe_post("api/tools/wpscan", {
            "url": url,
            "api_token": api_token,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def dalfox_scan(url: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Dalfox XSS vulnerability scanner.
        
        Args:
            url: Target URL with parameter
            additional_args: Extra arguments
        
        Returns:
            XSS vulnerability findings
        """
        logger.info(f"🦊 Dalfox: {url}")
        return kali_client.safe_post("api/tools/dalfox", {
            "url": url,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def httpx_probe(target: str, tech_detect: bool = False, status_code: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute httpx HTTP prober.
        
        Args:
            target: Target URL or domain
            tech_detect: Enable technology detection
            status_code: Show status codes
            additional_args: Extra arguments
        
        Returns:
            Probe results
        """
        logger.info(f"🌐 httpx: {target}")
        return kali_client.safe_post("api/tools/httpx", {
            "target": target,
            "tech_detect": tech_detect,
            "status_code": status_code,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def katana_crawl(url: str, depth: int = 2, js_crawl: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Katana web crawler.
        
        Args:
            url: Target URL
            depth: Crawl depth
            js_crawl: Enable JavaScript crawling
            additional_args: Extra arguments
        
        Returns:
            Crawl results
        """
        logger.info(f"🗡️ Katana: {url}")
        return kali_client.safe_post("api/tools/katana", {
            "url": url,
            "depth": depth,
            "js_crawl": js_crawl,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def arjun_param_discovery(url: str, method: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Arjun HTTP parameter discovery.
        
        Args:
            url: Target URL
            method: HTTP method (GET, POST)
            additional_args: Extra arguments
        
        Returns:
            Discovered parameters
        """
        logger.info(f"🔎 Arjun: {url}")
        return kali_client.safe_post("api/tools/arjun", {
            "url": url,
            "method": method,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def paramspider(domain: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute ParamSpider parameter mining.
        
        Args:
            domain: Target domain
            additional_args: Extra arguments
        
        Returns:
            Mined parameters
        """
        logger.info(f"🕷️ ParamSpider: {domain}")
        return kali_client.safe_post("api/tools/paramspider", {
            "domain": domain,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # SUBDOMAIN & OSINT TOOLS
    # ========================================================================
    
    @mcp.tool()
    def amass_enum(domain: str, mode: str = "enum", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Amass subdomain enumeration.
        
        Args:
            domain: Target domain
            mode: Amass mode (enum, intel, viz)
            additional_args: Extra arguments
        
        Returns:
            Subdomain enumeration results
        """
        logger.info(f"🌐 Amass: {domain}")
        return kali_client.safe_post("api/tools/amass", {
            "domain": domain,
            "mode": mode,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def subfinder_scan(domain: str, silent: bool = True, all_sources: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Subfinder passive subdomain discovery.
        
        Args:
            domain: Target domain
            silent: Silent mode
            all_sources: Use all sources
            additional_args: Extra arguments
        
        Returns:
            Discovered subdomains
        """
        logger.info(f"🔍 Subfinder: {domain}")
        return kali_client.safe_post("api/tools/subfinder", {
            "domain": domain,
            "silent": silent,
            "all_sources": all_sources,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def theharvester(domain: str, source: str = "all", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute theHarvester email/subdomain harvester.
        
        Args:
            domain: Target domain
            source: Data source (all, google, bing, etc.)
            additional_args: Extra arguments
        
        Returns:
            Harvested data
        """
        logger.info(f"🌾 theHarvester: {domain}")
        return kali_client.safe_post("api/tools/theharvester", {
            "domain": domain,
            "source": source,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # SMB/NETWORK ENUMERATION TOOLS
    # ========================================================================
    
    @mcp.tool()
    def netexec_scan(target: str, protocol: str = "smb", username: str = "", password: str = "", hash_value: str = "", module: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute NetExec (nxc) network enumeration.
        
        Args:
            target: Target IP or range
            protocol: Protocol (smb, ssh, winrm, mssql, ldap)
            username: Username for auth
            password: Password for auth
            hash_value: NTLM hash for pass-the-hash
            module: NetExec module to run
            additional_args: Extra arguments
        
        Returns:
            Enumeration results
        """
        logger.info(f"🔧 NetExec {protocol}: {target}")
        return kali_client.safe_post("api/tools/nxc", {
            "target": target,
            "protocol": protocol,
            "username": username,
            "password": password,
            "hash": hash_value,
            "module": module,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def enum4linux_scan(target: str, additional_args: str = "-a") -> Dict[str, Any]:
        """
        Execute Enum4linux SMB enumeration.
        
        Args:
            target: Target IP
            additional_args: Extra arguments (default: -a for all)
        
        Returns:
            SMB enumeration results
        """
        logger.info(f"🔍 Enum4linux: {target}")
        return kali_client.safe_post("api/tools/enum4linux", {
            "target": target,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def enum4linux_ng_scan(target: str, shares: bool = True, users: bool = True, groups: bool = True, username: str = "", password: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Enum4linux-ng enhanced SMB enumeration.
        
        Args:
            target: Target IP
            shares: Enumerate shares
            users: Enumerate users
            groups: Enumerate groups
            username: Username for auth
            password: Password for auth
            additional_args: Extra arguments
        
        Returns:
            SMB enumeration results
        """
        logger.info(f"🔍 Enum4linux-ng: {target}")
        return kali_client.safe_post("api/tools/enum4linux-ng", {
            "target": target,
            "shares": shares,
            "users": users,
            "groups": groups,
            "username": username,
            "password": password,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def smbmap_scan(target: str, username: str = "", password: str = "", domain: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute SMBMap share enumeration.
        
        Args:
            target: Target IP
            username: Username for auth
            password: Password for auth
            domain: Domain for auth
            additional_args: Extra arguments
        
        Returns:
            SMB share enumeration results
        """
        logger.info(f"📁 SMBMap: {target}")
        return kali_client.safe_post("api/tools/smbmap", {
            "target": target,
            "username": username,
            "password": password,
            "domain": domain,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # PASSWORD CRACKING TOOLS
    # ========================================================================
    
    @mcp.tool()
    def hydra_attack(target: str, service: str, username: str = "", username_file: str = "", password: str = "", password_file: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Hydra password brute forcer.
        
        Args:
            target: Target IP or hostname
            service: Service to attack (ssh, ftp, http-get, etc.)
            username: Single username
            username_file: File with usernames
            password: Single password
            password_file: File with passwords
            additional_args: Extra arguments
        
        Returns:
            Cracked credentials
        """
        logger.info(f"🔑 Hydra: {target} {service}")
        return kali_client.safe_post("api/tools/hydra", {
            "target": target,
            "service": service,
            "username": username,
            "username_file": username_file,
            "password": password,
            "password_file": password_file,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def john_crack(hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt", format_type: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute John the Ripper password cracker.
        
        Args:
            hash_file: File containing hashes
            wordlist: Wordlist file
            format_type: Hash format
            additional_args: Extra arguments
        
        Returns:
            Cracked passwords
        """
        logger.info(f"🔐 John: {hash_file}")
        return kali_client.safe_post("api/tools/john", {
            "hash_file": hash_file,
            "wordlist": wordlist,
            "format": format_type,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def hashcat_crack(hash_file: str, hash_type: str, wordlist: str = "/usr/share/wordlists/rockyou.txt", attack_mode: str = "0", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Hashcat GPU password cracker.
        
        Args:
            hash_file: File containing hashes
            hash_type: Hashcat hash type number
            wordlist: Wordlist file
            attack_mode: Attack mode (0=dict, 1=combo, 3=mask)
            additional_args: Extra arguments
        
        Returns:
            Cracked passwords
        """
        logger.info(f"🔥 Hashcat: {hash_file}")
        return kali_client.safe_post("api/tools/hashcat", {
            "hash_file": hash_file,
            "hash_type": hash_type,
            "wordlist": wordlist,
            "attack_mode": attack_mode,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # PAYLOAD GENERATION
    # ========================================================================
    
    @mcp.tool()
    def msfvenom_generate(payload: str, options: dict = None, format_type: str = "elf", output: str = "") -> Dict[str, Any]:
        """
        Generate payloads with MSFVenom.
        
        Args:
            payload: Payload name (e.g., linux/x64/shell_reverse_tcp)
            options: Payload options (LHOST, LPORT, etc.)
            format_type: Output format (elf, exe, py, raw, etc.)
            output: Output file path
        
        Returns:
            Payload generation result
        """
        logger.info(f"🎯 MSFVenom: {payload}")
        return kali_client.safe_post("api/tools/msfvenom", {
            "payload": payload,
            "options": options or {},
            "format": format_type,
            "output": output
        })
    
    # ========================================================================
    # WHITE BOX / SAST TOOLS
    # ========================================================================
    
    @mcp.tool()
    def semgrep_scan(path: str = ".", config: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Semgrep SAST scanner.
        
        Args:
            path: Path to scan
            config: Semgrep config/rules
            additional_args: Extra arguments
        
        Returns:
            Security findings
        """
        logger.info(f"🔬 Semgrep: {path}")
        return kali_client.safe_post("api/tools/semgrep", {
            "path": path,
            "config": config,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def bandit_scan(path: str = ".", severity: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Bandit Python security scanner.
        
        Args:
            path: Path to scan
            severity: Minimum severity level
            additional_args: Extra arguments
        
        Returns:
            Security findings
        """
        logger.info(f"🐍 Bandit: {path}")
        return kali_client.safe_post("api/tools/bandit", {
            "path": path,
            "severity": severity,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def safety_check(requirements_file: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Safety dependency vulnerability scanner.
        
        Args:
            requirements_file: Path to requirements.txt
            additional_args: Extra arguments
        
        Returns:
            Vulnerable dependencies
        """
        logger.info(f"🛡️ Safety check")
        return kali_client.safe_post("api/tools/safety", {
            "requirements_file": requirements_file,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def trufflehog_scan(target: str = ".", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute TruffleHog secret scanner.
        
        Args:
            target: Path or repo to scan
            additional_args: Extra arguments
        
        Returns:
            Found secrets
        """
        logger.info(f"🐷 TruffleHog: {target}")
        return kali_client.safe_post("api/tools/trufflehog", {
            "target": target,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def gitleaks_scan(path: str = ".", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Gitleaks secret scanner.
        
        Args:
            path: Path to scan
            additional_args: Extra arguments
        
        Returns:
            Found secrets
        """
        logger.info(f"🔐 Gitleaks: {path}")
        return kali_client.safe_post("api/tools/gitleaks", {
            "path": path,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def whitebox_comprehensive_scan(path: str = ".") -> Dict[str, Any]:
        """
        Execute comprehensive white box security scan.
        Checks for SQLi, XSS, command injection, path traversal, hardcoded secrets, and more.
        
        Args:
            path: Path to scan
        
        Returns:
            Comprehensive security findings
        """
        logger.info(f"🔍 White box scan: {path}")
        return kali_client.safe_post("api/tools/whitebox/scan", {"path": path})
    
    @mcp.tool()
    def dependency_check(path: str = ".", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute OWASP Dependency Check.
        
        Args:
            path: Path to scan
            additional_args: Extra arguments
        
        Returns:
            Dependency vulnerabilities
        """
        logger.info(f"📦 Dependency Check: {path}")
        return kali_client.safe_post("api/tools/whitebox/dependency-check", {
            "path": path,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # CLOUD SECURITY TOOLS
    # ========================================================================
    
    @mcp.tool()
    def prowler_scan(provider: str = "aws", profile: str = "", region: str = "", output_format: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Prowler cloud security scanner.
        
        Args:
            provider: Cloud provider (aws, azure, gcp)
            profile: AWS profile
            region: AWS region
            output_format: Output format
            additional_args: Extra arguments
        
        Returns:
            Cloud security findings
        """
        logger.info(f"☁️ Prowler: {provider}")
        return kali_client.safe_post("api/tools/prowler", {
            "provider": provider,
            "profile": profile,
            "region": region,
            "output_format": output_format,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def trivy_scan(target: str, scan_type: str = "image", severity: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Trivy container/filesystem scanner.
        
        Args:
            target: Image name or path
            scan_type: Scan type (image, fs, repo, config)
            severity: Severity filter
            additional_args: Extra arguments
        
        Returns:
            Vulnerability findings
        """
        logger.info(f"🔍 Trivy: {target}")
        return kali_client.safe_post("api/tools/trivy", {
            "target": target,
            "scan_type": scan_type,
            "severity": severity,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def kube_hunter_scan(remote: str = "", cidr: str = "", active: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Execute kube-hunter Kubernetes penetration tester.
        
        Args:
            remote: Remote target
            cidr: CIDR range to scan
            active: Enable active hunting
            additional_args: Extra arguments
        
        Returns:
            Kubernetes security findings
        """
        logger.info(f"🎯 kube-hunter")
        return kali_client.safe_post("api/tools/kube-hunter", {
            "remote": remote,
            "cidr": cidr,
            "active": active,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def kube_bench_check(targets: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute kube-bench CIS benchmark checker.
        
        Args:
            targets: Targets to check (master, node, etcd)
            additional_args: Extra arguments
        
        Returns:
            CIS benchmark results
        """
        logger.info(f"📋 kube-bench")
        return kali_client.safe_post("api/tools/kube-bench", {
            "targets": targets,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def checkov_scan(directory: str = ".", framework: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Execute Checkov IaC security scanner.
        
        Args:
            directory: Directory to scan
            framework: Framework (terraform, cloudformation, kubernetes)
            additional_args: Extra arguments
        
        Returns:
            IaC security findings
        """
        logger.info(f"📝 Checkov: {directory}")
        return kali_client.safe_post("api/tools/checkov", {
            "directory": directory,
            "framework": framework,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # BINARY ANALYSIS TOOLS
    # ========================================================================
    
    @mcp.tool()
    def checksec_analyze(binary: str) -> Dict[str, Any]:
        """
        Analyze binary security properties with checksec.
        
        Args:
            binary: Path to binary file
        
        Returns:
            Security properties (NX, PIE, RELRO, etc.)
        """
        logger.info(f"🔒 Checksec: {binary}")
        return kali_client.safe_post("api/tools/checksec", {"binary": binary})
    
    @mcp.tool()
    def strings_extract(binary: str, min_length: int = 4, additional_args: str = "") -> Dict[str, Any]:
        """
        Extract strings from binary.
        
        Args:
            binary: Path to binary file
            min_length: Minimum string length
            additional_args: Extra arguments
        
        Returns:
            Extracted strings
        """
        logger.info(f"📝 Strings: {binary}")
        return kali_client.safe_post("api/tools/strings", {
            "binary": binary,
            "min_length": min_length,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def binwalk_analyze(binary: str, extract: bool = False, additional_args: str = "") -> Dict[str, Any]:
        """
        Analyze binary with Binwalk.
        
        Args:
            binary: Path to binary file
            extract: Extract embedded files
            additional_args: Extra arguments
        
        Returns:
            Analysis results
        """
        logger.info(f"🔍 Binwalk: {binary}")
        return kali_client.safe_post("api/tools/binwalk", {
            "binary": binary,
            "extract": extract,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def radare2_analyze(binary: str, commands: str = "aaa;afl") -> Dict[str, Any]:
        """
        Analyze binary with Radare2.
        
        Args:
            binary: Path to binary file
            commands: R2 commands separated by semicolons
        
        Returns:
            Analysis output
        """
        logger.info(f"🔧 Radare2: {binary}")
        return kali_client.safe_post("api/tools/radare2", {
            "binary": binary,
            "commands": commands
        })
    
    @mcp.tool()
    def ropper_gadgets(binary: str, search: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Find ROP gadgets with Ropper.
        
        Args:
            binary: Path to binary file
            search: Search pattern
            additional_args: Extra arguments
        
        Returns:
            ROP gadgets
        """
        logger.info(f"🔗 Ropper: {binary}")
        return kali_client.safe_post("api/tools/ropper", {
            "binary": binary,
            "search": search,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def one_gadget_find(libc: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Find one-shot gadgets in libc.
        
        Args:
            libc: Path to libc
            additional_args: Extra arguments
        
        Returns:
            One-gadget offsets
        """
        logger.info(f"🎯 one_gadget: {libc}")
        return kali_client.safe_post("api/tools/one-gadget", {
            "libc": libc,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # FORENSICS TOOLS
    # ========================================================================
    
    @mcp.tool()
    def volatility_analyze(memory_dump: str, plugin: str = "pslist", additional_args: str = "") -> Dict[str, Any]:
        """
        Analyze memory dump with Volatility.
        
        Args:
            memory_dump: Path to memory dump
            plugin: Volatility plugin
            additional_args: Extra arguments
        
        Returns:
            Analysis results
        """
        logger.info(f"🧠 Volatility: {memory_dump}")
        return kali_client.safe_post("api/tools/volatility", {
            "memory_dump": memory_dump,
            "plugin": plugin,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def foremost_carve(image: str, output_dir: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Carve files from image with Foremost.
        
        Args:
            image: Path to image file
            output_dir: Output directory
            additional_args: Extra arguments
        
        Returns:
            Carved files
        """
        logger.info(f"🔪 Foremost: {image}")
        return kali_client.safe_post("api/tools/foremost", {
            "image": image,
            "output_dir": output_dir,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def exiftool_extract(file_path: str, additional_args: str = "") -> Dict[str, Any]:
        """
        Extract metadata with ExifTool.
        
        Args:
            file_path: Path to file
            additional_args: Extra arguments
        
        Returns:
            Metadata
        """
        logger.info(f"📷 ExifTool: {file_path}")
        return kali_client.safe_post("api/tools/exiftool", {
            "file": file_path,
            "additional_args": additional_args
        })
    
    @mcp.tool()
    def steghide_extract(file_path: str, action: str = "info", password: str = "", additional_args: str = "") -> Dict[str, Any]:
        """
        Extract hidden data with Steghide.
        
        Args:
            file_path: Path to image file
            action: Action (info, extract)
            password: Password if needed
            additional_args: Extra arguments
        
        Returns:
            Extraction results
        """
        logger.info(f"🔓 Steghide: {file_path}")
        return kali_client.safe_post("api/tools/steghide", {
            "file": file_path,
            "action": action,
            "password": password,
            "additional_args": additional_args
        })
    
    # ========================================================================
    # BROWSER AUTOMATION
    # ========================================================================
    
    @mcp.tool()
    def browser_navigate(url: str, action: str = "", selector: str = "", data: str = "", wait_for: str = "") -> Dict[str, Any]:
        """
        Automate browser actions with headless Chrome.
        
        Args:
            url: URL to navigate to
            action: Action (click, fill, screenshot, content, evaluate)
            selector: CSS selector for action
            data: Data for fill action
            wait_for: Selector to wait for
        
        Returns:
            Action result
        """
        logger.info(f"🌐 Browser: {url}")
        return kali_client.safe_post("api/browser/action", {
            "url": url,
            "action": action,
            "selector": selector,
            "data": data,
            "wait_for": wait_for
        })
    
    # ========================================================================
    # GIT/KNOWLEDGE BASE
    # ========================================================================
    
    @mcp.tool()
    def git_bind_repository(repo_url: str) -> Dict[str, Any]:
        """
        Bind a Git repository as knowledge base.
        
        Args:
            repo_url: GitHub repository URL
        
        Returns:
            Clone result
        """
        logger.info(f"📚 Git bind: {repo_url}")
        return kali_client.safe_post("api/git/bind", {"repo_url": repo_url})
    
    @mcp.tool()
    def git_store_data(category: str, filename: str, content: str) -> Dict[str, Any]:
        """
        Store data in Git knowledge base.
        
        Args:
            category: Category/folder name
            filename: File name
            content: Content to store
        
        Returns:
            Store result
        """
        logger.info(f"💾 Git store: {category}/{filename}")
        return kali_client.safe_post("api/git/store", {
            "category": category,
            "filename": filename,
            "content": content
        })
    
    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================
    
    @mcp.tool()
    def list_files(path: str = ".") -> Dict[str, Any]:
        """List files in a directory."""
        return kali_client.safe_get("api/files/list", {"path": path})
    
    @mcp.tool()
    def read_file(path: str) -> Dict[str, Any]:
        """Read file contents."""
        return kali_client.safe_get("api/files/read", {"path": path})
    
    @mcp.tool()
    def write_file(path: str, content: str) -> Dict[str, Any]:
        """Write content to file."""
        return kali_client.safe_post("api/files/write", {"path": path, "content": content})
    
    # ========================================================================
    # TASK MANAGEMENT
    # ========================================================================
    
    @mcp.tool()
    def list_tasks() -> Dict[str, Any]:
        """List all background tasks."""
        return kali_client.safe_get("api/tasks")
    
    @mcp.tool()
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get status of a background task."""
        return kali_client.safe_get(f"api/tasks/{task_id}")
    
    @mcp.tool()
    def send_task_input(task_id: str, input_data: str) -> Dict[str, Any]:
        """Send input to a running task."""
        return kali_client.safe_post(f"api/tasks/{task_id}/input", {"input": input_data})
    
    @mcp.tool()
    def kill_task(task_id: str) -> Dict[str, Any]:
        """Kill a running task."""
        return kali_client.safe_post(f"api/tasks/{task_id}/kill", {})
    
    # ========================================================================
    # DATABASE
    # ========================================================================
    
    @mcp.tool()
    def db_init_setup() -> Dict[str, Any]:
        """Initialize the Supabase database schema."""
        return kali_client.safe_post("api/db/init", {})
    
    return mcp

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="MCP Kali Server - MCP Client Interface")
    parser.add_argument("--server", default=os.environ.get("KALI_SERVER", DEFAULT_KALI_SERVER),
                       help="Kali server URL")
    parser.add_argument("--api-key", default=os.environ.get("KALI_API_KEY"),
                       help="API key for authentication")
    parser.add_argument("--timeout", type=int, default=DEFAULT_REQUEST_TIMEOUT,
                       help="Request timeout in seconds")
    args = parser.parse_args()
    
    logger.info("🔥 MCP Kali Server v2.0 - MCP Client Interface")
    logger.info(f"📡 Connecting to: {args.server}")
    
    kali_client = KaliToolsClient(args.server, args.api_key, args.timeout)
    mcp = setup_mcp_server(kali_client)
    
    logger.info("✅ MCP server ready with 150+ security tools")
    logger.info("🤖 12+ AI agents available")
    
    mcp.run()

if __name__ == "__main__":
    main()
