#!/usr/bin/env python3
import argparse
import asyncio
import aiohttp
import aiofiles
import re
import time

from typing import List, Dict, Tuple

from bs4 import BeautifulSoup

API_URL = "http://ip-api.com/json"
TIMEOUT = 10  # seconds

# Regular expression to match proxy with protocol
PROXY_REGEX = re.compile(r"^(?:(?P<protocol>http|https|socks4|socks5):\/\/)?(?P<ip>[^:]+):(?P<port>\d+)$")

# Global file handle for immediate writing
output_file_handle = None

def parse_ip_analysis_table(html_content, soup):
    """
    Parse HTML table to extract IP analysis data
    Returns a dictionary with extracted information
    """
    result = {
        'ASN': None,
        'ISP_Name': None,
        'City': None,
        'Postal_Code': None,
        'Datacenter': None,
        'Blacklists': {},
        'Proxies': {},
        'Fraud_Score': None
    }

    rows = soup.find_all('tr')
    current_section = None

    for row in rows:
        th_title = row.find('th', class_='title')
        if th_title:
            current_section = th_title.get_text(strip=True)
            continue
        
        if row.find('td', class_='subtitle'):
            continue
        
        th = row.find('th')
        td = row.find('td')

        if th and td:
            field_name = th.get_text(strip=True)
            field_value = td.get_text(strip=True)

            if field_name == 'ASN':
                result['ASN'] = field_value
            elif field_name == 'Datacenter':
                result['Datacenter'] = field_value
            elif field_name == 'ISP Name':
                link = td.find('a')
                if link:
                    result['ISP_Name'] = link.get_text(strip=True)
                else:
                    result['ISP_Name'] = field_value
            elif field_name == 'City':
                result['City'] = field_value
            elif field_name == 'Postal Code':
                result['Postal_Code'] = field_value
            elif current_section == 'External Blacklists':
                risk_div = td.find('div', class_='risk')
                if risk_div:
                    status = risk_div.get_text(strip=True)
                    result['Blacklists'][field_name] = status
            elif current_section == 'Proxies':
                risk_div = td.find('div', class_='risk')
                if risk_div:
                    status = risk_div.get_text(strip=True)
                    result['Proxies'][field_name] = status

    fraud_score_match = re.search(r'Fraud Score: (\d+)', html_content)
    
    if fraud_score_match:
        result['Fraud_Score'] = fraud_score_match.group(1)
    result['Datacenter'] = (result['Datacenter'].upper() if result['Datacenter'] is not None else result['Datacenter'])
    
    return result

def convert_to_yes_no(status):
    """Convert risk status to YES/NO format"""
    if status and status.lower() in ['yes', 'high', 'detected']:
        return 'YES'
    elif status and status.lower() in ['no', 'low', 'clean', 'unknown']:
        return 'NO'
    else:
        return status

def format_scamalytics_output(parsed_data):
    """Format the scamalytics data into the required output format"""
    basic_info = f"{parsed_data['ASN']}, {parsed_data['ISP_Name']}, {parsed_data['City']}, {parsed_data['Postal_Code']}, {parsed_data['Datacenter']}, {parsed_data['Fraud_Score']}"

    blacklist_mapping = {
        'Firehol': 'Firehol',
        'IP2ProxyLite': 'IP2ProxyLite', 
        'IPsum': 'IPsum',
        'Spamhaus': 'Spamhaus',
        'X4Bnet Spambot': 'X4Bnet'
    }

    active_blacklists = []
    for service, status in parsed_data['Blacklists'].items():
        converted_status = convert_to_yes_no(status)
        if converted_status == "YES":
            if service in blacklist_mapping:
                active_blacklists.append(blacklist_mapping[service])

    proxy_mapping = {
        'Anonymizing VPN': 'vpn',
        'Tor Exit Node': 'tor',
        'Server': 'server',
        'Public Proxy': 'p.proxy',
        'Web Proxy': 'w.proxy',
        'Search Engine Robot': 'se.bot'
    }

    active_proxies = []
    for service, status in parsed_data['Proxies'].items():
        converted_status = convert_to_yes_no(status)
        if converted_status == "YES":
            if service in proxy_mapping:
                active_proxies.append(proxy_mapping[service])

    output_line = basic_info

    if active_blacklists:
        blacklist_json = "{" + ", ".join(f'"{bl}"' for bl in active_blacklists) + "}"
        output_line += f" {blacklist_json}"

    if active_proxies:
        proxy_json = "{" + ", ".join(f'"{proxy}"' for proxy in active_proxies) + "}"
        output_line += f" {proxy_json}"

    return output_line

async def check_scamalytics_through_proxy(ip: str, proxy_url: str, protocol: str) -> str:
    """Get scamalytics information through the working proxy with fallback"""
    # Extract IP from the input (remove port if present)
    IP = re.match(r'^[^:]+', str(ip)).group()
    
    # List of URLs to try (HTTPS first, then HTTP if needed)
    urls_to_try = [
        f'https://scamalytics.com/ip/{IP}',
        f'http://scamalytics.com/ip/{IP}'  # Fallback to HTTP
    ]
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    timeout = aiohttp.ClientTimeout(total=TIMEOUT * 3)  # More time for scamalytics
    
    # Try each URL until one works
    for full_url in urls_to_try:
        try:
            if protocol in ('socks4', 'socks5'):
                import aiohttp_socks
                if protocol == 'socks4':
                    connector = aiohttp_socks.ProxyConnector.from_url(proxy_url, rdns=True)
                else:  # socks5
                    connector = aiohttp_socks.ProxyConnector.from_url(proxy_url)
                
                async with aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    connector_owner=False
                ) as session:
                    try:
                        async with session.get(full_url, headers=headers, ssl=False) as response:
                            if response.status == 200:
                                html_content = await response.text()
                                
                                # Check if we got a valid scamalytics page
                                if 'scamalytics' in html_content.lower() or 'fraud score' in html_content.lower():
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    parsed_data = parse_ip_analysis_table(html_content, soup)
                                    return format_scamalytics_output(parsed_data)
                                else:
                                    continue  # Try next Ur l
                            elif response.status in [403, 503, 400]:
                                continue  # try next URL
                            else:
                                continue  # Try next url
                    except (aiohttp.ClientError, asyncio.TimeoutError):
                        continue  # Try next URL
            else:
                # HTTP/S proxy
                connector = aiohttp.TCPConnector(ssl=False, enable_cleanup_closed=True)
                async with aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    connector_owner=False
                ) as session:
                    try:
                        async with session.get(
                            full_url, 
                            headers=headers, 
                            proxy=proxy_url,
                            ssl=False
                        ) as response:
                            if response.status == 200:
                                html_content = await response.text()
                                
                                # Check if we got a valid scamalytics page
                                if 'scamalytics' in html_content.lower() or 'fraud score' in html_content.lower():
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                    parsed_data = parse_ip_analysis_table(html_content, soup)
                                    return format_scamalytics_output(parsed_data)
                                else:
                                    continue  # Try next URL
                            elif response.status in [403, 503, 400]:
                                continue  # Try next URL
                            else:
                                continue  # Try next URL
                    except (aiohttp.ClientError, asyncio.TimeoutError):
                        continue  # Try next URL
        
        except Exception:
            continue  # Try next URL
    
    # If all attempts failed, fall back to direct connection
    return get_scamalytics_info(ip)

def get_scamalytics_info(ip: str) -> str:
    """Get scamalytics information directly without proxy, ur ip may be blocked"""
    try:
        import requests
        
        # Extract IP from the input (remove port if present)
        IP = re.match(r'^[^:]+', str(ip)).group()
        full_url = f'https://scamalytics.com/ip/{IP}'
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

        response = requests.get(full_url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            parsed_data = parse_ip_analysis_table(html_content, soup)
            return format_scamalytics_output(parsed_data)
        else:
            return f"Error: HTTP {response.status_code} from scamalytics"
            
    except Exception as e:
        return f"Error getting scamalytics info: {str(e)}"

async def write_result_immediately(result: Dict, use_proxy_for_scamalytics: bool = False):
    """Write a single result to the output file immediately"""
    global output_file_handle
    
    if result.get('status') == 'Working' and output_file_handle:
        # Extract IP from proxy string for scamalytics check
        proxy_ip = result['ip'] if result['ip'] else result['proxy'].split(':')[0]
        
        # Get scamalytics info
        if use_proxy_for_scamalytics:
            proxy_url = f"{result['protocol']}://{result['proxy']}"
            print(f"🔍 Checking scamalytics for {proxy_ip} through proxy...")
            scamalytics_info = await check_scamalytics_through_proxy(proxy_ip, proxy_url, result['protocol'])
        else:
            print(f"🔍 Checking scamalytics for {proxy_ip} directly...")
            scamalytics_info = get_scamalytics_info(proxy_ip)
        
        # Format the output line
        output_line = (f"{result['protocol']}://{result['proxy']} - "
                      f"Country: {result.get('country', 'Unknown')}, "
                      f"Ping: {result.get('ping', 'N/A')}ms - "
                      f"{scamalytics_info}\n")
        
        await output_file_handle.write(output_line)
        await output_file_handle.flush()  # Ensure immediate write to disk
        
        # Also print to console for real-time feedback
        print(f"✅ {result['protocol']}://{result['proxy']} - Country: {result.get('country', 'Unknown')}, Ping: {result.get('ping', 'N/A')}ms")

async def check_proxy(proxy: str, protocol: str, use_proxy_for_scamalytics: bool = False) -> Tuple[bool, Dict]:
    """
    Check if a proxy works with the specified protocol
    
    Args:
        proxy: The proxy in format IP:PORT
        protocol: The protocol to use (http, https, socks4, socks5)
        use_proxy_for_scamalytics: Whether to use the proxy for scamalytics lookup
    
    Returns:
        Tuple of (success, result_dict)
    """
    formatted_proxy = f"{protocol}://{proxy}"
    proxies = {
        "http": formatted_proxy,
        "https": formatted_proxy
    }
    
    try:
        connector = None
        if protocol in ('socks4', 'socks5'):
            import aiohttp_socks
            if protocol == 'socks4':
                connector = aiohttp_socks.ProxyConnector.from_url(formatted_proxy, rdns=True)
            else:  # socks5
                connector = aiohttp_socks.ProxyConnector.from_url(formatted_proxy)
        
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        
        if connector:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                start_time = time.time()
                async with session.get(API_URL) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            "proxy": proxy,
                            "protocol": protocol,
                            "ip": data.get("query", ""),
                            "country": data.get("country", ""),
                            "ping": round(response_time * 1000),  # ms
                            "status": "Working"
                        }
                        # Write result immediately
                        await write_result_immediately(result, use_proxy_for_scamalytics)
                        return True, result
        else:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                async with session.get(API_URL, proxy=proxies.get('http')) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        data = await response.json()
                        result = {
                            "proxy": proxy,
                            "protocol": protocol,
                            "ip": data.get("query", ""),
                            "country": data.get("country", ""),
                            "ping": round(response_time * 1000),  # ms
                            "status": "Working"
                        }
                        # Write result immediately
                        await write_result_immediately(result, use_proxy_for_scamalytics)
                        return True, result
    except Exception as e:
        pass
    
    return False, {
        "proxy": proxy,
        "protocol": protocol,
        "status": "Failed"
    }

async def process_proxy(proxy_line: str, protocols: List[str], use_proxy_for_scamalytics: bool = False) -> List[Dict]:
    """Process a single proxy line with multiple protocols if needed"""
    results = []
    match = PROXY_REGEX.match(proxy_line.strip())
    
    if not match:
        return results
    
    proxy_data = match.groupdict()
    ip_port = f"{proxy_data['ip']}:{proxy_data['port']}"
    original_protocol = proxy_data.get('protocol')
    
    # Determine which protocols to test
    protocols_to_test = []
    if 'all' in protocols:
        protocols_to_test = ['http', 'socks4', 'socks5']
    elif protocols:  
        protocols_to_test = protocols
    elif original_protocol:  
        protocols_to_test = [original_protocol]
    else:   
        protocols_to_test = ['http', 'socks4', 'socks5']
    
    for protocol in protocols_to_test:
        success, result = await check_proxy(ip_port, protocol, use_proxy_for_scamalytics)
        if success:
            results.append(result)
    
    return results

async def process_proxy_batch(batch: List[str], protocols: List[str], use_proxy_for_scamalytics: bool = False) -> List[Dict]:
    """Process a batch of proxies concurrently"""
    tasks = [process_proxy(proxy_line, protocols, use_proxy_for_scamalytics) for proxy_line in batch]
    results = await asyncio.gather(*tasks)
    # Flatten list of lists
    return [item for sublist in results for item in sublist]

def validate_protocols(protocols: List[str]) -> List[str]:
    """Validate and normalize protocol arguments"""
    valid_protocols = []
    for protocol in protocols:
        protocol = protocol.lower().strip('-')
        if protocol in ['http', 'https', 'socks4', 'socks5', 'all']:
            if protocol == 'https':
                protocol = 'http'  # Treat https as http for proxy testing
            valid_protocols.append(protocol)
    
    return valid_protocols

async def main():
    global output_file_handle
    
    parser = argparse.ArgumentParser(description='Proxy Checker Tool with Scamalytics Integration')
    parser.add_argument('input_file', help='File containing proxies to check')
    parser.add_argument('-o', '--output', default='results.txt', help='Output file for working proxies')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use')
    parser.add_argument('-all', action='store_true', help='Test all proxy types per IP')
    parser.add_argument('-http', action='store_true', help='Test HTTP proxies')
    parser.add_argument('-socks4', action='store_true', help='Test SOCKS4 proxies')
    parser.add_argument('-socks5', action='store_true', help='Test SOCKS5 proxies')
    parser.add_argument('--use-proxy-for-scamalytics', action='store_true', 
                       help='Use the proxy itself for scamalytics lookups (recommended)')
    
    args = parser.parse_args()
    
    # Determine which protocols to check
    protocols = []
    if args.all:
        protocols = ['all']
    else:
        if args.http:
            protocols.append('http')
        if args.socks4:
            protocols.append('socks4')
        if args.socks5:
            protocols.append('socks5')
    
    protocols = validate_protocols(protocols)
    
    # Read proxies from file
    proxies = []
    try:
        async with aiofiles.open(args.input_file, 'r') as f:
            proxies = [line.strip() for line in await f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading proxy file: {e}")
        return
    
    print(f"Loaded {len(proxies)} proxies from {args.input_file}")
    print(f"Testing protocols: {', '.join(protocols) if protocols else 'Based on proxy format or all'}")
    print(f"Using {args.threads} threads")
    print(f"Results will be written to: {args.output}")
    if args.use_proxy_for_scamalytics:
        print("Using proxies for scamalytics lookups")
    else:
        print("Using direct connection for scamalytics lookups")
    print("Starting proxy checks... (Press Ctrl+C to stop and save current results)\n")
    
    # Open output file for immediate writing
    try:
        output_file_handle = await aiofiles.open(args.output, 'w')
        
        # Process proxies in batches
        total_working = 0
        batch_size = max(1, len(proxies) // args.threads)
        
        try:
            for i in range(0, len(proxies), batch_size):
                batch = proxies[i:i+batch_size]
                results = await process_proxy_batch(batch, protocols, args.use_proxy_for_scamalytics)
                
                # Count 
                batch_working = sum(1 for r in results if r.get('status') == 'Working')
                total_working += batch_working
                
                # Print progress
                print(f"Progress: {min(i+batch_size, len(proxies))}/{len(proxies)} - Total Working: {total_working}")
        
        except KeyboardInterrupt:
            print(f"\n⚠️  Proxy checking interrupted by user")
            print(f"Current results have been saved to {args.output}")
        
        finally:
            await output_file_handle.close()
    
    except Exception as e:
        print(f"Error opening output file: {e}")
        return
    
    # Print final summary
    print(f"\n📊 Final Summary:")
    print(f"Total proxies processed: {min(len(proxies), i+batch_size) if 'i' in locals() else 0}")
    print(f"Working proxies found: {total_working}")
    print(f"Results saved to: {args.output}")

if __name__ == "__main__":
    try:
        import aiohttp_socks
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        if missing_package == "aiohttp_socks":
            print("aiohttp_socks package is required for SOCKS proxy support.")
            print("Please install it with: pip install aiohttp-socks")
        elif missing_package == "requests":
            print("requests package is required.")
            print("Please install it with: pip install requests")
        elif missing_package == "bs4":
            print("BeautifulSoup4 package is required.")
            print("Please install it with: pip install beautifulsoup4")
        exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProxy checking interrupted by user")