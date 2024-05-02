# Resources
- The tool can process a list of targets provided through a file or directly at the command line.
- PYFORCE uses a word list to try different combinations of URIs, subdomains, and virtual hosts.
- The tool can use simultaneous threads to speed up the Brute force process.
- You can set the request timeout, enable or disable automatic redirection, and specify custom ports for verification.
- The results found are printed on the console, indicating the type of item identified (URI, subdomain or virtual host) and its respective value.

# Use

- Run the pyforce.py script from the command line.
- Enter desired targets, you can provide ***URLs (http:// or https://), IP addresses, or a path to a file containing a list of targets.***
- Optionally, use arguments to customize execution:
  
![Py_image](https://github.com/mrfelpa/pyforce/assets/65371336/8362009f-adfd-4a36-8df8-5ec01e5ea961)

Example:

    ./pyforce.py http://hackingthissite.org -w Wordlist.txt -t 20

- This command will perform a brute force test on the ***http://hackingthissite.org target using the Wordlist.txt word list with 20 simultaneous threads.***

# License

- PYFORCE is licensed under the MIT license. See the LICENSE file for details.
- Feel free to modify it too.

# Disclaimer

- The author of the script is not responsible for the use of the script for illegal purposes.

- Use it responsibly and only for legitimate purposes, such as authorized penetration testing.

