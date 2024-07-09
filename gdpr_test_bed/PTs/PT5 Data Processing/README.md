# Data Processing Violations

This tool contains a `LogInspector` class that is used to analyze Android log data for Personally Identifiable Information (PII). It processes log files and corresponding PII log ID files to identify and analyze instances where sensitive information may have been exposed.

## Prerequisites

1. Before using the `LogInspector` class, ensure that the necessary directories are set up, containing the required log and PII log ID files. Additionally, check the configuration in the `LogConfig.py` file.

2. Pip install all requirements in gdpr_test_bed/PTs/requirements.txt

## Usage

To use the `LogInspector`, instantiate the class and call the desired analysis methods.

## Configuration

The configuration for the `LogInspector` is handled through the `LogConfig.py` file. It contains settings:

1. List of tags to exclude when looking for PII exposures. Typically used for tags that are system-related and not app-specific.

2. Specific false positives and other instance to disregard when looking for PII exposures.

## Methods

- `get_pii_types(update=True)`: Compile a list of PII types that may have been exposed within logs.
- `log_piilogid_join(log_path, piilogid_path, override=False)`: Create a new file in the join directory, representing an inner join between each PII log ID entry and its corresponding log entry.
- `log_pid_tracking(log_path)`: Parse through the given log file and record Process IDs (PIDs) based on origin.
- `log_pii_analysis(csv_file, override=False, filter_excluded_cases=False, filter_excluded_tags=False, activity_manager_only=False, app_package_only=False)`: Analyze log files for PII information and write results to a CSV file.
- `log_tag_analysis(csv_file)`: Analyze tag data (frequency, etc.) within the log files.

## Example Usage

```python
from LogConfig import *
from LogInspector import LogInspector

def main():
     # Usage requires class object
    logcat_inspector = LogInspector(verbose=True)

    # Equivalent to PII Exposure Stats sheet
    #logcat_inspector.log_pii_analysis('results-raw.csv', override=False, filter_excluded_cases=True)

    # Equivalent to Filtered PII Stats and App-PII Matrix sheets
    #logcat_inspector.log_pii_analysis('results-tag-filter.csv', override=False, filter_excluded_cases=True, filter_excluded_tags=True)

    # Equivalent to App-PII Matrix (AM-Packages Only) sheet
    #logcat_inspector.log_pii_analysis('results-am-only.csv', override=False, filter_excluded_cases=True, filter_excluded_tags=True,
    #                                  activity_manager_only=True)

    # Run log-pii analysis with all filters enabled (equivalent to App-PII Matrix (App-Package Only) sheet) 
    logcat_inspector.log_pii_analysis('results-all-filters.csv', override=False, filter_excluded_cases=True, filter_excluded_tags=True,
                                      activity_manager_only=True, app_package_only=True)
    
    # Run log tag analysis (equivalent to Log Tags sheet)
    logcat_inspector.log_tag_analysis('tags.csv')

if __name__ == '__main__':
    main()
```
