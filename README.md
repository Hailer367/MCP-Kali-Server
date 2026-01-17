# MCP Kali Server v2.0

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0-red?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Tools-150+-blue?style=for-the-badge" alt="Tools">
  <img src="https://img.shields.io/badge/AI%20Agents-12+-green?style=for-the-badge" alt="Agents">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

**MCP Kali Server** is an advanced AI-powered penetration testing framework that connects MCP-compatible AI agents (Claude, GPT, etc.) to a comprehensive suite of 150+ security tools through a unified API interface.

---

## Features

### 150+ Security Tools Integration

#### Network Scanning
- **Nmap** - Port scanning and service detection
- **Rustscan** - Ultra-fast port scanner
- **Masscan** - High-speed network scanner
- **AutoRecon** - Automated reconnaissance

#### Web Application Testing
- **FFuf** - Fast web fuzzer
- **Gobuster** - Directory/DNS enumeration
- **Feroxbuster** - Recursive content discovery
- **Dirsearch** - Web path scanner
- **Nuclei** - Template-based vulnerability scanner
- **Nikto** - Web vulnerability scanner
- **SQLMap** - SQL injection tester
- **WPScan** - WordPress security scanner
- **Dalfox** - XSS vulnerability scanner
- **httpx** - HTTP probe tool
- **Katana** - Web crawler
- **Arjun** - Parameter discovery
- **ParamSpider** - Parameter mining

#### Subdomain & OSINT
- **Amass** - Subdomain enumeration
- **Subfinder** - Passive subdomain discovery
- **theHarvester** - Email/subdomain harvester

#### SMB/Network Enumeration
- **NetExec (nxc)** - Network enumeration (successor to CrackMapExec)
- **Enum4linux** / **Enum4linux-ng** - SMB enumeration
- **SMBMap** - Share enumeration

#### Password Cracking
- **Hydra** - Brute force tool
- **John the Ripper** - Password cracker
- **Hashcat** - GPU-accelerated hash cracker

#### White Box / SAST (Static Analysis Security Testing)
- **Semgrep** - Multi-language SAST scanner
- **Bandit** - Python security scanner
- **Safety** - Python dependency scanner
- **TruffleHog** - Secret scanner
- **Gitleaks** - Git secret scanner
- **Snyk** - Vulnerability scanner
- **OWASP Dependency Check** - Dependency vulnerability scanner
- **CodeQL** - Advanced code analysis
- **Custom Pattern Scanner** - SQLi, XSS, Command Injection, Path Traversal, Hardcoded Secrets, XXE, LDAP Injection detection

#### Cloud Security
- **Prowler** - AWS/Azure/GCP security scanner
- **Scout Suite** - Multi-cloud security auditing
- **Trivy** - Container vulnerability scanner
- **kube-hunter** - Kubernetes penetration tester
- **kube-bench** - CIS benchmark checker
- **Docker Bench Security** - Docker security audit
- **Checkov** - Infrastructure as Code scanner
- **Terrascan** - IaC security scanner

#### Binary Analysis
- **checksec** - Binary security properties
- **Binwalk** - Firmware analysis
- **Radare2** - Reverse engineering framework
- **Ropper** - ROP gadget finder
- **one_gadget** - libc gadget finder
- **objdump** - Binary disassembly
- **strings** - String extraction

#### Forensics
- **Volatility** - Memory forensics
- **Foremost** - File carving
- **ExifTool** - Metadata extraction
- **Steghide** - Steganography tool

#### Payload Generation
- **MSFVenom** - Metasploit payload generator

#### Browser Automation
- **Playwright** - Headless browser automation

---

### 12+ Autonomous AI Agents

1. **Bug Bounty Agent** - Automated reconnaissance and scope analysis
2. **CTF Agent** - Challenge type analysis and tool recommendations
3. **CVE Intelligence Agent** - CVE search and exploit information gathering
4. **Exploit Generator Agent** - Payload generation for various vulnerability types
5. **Vulnerability Correlator** - Build attack chains from discovered vulnerabilities
6. **Technology Detector** - Identify technology stacks from headers and content
7. **Rate Limit Detector** - Analyze rate limiting behavior
8. **Failure Recovery System** - Automatic error handling and tool alternatives
9. **Performance Monitor** - System resource monitoring
10. **Intelligent Decision Engine** - AI-powered tool selection and parameter optimization
11. **Attack Pattern Engine** - Predefined attack workflows
12. **Target Profiler** - Comprehensive target analysis

---

### Advanced Features

- **Intelligent Decision Engine** - AI-powered tool selection based on target analysis
- **Modern Visual Engine** - Beautiful terminal output with colors and styling
- **LRU Cache System** - Smart caching of command results for faster operations
- **PTY Support** - Interactive terminal support for complex tools
- **Background Task Management** - Run long-running scans asynchronously
- **Supabase Integration** - Persistent database storage for findings
- **Git Knowledge Base** - Store and sync findings with GitHub
- **API Key Authentication** - Secure API access control

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MCP AI Agents                                 │
│              (Claude Desktop, VS Code, 5ire, etc.)                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ MCP Protocol
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     mcp_server.py                                    │
│              MCP Client Interface (FastMCP)                         │
│    ┌────────────────┬────────────────┬────────────────────────┐     │
│    │  Tool Wrappers │  Agent Calls   │   Result Processing    │     │
│    └────────────────┴────────────────┴────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    kali_server.py                                    │
│               Flask API Server (Port 5000)                          │
│  ┌────────────────┬─────────────────┬────────────────────────────┐  │
│  │  150+ Tools    │   12+ Agents    │   Decision Engine          │  │
│  ├────────────────┼─────────────────┼────────────────────────────┤  │
│  │  Visual Engine │   Cache System  │   Task Management          │  │
│  └────────────────┴─────────────────┴────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   Kali      │ │  Supabase   │ │   GitHub    │
            │   Tools     │ │  Database   │ │   K-Base    │
            └─────────────┘ └─────────────┘ └─────────────┘
```

---

## Installation

### Prerequisites

- Python 3.9+
- Kali Linux (recommended) or Debian-based Linux
- Go 1.19+ (for some tools)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Hailer367/MCP-Kali-Server.git
cd MCP-Kali-Server

# Install Python dependencies
pip3 install flask requests psutil mcp supabase playwright

# Install Playwright browsers
playwright install chromium

# Install security tools (see Commands.md for full list)
sudo apt install -y nmap ffuf gobuster nuclei nikto sqlmap

# Start the API server
python3 kali_server.py

# In another terminal, start the MCP interface
python3 mcp_server.py
```

### Tool Installation

See **[Commands.md](Commands.md)** for comprehensive installation scripts for all 150+ tools.

---

## Configuration

### Environment Variables

```bash
# Required
export API_PORT=5000           # API server port
export API_HOST=0.0.0.0        # API server host

# Authentication (optional but recommended)
export KALI_API_KEY=your_secure_key

# Supabase Integration (optional)
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your_supabase_key

# GitHub Knowledge Base (optional)
export TOKEN=your_github_token

# Performance tuning
export COMMAND_TIMEOUT=300     # Command timeout in seconds
export CACHE_TTL=3600          # Cache time-to-live
export MAX_CACHE_SIZE=1000     # Maximum cached commands
```

### MCP Configuration (Claude Desktop)

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "mcp-kali-server": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "KALI_SERVER": "http://localhost:5000",
        "KALI_API_KEY": "your_api_key"
      }
    }
  }
}
```

---

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and status |
| `/api/command` | POST | Execute generic command |
| `/api/system/info` | GET | System information |
| `/api/cache/stats` | GET | Cache statistics |
| `/api/telemetry` | GET | Server telemetry |

### Intelligence & Agents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/intelligence/analyze-target` | POST | Analyze target profile |
| `/api/intelligence/select-tools` | POST | AI-powered tool selection |
| `/api/intelligence/attack-pattern` | POST | Get attack patterns |
| `/api/agents/bugbounty/recon` | POST | Bug bounty reconnaissance |
| `/api/agents/ctf/analyze` | POST | CTF challenge analysis |
| `/api/agents/cve/search` | POST | CVE search |
| `/api/agents/exploit/generate` | POST | Generate exploit payloads |

### Security Tools

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tools/nmap` | POST | Nmap scan |
| `/api/tools/nuclei` | POST | Nuclei scan |
| `/api/tools/ffuf` | POST | FFuf fuzzing |
| `/api/tools/gobuster` | POST | Gobuster enumeration |
| `/api/tools/sqlmap` | POST | SQLMap testing |
| `/api/tools/semgrep` | POST | Semgrep SAST |
| `/api/tools/whitebox/scan` | POST | Comprehensive white box scan |
| `/api/tools/trivy` | POST | Trivy container scan |
| `/api/tools/prowler` | POST | Cloud security scan |

---

## Usage Examples

### Using with Claude

```
Claude, scan the target 10.10.10.1 for open ports and vulnerabilities.

Claude, analyze this web application https://example.com for security issues.

Claude, I'm working on a bug bounty for hackerone.com, help me with reconnaissance.

Claude, I have a CTF web challenge, help me find the vulnerability.
```

### Using the API Directly

```bash
# Nmap scan
curl -X POST http://localhost:5000/api/tools/nmap \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{"target": "10.10.10.1", "scan_type": "-sCV", "ports": "22,80,443"}'

# Analyze target
curl -X POST http://localhost:5000/api/intelligence/analyze-target \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{"target": "https://example.com"}'

# White box scan
curl -X POST http://localhost:5000/api/tools/whitebox/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{"path": "/path/to/source/code"}'
```

---

## MCP Tools Reference

The MCP server exposes 80+ tools for AI agents. Key tools include:

### Network Scanning
- `nmap_scan` - Port scanning with service detection
- `rustscan` - Ultra-fast port scanning
- `masscan` - High-speed network scanning

### Web Testing
- `nuclei_scan` - Template-based vulnerability scanning
- `ffuf_scan` - Web fuzzing
- `sqlmap_scan` - SQL injection testing
- `wpscan` - WordPress security scanning

### Intelligence
- `analyze_target` - AI-powered target analysis
- `select_optimal_tools` - Intelligent tool selection
- `bugbounty_recon` - Automated bug bounty reconnaissance
- `ctf_analyze_challenge` - CTF challenge analysis

### White Box
- `semgrep_scan` - SAST scanning
- `whitebox_comprehensive_scan` - Multi-pattern security scan
- `trufflehog_scan` - Secret detection

### Cloud
- `prowler_scan` - Cloud security scanning
- `trivy_scan` - Container vulnerability scanning

---

## Database Schema

When using Supabase integration:

```sql
-- Targets table
CREATE TABLE targets (
    id UUID PRIMARY KEY,
    host TEXT NOT NULL,
    target_type TEXT,
    risk_level TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vulnerabilities table
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY,
    target_id UUID REFERENCES targets(id),
    tool TEXT,
    vuln_type TEXT,
    severity TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scan results table
CREATE TABLE scan_results (
    id UUID PRIMARY KEY,
    target_id UUID REFERENCES targets(id),
    tool TEXT,
    output TEXT,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Security Considerations

1. **API Key Authentication** - Always use `KALI_API_KEY` in production
2. **Network Isolation** - Run on isolated network segments
3. **Tool Permissions** - Some tools require root privileges
4. **Legal Authorization** - Only test systems you have permission to test
5. **Data Protection** - Secure database credentials and tokens

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. Users are responsible for ensuring they have proper authorization before testing any systems. The authors are not responsible for misuse or damage caused by this tool.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Inspired by [HexStrike AI](https://github.com/0x4m4/hexstrike-ai)
- Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- Powered by the amazing security tools community

---

**Made with for the security community**

*MCP Kali Server v2.0 - Advanced AI-Powered Penetration Testing*
