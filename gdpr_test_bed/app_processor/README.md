# App Processor

## Overview

The `AndrozooProcessor` class is designed to process apks from the Androzoo dataset, specifically focusing on building a dataset of mhealth apps and their descriptions. It includes functionality to fetch app details, build a dataset, parse and clean the dataset, and finally, predict the mhealth apps using a fine-tuned deBERTa model.

## Class Methods

### 1. `__init__(self, config_path=None)`

- Initializes the AndrozooProcessor with default values.

### 2. `build_dataset(self)`

- Builds a dataset of apps and their descriptions by fetching details from the google play store (EU)
- Uses multi-threading for parallel execution to improve efficiency.
- The resulting dataset is stored in a Pandas DataFrame and saved to a CSV file named `apps_df.csv`.

### 3. `parse_and_clean(self)`

- Parses and cleans the Androzoo dataset for potential apps.
- Reads a filtered Androzoo CSV file, removes quotes from app names, and selects a subset of app names for further processing.
- Returns a list of app names.

### 4. `parse_apps(self)`

- Parses the descriptions of apps in the dataset and predicts whether they are health-related using the fine-tuned model.
- Outputs the list of health-related apps (`mhealth_apps`) and prints progress during processing.

## Usage

1. Instantiate the `AndrozooProcessor` class.
2. Call the `parse_and_clean` method to prepare the dataset for further processing.
3. Call the `build_dataset` method to fetch app details and build the dataset.
4. Call the `parse_apps` method to predict health-related apps.


## Example

```python
# Instantiate AndrozooProcessor 
processor = AndrozooProcessor()

# Parse and clean the dataset
app_id_list = processor.parse_and_clean()

# Build the dataset
processor.build_dataset()

# Parse apps and predict health-related apps
processor.parse_apps()
