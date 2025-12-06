# Proxy Checkers

Two Python tools for validating and analyzing proxy servers with different levels of detail.

---

## Tools

### 1. proxy_checker_simple.py
Basic proxy validation tool that tests connectivity and response time.

**Features:**
- Tests HTTP, SOCKS4, and SOCKS5 proxies
- Validates proxy functionality via ip-api.com
- Reports country and ping time
- Multi-threaded for fast processing

**Output Format:**
```
socks5://68.1.210.189:4145 - Country: United States, Ping: 1542ms
socks5://47.251.87.74:85 - Country: United Kingdom, Ping: 6570ms
socks5://142.54.235.9:4145 - Country: United States, Ping: 1411ms
```

**Usage:**
```bash
python proxy_checker_simple.py proxies.txt -o working_proxies.txt -t 50
python proxy_checker_simple.py proxies.txt -all          # Test all protocols
python proxy_checker_simple.py proxies.txt -http -socks5 # Test specific protocols
```

---

### 2. proxy_checker_with_scamalytics.py
Advanced proxy validator with comprehensive threat intelligence integration.

**Features:**
- All features from simple checker
- Scamalytics fraud score analysis
- ISP and datacenter detection
- Blacklist checking (Firehol, IPsum, Spamhaus, X4Bnet)
- Proxy type detection (VPN, Tor, Public Proxy, Web Proxy)
- Can use proxies themselves for scamalytics lookups (bypasses rate limits)
- Real-time results writing
- Graceful interrupt handling (Ctrl+C saves current results)

**Output Format:**
```
socks5://184.181.178.33:4145 - Country: United States, Ping: 1283ms - 22773, Cox Communications Inc., Pensacola, 32516, NO, 17 {"Firehol", "IPsum", "X4Bnet"} {"p.proxy"}
socks5://192.111.137.37:18762 - Country: United States, Ping: 2397ms - 46562, Total Server Solutions L.L.C., Atlanta (Fairlie-Poplar), 30303, UNKNOWN, 0 {"Firehol", "IPsum"} {"vpn"}
```

**Output Breakdown:**
```
[protocol]://[ip]:[port] - Country: [country], Ping: [ms] - [ASN], [ISP], [City], [Postal], [Datacenter], [FraudScore] {[Blacklists]} {[ProxyTypes]}
```

**Usage:**
```bash
# Basic usage (direct scamalytics lookup)
python proxy_checker_with_scamalytics.py proxies.txt -o results.txt -t 50

# Use proxies for scamalytics (recommended - bypasses IP rate limits)
python proxy_checker_with_scamalytics.py proxies.txt -o results.txt --use-proxy-for-scamalytics

# Test specific protocols
python proxy_checker_with_scamalytics.py proxies.txt -socks5 -o socks_only.txt

# Test all protocols per IP
python proxy_checker_with_scamalytics.py proxies.txt -all -o all_protocols.txt
```

---

## Installation

### Simple Checker Requirements:
```bash
pip install aiohttp aiofiles aiohttp-socks
```

### Advanced Checker Requirements:
```bash
pip install aiohttp aiofiles aiohttp-socks requests beautifulsoup4
```

---

## Input Format

Both tools accept proxy lists in the following formats:
```
192.168.1.1:8080
http://192.168.1.1:8080
socks5://192.168.1.1:1080
```

If no protocol is specified, the tool will test based on command-line flags or test all protocols by default.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `input_file` | File containing proxies to check (one per line) |
| `-o, --output` | Output file for working proxies (default: results.txt) |
| `-t, --threads` | Number of concurrent threads (default: 10) |
| `-all` | Test all proxy protocols (HTTP, SOCKS4, SOCKS5) per IP |
| `-http` | Test only HTTP/HTTPS proxies |
| `-socks4` | Test only SOCKS4 proxies |
| `-socks5` | Test only SOCKS5 proxies |
| `--use-proxy-for-scamalytics` | Use proxy itself for scamalytics lookups (advanced checker only) |

---

## Scamalytics Data Fields

The advanced checker provides detailed threat intelligence:

- **ASN**: Autonomous System Number
- **ISP**: Internet Service Provider name
- **City/Postal**: Geographic location
- **Datacenter**: YES/NO - indicates if IP is from a datacenter
- **Fraud Score**: 0-100 risk score (higher = more suspicious)
- **Blacklists**: External blacklist status (Firehol, IPsum, Spamhaus, X4Bnet)
- **Proxy Types**: Detected proxy/VPN types (vpn, tor, p.proxy, w.proxy, se.bot, server)

---

## Performance Tips

1. **Use `--use-proxy-for-scamalytics`** when checking large lists to avoid IP-based rate limiting
2. **Adjust thread count** based on your network: `-t 100` for fast connections, `-t 20` for stability
3. **Interrupt safely** with Ctrl+C - current results are automatically saved
4. **Test specific protocols** first if you know your proxy types to save time

---

## Use Cases

**Simple Checker:**
- Quick proxy validation
- Basic connectivity testing
- When you don't need threat intelligence

**Advanced Checker:**
- Proxy security assessment
- Fraud detection and risk analysis
- Identifying datacenter vs residential IPs
- Finding clean proxies (no blacklists)
- Detecting proxy/VPN types for specific use cases

---

## Notes

- Both tools validate proxies against `ip-api.com` for geo-location
- The advanced checker queries `scamalytics.com` for threat intelligence
- Results are written in real-time (safe to interrupt)
- Failed proxies are silently discarded from output
- HTTPS proxies are tested as HTTP (standard proxy behavior)



[back to top](#proxy-checkers)

[HOME](/README.md)