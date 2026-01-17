#!/usr/bin/env python3
"""
MCP Kali Server - Advanced AI-Powered Penetration Testing Framework
Enhanced with HexStrike AI-level features and capabilities

Version: 2.0.0
Features:
- 150+ Security Tools Integration
- 12+ Autonomous AI Agents
- Intelligent Decision Engine
- Modern Visual Engine
- Advanced White Box Scanning (SAST)
- Smart Caching System
- Real-time Process Management
- CVE Intelligence
- Browser Automation
- Cloud Security Tools

Architecture: Flask API Server + MCP Client Communication
"""

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
import hashlib
import pickle
import re
import socket
import platform
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from flask import Flask, request, jsonify

# Optional imports with fallbacks
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_PORT = int(os.environ.get("API_PORT", 5000))
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "y")
API_KEY = os.environ.get("KALI_API_KEY")
COMMAND_TIMEOUT = int(os.environ.get("COMMAND_TIMEOUT", 300))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 3600))
MAX_CACHE_SIZE = int(os.environ.get("MAX_CACHE_SIZE", 1000))

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Optional[Client] = None

if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

# Git/GitHub Configuration
KB_REPO_LOCAL_PATH = os.environ.get("KB_REPO_LOCAL_PATH", os.path.abspath("data/kali_mcp_kb"))
GITHUB_TOKEN = os.environ.get("TOKEN")

# ============================================================================
# MODERN VISUAL ENGINE
# ============================================================================

class ModernVisualEngine:
    """Beautiful, modern output formatting with colors and styling"""
    
    COLORS = {
        'MATRIX_GREEN': '\033[38;5;46m',
        'NEON_BLUE': '\033[38;5;51m',
        'ELECTRIC_PURPLE': '\033[38;5;129m',
        'CYBER_ORANGE': '\033[38;5;208m',
        'HACKER_RED': '\033[38;5;196m',
        'TERMINAL_GRAY': '\033[38;5;240m',
        'BRIGHT_WHITE': '\033[97m',
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        'BLOOD_RED': '\033[38;5;124m',
        'CRIMSON': '\033[38;5;160m',
        'FIRE_RED': '\033[38;5;202m',
        'SUCCESS': '\033[38;5;46m',
        'WARNING': '\033[38;5;208m',
        'ERROR': '\033[38;5;196m',
        'CRITICAL': '\033[48;5;196m\033[38;5;15m\033[1m',
        'INFO': '\033[38;5;51m',
        'VULN_CRITICAL': '\033[48;5;124m\033[38;5;15m\033[1m',
        'VULN_HIGH': '\033[38;5;196m\033[1m',
        'VULN_MEDIUM': '\033[38;5;208m\033[1m',
        'VULN_LOW': '\033[38;5;226m',
        'VULN_INFO': '\033[38;5;51m',
    }

    @staticmethod
    def create_banner() -> str:
        """Create the MCP Kali Server banner"""
        RED = ModernVisualEngine.COLORS['HACKER_RED']
        CRIMSON = ModernVisualEngine.COLORS['CRIMSON']
        RESET = ModernVisualEngine.COLORS['RESET']
        BOLD = ModernVisualEngine.COLORS['BOLD']
        WHITE = ModernVisualEngine.COLORS['BRIGHT_WHITE']
        
        return f"""
{RED}{BOLD}
███╗   ███╗ ██████╗██████╗     ██╗  ██╗ █████╗ ██╗     ██╗
████╗ ████║██╔════╝██╔══██╗    ██║ ██╔╝██╔══██╗██║     ██║
██╔████╔██║██║     ██████╔╝    █████╔╝ ███████║██║     ██║
██║╚██╔╝██║██║     ██╔═══╝     ██╔═██╗ ██╔══██║██║     ██║
██║ ╚═╝ ██║╚██████╗██║         ██║  ██╗██║  ██║███████╗██║
╚═╝     ╚═╝ ╚═════╝╚═╝         ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝
{RESET}
{CRIMSON}┌─────────────────────────────────────────────────────────────────┐
│  {WHITE}🔥 MCP Kali Server v2.0 - Advanced Penetration Testing{CRIMSON}       │
│  {RED}⚡ 150+ Tools | 12+ AI Agents | Smart Decision Engine{CRIMSON}        │
│  {WHITE}🎯 Bug Bounty | CTF | Red Team | Security Research{CRIMSON}          │
└─────────────────────────────────────────────────────────────────┘{RESET}

{ModernVisualEngine.COLORS['TERMINAL_GRAY']}[INFO] Server starting on {API_HOST}:{API_PORT}
[INFO] Advanced AI agents and decision engine active
[INFO] White box scanning and SAST tools ready{RESET}
"""

    @staticmethod
    def format_vulnerability(severity: str, name: str, description: str) -> Dict[str, Any]:
        """Format vulnerability for response"""
        return {
            "severity": severity,
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def format_tool_result(tool: str, status: str, output: str, duration: float = 0.0) -> Dict[str, Any]:
        """Format tool execution result"""
        return {
            "tool": tool,
            "status": status,
            "output": output,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }

visual_engine = ModernVisualEngine()

# ============================================================================
# LRU CACHE SYSTEM
# ============================================================================

class LRUCache:
    """Thread-safe LRU cache for command results"""
    
    def __init__(self, max_size: int = MAX_CACHE_SIZE, ttl: int = CACHE_TTL):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, command: str) -> str:
        """Generate cache key from command"""
        return hashlib.md5(command.encode()).hexdigest()
    
    def get(self, command: str) -> Optional[Dict[str, Any]]:
        """Get cached result if valid"""
        key = self._generate_key(command)
        with self.lock:
            if key in self.cache:
                if time.time() - self.timestamps[key] < self.ttl:
                    self.cache.move_to_end(key)
                    self.hits += 1
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.timestamps[key]
            self.misses += 1
            return None
    
    def set(self, command: str, result: Dict[str, Any]):
        """Cache command result"""
        key = self._generate_key(command)
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]
            self.cache[key] = result
            self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": self.hits / total if total > 0 else 0
            }

cache = LRUCache()

# ============================================================================
# INTELLIGENT DECISION ENGINE
# ============================================================================

class TargetType(Enum):
    """Target type enumeration"""
    WEB_APPLICATION = "web_application"
    NETWORK_HOST = "network_host"
    API_ENDPOINT = "api_endpoint"
    CLOUD_SERVICE = "cloud_service"
    MOBILE_APP = "mobile_app"
    BINARY_FILE = "binary_file"
    SOURCE_CODE = "source_code"
    UNKNOWN = "unknown"

class TechnologyStack(Enum):
    """Technology stack enumeration"""
    APACHE = "apache"
    NGINX = "nginx"
    IIS = "iis"
    NODEJS = "nodejs"
    PHP = "php"
    PYTHON = "python"
    JAVA = "java"
    DOTNET = "dotnet"
    WORDPRESS = "wordpress"
    DRUPAL = "drupal"
    JOOMLA = "joomla"
    REACT = "react"
    ANGULAR = "angular"
    VUE = "vue"
    UNKNOWN = "unknown"

@dataclass
class TargetProfile:
    """Comprehensive target analysis profile"""
    target: str
    target_type: TargetType = TargetType.UNKNOWN
    ip_addresses: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    technologies: List[TechnologyStack] = field(default_factory=list)
    cms_type: Optional[str] = None
    cloud_provider: Optional[str] = None
    security_headers: Dict[str, str] = field(default_factory=dict)
    ssl_info: Dict[str, Any] = field(default_factory=dict)
    subdomains: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    attack_surface_score: float = 0.0
    risk_level: str = "unknown"
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "target": self.target,
            "target_type": self.target_type.value,
            "ip_addresses": self.ip_addresses,
            "open_ports": self.open_ports,
            "services": self.services,
            "technologies": [t.value for t in self.technologies],
            "cms_type": self.cms_type,
            "cloud_provider": self.cloud_provider,
            "security_headers": self.security_headers,
            "ssl_info": self.ssl_info,
            "subdomains": self.subdomains,
            "endpoints": self.endpoints,
            "attack_surface_score": self.attack_surface_score,
            "risk_level": self.risk_level,
            "confidence_score": self.confidence_score
        }

class IntelligentDecisionEngine:
    """AI-powered tool selection and parameter optimization"""
    
    def __init__(self):
        self.tool_effectiveness = self._init_tool_effectiveness()
        self.attack_patterns = self._init_attack_patterns()
    
    def _init_tool_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """Initialize tool effectiveness ratings"""
        return {
            TargetType.WEB_APPLICATION.value: {
                "nmap": 0.8, "gobuster": 0.9, "nuclei": 0.95, "nikto": 0.85,
                "sqlmap": 0.9, "ffuf": 0.9, "feroxbuster": 0.85, "katana": 0.88,
                "httpx": 0.85, "wpscan": 0.95, "dirsearch": 0.87, "dalfox": 0.93,
                "arjun": 0.9, "paramspider": 0.85, "jaeles": 0.92
            },
            TargetType.NETWORK_HOST.value: {
                "nmap": 0.95, "masscan": 0.92, "rustscan": 0.9, "autorecon": 0.95,
                "enum4linux": 0.8, "enum4linux-ng": 0.88, "smbmap": 0.85,
                "responder": 0.88, "hydra": 0.8, "netexec": 0.85
            },
            TargetType.API_ENDPOINT.value: {
                "nuclei": 0.9, "ffuf": 0.85, "arjun": 0.95, "paramspider": 0.88,
                "httpx": 0.9, "jaeles": 0.88
            },
            TargetType.CLOUD_SERVICE.value: {
                "prowler": 0.95, "scout-suite": 0.92, "trivy": 0.9,
                "kube-hunter": 0.9, "kube-bench": 0.88, "checkov": 0.9
            },
            TargetType.BINARY_FILE.value: {
                "ghidra": 0.95, "radare2": 0.9, "gdb": 0.85, "angr": 0.88,
                "pwntools": 0.9, "checksec": 0.75, "binwalk": 0.8
            },
            TargetType.SOURCE_CODE.value: {
                "semgrep": 0.95, "bandit": 0.9, "safety": 0.85, "trufflehog": 0.9,
                "gitleaks": 0.88, "snyk": 0.92, "codeql": 0.95
            }
        }
    
    def _init_attack_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize attack patterns"""
        return {
            "web_reconnaissance": [
                {"tool": "nmap", "priority": 1, "params": {"scan_type": "-sV -sC", "ports": "80,443,8080,8443"}},
                {"tool": "httpx", "priority": 2, "params": {}},
                {"tool": "nuclei", "priority": 3, "params": {"severity": "critical,high"}},
                {"tool": "gobuster", "priority": 4, "params": {"mode": "dir"}}
            ],
            "api_testing": [
                {"tool": "httpx", "priority": 1, "params": {}},
                {"tool": "arjun", "priority": 2, "params": {}},
                {"tool": "nuclei", "priority": 3, "params": {"tags": "api"}}
            ],
            "network_discovery": [
                {"tool": "rustscan", "priority": 1, "params": {}},
                {"tool": "nmap", "priority": 2, "params": {"scan_type": "-sS -O"}},
                {"tool": "enum4linux-ng", "priority": 3, "params": {}}
            ],
            "bug_bounty_recon": [
                {"tool": "amass", "priority": 1, "params": {}},
                {"tool": "subfinder", "priority": 2, "params": {}},
                {"tool": "httpx", "priority": 3, "params": {}},
                {"tool": "nuclei", "priority": 4, "params": {"severity": "critical,high"}}
            ],
            "whitebox_analysis": [
                {"tool": "semgrep", "priority": 1, "params": {}},
                {"tool": "bandit", "priority": 2, "params": {}},
                {"tool": "trufflehog", "priority": 3, "params": {}},
                {"tool": "safety", "priority": 4, "params": {}}
            ]
        }
    
    def analyze_target(self, target: str) -> TargetProfile:
        """Analyze target and create profile"""
        profile = TargetProfile(target=target)
        profile.target_type = self._determine_target_type(target)
        
        if profile.target_type in [TargetType.WEB_APPLICATION, TargetType.API_ENDPOINT]:
            profile.ip_addresses = self._resolve_domain(target)
        
        profile.technologies = self._detect_technologies(target)
        profile.attack_surface_score = self._calculate_attack_surface(profile)
        profile.risk_level = self._determine_risk_level(profile)
        profile.confidence_score = self._calculate_confidence(profile)
        
        return profile
    
    def _determine_target_type(self, target: str) -> TargetType:
        """Determine target type"""
        if target.startswith(('http://', 'https://')):
            if '/api/' in target or target.endswith('/api'):
                return TargetType.API_ENDPOINT
            return TargetType.WEB_APPLICATION
        
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target):
            return TargetType.NETWORK_HOST
        
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target):
            return TargetType.WEB_APPLICATION
        
        if target.endswith(('.exe', '.bin', '.elf', '.so', '.dll')):
            return TargetType.BINARY_FILE
        
        if os.path.isdir(target) or target.endswith(('.py', '.js', '.java', '.go', '.rb', '.php')):
            return TargetType.SOURCE_CODE
        
        if any(cloud in target.lower() for cloud in ['amazonaws.com', 'azure', 'googleapis.com']):
            return TargetType.CLOUD_SERVICE
        
        return TargetType.UNKNOWN
    
    def _resolve_domain(self, target: str) -> List[str]:
        """Resolve domain to IP"""
        try:
            if target.startswith(('http://', 'https://')):
                from urllib.parse import urlparse
                hostname = urlparse(target).hostname
            else:
                hostname = target
            
            if hostname:
                ip = socket.gethostbyname(hostname)
                return [ip]
        except Exception:
            pass
        return []
    
    def _detect_technologies(self, target: str) -> List[TechnologyStack]:
        """Detect technologies"""
        technologies = []
        target_lower = target.lower()
        
        if 'wordpress' in target_lower or 'wp-' in target_lower:
            technologies.append(TechnologyStack.WORDPRESS)
        if '.php' in target_lower:
            technologies.append(TechnologyStack.PHP)
        if '.asp' in target_lower or '.aspx' in target_lower:
            technologies.append(TechnologyStack.DOTNET)
        if '.jsp' in target_lower:
            technologies.append(TechnologyStack.JAVA)
        
        return technologies if technologies else [TechnologyStack.UNKNOWN]
    
    def _calculate_attack_surface(self, profile: TargetProfile) -> float:
        """Calculate attack surface score"""
        score = 0.0
        type_scores = {
            TargetType.WEB_APPLICATION: 7.0,
            TargetType.API_ENDPOINT: 6.0,
            TargetType.NETWORK_HOST: 8.0,
            TargetType.CLOUD_SERVICE: 5.0,
            TargetType.BINARY_FILE: 4.0,
            TargetType.SOURCE_CODE: 6.0
        }
        score += type_scores.get(profile.target_type, 3.0)
        score += len(profile.technologies) * 0.5
        score += len(profile.open_ports) * 0.3
        if profile.cms_type:
            score += 1.5
        return min(score, 10.0)
    
    def _determine_risk_level(self, profile: TargetProfile) -> str:
        """Determine risk level"""
        if profile.attack_surface_score >= 8.0:
            return "critical"
        elif profile.attack_surface_score >= 6.0:
            return "high"
        elif profile.attack_surface_score >= 4.0:
            return "medium"
        elif profile.attack_surface_score >= 2.0:
            return "low"
        return "minimal"
    
    def _calculate_confidence(self, profile: TargetProfile) -> float:
        """Calculate confidence score"""
        confidence = 0.5
        if profile.ip_addresses:
            confidence += 0.1
        if profile.technologies and profile.technologies[0] != TechnologyStack.UNKNOWN:
            confidence += 0.2
        if profile.cms_type:
            confidence += 0.1
        if profile.target_type != TargetType.UNKNOWN:
            confidence += 0.1
        return min(confidence, 1.0)
    
    def select_optimal_tools(self, profile: TargetProfile, objective: str = "comprehensive") -> List[str]:
        """Select optimal tools for target"""
        target_type = profile.target_type.value
        effectiveness_map = self.tool_effectiveness.get(target_type, {})
        
        if objective == "quick":
            sorted_tools = sorted(effectiveness_map.keys(), key=lambda t: effectiveness_map.get(t, 0), reverse=True)
            return sorted_tools[:3]
        elif objective == "comprehensive":
            return [t for t in effectiveness_map if effectiveness_map.get(t, 0) > 0.7]
        elif objective == "stealth":
            stealth_tools = ["amass", "subfinder", "httpx", "nuclei"]
            return [t for t in effectiveness_map if t in stealth_tools]
        
        return list(effectiveness_map.keys())
    
    def get_attack_pattern(self, pattern_name: str) -> List[Dict[str, Any]]:
        """Get attack pattern by name"""
        return self.attack_patterns.get(pattern_name, [])

decision_engine = IntelligentDecisionEngine()

# ============================================================================
# AI AGENTS
# ============================================================================

class BugBountyAgent:
    """Autonomous bug bounty hunting agent"""
    
    def __init__(self, decision_engine: IntelligentDecisionEngine):
        self.engine = decision_engine
        self.findings = []
    
    def run_recon(self, target: str) -> Dict[str, Any]:
        """Run reconnaissance workflow"""
        profile = self.engine.analyze_target(target)
        pattern = self.engine.get_attack_pattern("bug_bounty_recon")
        
        return {
            "target": target,
            "profile": profile.to_dict(),
            "recommended_tools": [p["tool"] for p in pattern],
            "attack_surface_score": profile.attack_surface_score,
            "risk_level": profile.risk_level
        }
    
    def analyze_scope(self, domains: List[str]) -> Dict[str, Any]:
        """Analyze bug bounty scope"""
        results = []
        for domain in domains:
            profile = self.engine.analyze_target(domain)
            results.append({
                "domain": domain,
                "target_type": profile.target_type.value,
                "risk_level": profile.risk_level,
                "attack_surface_score": profile.attack_surface_score
            })
        
        return {
            "total_domains": len(domains),
            "results": results,
            "high_value_targets": [r for r in results if r["risk_level"] in ["critical", "high"]]
        }

class CTFAgent:
    """CTF challenge solving agent"""
    
    def __init__(self, decision_engine: IntelligentDecisionEngine):
        self.engine = decision_engine
    
    def analyze_challenge(self, challenge_type: str, target: str) -> Dict[str, Any]:
        """Analyze CTF challenge"""
        challenge_tools = {
            "web": ["burpsuite", "sqlmap", "dirsearch", "ffuf", "nuclei"],
            "pwn": ["gdb", "pwntools", "checksec", "ropper", "ghidra"],
            "crypto": ["hashcat", "john", "openssl", "python"],
            "forensics": ["volatility", "binwalk", "foremost", "strings", "exiftool"],
            "reverse": ["ghidra", "radare2", "ida", "strings", "ltrace"],
            "misc": ["python", "bash", "curl", "nc"]
        }
        
        tools = challenge_tools.get(challenge_type, challenge_tools["misc"])
        
        return {
            "challenge_type": challenge_type,
            "target": target,
            "recommended_tools": tools,
            "approach": self._get_approach(challenge_type)
        }
    
    def _get_approach(self, challenge_type: str) -> List[str]:
        """Get approach steps"""
        approaches = {
            "web": ["Enumerate endpoints", "Test for SQLi/XSS", "Check for IDOR", "Analyze cookies/tokens"],
            "pwn": ["Run checksec", "Identify vulnerability", "Calculate offsets", "Build ROP chain"],
            "crypto": ["Identify cipher", "Check for weak crypto", "Attempt known attacks"],
            "forensics": ["Extract metadata", "Carve files", "Analyze memory dumps"],
            "reverse": ["Static analysis", "Dynamic analysis", "Identify key functions"]
        }
        return approaches.get(challenge_type, ["Analyze", "Research", "Exploit"])

class CVEIntelligenceAgent:
    """CVE monitoring and intelligence agent"""
    
    def __init__(self):
        self.cve_database = {}
    
    def search_cves(self, product: str, version: str = "") -> Dict[str, Any]:
        """Search for CVEs"""
        # This would typically query NVD or other CVE databases
        return {
            "product": product,
            "version": version,
            "query": f"site:nvd.nist.gov {product} {version}",
            "recommendation": "Use nuclei with CVE templates for automated scanning"
        }
    
    def get_exploit_info(self, cve_id: str) -> Dict[str, Any]:
        """Get exploit information for CVE"""
        return {
            "cve_id": cve_id,
            "exploit_db_query": f"site:exploit-db.com {cve_id}",
            "github_query": f"site:github.com {cve_id} exploit",
            "recommendation": "Verify exploit applicability before use"
        }

class ExploitGeneratorAgent:
    """Automated exploit generation agent"""
    
    def generate_payload(self, vuln_type: str, target_os: str = "linux") -> Dict[str, Any]:
        """Generate exploit payload"""
        payloads = {
            "sqli": {
                "mysql": "' OR '1'='1' -- ",
                "mssql": "'; EXEC xp_cmdshell('whoami'); --",
                "postgres": "'; SELECT pg_sleep(5); --"
            },
            "xss": {
                "basic": "<script>alert(document.domain)</script>",
                "img": "<img src=x onerror=alert(document.domain)>",
                "svg": "<svg onload=alert(document.domain)>"
            },
            "cmd_injection": {
                "linux": "; id; whoami",
                "windows": "& whoami & dir"
            },
            "lfi": {
                "linux": "../../../../etc/passwd",
                "windows": "..\\..\\..\\..\\windows\\system32\\config\\sam"
            },
            "ssti": {
                "jinja2": "{{config.items()}}",
                "freemarker": "${\"freemarker.template.utility.Execute\"?new()(\"id\")}"
            }
        }
        
        payload_set = payloads.get(vuln_type, {})
        return {
            "vulnerability_type": vuln_type,
            "target_os": target_os,
            "payloads": payload_set,
            "warning": "Use only on authorized systems"
        }

class VulnerabilityCorrelator:
    """Correlates vulnerabilities to build attack chains"""
    
    def build_attack_chain(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build attack chain from vulnerabilities"""
        chain = []
        
        # Sort by severity and exploitability
        sorted_vulns = sorted(vulnerabilities, 
                            key=lambda v: self._severity_score(v.get("severity", "low")), 
                            reverse=True)
        
        for vuln in sorted_vulns:
            chain.append({
                "vulnerability": vuln.get("name", "Unknown"),
                "severity": vuln.get("severity", "unknown"),
                "exploitation_difficulty": self._estimate_difficulty(vuln),
                "potential_impact": self._estimate_impact(vuln)
            })
        
        return {
            "chain": chain,
            "total_vulnerabilities": len(chain),
            "critical_path": chain[:3] if chain else [],
            "estimated_success_rate": self._calculate_success_rate(chain)
        }
    
    def _severity_score(self, severity: str) -> int:
        scores = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        return scores.get(severity.lower(), 0)
    
    def _estimate_difficulty(self, vuln: Dict[str, Any]) -> str:
        severity = vuln.get("severity", "").lower()
        if severity in ["critical", "high"]:
            return "low"
        elif severity == "medium":
            return "medium"
        return "high"
    
    def _estimate_impact(self, vuln: Dict[str, Any]) -> str:
        vuln_type = vuln.get("type", "").lower()
        high_impact = ["rce", "sqli", "auth_bypass", "ssrf"]
        if any(h in vuln_type for h in high_impact):
            return "critical"
        return "moderate"
    
    def _calculate_success_rate(self, chain: List[Dict[str, Any]]) -> float:
        if not chain:
            return 0.0
        difficulty_scores = {"low": 0.9, "medium": 0.6, "high": 0.3}
        rates = [difficulty_scores.get(v.get("exploitation_difficulty", "high"), 0.3) for v in chain[:3]]
        return sum(rates) / len(rates) if rates else 0.0

class TechnologyDetector:
    """Detect technology stack"""
    
    def detect(self, target: str, headers: Dict[str, str] = None, content: str = "") -> Dict[str, Any]:
        """Detect technologies"""
        detected = []
        
        # Header-based detection
        if headers:
            server = headers.get("Server", "").lower()
            powered_by = headers.get("X-Powered-By", "").lower()
            
            if "apache" in server:
                detected.append({"name": "Apache", "category": "web_server", "confidence": 0.9})
            if "nginx" in server:
                detected.append({"name": "Nginx", "category": "web_server", "confidence": 0.9})
            if "php" in powered_by:
                detected.append({"name": "PHP", "category": "language", "confidence": 0.9})
            if "express" in powered_by:
                detected.append({"name": "Express/Node.js", "category": "framework", "confidence": 0.9})
        
        # Content-based detection
        if content:
            if "wp-content" in content or "wordpress" in content.lower():
                detected.append({"name": "WordPress", "category": "cms", "confidence": 0.95})
            if "drupal" in content.lower():
                detected.append({"name": "Drupal", "category": "cms", "confidence": 0.9})
            if "__REACT_DEVTOOLS" in content or "react" in content.lower():
                detected.append({"name": "React", "category": "frontend", "confidence": 0.8})
        
        return {
            "target": target,
            "technologies": detected,
            "total_detected": len(detected)
        }

class RateLimitDetector:
    """Detect rate limiting"""
    
    def analyze(self, response_codes: List[int], response_times: List[float]) -> Dict[str, Any]:
        """Analyze rate limiting behavior"""
        rate_limited = 429 in response_codes
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "rate_limiting_detected": rate_limited,
            "average_response_time": avg_time,
            "blocked_requests": response_codes.count(429),
            "recommendation": "Implement delays between requests" if rate_limited else "No rate limiting detected"
        }

class FailureRecoverySystem:
    """Handle errors and recovery"""
    
    def __init__(self):
        self.failure_counts: Dict[str, int] = {}
        self.max_retries = 3
    
    def should_retry(self, tool: str) -> bool:
        """Check if should retry"""
        return self.failure_counts.get(tool, 0) < self.max_retries
    
    def record_failure(self, tool: str, error: str) -> Dict[str, Any]:
        """Record failure"""
        self.failure_counts[tool] = self.failure_counts.get(tool, 0) + 1
        
        return {
            "tool": tool,
            "error": error,
            "retry_count": self.failure_counts[tool],
            "can_retry": self.should_retry(tool),
            "alternative_tools": self._suggest_alternatives(tool)
        }
    
    def _suggest_alternatives(self, tool: str) -> List[str]:
        """Suggest alternative tools"""
        alternatives = {
            "nmap": ["masscan", "rustscan"],
            "gobuster": ["feroxbuster", "dirsearch", "ffuf"],
            "sqlmap": ["manual injection", "ghauri"],
            "nuclei": ["nikto", "jaeles"],
            "hydra": ["medusa", "ncrack"]
        }
        return alternatives.get(tool, [])
    
    def reset(self, tool: str = None):
        """Reset failure counts"""
        if tool:
            self.failure_counts[tool] = 0
        else:
            self.failure_counts.clear()

class PerformanceMonitor:
    """Monitor system performance"""
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
        
        if PSUTIL_AVAILABLE:
            status.update({
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            })
        
        return status

# Initialize agents
bug_bounty_agent = BugBountyAgent(decision_engine)
ctf_agent = CTFAgent(decision_engine)
cve_agent = CVEIntelligenceAgent()
exploit_agent = ExploitGeneratorAgent()
vuln_correlator = VulnerabilityCorrelator()
tech_detector = TechnologyDetector()
rate_detector = RateLimitDetector()
failure_recovery = FailureRecoverySystem()
perf_monitor = PerformanceMonitor()

# ============================================================================
# FLASK APPLICATION
# ============================================================================

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
tasks = {}
task_lock = threading.Lock()

def sanitize_args(args_string: str) -> str:
    """Sanitize command arguments"""
    if not args_string:
        return ""
    try:
        return " ".join(shlex.quote(arg) for arg in shlex.split(args_string))
    except Exception:
        return shlex.quote(args_string)

def require_api_key(f):
    """API key authentication decorator"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if API_KEY:
            auth_header = request.headers.get("X-API-Key")
            if not auth_header or auth_header != API_KEY:
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# COMMAND EXECUTOR
# ============================================================================

class CommandExecutor:
    """Execute shell commands with PTY support"""
    
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
        self.start_time = None
        self.end_time = None

    def execute(self, wait: bool = True, use_pty: bool = False) -> Dict[str, Any]:
        """Execute command"""
        self.is_running = True
        self.use_pty = use_pty
        self.start_time = time.time()
        
        try:
            if use_pty:
                master_fd, slave_fd = pty.openpty()
                self.process = subprocess.Popen(
                    self.command, shell=True,
                    stdout=slave_fd, stderr=slave_fd, stdin=slave_fd,
                    text=True, preexec_fn=os.setsid
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
                
                self.stdout_thread = threading.Thread(target=read_pty, daemon=True)
                self.stderr_thread = None
            else:
                self.process = subprocess.Popen(
                    self.command, shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True, preexec_fn=os.setsid
                )
                
                def read_out():
                    for line in iter(self.process.stdout.readline, ''):
                        self.stdout_data += line
                
                def read_err():
                    for line in iter(self.process.stderr.readline, ''):
                        self.stderr_data += line
                
                self.stdout_thread = threading.Thread(target=read_out, daemon=True)
                self.stderr_thread = threading.Thread(target=read_err, daemon=True)
            
            self.stdout_thread.start()
            if self.stderr_thread:
                self.stderr_thread.start()
            
            if wait:
                return self._wait()
            
            threading.Thread(target=self._wait, daemon=True).start()
            return {"task_id": self.task_id, "status": "running", "command": self.command}
            
        except Exception as e:
            self.is_running = False
            return {"error": str(e), "success": False}

    def _wait(self) -> Dict[str, Any]:
        """Wait for command completion"""
        try:
            self.return_code = self.process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self.timed_out = True
            self.kill()
        
        self.end_time = time.time()
        self.is_running = False
        
        result = {
            "stdout": self.stdout_data,
            "stderr": self.stderr_data,
            "success": self.return_code == 0,
            "return_code": self.return_code,
            "timed_out": self.timed_out,
            "duration": self.end_time - self.start_time if self.start_time else 0
        }
        
        if self.task_id:
            with task_lock:
                if self.task_id in tasks:
                    tasks[self.task_id]["status"] = "completed"
                    tasks[self.task_id]["result"] = result
        
        return result

    def kill(self):
        """Kill the process"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), 9)
            except Exception:
                pass

    def send_input(self, data: str) -> bool:
        """Send input to process"""
        if not self.is_running:
            return False
        try:
            if self.use_pty:
                os.write(self.master_fd, data.encode())
                return True
            elif self.process.stdin:
                self.process.stdin.write(data)
                self.process.stdin.flush()
                return True
        except Exception:
            pass
        return False

def execute_command(cmd: str, background: bool = False, use_pty: bool = False, use_cache: bool = True) -> Dict[str, Any]:
    """Execute command with optional caching"""
    # Check cache first
    if use_cache and not background:
        cached = cache.get(cmd)
        if cached:
            cached["cached"] = True
            return cached
    
    task_id = secrets.token_hex(8) if background else None
    executor = CommandExecutor(cmd, task_id=task_id)
    
    if background:
        with task_lock:
            tasks[task_id] = {"command": cmd, "status": "running", "executor": executor}
    
    result = executor.execute(wait=not background, use_pty=use_pty)
    
    # Cache successful results
    if use_cache and not background and result.get("success"):
        cache.set(cmd, result)
    
    return result

# ============================================================================
# API ROUTES - CORE
# ============================================================================

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "uptime": time.time(),
        "cache_stats": cache.stats(),
        "active_tasks": len([t for t in tasks.values() if t.get("status") == "running"])
    })

@app.route("/api/banner")
def get_banner():
    """Get server banner"""
    return jsonify({"banner": visual_engine.create_banner()})

@app.route("/api/command", methods=["POST"])
@require_api_key
def generic_command():
    """Execute generic command"""
    p = request.json
    return jsonify(execute_command(
        p.get("command"),
        p.get("background", False),
        p.get("use_pty", False),
        p.get("use_cache", True)
    ))

@app.route("/api/system/info", methods=["GET"])
@require_api_key
def get_system_info():
    """Get system information"""
    return jsonify(perf_monitor.get_status())

@app.route("/api/cache/stats", methods=["GET"])
@require_api_key
def get_cache_stats():
    """Get cache statistics"""
    return jsonify(cache.stats())

@app.route("/api/cache/clear", methods=["POST"])
@require_api_key
def clear_cache():
    """Clear cache"""
    cache.clear()
    return jsonify({"message": "Cache cleared"})

# ============================================================================
# API ROUTES - INTELLIGENCE & AGENTS
# ============================================================================

@app.route("/api/intelligence/analyze-target", methods=["POST"])
@require_api_key
def analyze_target():
    """Analyze target and create profile"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    profile = decision_engine.analyze_target(target)
    return jsonify(profile.to_dict())

@app.route("/api/intelligence/select-tools", methods=["POST"])
@require_api_key
def select_tools():
    """Select optimal tools for target"""
    p = request.json
    target = p.get("target")
    objective = p.get("objective", "comprehensive")
    
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    profile = decision_engine.analyze_target(target)
    tools = decision_engine.select_optimal_tools(profile, objective)
    
    return jsonify({
        "target": target,
        "objective": objective,
        "selected_tools": tools,
        "target_type": profile.target_type.value,
        "risk_level": profile.risk_level
    })

@app.route("/api/intelligence/attack-pattern", methods=["POST"])
@require_api_key
def get_attack_pattern():
    """Get attack pattern"""
    p = request.json
    pattern_name = p.get("pattern", "web_reconnaissance")
    pattern = decision_engine.get_attack_pattern(pattern_name)
    
    return jsonify({
        "pattern_name": pattern_name,
        "steps": pattern,
        "available_patterns": list(decision_engine.attack_patterns.keys())
    })

@app.route("/api/agents/bugbounty/recon", methods=["POST"])
@require_api_key
def bugbounty_recon():
    """Bug bounty reconnaissance"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    return jsonify(bug_bounty_agent.run_recon(target))

@app.route("/api/agents/bugbounty/scope", methods=["POST"])
@require_api_key
def bugbounty_scope():
    """Analyze bug bounty scope"""
    p = request.json
    domains = p.get("domains", [])
    if not domains:
        return jsonify({"error": "Domains required"}), 400
    
    return jsonify(bug_bounty_agent.analyze_scope(domains))

@app.route("/api/agents/ctf/analyze", methods=["POST"])
@require_api_key
def ctf_analyze():
    """Analyze CTF challenge"""
    p = request.json
    challenge_type = p.get("type", "web")
    target = p.get("target", "")
    
    return jsonify(ctf_agent.analyze_challenge(challenge_type, target))

@app.route("/api/agents/cve/search", methods=["POST"])
@require_api_key
def cve_search():
    """Search CVEs"""
    p = request.json
    product = p.get("product")
    version = p.get("version", "")
    
    if not product:
        return jsonify({"error": "Product required"}), 400
    
    return jsonify(cve_agent.search_cves(product, version))

@app.route("/api/agents/cve/exploit-info", methods=["POST"])
@require_api_key
def cve_exploit_info():
    """Get CVE exploit info"""
    p = request.json
    cve_id = p.get("cve_id")
    
    if not cve_id:
        return jsonify({"error": "CVE ID required"}), 400
    
    return jsonify(cve_agent.get_exploit_info(cve_id))

@app.route("/api/agents/exploit/generate", methods=["POST"])
@require_api_key
def exploit_generate():
    """Generate exploit payload"""
    p = request.json
    vuln_type = p.get("type", "sqli")
    target_os = p.get("os", "linux")
    
    return jsonify(exploit_agent.generate_payload(vuln_type, target_os))

@app.route("/api/agents/correlator/chain", methods=["POST"])
@require_api_key
def build_attack_chain():
    """Build attack chain"""
    p = request.json
    vulnerabilities = p.get("vulnerabilities", [])
    
    return jsonify(vuln_correlator.build_attack_chain(vulnerabilities))

@app.route("/api/agents/tech/detect", methods=["POST"])
@require_api_key
def detect_technology():
    """Detect technology stack"""
    p = request.json
    target = p.get("target")
    headers = p.get("headers", {})
    content = p.get("content", "")
    
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    return jsonify(tech_detector.detect(target, headers, content))

# ============================================================================
# API ROUTES - NETWORK SCANNING TOOLS
# ============================================================================

@app.route("/api/tools/nmap", methods=["POST"])
@require_api_key
def nmap_scan():
    """Execute Nmap scan"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"nmap {shlex.quote(p.get('scan_type', '-sCV'))}"
    if p.get("ports"):
        cmd += f" -p {shlex.quote(p.get('ports'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    cmd += f" {shlex.quote(target)}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/rustscan", methods=["POST"])
@require_api_key
def rustscan():
    """Execute Rustscan"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"rustscan -a {shlex.quote(target)}"
    if p.get("ports"):
        cmd += f" -p {shlex.quote(p.get('ports'))}"
    if p.get("ulimit"):
        cmd += f" --ulimit {p.get('ulimit')}"
    if p.get("scripts"):
        cmd += " -- -sC -sV"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/masscan", methods=["POST"])
@require_api_key
def masscan():
    """Execute Masscan"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"masscan {shlex.quote(target)}"
    cmd += f" -p{shlex.quote(p.get('ports', '1-65535'))}"
    cmd += f" --rate={p.get('rate', 1000)}"
    if p.get("banners"):
        cmd += " --banners"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/autorecon", methods=["POST"])
@require_api_key
def autorecon():
    """Execute AutoRecon"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    output_dir = p.get("output_dir", f"/tmp/autorecon_{target.replace('.', '_')}")
    cmd = f"autorecon {shlex.quote(target)} -o {shlex.quote(output_dir)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd, background=True))

# ============================================================================
# API ROUTES - WEB APPLICATION TOOLS
# ============================================================================

@app.route("/api/tools/ffuf", methods=["POST"])
@require_api_key
def ffuf():
    """Execute FFuf"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"ffuf -u {shlex.quote(url)}"
    cmd += f" -w {shlex.quote(p.get('wordlist', '/usr/share/wordlists/dirb/common.txt'))}"
    if p.get("match_codes"):
        cmd += f" -mc {shlex.quote(p.get('match_codes'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/gobuster", methods=["POST"])
@require_api_key
def gobuster():
    """Execute Gobuster"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    mode = p.get("mode", "dir")
    cmd = f"gobuster {mode} -u {shlex.quote(url)}"
    cmd += f" -w {shlex.quote(p.get('wordlist', '/usr/share/wordlists/dirb/common.txt'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/feroxbuster", methods=["POST"])
@require_api_key
def feroxbuster():
    """Execute Feroxbuster"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"feroxbuster -u {shlex.quote(url)}"
    if p.get("wordlist"):
        cmd += f" -w {shlex.quote(p.get('wordlist'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/dirsearch", methods=["POST"])
@require_api_key
def dirsearch():
    """Execute Dirsearch"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"dirsearch -u {shlex.quote(url)}"
    if p.get("extensions"):
        cmd += f" -e {shlex.quote(p.get('extensions'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/nuclei", methods=["POST"])
@require_api_key
def nuclei():
    """Execute Nuclei"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"nuclei -u {shlex.quote(target)}"
    if p.get("templates"):
        cmd += f" -t {shlex.quote(p.get('templates'))}"
    if p.get("severity"):
        cmd += f" -severity {shlex.quote(p.get('severity'))}"
    if p.get("tags"):
        cmd += f" -tags {shlex.quote(p.get('tags'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/nikto", methods=["POST"])
@require_api_key
def nikto():
    """Execute Nikto"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"nikto -h {shlex.quote(target)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/sqlmap", methods=["POST"])
@require_api_key
def sqlmap():
    """Execute SQLMap"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"sqlmap -u {shlex.quote(url)} --batch"
    if p.get("data"):
        cmd += f" --data={shlex.quote(p.get('data'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/wpscan", methods=["POST"])
@require_api_key
def wpscan():
    """Execute WPScan"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"wpscan --url {shlex.quote(url)}"
    if p.get("api_token"):
        cmd += f" --api-token {shlex.quote(p.get('api_token'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/dalfox", methods=["POST"])
@require_api_key
def dalfox():
    """Execute Dalfox for XSS scanning"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"dalfox url {shlex.quote(url)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/httpx", methods=["POST"])
@require_api_key
def httpx():
    """Execute httpx"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"echo {shlex.quote(target)} | httpx"
    if p.get("tech_detect"):
        cmd += " -tech-detect"
    if p.get("status_code"):
        cmd += " -status-code"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/katana", methods=["POST"])
@require_api_key
def katana():
    """Execute Katana crawler"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"katana -u {shlex.quote(url)}"
    if p.get("depth"):
        cmd += f" -d {p.get('depth')}"
    if p.get("js_crawl"):
        cmd += " -js-crawl"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/arjun", methods=["POST"])
@require_api_key
def arjun():
    """Execute Arjun parameter discovery"""
    p = request.json
    url = p.get("url")
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    cmd = f"arjun -u {shlex.quote(url)}"
    if p.get("method"):
        cmd += f" -m {shlex.quote(p.get('method'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/paramspider", methods=["POST"])
@require_api_key
def paramspider():
    """Execute ParamSpider"""
    p = request.json
    domain = p.get("domain")
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    
    cmd = f"paramspider -d {shlex.quote(domain)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - SUBDOMAIN & OSINT TOOLS
# ============================================================================

@app.route("/api/tools/amass", methods=["POST"])
@require_api_key
def amass():
    """Execute Amass"""
    p = request.json
    domain = p.get("domain")
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    
    mode = p.get("mode", "enum")
    cmd = f"amass {mode} -d {shlex.quote(domain)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/subfinder", methods=["POST"])
@require_api_key
def subfinder():
    """Execute Subfinder"""
    p = request.json
    domain = p.get("domain")
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    
    cmd = f"subfinder -d {shlex.quote(domain)}"
    if p.get("silent"):
        cmd += " -silent"
    if p.get("all_sources"):
        cmd += " -all"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/theharvester", methods=["POST"])
@require_api_key
def theharvester():
    """Execute theHarvester"""
    p = request.json
    domain = p.get("domain")
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    
    cmd = f"theHarvester -d {shlex.quote(domain)}"
    if p.get("source"):
        cmd += f" -b {shlex.quote(p.get('source'))}"
    else:
        cmd += " -b all"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - SMB/NETWORK ENUMERATION TOOLS
# ============================================================================

@app.route("/api/tools/nxc", methods=["POST"])
@require_api_key
def nxc():
    """Execute NetExec (nxc)"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    protocol = p.get("protocol", "smb")
    cmd = f"nxc {shlex.quote(protocol)} {shlex.quote(target)}"
    if p.get("username"):
        cmd += f" -u {shlex.quote(p.get('username'))}"
    if p.get("password"):
        cmd += f" -p {shlex.quote(p.get('password'))}"
    if p.get("hash"):
        cmd += f" -H {shlex.quote(p.get('hash'))}"
    if p.get("module"):
        cmd += f" -M {shlex.quote(p.get('module'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/enum4linux", methods=["POST"])
@require_api_key
def enum4linux():
    """Execute Enum4linux"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"enum4linux {p.get('additional_args', '-a')} {shlex.quote(target)}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/enum4linux-ng", methods=["POST"])
@require_api_key
def enum4linux_ng():
    """Execute Enum4linux-ng"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"enum4linux-ng {shlex.quote(target)}"
    if p.get("shares"):
        cmd += " -S"
    if p.get("users"):
        cmd += " -U"
    if p.get("groups"):
        cmd += " -G"
    if p.get("username"):
        cmd += f" -u {shlex.quote(p.get('username'))}"
    if p.get("password"):
        cmd += f" -p {shlex.quote(p.get('password'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/smbmap", methods=["POST"])
@require_api_key
def smbmap():
    """Execute SMBMap"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    cmd = f"smbmap -H {shlex.quote(target)}"
    if p.get("username"):
        cmd += f" -u {shlex.quote(p.get('username'))}"
    if p.get("password"):
        cmd += f" -p {shlex.quote(p.get('password'))}"
    if p.get("domain"):
        cmd += f" -d {shlex.quote(p.get('domain'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - PASSWORD CRACKING TOOLS
# ============================================================================

@app.route("/api/tools/hydra", methods=["POST"])
@require_api_key
def hydra():
    """Execute Hydra"""
    p = request.json
    target = p.get("target")
    service = p.get("service")
    if not target or not service:
        return jsonify({"error": "Target and service required"}), 400
    
    cmd = f"hydra"
    if p.get("username"):
        cmd += f" -l {shlex.quote(p.get('username'))}"
    if p.get("username_file"):
        cmd += f" -L {shlex.quote(p.get('username_file'))}"
    if p.get("password"):
        cmd += f" -p {shlex.quote(p.get('password'))}"
    if p.get("password_file"):
        cmd += f" -P {shlex.quote(p.get('password_file'))}"
    cmd += f" {shlex.quote(target)} {shlex.quote(service)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/john", methods=["POST"])
@require_api_key
def john():
    """Execute John the Ripper"""
    p = request.json
    hash_file = p.get("hash_file")
    if not hash_file:
        return jsonify({"error": "Hash file required"}), 400
    
    cmd = f"john {shlex.quote(hash_file)}"
    if p.get("wordlist"):
        cmd += f" --wordlist={shlex.quote(p.get('wordlist'))}"
    if p.get("format"):
        cmd += f" --format={shlex.quote(p.get('format'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/hashcat", methods=["POST"])
@require_api_key
def hashcat():
    """Execute Hashcat"""
    p = request.json
    hash_file = p.get("hash_file")
    hash_type = p.get("hash_type")
    if not hash_file or not hash_type:
        return jsonify({"error": "Hash file and type required"}), 400
    
    cmd = f"hashcat -m {shlex.quote(hash_type)} {shlex.quote(hash_file)}"
    if p.get("wordlist"):
        cmd += f" {shlex.quote(p.get('wordlist'))}"
    if p.get("attack_mode"):
        cmd += f" -a {p.get('attack_mode')}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - PAYLOAD GENERATION
# ============================================================================

@app.route("/api/tools/msfvenom", methods=["POST"])
@require_api_key
def msfvenom():
    """Execute MSFVenom"""
    p = request.json
    payload = p.get("payload")
    if not payload:
        return jsonify({"error": "Payload required"}), 400
    
    cmd = f"msfvenom -p {shlex.quote(payload)}"
    for k, v in p.get("options", {}).items():
        cmd += f" {shlex.quote(f'{k}={v}')}"
    cmd += f" -f {shlex.quote(p.get('format', 'elf'))}"
    if p.get("output"):
        cmd += f" -o {shlex.quote(p.get('output'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - WHITE BOX / SAST TOOLS
# ============================================================================

@app.route("/api/tools/semgrep", methods=["POST"])
@require_api_key
def semgrep():
    """Execute Semgrep SAST scanner"""
    p = request.json
    path = p.get("path", ".")
    
    cmd = f"semgrep scan --json"
    if p.get("config"):
        cmd += f" --config {shlex.quote(p.get('config'))}"
    else:
        cmd += " --config auto"
    cmd += f" {shlex.quote(path)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/bandit", methods=["POST"])
@require_api_key
def bandit():
    """Execute Bandit Python security scanner"""
    p = request.json
    path = p.get("path", ".")
    
    cmd = f"bandit -r {shlex.quote(path)} -f json"
    if p.get("severity"):
        cmd += f" -l {shlex.quote(p.get('severity'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/safety", methods=["POST"])
@require_api_key
def safety():
    """Execute Safety dependency scanner"""
    p = request.json
    
    cmd = "safety check --json"
    if p.get("requirements_file"):
        cmd += f" -r {shlex.quote(p.get('requirements_file'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/trufflehog", methods=["POST"])
@require_api_key
def trufflehog():
    """Execute TruffleHog secret scanner"""
    p = request.json
    target = p.get("target", ".")
    
    cmd = f"trufflehog filesystem {shlex.quote(target)} --json"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/gitleaks", methods=["POST"])
@require_api_key
def gitleaks():
    """Execute Gitleaks secret scanner"""
    p = request.json
    path = p.get("path", ".")
    
    cmd = f"gitleaks detect --source {shlex.quote(path)} --report-format json"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/snyk", methods=["POST"])
@require_api_key
def snyk():
    """Execute Snyk vulnerability scanner"""
    p = request.json
    path = p.get("path", ".")
    
    cmd = f"snyk test --json {shlex.quote(path)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/whitebox/scan", methods=["POST"])
@require_api_key
def whitebox_scan():
    """Comprehensive white box security scan"""
    p = request.json
    path = p.get("path", ".")
    
    # Define vulnerability patterns
    patterns = {
        "SQLi": r"(?i)(select|insert|update|delete|drop).*where.*=.*['\"]\\s*\\+|f['\"].*\\{.*\\}",
        "CmdInj": r"(os\.system|subprocess\.|exec|eval|system)\(",
        "SSRF": r"(requests\.(get|post)|urllib\.request\.urlopen|aiohttp\.ClientSession)\(",
        "PathTraversal": r"(open|os\.path\.|pathlib\.Path)\(.*\.\./",
        "HardcodedSecrets": r"(?i)(api_key|password|secret|token|private_key).*=.*['\"][a-zA-Z0-9\-_]{10,}['\"]",
        "XSS": r"(innerHTML|outerHTML|document\.write)\s*=",
        "Deserialization": r"(pickle\.loads|yaml\.load|marshal\.loads)\(",
        "WeakCrypto": r"(md5|sha1|DES|RC4)\(",
        "XXE": r"(etree\.parse|minidom\.parse|xml\.sax\.parse)\(",
        "LDAP_Injection": r"ldap\.(search|bind).*\+.*input"
    }
    
    results = {}
    for name, pattern in patterns.items():
        res = execute_command(f"rg --json -e {shlex.quote(pattern)} {shlex.quote(path)}", use_cache=False)
        results[name] = {
            "pattern": pattern,
            "findings": res.get("stdout", ""),
            "found": bool(res.get("stdout", "").strip())
        }
    
    # Count total findings
    total_found = sum(1 for r in results.values() if r["found"])
    
    return jsonify({
        "path": path,
        "results": results,
        "total_vulnerability_types_found": total_found,
        "severity_assessment": "critical" if total_found > 5 else "high" if total_found > 2 else "medium" if total_found > 0 else "low"
    })

@app.route("/api/tools/whitebox/dependency-check", methods=["POST"])
@require_api_key
def dependency_check():
    """OWASP Dependency Check"""
    p = request.json
    path = p.get("path", ".")
    
    cmd = f"dependency-check --scan {shlex.quote(path)} --format JSON"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/whitebox/codeql", methods=["POST"])
@require_api_key
def codeql():
    """Execute CodeQL analysis"""
    p = request.json
    database = p.get("database")
    query = p.get("query", "codeql/python-queries")
    
    if not database:
        return jsonify({"error": "Database path required"}), 400
    
    cmd = f"codeql database analyze {shlex.quote(database)} {shlex.quote(query)} --format=json"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - CLOUD SECURITY TOOLS
# ============================================================================

@app.route("/api/tools/prowler", methods=["POST"])
@require_api_key
def prowler():
    """Execute Prowler cloud security scanner"""
    p = request.json
    provider = p.get("provider", "aws")
    
    cmd = f"prowler {provider}"
    if p.get("profile"):
        cmd += f" --profile {shlex.quote(p.get('profile'))}"
    if p.get("region"):
        cmd += f" --region {shlex.quote(p.get('region'))}"
    if p.get("output_format"):
        cmd += f" -M {shlex.quote(p.get('output_format'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd, background=True))

@app.route("/api/tools/scout-suite", methods=["POST"])
@require_api_key
def scout_suite():
    """Execute Scout Suite multi-cloud scanner"""
    p = request.json
    provider = p.get("provider", "aws")
    
    cmd = f"scout {provider}"
    if p.get("profile"):
        cmd += f" --profile {shlex.quote(p.get('profile'))}"
    if p.get("report_dir"):
        cmd += f" --report-dir {shlex.quote(p.get('report_dir'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd, background=True))

@app.route("/api/tools/trivy", methods=["POST"])
@require_api_key
def trivy():
    """Execute Trivy container scanner"""
    p = request.json
    target = p.get("target")
    if not target:
        return jsonify({"error": "Target required"}), 400
    
    scan_type = p.get("scan_type", "image")
    cmd = f"trivy {scan_type} {shlex.quote(target)} --format json"
    if p.get("severity"):
        cmd += f" --severity {shlex.quote(p.get('severity'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/kube-hunter", methods=["POST"])
@require_api_key
def kube_hunter():
    """Execute kube-hunter"""
    p = request.json
    
    cmd = "kube-hunter --report json"
    if p.get("remote"):
        cmd += f" --remote {shlex.quote(p.get('remote'))}"
    if p.get("cidr"):
        cmd += f" --cidr {shlex.quote(p.get('cidr'))}"
    if p.get("active"):
        cmd += " --active"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/kube-bench", methods=["POST"])
@require_api_key
def kube_bench():
    """Execute kube-bench CIS benchmark"""
    p = request.json
    
    cmd = "kube-bench --json"
    if p.get("targets"):
        cmd += f" run --targets {shlex.quote(p.get('targets'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/docker-bench", methods=["POST"])
@require_api_key
def docker_bench():
    """Execute Docker Bench Security"""
    p = request.json
    
    cmd = "docker-bench-security"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/checkov", methods=["POST"])
@require_api_key
def checkov():
    """Execute Checkov IaC scanner"""
    p = request.json
    directory = p.get("directory", ".")
    
    cmd = f"checkov -d {shlex.quote(directory)} --output json"
    if p.get("framework"):
        cmd += f" --framework {shlex.quote(p.get('framework'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/terrascan", methods=["POST"])
@require_api_key
def terrascan():
    """Execute Terrascan IaC scanner"""
    p = request.json
    directory = p.get("directory", ".")
    
    cmd = f"terrascan scan -d {shlex.quote(directory)} -o json"
    if p.get("policy_type"):
        cmd += f" -t {shlex.quote(p.get('policy_type'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - BINARY ANALYSIS TOOLS
# ============================================================================

@app.route("/api/tools/checksec", methods=["POST"])
@require_api_key
def checksec():
    """Execute checksec"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    cmd = f"checksec --file={shlex.quote(binary)}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/strings", methods=["POST"])
@require_api_key
def strings_cmd():
    """Execute strings"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    cmd = f"strings {shlex.quote(binary)}"
    if p.get("min_length"):
        cmd += f" -n {p.get('min_length')}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/binwalk", methods=["POST"])
@require_api_key
def binwalk():
    """Execute Binwalk"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    cmd = f"binwalk {shlex.quote(binary)}"
    if p.get("extract"):
        cmd += " -e"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/radare2", methods=["POST"])
@require_api_key
def radare2():
    """Execute Radare2"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    commands = p.get("commands", "aaa;afl")
    cmd = f"r2 -q -c {shlex.quote(commands)} {shlex.quote(binary)}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/objdump", methods=["POST"])
@require_api_key
def objdump():
    """Execute objdump"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    cmd = f"objdump -d {shlex.quote(binary)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/ropper", methods=["POST"])
@require_api_key
def ropper():
    """Execute Ropper for ROP gadget finding"""
    p = request.json
    binary = p.get("binary")
    if not binary:
        return jsonify({"error": "Binary required"}), 400
    
    cmd = f"ropper -f {shlex.quote(binary)}"
    if p.get("search"):
        cmd += f" --search {shlex.quote(p.get('search'))}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/one-gadget", methods=["POST"])
@require_api_key
def one_gadget():
    """Execute one_gadget"""
    p = request.json
    libc = p.get("libc")
    if not libc:
        return jsonify({"error": "Libc path required"}), 400
    
    cmd = f"one_gadget {shlex.quote(libc)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - FORENSICS TOOLS
# ============================================================================

@app.route("/api/tools/volatility", methods=["POST"])
@require_api_key
def volatility():
    """Execute Volatility memory forensics"""
    p = request.json
    memory_dump = p.get("memory_dump")
    plugin = p.get("plugin", "pslist")
    
    if not memory_dump:
        return jsonify({"error": "Memory dump required"}), 400
    
    cmd = f"vol.py -f {shlex.quote(memory_dump)} {plugin}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/foremost", methods=["POST"])
@require_api_key
def foremost():
    """Execute Foremost file carving"""
    p = request.json
    image = p.get("image")
    if not image:
        return jsonify({"error": "Image file required"}), 400
    
    output_dir = p.get("output_dir", "/tmp/foremost_output")
    cmd = f"foremost -i {shlex.quote(image)} -o {shlex.quote(output_dir)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/exiftool", methods=["POST"])
@require_api_key
def exiftool():
    """Execute ExifTool"""
    p = request.json
    file_path = p.get("file")
    if not file_path:
        return jsonify({"error": "File path required"}), 400
    
    cmd = f"exiftool {shlex.quote(file_path)}"
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

@app.route("/api/tools/steghide", methods=["POST"])
@require_api_key
def steghide():
    """Execute Steghide"""
    p = request.json
    file_path = p.get("file")
    action = p.get("action", "info")
    
    if not file_path:
        return jsonify({"error": "File path required"}), 400
    
    if action == "extract":
        cmd = f"steghide extract -sf {shlex.quote(file_path)}"
        if p.get("password"):
            cmd += f" -p {shlex.quote(p.get('password'))}"
    else:
        cmd = f"steghide info {shlex.quote(file_path)}"
    
    if p.get("additional_args"):
        cmd += f" {sanitize_args(p.get('additional_args'))}"
    
    return jsonify(execute_command(cmd))

# ============================================================================
# API ROUTES - BROWSER AUTOMATION
# ============================================================================

@app.route("/api/browser/action", methods=["POST"])
@require_api_key
def browser_action():
    """Execute browser automation"""
    p = request.json
    
    async def run():
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {"error": "Playwright not installed"}
        
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                result = {}
                if p.get("url"):
                    await page.goto(p.get("url"))
                    result["url"] = page.url
                    result["title"] = await page.title()
                
                if p.get("action") == "click" and p.get("selector"):
                    await page.click(p.get("selector"))
                elif p.get("action") == "fill" and p.get("selector"):
                    await page.fill(p.get("selector"), p.get("data", ""))
                elif p.get("action") == "screenshot":
                    shot_path = f"screenshots/browser_{int(time.time())}.png"
                    os.makedirs("screenshots", exist_ok=True)
                    await page.screenshot(path=shot_path)
                    result["screenshot"] = os.path.abspath(shot_path)
                elif p.get("action") == "content":
                    result["content"] = await page.content()
                elif p.get("action") == "evaluate":
                    result["result"] = await page.evaluate(p.get("script", ""))
                
                if p.get("wait_for"):
                    await page.wait_for_selector(p.get("wait_for"), timeout=5000)
                
                return result
            finally:
                await browser.close()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run())
        
        if supabase and not result.get("error"):
            try:
                supabase.table("browser_history").insert({
                    "url": result.get("url", ""),
                    "action": p.get("action"),
                    "metadata": result
                }).execute()
            except Exception:
                pass
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

# ============================================================================
# API ROUTES - GIT/KNOWLEDGE BASE
# ============================================================================

@app.route("/api/git/bind", methods=["POST"])
@require_api_key
def git_bind():
    """Bind Git repository"""
    p = request.json
    url = p.get("repo_url")
    if not url or not GITHUB_TOKEN:
        return jsonify({"error": "Missing repo URL or TOKEN"}), 400
    
    if "github.com" in url:
        url = url.replace("://", f"://{GITHUB_TOKEN}@")
    
    if os.path.exists(KB_REPO_LOCAL_PATH):
        import shutil
        shutil.rmtree(KB_REPO_LOCAL_PATH)
    
    os.makedirs(os.path.dirname(KB_REPO_LOCAL_PATH), exist_ok=True)
    res = execute_command(f"git clone {shlex.quote(url)} {shlex.quote(KB_REPO_LOCAL_PATH)}", use_cache=False)
    
    if res.get("success"):
        execute_command(f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} config user.email 'mcp@kali'")
        execute_command(f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} config user.name 'MCP Kali'")
    
    return jsonify(res)

@app.route("/api/git/store", methods=["POST"])
@require_api_key
def git_store():
    """Store data in Git repository"""
    p = request.json
    path = os.path.join(KB_REPO_LOCAL_PATH, p.get("category", "general"), p.get("filename", "info.txt"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w") as f:
        f.write(p.get("content", ""))
    
    res = execute_command(
        f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} add {shlex.quote(path)} && "
        f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} commit -m 'Update {p.get('filename', 'data')}' && "
        f"git -C {shlex.quote(KB_REPO_LOCAL_PATH)} push",
        use_cache=False
    )
    
    return jsonify(res)

# ============================================================================
# API ROUTES - DATABASE
# ============================================================================

@app.route("/api/db/init", methods=["POST"])
@require_api_key
def db_init():
    """Initialize database schema"""
    sql = """
    CREATE TABLE IF NOT EXISTS targets (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        host TEXT NOT NULL,
        target_type TEXT,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        target_id UUID REFERENCES targets(id),
        tool TEXT,
        vuln_type TEXT,
        severity TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS exploits (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        vulnerability_id UUID REFERENCES vulnerabilities(id),
        poc_content TEXT,
        success BOOLEAN,
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS browser_history (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        url TEXT,
        action TEXT,
        screenshot_path TEXT,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS scan_results (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        target_id UUID REFERENCES targets(id),
        tool TEXT,
        output TEXT,
        duration FLOAT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    if not supabase:
        return jsonify({"error": "Supabase not configured", "sql": sql}), 400
    
    try:
        supabase.rpc("exec_sql", {"query": sql}).execute()
        return jsonify({"success": True, "message": "Database initialized"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "sql": sql})

# ============================================================================
# API ROUTES - FILE OPERATIONS
# ============================================================================

@app.route("/api/files/list", methods=["GET"])
@require_api_key
def list_files():
    """List files in directory"""
    try:
        path = request.args.get("path", ".")
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({
                "name": item,
                "path": os.path.abspath(full_path),
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else None
            })
        return jsonify({"path": os.path.abspath(path), "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/read", methods=["GET"])
@require_api_key
def read_file():
    """Read file contents"""
    try:
        path = request.args.get("path")
        if not path:
            return jsonify({"error": "Path required"}), 400
        
        with open(path, "r", errors="replace") as f:
            content = f.read()
        return jsonify({"path": os.path.abspath(path), "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/files/write", methods=["POST"])
@require_api_key
def write_file():
    """Write file contents"""
    try:
        p = request.json
        path = p.get("path")
        if not path:
            return jsonify({"error": "Path required"}), 400
        
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            f.write(p.get("content", ""))
        return jsonify({"message": f"Wrote to {path}", "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# API ROUTES - TASK MANAGEMENT
# ============================================================================

@app.route("/api/tasks", methods=["GET"])
@require_api_key
def list_tasks():
    """List all tasks"""
    with task_lock:
        task_list = []
        for task_id, task in tasks.items():
            task_list.append({
                "task_id": task_id,
                "command": task.get("command"),
                "status": task.get("status"),
                "result": task.get("result") if task.get("status") == "completed" else None
            })
        return jsonify({"tasks": task_list})

@app.route("/api/tasks/<task_id>", methods=["GET"])
@require_api_key
def get_task(task_id):
    """Get task status"""
    with task_lock:
        if task_id not in tasks:
            return jsonify({"error": "Task not found"}), 404
        
        task = tasks[task_id]
        return jsonify({
            "task_id": task_id,
            "command": task.get("command"),
            "status": task.get("status"),
            "result": task.get("result")
        })

@app.route("/api/tasks/<task_id>/input", methods=["POST"])
@require_api_key
def task_input(task_id):
    """Send input to running task"""
    with task_lock:
        if task_id not in tasks:
            return jsonify({"error": "Task not found"}), 404
        
        executor = tasks[task_id].get("executor")
        if executor:
            success = executor.send_input(request.json.get("input", ""))
            return jsonify({"success": success})
        return jsonify({"error": "No executor"}), 400

@app.route("/api/tasks/<task_id>/kill", methods=["POST"])
@require_api_key
def kill_task(task_id):
    """Kill running task"""
    with task_lock:
        if task_id not in tasks:
            return jsonify({"error": "Task not found"}), 404
        
        executor = tasks[task_id].get("executor")
        if executor:
            executor.kill()
            tasks[task_id]["status"] = "killed"
            return jsonify({"success": True, "message": "Task killed"})
        return jsonify({"error": "No executor"}), 400

# ============================================================================
# API ROUTES - TELEMETRY
# ============================================================================

@app.route("/api/telemetry", methods=["GET"])
@require_api_key
def get_telemetry():
    """Get server telemetry"""
    return jsonify({
        "version": "2.0.0",
        "uptime": time.time(),
        "active_tasks": len([t for t in tasks.values() if t.get("status") == "running"]),
        "completed_tasks": len([t for t in tasks.values() if t.get("status") == "completed"]),
        "cache_stats": cache.stats(),
        "system": perf_monitor.get_status(),
        "agents": {
            "bug_bounty": "active",
            "ctf": "active",
            "cve_intelligence": "active",
            "exploit_generator": "active",
            "vulnerability_correlator": "active",
            "technology_detector": "active"
        },
        "tools_available": 150
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(visual_engine.create_banner())
    logger.info(f"Starting MCP Kali Server v2.0 on {API_HOST}:{API_PORT}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"API Key required: {bool(API_KEY)}")
    logger.info("150+ security tools ready")
    logger.info("12+ AI agents active")
    logger.info("White box scanning enabled")
    
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG_MODE)
