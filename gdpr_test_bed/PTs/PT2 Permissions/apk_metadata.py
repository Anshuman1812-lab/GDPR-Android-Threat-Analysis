from google_play_scraper import app
import csv

def get_metadata(apk_list):
    metadata_list = []
    error_apk_names = []
    for apk_name in apk_list:
        try:
            result = app(apk_name)
            metadata = {
                'Name': result['title'],
                'Package Name': result['appId'],
                'Developer': result['developer'],
                'Number of Downloads': result['installs'],
                'Number of Ratings': result['ratings'],
                'Average Rating': result['score'],
                'Number of Reviews': result['reviews']
            }
            metadata_list.append(metadata)
        except Exception as e:
            print(f"Error fetching metadata for {apk_name}: {e}")
            error_apk_names.append(apk_name)

    # Save error APK names to a new CSV
    if error_apk_names:
        error_csv_file = "failed_apk_list.csv"
        with open(error_csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(map(lambda x: [x], error_apk_names))
        print(f"Error APK names saved to: {error_csv_file}")

    return metadata_list

def save_to_csv(metadata_list, output_file):
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Package Name', 'Developer', 'Number of Downloads', 'Number of Ratings', 'Average Rating', 'Number of Reviews']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for metadata in metadata_list:
            writer.writerow(metadata)

def main(input_file, output_file):
    with open(input_file, 'r') as file:
        apk_list = file.read().splitlines()
    metadata_list = get_metadata(apk_list)
    save_to_csv(metadata_list, output_file)

if __name__ == "__main__":
    input_file = "apk_list.csv"  # Input file containing list of APKs, each APK in a new line
    output_file = "apk_metadata.csv"  # Output CSV file to save metadata
    main(input_file, output_file)
