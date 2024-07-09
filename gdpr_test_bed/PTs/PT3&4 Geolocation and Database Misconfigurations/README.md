# Firebase Misconfiguration Transparent

This testbed is based off of the [original Firebase Scanner](https://github.com/shivsahni/FireBaseScanner/blob/master/README.md) by [shivsahni](https://github.com/shivsahni). 

Noteworthy improvements include, porting to python3, multithreading in file searching, and the integration of pattern-matching techniques on JSON object keys, allowing the identification of personally identifiable information (PII) while ensuring the confidentiality of the actual data. In addition to these enhancements, the tool conducts a thorough geolocation analysis to determine the country of origin for the database, thereby scrutinizing for any potential cross-border data transfers.

## Prerequisites
- Python 3.x
- This script assumes you have decompiled the selected APK files during exection of `PT2 Permissions`. 

## Usage

```bash
python scanner.py
```

# Firebase Geolocation

This Python script serves as a tool for extracting geolocation information for a given dictionary of APK names and corresponding Firebase URLs. The script leverages DNS resolution to obtain the IP addresses associated with the URLs and queries the ipinfo.io API to retrieve geolocation details. Additionally, the script establishes a secure connection to the specified URLs and fetches SSL certificate information.

## Prerequisites
- Python 3.x
- To run the geolocation.py script individually, make sure to update the 'url_dict{}' dictionary in the main() with required details.

```bash
python geolocation.py
```

## Output

Upon execution, the tool produces three CSV files:

- **firebaseProject.csv:** This file encompasses the APK files, detailed information about their identified Firebase projects, providing insights into their security status, and found PII types.

- **firebaseProjectNotFound.csv:** A comprehensive list of Firebase URLs that were not located during the scanning process is presented in this file.

- **url_locations.csv:** A list of all the Firebase URLs detected in the scanner.py script, along with their country of origin.