import argparse
import requests
import socket
import threading
import time
import os
import json
import re
from colorama import Fore, Style
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import table
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings



class BruteForceTester:

    def __init__(self, targets, wordlist, threads=10, timeout=5, follow_redirects=True, ports=None, auth=None):
        self.targets = targets
        self.wordlist = wordlist
        self.threads = threads
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.ports = ports
        self.auth = auth
        self.found_items = set()
        self.lock = threading.Lock()

    def check_uri(self, target, uri):
        url = f"{target}/{uri}"
        try:
            response = requests.get(url, timeout=self.timeout, allow_redirects=self.follow_redirects, auth=self.auth)
            if response.status_code == 200:
                with self.lock:
                    print(Fore.GREEN + f"Found: {url}" + Style.RESET_ALL)
                    self.found_items.add(url)

        except requests.exceptions.RequestException as e:

            logging.debug(f"Error checking URI: {url} - {e}")

    def check_dns_subdomain(self, target, subdomain):
        domain = f"{subdomain}.{target}"
        try:
            
            ip_address = socket.gethostbyname(domain)
            with self.lock:
                print(Fore.GREEN + f"Found: {domain} - {ip_address}" + Style.RESET_ALL)
                self.found_items.add(domain)
        except socket.error as e:
            logging.debug(f"Error checking DNS subdomain: {domain} - {e}")

    def check_virtual_host(self, target, host):
        headers = {'Host': host}
        try:
            response = requests.get(target, headers=headers, timeout=self.timeout, allow_redirects=self.follow_redirects, auth=self.auth)
            if response.status_code == 200:
                with self.lock:
                    print(Fore.GREEN + f"Found: {host}" + Style.RESET_ALL)
                    self.found_items.add(host)
        except requests.exceptions.RequestException as e:
            logging.debug(f"Error checking virtual host: {host} - {e}")

    def check_directory(self, target, directory):
        url = f"{target}/{directory}"
        try:
            response = requests.get(url, timeout=self.timeout, allow_redirects=self.follow_redirects, auth=self.auth)
            if response.status_code == 200:
                with self.lock:
                    print(Fore.GREEN + f"Found: {url}" + Style.RESET_ALL)
                    self.found_items.add(url)
        except requests.exceptions.RequestException as e:
            logging.debug(f"Error checking directory: {url} - {e}")

    def brute_force(self, target):
        with open(self.wordlist) as f:
            lines = f.readlines()
        for line in lines:
            uri = line.strip()
            self.check_uri(target, uri)
            self.check_dns_subdomain(target, uri)
            self.check_virtual_host(target, uri)
            self.check_directory(target, uri)

    def run(self):
        threads = []
        for target in self.targets:
            logging.info(Fore.CYAN + f"Testing {target}..." + Style.RESET_ALL)
            for _ in range(self.threads):
                thread = threading.Thread(target=self.brute_force, args=(target,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        logging.info(Fore.YELLOW + "Brute force testing completed." + Style.RESET_ALL)
        return self.found_items

def main():

    parser = argparse.ArgumentParser(description="PYFORCE - Brute force testing tool")
    parser.add_argument("targets", nargs="+", help="Target URL, IP address, or a file containing a list of targets")
    parser.add_argument("-w", "--wordlist", default="wordlist.txt", help="Wordlist file (default: wordlist.txt)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-timeout", "--timeout", type=float, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("-nr", "--no-redirects", action="store_false", help="Disable following redirects (default: enabled)")
    parser.add_argument("-p", "--ports", nargs="+", type=int, help="Custom ports to check")
    parser.add_argument("-a", "--auth", help="Authentication credentials (username:password)")
    parser.add_argument("-o", "--output", help="Output file for JSON report")
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



    auth = None
    if args.auth:
        username, password = args.auth.split(":")
        auth = (username, password)

    tester = BruteForceTester(targets, args.wordlist, args.threads, args.timeout, args.no_redirects, args.ports, auth)
    found_items = tester.run()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(list(found_items), f, indent=4)

    print(Fore.MAGENTA + "Found items:" + Style.RESET_ALL)
    for item in found_items:
        print(item)

    kb = KeyBindings()

    @kb.add('c-c')

    def _(event):
        event.app.exit()

    completer = WordCompleter(['help', 'exit', 'run', 'targets', 'wordlist', 'threads', 'timeout', 'redirects', 'ports', 'auth', 'output'])

    while True:
        try:
            user_input = prompt('pyforce> ', completer=completer, history=FileHistory('.pyforce_history'), key_bindings=kb)
            if user_input == 'help':

                print(Fore.YELLOW + "Available commands:" + Style.RESET_ALL)
                print("  help - Show this help message")
                print("  exit - Exit the program")
                print("  run - Start the brute force testing")
                print("  targets - Set the target(s)")
                print("  wordlist - Set the wordlist file")
                print("  threads - Set the number of threads")
                print("  timeout - Set the request timeout")
                print("  redirects - Enable or disable following redirects")
                print("  ports - Set the custom ports to check")
                print("  auth - Set the authentication credentials")
                print("  output - Set the output file for JSON report")

            elif user_input == 'exit':
                break
            elif user_input == 'run':
                tester.run()
            elif user_input.startswith('targets'):
                _, *new_targets = user_input.split()
                tester.targets = new_targets
                print(Fore.GREEN + f"Targets set to: {', '.join(tester.targets)}" + Style.RESET_ALL)

            elif user_input.startswith('wordlist'):
                _, wordlist = user_input.split()
                tester.wordlist = wordlist
                print(Fore.GREEN + f"Wordlist set to: {tester.wordlist}" + Style.RESET_ALL)

            elif user_input.startswith('threads'):
                _, threads = user_input.split()
                tester.threads = int(threads)
                print(Fore.GREEN + f"Threads set to: {tester.threads}" + Style.RESET_ALL)

            elif user_input.startswith('timeout'):
                _, timeout = user_input.split()
                tester.timeout = float(timeout)
                print(Fore.GREEN + f"Timeout set to: {tester.timeout}" + Style.RESET_ALL)

            elif user_input.startswith('redirects'):
                _, value = user_input.split()
                tester.follow_redirects = value.lower() == 'true'
                print(Fore.GREEN + f"Following redirects: {tester.follow_redirects}" + Style.RESET_ALL)

            elif user_input.startswith('ports'):
                _, *ports = user_input.split()
                tester.ports = [int(port) for port in ports]
                print(Fore.GREEN + f"Custom ports set to: {', '.join(map(str, tester.ports))}" + Style.RESET_ALL)

            elif user_input.startswith('auth'):
                _, auth = user_input.split()
                username, password = auth.split(":")
                tester.auth = (username, password)
                print(Fore.GREEN + f"Authentication set to: {username}:{password}" + Style.RESET_ALL)

            elif user_input.startswith('output'):
                _, output = user_input.split()
                tester.output = output
                print(Fore.GREEN + f"Output file set to: {tester.output}" + Style.RESET_ALL)

            else:
                print(Fore.RED + "Invalid command. Type 'help' for available commands." + Style.RESET_ALL)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":

    import logging

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

    main()