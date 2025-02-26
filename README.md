# GDPR Android Threat Analysis

Welcome to the **GDPR Android Threat Analysis**, a comprehensive environment designed for evaluating and executing privacy threat detection tools in the context of the General Data Protection Regulation (GDPR). This testbed enables users to analyze various privacy threats associated with mobile applications, particularly Android apps, and ensure compliance with GDPR standards.

## Project Overview

The GDPR Android Threat Analysis provides a structured environment for detecting and analyzing privacy threats in mobile applications. By leveraging various tools and scripts, researchers, developers, and security professionals can systematically evaluate the compliance of Android apps with GDPR principles.

## Directory Structure

The project is organized into the following directories:
```
|- Project Root
  |- PTs
  |- app_procesor
  |- download_agent
  |- apks
```
- **PTs**: Contains code and documentation for each privacy threat detection tool.
- **app_processor**: Code for identifying new medical health (mHealth) applications using a fine-tuned deBERTa model.
- **download_agent**: Scripts for automatically downloading APKs from the Google Play Store using a rooted Android device.
- **apks**: Directory for storing all application APK files for analysis.

## Privacy Threat Detection Tools

The project includes several privacy threat detection tools categorized as follows:

### PT1 - Consent
- **Purpose**: Analyze consent notices and detect potential GDPR violations related to consent in Android apps.
- **Components**:
  - Source code for identifying consent notices in Android apps.
  - Scripts for detecting potential GDPR consent violations.
  - A dataset containing identified consent notices in various apps.
- **Reference**: Based on the paper "Freely Given Consent? Studying Consent Notice of Third-Party Tracking and Its Violations of GDPR in Android Apps" (CCS 2022) by CISPA researchers.

### PT2 - Permissions
- **Purpose**: Analyze app permissions and assess the fidelity of permission descriptions.
- **Components**:
  - Script for evaluating permission descriptions (`permission.py`).
  - Documentation for the Permissions PT (`README.md`).

### PT3 & PT4 - Geolocation and Database Misconfigurations
- **Purpose**: Evaluate geolocation of database URLs and identify misconfigurations in databases.
- **Components**:
  - Script for analyzing database URLs (`geolocation.py`).
  - Scanning tool for detecting database misconfigurations (`scanner.py`).
  - Documentation on these tests (`README.md`).

### PT5 - Data Processing
- **Purpose**: Inspect and analyze data processing logs for GDPR compliance.
- **Components**:
  - Script for log analysis (`LogInspector.py`).
  - Documentation for the Data Processing PT (`README.md`).
  - Configuration file for log processing (`LogConfig.py`).

### PT6 - Data Sharing
- **Purpose**: Study the sharing of Personally Identifiable Information (PII) in Android apps and detect potential violations of GDPR.
- **Components**:
  - Script for detecting PII using string matching (`detecting-pii-string-matching.py`).
  - Tool for analyzing network traffic related to data sharing (`network-traffic-analysis.py`).
  - Documentation for the Data Sharing PT (`README.md`).
- **Reference**: Based on the paper "Share First, Ask Later (or Never?) - Studying Violations of GDPR's Explicit Consent in Android Apps" (USENIX Security 2021) by CISPA researchers.

## General Files

- **apks.csv**: A CSV file listing all APKs designated for testing against various privacy threat tools.
- **requirements.txt**: Specifies the Python dependencies required to run the provided scripts and tools.

## Installation

To set up the GDPR Privacy Threat Test Bed, follow these steps:

1. **Clone the repository:**
   
   ```bash
   git clone https://github.com/Anshuman1812-lab/GDPR-Android-Threat-Analysis.git
   cd gdpr-privacy-threat-test-bed
   
3. **Create the apks directory:**

   ```bash
   mkdir apks
   
5. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   
