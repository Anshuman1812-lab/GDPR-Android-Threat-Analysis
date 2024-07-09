from os import listdir
import csv
import subprocess
import argparse
import scanner
from concurrent.futures import ThreadPoolExecutor

class jadx: 
    
    def __init__(self, apks):
        self.apk_dict = {}
        with open(apks, encoding="utf-8-sig") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                apk_name = row[0]
                apk_path = row[1]
                self.apk_dict[apk_name] = apk_path
 
    def decompile_single(self, file_name):
        file_path = self.apk_dict[file_name]
        print(f"Decompiling {file_name} ... ")
        result = subprocess.run(["jadx " + file_path + " -d " + "./jadx_results/" + file_name.replace('.apk', '')], shell=True)
        print(f"Finished decompiling {file_name}")

    def decompile(self):
        # print(self.apk_dict)
        files = self.apk_dict.keys()
        print("Starting decompilation process")
        
        with ThreadPoolExecutor() as executor:
            executor.map(self.decompile_single, files)
        
        print(f"✅ Finished Decompiling {len(files)} apps\n")

def main():
    parser = argparse.ArgumentParser(description="Batch Decompile Directory of APK's")
    parser.add_argument('-l', '--list', dest='list', required=True, help='path to CSV containing details of apk files')

    args = parser.parse_args()
    csv_file = args.list
    jadx_obj = jadx(csv_file)
    jadx_obj.decompile()
    scanner.main()

if __name__ == "__main__":
    main()
