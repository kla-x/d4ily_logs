#!/usr/bin/env python3
import argparse
import asyncio
import aiohttp
import aiofiles
import re
import time
from typing import List, Dict, Tuple

API_URL = "http://ip-api.com/json"
TIMEOUT = 10  # seconds

# Regular expression to match proxy with protocol
PROXY_REGEX = re.compile(r"^(?:(?P<protocol>http|https|socks4|socks5):\/\/)?(?P<ip>[^:]+):(?P<port>\d+)$")

async def check_proxy(proxy: str, protocol: str) -> Tuple[bool, Dict]:
    """
    Check if a proxy works with the specified protocol
    
    Args:
        proxy: The proxy in format IP:PORT
        protocol: The protocol to use (http, https, socks4, socks5)
    
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
                        return True, {
                            "proxy": proxy,
                            "protocol": protocol,
                            "ip": data.get("query", ""),
                            "country": data.get("country", ""),
                            "ping": round(response_time * 1000),  # ms
                            "status": "Working"
                        }
        else:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                async with session.get(API_URL, proxy=proxies.get('http')) as response:
                    response_time = time.time() - start_time
                    if response.status == 200:
                        data = await response.json()
                        return True, {
                            "proxy": proxy,
                            "protocol": protocol,
                            "ip": data.get("query", ""),
                            "country": data.get("country", ""),
                            "ping": round(response_time * 1000),  # ms
                            "status": "Working"
                        }
    except Exception as e:
        pass
    
    return False, {
        "proxy": proxy,
        "protocol": protocol,
        "status": "Failed"
    }

async def process_proxy(proxy_line: str, protocols: List[str]) -> List[Dict]:
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
    elif protocols:  # Specific protocols from command line
        protocols_to_test = protocols
    elif original_protocol:  # Protocol from proxy string
        protocols_to_test = [original_protocol]
    else:  # No protocol specified anywhere, test all
        protocols_to_test = ['http', 'socks4', 'socks5']
    
    for protocol in protocols_to_test:
        success, result = await check_proxy(ip_port, protocol)
        if success:
            results.append(result)
    
    return results

async def process_proxy_batch(batch: List[str], protocols: List[str]) -> List[Dict]:
    """Process a batch of proxies concurrently"""
    tasks = [process_proxy(proxy_line, protocols) for proxy_line in batch]
    results = await asyncio.gather(*tasks)
    # Flatten list of lists
    return [item for sublist in results for item in sublist]

async def save_results(results: List[Dict], output_file: str):
    """Save results to the specified output file"""
    async with aiofiles.open(output_file, 'w') as f:
        for result in results:
            if result.get('status') == 'Working':
                await f.write(f"{result['protocol']}://{result['proxy']} - Country: {result.get('country', 'Unknown')}, Ping: {result.get('ping', 'N/A')}ms\n")

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
    parser = argparse.ArgumentParser(description='Proxy Checker Tool')
    parser.add_argument('input_file', help='File containing proxies to check')
    parser.add_argument('-o', '--output', default='results.txt', help='Output file for working proxies')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads to use')
    parser.add_argument('-all', action='store_true', help='Test all proxy types per IP')
    parser.add_argument('-http', action='store_true', help='Test HTTP proxies')
    parser.add_argument('-socks4', action='store_true', help='Test SOCKS4 proxies')
    parser.add_argument('-socks5', action='store_true', help='Test SOCKS5 proxies')
    
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
    
    # Process proxies in batches
    all_results = []
    batch_size = max(1, len(proxies) // args.threads)
    
    for i in range(0, len(proxies), batch_size):
        batch = proxies[i:i+batch_size]
        results = await process_proxy_batch(batch, protocols)
        all_results.extend(results)
        
        # Print progress
        working = sum(1 for r in all_results if r.get('status') == 'Working')
        print(f"Progress: {min(i+batch_size, len(proxies))}/{len(proxies)} - Working: {working}")
    
    # Save results to file
    await save_results(all_results, args.output)
    
    # Print summary
    working = sum(1 for r in all_results if r.get('status') == 'Working')
    print(f"\nSummary:")
    print(f"Total proxies checked: {len(proxies)}")
    print(f"Working proxies: {working}")
    print(f"Results saved to {args.output}")
    
    # Print by protocol type
    protocols_found = {}
    for r in all_results:
        if r.get('status') == 'Working':
            protocol = r.get('protocol', 'unknown')
            protocols_found[protocol] = protocols_found.get(protocol, 0) + 1
    
    for protocol, count in protocols_found.items():
        print(f"Working {protocol.upper()} proxies: {count}")

if __name__ == "__main__":
    try:
        import aiohttp_socks
    except ImportError:
        print("aiohttp_socks package is required for SOCKS proxy support.")
        print("Please install it with: pip install aiohttp-socks")
        exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProxy checking interrupted by user")