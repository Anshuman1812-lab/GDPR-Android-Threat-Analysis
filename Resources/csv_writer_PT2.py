import os
import csv
import subprocess
from pathlib import Path

aapt_path = Path("/lib/android-sdk/build-tools/29.0.3/aapt") # Path to aapt

def get_appname(directory_path, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['Package Name','APK']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()

        # Iterate through files in the specified directory
        for filename in os.listdir(directory_path):
            if filename.endswith(".apk"):
                # Construct the full path to the APK file
                apk_path = os.path.join(directory_path, filename)
                
                # Use aapt to extract the package name
                result = subprocess.run([str(aapt_path), 'dump', 'badging', apk_path], capture_output=True, text=True)
                
                # Parse the package name from the output
                package_name = None
                for line in result.stdout.split('\n'):
                    if line.startswith("package:"):
                        package_name = line.split("'")[1]
                        break
                
                # Write the results to the CSV file
                csv_writer.writerow({'Package Name': package_name, 'APK': apk_path})

if __name__ == "__main__":
    directory_path = "/home/viper18/Desktop/GDPR/gdpr_test_bed/apks" # Location of apps
    output_csv = "apk_files_PT2.csv"

    get_appname(directory_path, output_csv)
