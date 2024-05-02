import argparse
import requests
import socket
import threading
import time
import os

class BruteForceTester:
    def __init__(self, targets, wordlist, threads=10, timeout=5, follow_redirects=True, ports=None):
        self.targets = targets
        self.wordlist = wordlist
        self.threads = threads
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.ports = ports
        self.found_items = set()

    def check_uri(self, target, uri):
        url = f"{target}/{uri}"
        try:
            response = requests.get(url, timeout=self.timeout, allow_redirects=self.follow_redirects)
            if response.status_code == 200:
                print(f"Found: {url}")
                self.found_items.add(url)
        except requests.exceptions.RequestException:
            pass

    def check_dns_subdomain(self, target, subdomain):
        domain = f"{subdomain}.{target}"
        try:
            ip_address = socket.gethostbyname(domain)
            print(f"Found: {domain} - {ip_address}")
            self.found_items.add(domain)
        except socket.error:
            pass

    def check_virtual_host(self, target, host):
        headers = {'Host': host}
        try:
            response = requests.get(target, headers=headers, timeout=self.timeout, allow_redirects=self.follow_redirects)
            if response.status_code == 200:
                print(f"Found: {host}")
                self.found_items.add(host)
        except requests.exceptions.RequestException:
            pass

    def brute_force(self, target):
        with open(self.wordlist) as f:
            lines = f.readlines()
        for line in lines:
            uri = line.strip()
            self.check_uri(target, uri)
            self.check_dns_subdomain(target, uri)
            self.check_virtual_host(target, uri)

    def run(self):
        for target in self.targets:
            print(f"Testing {target}...")
            self.brute_force(target)
        print("Brute force testing completed.")

def main():
    parser = argparse.ArgumentParser(description=" PYFORCE - Brute force testing tool")
    parser.add_argument("targets", nargs="+", help="Target URL, IP address, or a file containing a list of targets")
    parser.add_argument("-w", "--wordlist", default="wordlist.txt", help="Wordlist file (default: wordlist.txt)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-timeout", "--timeout", type=float, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("-nr", "--no-redirects", action="store_false", help="Disable following redirects (default: enabled)")
    parser.add_argument("-p", "--ports", nargs="+", type=int, help="Custom ports to check")
    args = parser.parse_args()

    targets = []
    for target in args.targets:
        if target.startswith("http://") or target.startswith("https://"):
            targets.append(target.rstrip("/"))
        elif target.startswith("file://"):
            with open(target[7:]) as file:
                targets.extend([line.strip() for line in file])
        else:
            targets.append(target)

    tester = BruteForceTester(targets, args.wordlist, args.threads, args.timeout, args.no_redirects, args.ports)
    tester.run()

if __name__ == "__main__":
    main()
