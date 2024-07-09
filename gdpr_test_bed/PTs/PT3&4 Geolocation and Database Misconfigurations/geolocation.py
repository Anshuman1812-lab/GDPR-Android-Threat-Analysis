import csv
import json
import pprint
import re
import socket
import ssl
import subprocess
import sys
import dns.resolver

def get_location_by_url(hostname_dict):
    
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']

    rows = []

    with open('url_locations.csv', 'w', newline='') as f:
        writer = csv.writer(f) 
        writer.writerow(['APK', 'URL', 'Country'])

        for apk, hostname in hostname_dict.items():
        
            hostname_url = re.sub(r'^https://|(?<!\.)\/\.json$', '', hostname)

            try:
                answers = dns.resolver.resolve(hostname_url, 'A')
                ip = answers[0].to_text()
            except dns.resolver.NoAnswer:
                print(f"No DNS response for {hostname_url}")
                continue
        
            try:
                result = subprocess.run(
                    ["curl", f"http://ipinfo.io/{ip}"],
                    capture_output=True, text=True  
                )

            except:
                print("Error curl request failed")
                continue

            response_json = json.loads(result.stdout)

            country_name = response_json.get('country', 'N/A')

            row = [apk.split('--')[0], hostname, country_name]
            rows.append(row)

            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(socket.socket(), server_hostname=hostname_url)
            s.connect((hostname_url, 443))
            cert = s.getpeercert()

        writer.writerows(rows)

if __name__ == "__main__":
    url_dict = {
        'com.phonegap.dtrack': 'https://www.flipkart.com',
        'com.doctella.doc': 'https://www.snapdeal.com',
        'com.trainerize.rpmathlete': 'https://www.amazon.in',
        'com.trainerize.prestigestrengthfitness': 'https://com-trainerize-trainerize.firebaseio.com/.json',
        'com.sccfitness': 'https://mywellness-app-3.firebaseio.com/.json',
        'com.fourdesire.plantnanny2': 'https://plant-nanny-2.firebaseio.com/.json'
    }
    get_location_by_url(url_dict)