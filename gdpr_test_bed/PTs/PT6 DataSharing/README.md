# Data Sharing Violations
Code and part of the README.md is from this paper: ["Share First, Ask Later (or Never?) - Studying Violations of GDPR's Explicit Consent in Android Apps" (USENIX Security 2021)](https://publications.cispa.saarland/3400/1/nguyen2021gdpr.pdf)

*Overview*: This tool performs analysis on Android applications wihtout user interaction (Only opening the app) and capturing network transmission data. We change the scope of prevoise work to focus on GDPR data sharing violation such as PII's that are sent without consnet. 

# Prerequisite
1. A rooted Android device (Testing done with Pixel 7a that is running Android 13).
2. Installing Frida for your devices (see this tutorial https://frida.re/docs/android/)
3. Installing mitmproxy for your server as well as the mitmproxy CA certificate has to be installed on the client Android devices (see this documentation https://docs.mitmproxy.org/stable/)

# How to Install
1. Pip install all requirements in gdpr_test_bed/PTs/requirements.txt
2. Start the Frida server on your Android devices (`adb shell "su -c /data/local/tmp/frida-server &"`)
3. Change the network setting on your Android devices to your Proxy server. 

## Network Traffic Analysis: 

In the first step of the testbed we aim to identify apps that send some data when started. To achieve that, we install the app in question and grant all requested permissions listed in the manifest, i.e., both install time and runtime permissions. Subsequently, we launch the app and record its network traffic.

`python network-traffic-analysis.py -s FA6AL0309062 -p 8080 -f apk_file_input.csv -o output/`

| Parameter  | Description |
| ------------- | ------------- |
| -s  | The Android device serial number  |
| -p  | The port of proxy server  |
| -f  | The csv file that contains package name and the corresponding path to the apk file. For example: each line in this csv file is a `"package_name","file_path"`  |
| -o  | The output directory |

## Traffic Log Analyzer (String-Matching Device-Bound Data): 

The second step is to identify personal data that is tied to the phone, such as the location, the AAID, or the MAC address. Since such information is accessible by apps, we extract the relevant values from the phone through the Android debug bridge to ensure we know these values for each phone.

| Data Type  | Description |
| ------------- | ------------- |
|AAID | Android Advertising ID|
|BSSID | Router MAC addresses of nearby hotspots|
|Email | Email address of phone owner|
|GPS | User location|
|IMEI | Mobile phone equipment ID|
|IMSI | SIM card ID|
|MAC | MAC address of WiFi interface|
|PHONE | Mobile phone’s number|
|SIM_SERIAL | SIM card ID|
|SERIAL | Phone hardware ID (serial number)|
|SSID | Router SSIDs of nearby hotspots|
|GSF ID | Google Services Framework ID|

To detect the above data, you can use this script (note that there are some data that could not be easily extracted by adb command, so you can use the Device ID app to get them, and then update this data accordingly in the script, i.e., the DEVICE_PII_DICT and GPS_DICT variables):

`python detecting-pii-string-matching.py -s FA6AL0309062 -f apk_file_input.csv -d output/`

| Parameter  | Description |
| ------------- | ------------- |
| -s  | The Android device serial number  |
| -f  | The csv file that contains package name and the corresponding path to the apk file. For example: each line in this csv file is a `"package_name","file_path"`  |
| -d  | The directory that contains the output of the network traffic analysis|

## Output

The output will contain a CSV file with the following columns:

| package_name | host_url      | key               |
|--------------|---------------|-------------------|
| value_1      | value_1_host  | value_1_key       |
| value_2      | value_2_host  | value_2_key       |
| ...          | ...           | ...               |

Where `key` represents the Personally Identifiable Information (PII) found in traffic logs, `host_url` repersents the domain the PII was sent, and `package_name` repersents the app in question. 


