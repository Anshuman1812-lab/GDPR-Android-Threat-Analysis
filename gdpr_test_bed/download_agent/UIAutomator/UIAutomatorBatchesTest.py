from UIAutomator import UIAutomator
from random import seed, shuffle

def main():
    packages = []
    package_file = '/Users/ethanmyers/gdpr_test_bed/download_agent/UIAutomatorTests/package_list_batch.txt'

    with open(package_file, 'r') as f:
        for package in f.readlines():
            packages.append(package.strip())
        f.close()
    seed(1)
    shuffle(packages)

    print(len(packages), 'packages')
    max_batch=7
    results = UIAutomator.bulk_playstore_install(packages, max_batch=max_batch)

    for package, result in results.items():
        print(f'{package}, Installed: {result[0]}, Time: {result[1]}')

if __name__ == '__main__':
    main()