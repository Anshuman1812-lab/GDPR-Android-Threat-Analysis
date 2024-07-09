from UIAutomator import UIAutomator, ADB_PATH, DEVICE
import csv
from random import seed, shuffle
import subprocess

def get_package_size(package):
    command = [ADB_PATH, '-s', DEVICE, 'shell', 'pm', 'path', package]
    output = subprocess.run(command, capture_output=True, check=True).stdout.decode()
    paths = output.split('\n')
    size = 0
    for path in paths:
        if len(path) <= len('package:'):
            continue
        path = path[len('package:'):].strip()
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'stat', '-c', '%s', path]
        size += int(subprocess.run(command, capture_output=True, check=True).stdout.decode())
    return float(size)

def main():
    csv_file = 'UIAutomatorTest.csv'
    packages = []
    package_file = 'package_list_small.txt'

    with open(package_file, 'r') as f:
        for package in f.readlines():
            packages.append(package.strip())
        f.close()
    seed(1)
    shuffle(packages)

    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['Package Name', 'Size (MB)', 'Install Time (Seconds)']
        writer.writerow(header)
        f.close()

    for package in packages:
        installed, install_time = UIAutomator.playstore_install(package)
        if installed:
            print(f'Install time: {round(install_time, 6)} seconds')
            # Get size in Megabytes
            size = get_package_size(package) / 1000000
            print(f'Size: {size} MB')
            print(f'Writing results for {package} to {csv_file}')
            result_row = [package, size, round(install_time, 6)]
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(result_row)
                f.close()

            print(f'Uninstalling {package}')
            UIAutomator.uninstall_package(package)
        print()

if __name__ == '__main__':
    main()