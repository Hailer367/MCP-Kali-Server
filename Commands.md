# MCP Kali Server - Installation Commands

This document contains tested installation scripts for all tools integrated with MCP Kali Server v2.0.

---

## Table of Contents
1. [Core Dependencies](#core-dependencies)
2. [Network Scanning Tools](#network-scanning-tools)
3. [Web Application Tools](#web-application-tools)
4. [Subdomain & OSINT Tools](#subdomain--osint-tools)
5. [SMB/Network Enumeration Tools](#smbnetwork-enumeration-tools)
6. [Password Cracking Tools](#password-cracking-tools)
7. [White Box / SAST Tools](#white-box--sast-tools)
8. [Cloud Security Tools](#cloud-security-tools)
9. [Binary Analysis Tools](#binary-analysis-tools)
10. [Forensics Tools](#forensics-tools)
11. [Payload Generation Tools](#payload-generation-tools)
12. [Browser Automation](#browser-automation)
13. [Quick Install Scripts](#quick-install-scripts)

---

## Core Dependencies

### Python Requirements
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install MCP Kali Server Python dependencies
pip3 install flask requests psutil mcp

# Optional: Supabase for database integration
pip3 install supabase
```

### System Essentials
```bash
# Essential build tools
sudo apt install -y build-essential git curl wget unzip jq

# Network utilities
sudo apt install -y net-tools dnsutils netcat-openbsd
```

---

## Network Scanning Tools

### Nmap
```bash
# Install Nmap
sudo apt install -y nmap

# Verify installation
nmap --version

# Optional: Install Nmap scripts
sudo nmap --script-updatedb
```

### Rustscan
```bash
# Install from release (recommended for Kali)
wget https://github.com/RustScan/RustScan/releases/download/2.3.0/rustscan_2.3.0_amd64.deb
sudo dpkg -i rustscan_2.3.0_amd64.deb
rm rustscan_2.3.0_amd64.deb

# Verify installation
rustscan --version

# Alternative: Install via cargo
# sudo apt install -y cargo
# cargo install rustscan
```

### Masscan
```bash
# Install Masscan
sudo apt install -y masscan

# Verify installation
masscan --version
```

### AutoRecon
```bash
# Install AutoRecon
pip3 install git+https://github.com/Tib3rius/AutoRecon.git

# Or via pipx (recommended)
sudo apt install -y pipx
pipx ensurepath
pipx install git+https://github.com/Tib3rius/AutoRecon.git

# Verify installation
autorecon --help
```

---

## Web Application Tools

### FFuf
```bash
# Install FFuf
sudo apt install -y ffuf

# Alternative: Install from Go
# go install github.com/ffuf/ffuf/v2@latest

# Verify installation
ffuf -V
```

### Gobuster
```bash
# Install Gobuster
sudo apt install -y gobuster

# Verify installation
gobuster version
```

### Feroxbuster
```bash
# Install from release
sudo apt install -y feroxbuster

# Alternative: Install from script
curl -sL https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh | bash

# Verify installation
feroxbuster --version
```

### Dirsearch
```bash
# Install Dirsearch
sudo apt install -y dirsearch

# Alternative: Clone from GitHub
git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch
chmod +x /opt/dirsearch/dirsearch.py
sudo ln -sf /opt/dirsearch/dirsearch.py /usr/local/bin/dirsearch

# Verify installation
dirsearch --version
```

### Nuclei
```bash
# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Alternative: Download binary
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
unzip nuclei_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
rm nuclei_linux_amd64.zip

# Update templates
nuclei -update-templates

# Verify installation
nuclei -version
```

### Nikto
```bash
# Install Nikto
sudo apt install -y nikto

# Verify installation
nikto -Version
```

### SQLMap
```bash
# Install SQLMap
sudo apt install -y sqlmap

# Verify installation
sqlmap --version
```

### WPScan
```bash
# Install WPScan
sudo apt install -y wpscan

# Alternative: Install via Ruby gem
sudo gem install wpscan

# Update database
wpscan --update

# Verify installation
wpscan --version
```

### Dalfox
```bash
# Install Dalfox
go install github.com/hahwul/dalfox/v2@latest

# Verify installation
dalfox version
```

### httpx
```bash
# Install httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Alternative: Download binary
wget https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_linux_amd64.zip
unzip httpx_linux_amd64.zip
sudo mv httpx /usr/local/bin/
rm httpx_linux_amd64.zip

# Verify installation
httpx -version
```

### Katana
```bash
# Install Katana
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Verify installation
katana -version
```

### Arjun
```bash
# Install Arjun
pip3 install arjun

# Verify installation
arjun --help
```

### ParamSpider
```bash
# Install ParamSpider
pip3 install paramspider

# Alternative: Clone from GitHub
git clone https://github.com/devanshbatham/ParamSpider /opt/ParamSpider
cd /opt/ParamSpider
pip3 install -r requirements.txt
sudo ln -sf /opt/ParamSpider/paramspider.py /usr/local/bin/paramspider

# Verify installation
paramspider --help
```

---

## Subdomain & OSINT Tools

### Amass
```bash
# Install Amass
sudo apt install -y amass

# Alternative: Install via Go
go install -v github.com/owasp-amass/amass/v4/...@master

# Verify installation
amass -version
```

### Subfinder
```bash
# Install Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Alternative: Download binary
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_linux_amd64.zip
unzip subfinder_linux_amd64.zip
sudo mv subfinder /usr/local/bin/
rm subfinder_linux_amd64.zip

# Verify installation
subfinder -version
```

### theHarvester
```bash
# Install theHarvester
sudo apt install -y theharvester

# Alternative: Clone from GitHub
git clone https://github.com/laramies/theHarvester /opt/theHarvester
cd /opt/theHarvester
pip3 install -r requirements.txt
sudo ln -sf /opt/theHarvester/theHarvester.py /usr/local/bin/theHarvester

# Verify installation
theHarvester -h
```

---

## SMB/Network Enumeration Tools

### NetExec (nxc)
```bash
# Install NetExec (successor to CrackMapExec)
pip3 install netexec

# Alternative: Install from GitHub
pipx install git+https://github.com/Pennyw0rth/NetExec

# Verify installation
nxc --version
```

### Enum4linux
```bash
# Install Enum4linux
sudo apt install -y enum4linux

# Verify installation
enum4linux -h
```

### Enum4linux-ng
```bash
# Install Enum4linux-ng
pip3 install enum4linux-ng

# Alternative: Clone from GitHub
git clone https://github.com/cddmp/enum4linux-ng /opt/enum4linux-ng
cd /opt/enum4linux-ng
pip3 install -r requirements.txt
sudo ln -sf /opt/enum4linux-ng/enum4linux-ng.py /usr/local/bin/enum4linux-ng

# Verify installation
enum4linux-ng -h
```

### SMBMap
```bash
# Install SMBMap
sudo apt install -y smbmap

# Alternative: Install via pip
pip3 install smbmap

# Verify installation
smbmap -h
```

---

## Password Cracking Tools

### Hydra
```bash
# Install Hydra
sudo apt install -y hydra

# Verify installation
hydra -h
```

### John the Ripper
```bash
# Install John the Ripper
sudo apt install -y john

# Verify installation
john --version
```

### Hashcat
```bash
# Install Hashcat
sudo apt install -y hashcat

# Verify installation
hashcat --version
```

---

## White Box / SAST Tools

### Semgrep
```bash
# Install Semgrep
pip3 install semgrep

# Alternative: Install via package manager
# For newer Debian/Ubuntu:
# sudo apt install -y semgrep

# Verify installation
semgrep --version

# Update rules
semgrep --config auto --update
```

### Bandit (Python Security)
```bash
# Install Bandit
pip3 install bandit

# Verify installation
bandit --version
```

### Safety (Python Dependencies)
```bash
# Install Safety
pip3 install safety

# Verify installation
safety --version
```

### TruffleHog (Secret Scanner)
```bash
# Install TruffleHog v3
pip3 install trufflehog

# Alternative: Install via Go
go install github.com/trufflesecurity/trufflehog/v3@latest

# Verify installation
trufflehog --version
```

### Gitleaks
```bash
# Install Gitleaks
go install github.com/gitleaks/gitleaks/v8@latest

# Alternative: Download binary
wget https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz
tar -xzf gitleaks_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/
rm gitleaks_linux_x64.tar.gz

# Verify installation
gitleaks version
```

### Snyk (Commercial - Free tier available)
```bash
# Install Snyk CLI
npm install -g snyk

# Alternative: Standalone binary
curl -sL https://static.snyk.io/cli/latest/snyk-linux -o snyk
chmod +x snyk
sudo mv snyk /usr/local/bin/

# Authenticate (required)
snyk auth

# Verify installation
snyk --version
```

### OWASP Dependency Check
```bash
# Download latest release
VERSION=$(curl -s https://api.github.com/repos/jeremylong/DependencyCheck/releases/latest | jq -r '.tag_name' | sed 's/v//')
wget https://github.com/jeremylong/DependencyCheck/releases/download/v${VERSION}/dependency-check-${VERSION}-release.zip
unzip dependency-check-${VERSION}-release.zip -d /opt/
sudo ln -sf /opt/dependency-check/bin/dependency-check.sh /usr/local/bin/dependency-check
rm dependency-check-${VERSION}-release.zip

# Verify installation
dependency-check --version
```

### Ripgrep (for pattern scanning)
```bash
# Install Ripgrep
sudo apt install -y ripgrep

# Verify installation
rg --version
```

---

## Cloud Security Tools

### Prowler (AWS/Azure/GCP)
```bash
# Install Prowler
pip3 install prowler

# Alternative: Clone from GitHub
git clone https://github.com/prowler-cloud/prowler /opt/prowler
cd /opt/prowler
pip3 install -r requirements.txt
sudo ln -sf /opt/prowler/prowler.py /usr/local/bin/prowler

# Verify installation
prowler --version
```

### Scout Suite
```bash
# Install Scout Suite
pip3 install scoutsuite

# Verify installation
scout --version
```

### Trivy (Container Scanner)
```bash
# Install Trivy
sudo apt install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install -y trivy

# Alternative: Direct binary
wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz
tar -xzf trivy_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/
rm trivy_Linux-64bit.tar.gz

# Verify installation
trivy --version
```

### kube-hunter
```bash
# Install kube-hunter
pip3 install kube-hunter

# Verify installation
kube-hunter --help
```

### kube-bench
```bash
# Download latest release
wget https://github.com/aquasecurity/kube-bench/releases/latest/download/kube-bench_linux_amd64.tar.gz
tar -xzf kube-bench_linux_amd64.tar.gz
sudo mv kube-bench /usr/local/bin/
rm kube-bench_linux_amd64.tar.gz

# Verify installation
kube-bench version
```

### Docker Bench Security
```bash
# Clone Docker Bench
git clone https://github.com/docker/docker-bench-security.git /opt/docker-bench-security
chmod +x /opt/docker-bench-security/docker-bench-security.sh
sudo ln -sf /opt/docker-bench-security/docker-bench-security.sh /usr/local/bin/docker-bench-security

# Verify installation
docker-bench-security -h
```

### Checkov (IaC Scanner)
```bash
# Install Checkov
pip3 install checkov

# Verify installation
checkov --version
```

### Terrascan
```bash
# Install Terrascan
curl -L "$(curl -s https://api.github.com/repos/tenable/terrascan/releases/latest | jq -r '.assets[] | select(.name | contains("Linux_x86_64")) | .browser_download_url')" > terrascan.tar.gz
tar -xzf terrascan.tar.gz
sudo mv terrascan /usr/local/bin/
rm terrascan.tar.gz

# Verify installation
terrascan version
```

---

## Binary Analysis Tools

### checksec
```bash
# Install checksec
sudo apt install -y checksec

# Verify installation
checksec --version
```

### Binwalk
```bash
# Install Binwalk
sudo apt install -y binwalk

# Verify installation
binwalk --help
```

### Radare2
```bash
# Install Radare2
sudo apt install -y radare2

# Alternative: Install from source (latest)
git clone https://github.com/radareorg/radare2 /tmp/radare2
cd /tmp/radare2
sys/install.sh
cd -

# Verify installation
r2 -v
```

### Ropper
```bash
# Install Ropper
pip3 install ropper

# Verify installation
ropper --version
```

### one_gadget
```bash
# Install one_gadget
sudo gem install one_gadget

# Verify installation
one_gadget --version
```

### pwntools
```bash
# Install pwntools
pip3 install pwntools

# Verify installation
python3 -c "import pwn; print(pwn.version)"
```

### GDB with pwndbg
```bash
# Install GDB
sudo apt install -y gdb

# Install pwndbg
git clone https://github.com/pwndbg/pwndbg /opt/pwndbg
cd /opt/pwndbg
./setup.sh

# Verify installation
gdb --version
```

---

## Forensics Tools

### Volatility3
```bash
# Install Volatility3
pip3 install volatility3

# Alternative: Clone from GitHub
git clone https://github.com/volatilityfoundation/volatility3 /opt/volatility3
cd /opt/volatility3
pip3 install -r requirements.txt
sudo ln -sf /opt/volatility3/vol.py /usr/local/bin/vol.py

# Verify installation
vol.py --help
```

### Foremost
```bash
# Install Foremost
sudo apt install -y foremost

# Verify installation
foremost -V
```

### ExifTool
```bash
# Install ExifTool
sudo apt install -y exiftool

# Verify installation
exiftool -ver
```

### Steghide
```bash
# Install Steghide
sudo apt install -y steghide

# Verify installation
steghide --version
```

---

## Payload Generation Tools

### Metasploit Framework
```bash
# Install Metasploit Framework
sudo apt install -y metasploit-framework

# Alternative: Install from installer
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod +x msfinstall
sudo ./msfinstall

# Initialize database
sudo msfdb init

# Verify installation
msfvenom --version
```

---

## Browser Automation

### Playwright
```bash
# Install Playwright for Python
pip3 install playwright

# Install browser binaries
playwright install chromium

# Verify installation
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright installed')"
```

---

## Quick Install Scripts

### Install All Essential Tools (Kali Linux)
```bash
#!/bin/bash
# quick-install-essential.sh - Install essential MCP Kali Server tools

set -e

echo "[*] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "[*] Installing essential tools..."
sudo apt install -y \
    nmap masscan \
    ffuf gobuster feroxbuster dirsearch \
    nikto sqlmap wpscan \
    amass theharvester \
    enum4linux smbmap \
    hydra john hashcat \
    binwalk radare2 checksec \
    foremost exiftool steghide \
    metasploit-framework \
    ripgrep jq curl wget git

echo "[*] Installing Python tools..."
pip3 install --upgrade pip
pip3 install \
    flask requests psutil mcp \
    arjun paramspider \
    netexec enum4linux-ng \
    semgrep bandit safety trufflehog \
    prowler scoutsuite checkov \
    kube-hunter \
    ropper pwntools \
    volatility3 \
    playwright

echo "[*] Installing Playwright browsers..."
playwright install chromium

echo "[*] Installing Go tools..."
if command -v go &> /dev/null; then
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install github.com/hahwul/dalfox/v2@latest
    go install github.com/gitleaks/gitleaks/v8@latest
fi

echo "[*] Updating Nuclei templates..."
nuclei -update-templates 2>/dev/null || true

echo "[+] Installation complete!"
```

### Install All Tools (Full)
```bash
#!/bin/bash
# quick-install-full.sh - Install ALL MCP Kali Server tools

set -e

echo "[*] Running essential install first..."
./quick-install-essential.sh

echo "[*] Installing additional tools..."

# Rustscan
wget -q https://github.com/RustScan/RustScan/releases/download/2.3.0/rustscan_2.3.0_amd64.deb
sudo dpkg -i rustscan_2.3.0_amd64.deb
rm rustscan_2.3.0_amd64.deb

# Trivy
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install -y trivy

# one_gadget
sudo gem install one_gadget

# pwndbg
git clone https://github.com/pwndbg/pwndbg /opt/pwndbg 2>/dev/null || true
cd /opt/pwndbg && ./setup.sh

echo "[+] Full installation complete!"
```

### Verify All Installations
```bash
#!/bin/bash
# verify-tools.sh - Verify tool installations

echo "=== Network Scanning ==="
nmap --version 2>/dev/null && echo "✓ nmap" || echo "✗ nmap"
masscan --version 2>/dev/null && echo "✓ masscan" || echo "✗ masscan"
rustscan --version 2>/dev/null && echo "✓ rustscan" || echo "✗ rustscan"

echo ""
echo "=== Web Application ==="
ffuf -V 2>/dev/null && echo "✓ ffuf" || echo "✗ ffuf"
gobuster version 2>/dev/null && echo "✓ gobuster" || echo "✗ gobuster"
nuclei -version 2>/dev/null && echo "✓ nuclei" || echo "✗ nuclei"
nikto -Version 2>/dev/null && echo "✓ nikto" || echo "✗ nikto"
sqlmap --version 2>/dev/null && echo "✓ sqlmap" || echo "✗ sqlmap"

echo ""
echo "=== SAST/White Box ==="
semgrep --version 2>/dev/null && echo "✓ semgrep" || echo "✗ semgrep"
bandit --version 2>/dev/null && echo "✓ bandit" || echo "✗ bandit"
gitleaks version 2>/dev/null && echo "✓ gitleaks" || echo "✗ gitleaks"

echo ""
echo "=== Cloud Security ==="
trivy --version 2>/dev/null && echo "✓ trivy" || echo "✗ trivy"
checkov --version 2>/dev/null && echo "✓ checkov" || echo "✗ checkov"

echo ""
echo "=== Binary Analysis ==="
checksec --version 2>/dev/null && echo "✓ checksec" || echo "✗ checksec"
r2 -v 2>/dev/null && echo "✓ radare2" || echo "✗ radare2"
binwalk --help 2>/dev/null && echo "✓ binwalk" || echo "✗ binwalk"

echo ""
echo "=== Forensics ==="
foremost -V 2>/dev/null && echo "✓ foremost" || echo "✗ foremost"
exiftool -ver 2>/dev/null && echo "✓ exiftool" || echo "✗ exiftool"

echo ""
echo "=== Payload Generation ==="
msfvenom --version 2>/dev/null && echo "✓ msfvenom" || echo "✗ msfvenom"

echo ""
echo "Verification complete!"
```

---

## Environment Variables

Create a `.env` file or export these variables:

```bash
# Required for MCP Kali Server
export API_PORT=5000
export API_HOST=0.0.0.0
export KALI_API_KEY=your_secure_api_key_here

# Optional: Supabase integration
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=your_supabase_key

# Optional: GitHub integration
export TOKEN=your_github_token

# Optional: Command settings
export COMMAND_TIMEOUT=300
export CACHE_TTL=3600
export MAX_CACHE_SIZE=1000
```

---

## Starting the Server

```bash
# Start the API server
python3 kali_server.py

# Start with custom port
API_PORT=8080 python3 kali_server.py

# Start with API key
KALI_API_KEY=mysecretkey python3 kali_server.py

# Start the MCP client
python3 mcp_server.py --server http://localhost:5000
```

---

## Troubleshooting

### Common Issues

1. **"Command not found" errors**
   - Ensure the tool is installed: `which <tool>`
   - Add Go bin to PATH: `export PATH=$PATH:$(go env GOPATH)/bin`
   - Add local bin to PATH: `export PATH=$PATH:~/.local/bin`

2. **Permission denied errors**
   - Run with sudo for tools that require root
   - Check file permissions: `ls -la /usr/local/bin/<tool>`

3. **Python module not found**
   - Install missing module: `pip3 install <module>`
   - Use virtual environment: `python3 -m venv venv && source venv/bin/activate`

4. **Go tools not found**
   - Install Go: `sudo apt install golang`
   - Set GOPATH: `export GOPATH=$HOME/go`
   - Add to PATH: `export PATH=$PATH:$GOPATH/bin`

---

## References

- [Nmap Official](https://nmap.org/)
- [Nuclei by ProjectDiscovery](https://github.com/projectdiscovery/nuclei)
- [Semgrep](https://semgrep.dev/)
- [Trivy](https://github.com/aquasecurity/trivy)
- [Metasploit Framework](https://www.metasploit.com/)
- [Playwright](https://playwright.dev/)

---

*Last Updated: January 2026*
*MCP Kali Server v2.0*
