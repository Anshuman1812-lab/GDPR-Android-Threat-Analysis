# Permission-Description Fidelity Analyzer

*Overview*: This tool analyzes Android applications (APKs) to identify requested permissions and assess the fidelity of permission descriptions using a fine-tuned BERT model. The analysis involves decompiling the APKs, processing the app descriptions, and predicting potential requested permissions based on the app's description.

For example let’s say the model can predict xyz permissions. Based on an application description the model predicts the app is using x and y permissions. But within the manifest we see the app is requesting x, y and z permissions. This would be a permission-description fidelity issue. Hence a gap between the requested permissions and the permissions a user would expect via reading the apps description.

The fine-tuned model can be found [here](https://huggingface.co/etham13/permissions_bert_uncased/settings)

## Prerequisites
- Python 3.x
- Huggingface login token

## Setup

1. Install the required dependencies in gdpr_test_bed/PTs/requirements.txt
2. Replace the placeholder HF token in the `login` function with your Hugging Face token (commented out by default).

## Usage

1. Update the `apk_files_PT2.csv` file with the names and paths of the APKs to analyze.
2. Run the script using the command:

```bash
python permission.py
```

## Output

### 1. `sentences_with_predictions.csv`

This file contains detailed results for each app, including the app ID, individual sentences from the app's description, and the predicted permissions based on the model's inference.

| app_id         | sentence                                      | predictions   |
| -------------- | --------------------------------------------- | ------------- |
| app| "record and track your snoring with the no.1 snore app." | ['MICROPHONE'] |

### 2. `permission_description_fidelity_results.csv`

This file provides a summary of permission fidelity for each app, indicating whether there is a permission description fidelity (PFD) detected. It includes the app name and a boolean value (True/False) representing the presence of PFD.

| app_name         | permission_description_fidelity |
| ---------------- | -------------------------------- |
| app | True                            |

In the example above, an app has a detected permission description fidelity. 

### 3. `meta_data.csv`

This file contains five columns: *app_name, requested_filtered_permissions, permission_gap, predicted_permissions, all_requested_permissions*.

 - *Filtered_requested_permissions* gathers the permissions out of the manifest file and only keeps the permissions the model can predict.

 - *All_requested_permissions* returns ALL permissions requested within the apps manifest file, even if the model was not fine tuned to predict them.

 - *Predicted_permissions* is the output from the fine tuned model.

 - *Permission_gap* shows if there are permissions that were requested within the manifest file but were not detected by the model.