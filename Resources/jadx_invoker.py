from os import listdir
import subprocess
import argparse


class jadx: 
    
    def __init__(self, apks):
        self.system_path = True
        self.apk_dir = apks
 
    def decompile(self):
        print(self.apk_dir)
        count = 0
        files = [f for f in listdir(self.apk_dir)]
        print("Starting decompilation process")
        for file in files:
            print(f"Decompiling {file} ... ")
            result = subprocess.run(
                    ["jadx", self.apk_dir +'/'+ file,  "-d", "./jadx_results/" + file.replace('.apk', '')], shell=True
            )
            count = count + 1
         
        print(f"✅ Finished Decompiling {count} apps")

def main():
    parser = argparse.ArgumentParser(description="Batch Decompile Directory of APK's")
    # parser.add_argument('--jadxPath', help='path to jadx')
    parser.add_argument('--apks', help='path to apks')

    args = parser.parse_args()
    # apk_dir = args.apks
    apk_dir = '/home/viper18/Desktop/GDPR/gdpr_test_bed/apks/'
    jadx_obj = jadx(apk_dir)
    jadx_obj.decompile()

if __name__ == "__main__":
    main()
