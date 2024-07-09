import os
import subprocess

apk_dir = '/home/viper18/Desktop/GDPR/gdpr_test_bed/apks/' # Local path of the downloaded apk files

result = subprocess.run(["rm -rf " + apk_dir + "*.split_*"], shell=True)

for filename in os.listdir(apk_dir):
    if not filename.endswith('.apk'):
        print(f'{filename}') # List out all non-apk files in the directory.

print(f'Split configuration files removed successfully!!!')
