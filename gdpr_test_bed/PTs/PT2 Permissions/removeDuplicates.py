import pandas as pd

def remove_duplicates(input_csv, output_csv):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv)

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    # input_csv = "firebaseProject.csv"
    # input_csv = "firebaseProjectNotFound.csv"
    input_csv = "apk_metadata.csv"  # Specify the input CSV file path
    # input_csv = "url_locations.csv"
    output_csv = "output.csv"  # Specify the output CSV file path

    remove_duplicates(input_csv, output_csv)
