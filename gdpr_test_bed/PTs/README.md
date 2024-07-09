# Privacy Threat Testbeds (PT) Root Directory

This directory houses subdirectories for various Privacy Threat (PT) testbeds. The directory structure is organized based on different PTs, and each subdirectory contains relevant scripts, tools, and documentation for conducting privacy threat assessments.

## Directory Structure:

*NOTE* All PTs assume there is an `apks` directory at the project root. This needs to be created after cloning the repo. Place all *.apk files there. 

### PT1 Consent:
Code from the paper: "Freely Given Consent? Studying Consent Notice of Third-Party Tracking and Its Violations of GDPR in Android Apps" (CCS 2022) by CISPA researchers (https://github.com/cispa/consent-notices/tree/main).

The repo has three main components:

1. Consent Notices Analysis presents the source code to identifying consent notices currently implemented in Android apps.
2. Automating GDPR Violations Detection presents the source code of our approaches to detecting potential GDPR consent violations.
3. Consent Notices Dataset contains the identified consent notices dataset in Android apps.

### PT2 Permissions:
- `permission.py`: Script for analyzing and assessing app permissions-description fidelity.
- `README.md`: Documentation for the Permissions PT.

### PT3&4 Geolocation and Database Misconfigurations:
- `geolocation.py`: Script for evaluating geolocation of database urls.
- `scanner.py`: Tool for scanning and identifying database misconfigurations.
- `README.md`: Detailed information on geolocation and database misconfigurations PT.

### PT5 Data Processing:
- `LogInspector.py`: Script for inspecting and analyzing data processing logs.
- `README.md`: Documentation for the Data Processing PT.
- `LogConfig.py`: Configuration file for log processing.

### PT6 DataSharing:

Contains code from the paper: "Share First, Ask Later (or Never?) - Studying Violations of GDPR's Explicit Consent in Android Apps" (USENIX Security 2021) by CISPA reaseachers (https://github.com/cispa/gdpr-consent/tree/main)


- `detecting-pii-string-matching.py`: Script for detecting Personally Identifiable Information (PII) using string matching.
- `network-traffic-analysis.py`: Tool for analyzing network traffic related to data sharing.
- `README.md`: Information on the Data Sharing PT.

## General Files:
- `apks.csv`: CSV file containing a list of APKs for testing each PT.
- `requirements.txt`: Python dependencies required for running the scripts.

## How to Use:
1. Navigate to the specific PT directory of interest.
2. Follow the instructions provided in the respective README.md file for each PT.
3. Run the scripts on the APKs listed in `apks.csv` to assess privacy threats.
4. Refer to the generated output files and documentation for analysis results.

Please ensure that you have the required dependencies installed as specified in `requirements.txt` before running any scripts.
