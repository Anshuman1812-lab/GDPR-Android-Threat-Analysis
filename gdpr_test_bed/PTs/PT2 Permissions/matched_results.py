import csv

def read_csv(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_csv(data, filename, fieldnames):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def filter_rows(csv_a, csv_b, output_csv):
    data_a = read_csv(csv_a)
    data_b = read_csv(csv_b)

    filtered_data = []
    for row_b in data_b:
        app_name_b = row_b['app_name']
        for row_a in data_a:
            package_name_a = row_a['Package Name']
            if app_name_b == package_name_a:
                filtered_data.append(row_b)
                break

    fieldnames = data_b[0].keys()
    write_csv(filtered_data, output_csv, fieldnames)

# Replace filenames with your actual filenames
csv_a_filename = '/home/viper18/Desktop/GDPR/gdpr_test_bed/PTs/PT2 Permissions/apk_metadata_filtered.csv'
csv_b_filename = '/home/viper18/Desktop/GDPR/gdpr_test_bed/PTs/PT2 Permissions/New Results/meta_data.csv'
output_csv_filename = '/home/viper18/Desktop/GDPR/gdpr_test_bed/PTs/PT2 Permissions/matched_results.csv'

filter_rows(csv_a_filename, csv_b_filename, output_csv_filename)
