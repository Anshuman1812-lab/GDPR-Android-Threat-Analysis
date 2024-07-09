from xml.dom import NotFoundErr
import xml.etree.ElementTree as ET
import string
import re
import nltk
import emoji
import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from google_play_scraper import app as gp_app
import subprocess
import os
import git # Used to get project root

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# data preprocessing
nltk.download('punkt')
nltk.download("stopwords")

class PT2:
    def __init__(self):
        # Huggingface repo path
        PRETRAINED_PATH = os.path.join('etham13', 'permissions_bert_uncased')

        self.labels = ['STORAGE', 'CONTACTS', 'LOCATION', 'CAMERA', 'MICROPHONE', 'SMS', 'CALL_LOG', 'PHONE', 'CALENDAR', 'SETTINGS', 'TASKS']
        self.label_to_permission = {
            'STORAGE': ["WRITE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE"],
            'CONTACTS': ["GET_ACCOUNTS", "READ_CONTACTS", "WRITE_CONTACTS"],
            'LOCATION': ["ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION"],
            'CAMERA': ["CAMERA"],
            'MICROPHONE': ["RECORD_AUDIO"],
            'SMS': ["READ_SMS", "SEND_SMS"],
            'CALL_LOG': ["READ_CALL_LOG"],
            'PHONE': ["CALL_PHONE"],
            'CALENDAR': ["READ_CALENDAR"],
            'SETTINGS': ["WRITE_SETTINGS"],
            'TASKS': ["GET_TASKS", "KILL_BACKGROUND_PROCESS"]
        }
        self.id2label = {idx: label for idx, label in enumerate(self.labels)}
        self.tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_PATH)
        self.model = AutoModelForSequenceClassification.from_pretrained(PRETRAINED_PATH)
        
        self.sentences_with_predictions_df = pd.DataFrame(columns=['app_id', 'sentence', 'predictions'])
        self.sentences = None
        self.description = ''
        self.apk_path = ''
        self.requested_permissions = set()
        self.labels_all = set()
        self.permission_gap_list = []
        self.df = None
        self.all_permissions = None

    def remove_emojis(self, text):
        return emoji.replace_emoji(text, replace='')

    def remove_html_tags(self, text):
        clean = re.compile("<.*?>")
        temp = re.sub(clean, "", text)
        return temp if temp else text

    def remove_urls(self, text):
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        return url_pattern.sub("", text) if isinstance(text, str) else text

    def remove_punctuation(self, text):
        translator = str.maketrans("", "", string.punctuation)
        return text.translate(translator)

    def preprocess_text(self):
        text_no_html = self.remove_html_tags(self.description)
        text_no_urls = self.remove_urls(text_no_html)
        text_no_emojis = self.remove_emojis(text_no_urls)
        return text_no_emojis.lower()

    def inference(self):
        sentence_predictions = []
        
        for sentence in self.sentences:
            encoding = self.tokenizer(sentence, return_tensors="pt", max_length=512, truncation=True)
            encoding = {k: v.to(self.model.device) for k, v in encoding.items()}
            
            outputs = self.model(**encoding)
            logits = outputs.logits

            sigmoid = torch.nn.Sigmoid()
            probs = sigmoid(logits.squeeze().cpu())
            predictions = np.zeros(probs.shape)
            predictions[np.where(probs >= 0.5)] = 1

            predicted_labels = [self.id2label[idx] for idx, label in enumerate(predictions) if label == 1.0]
            sentence_predictions.extend(predicted_labels)

            if len(predicted_labels) > 0:
                new_data = pd.DataFrame({
                'app_id': [self.app_name],
                'sentence': [sentence],
                'predictions': [predicted_labels]
                })
                
                self.sentences_with_predictions_df = pd.concat([self.sentences_with_predictions_df, new_data], ignore_index=True)
               
                for label in predicted_labels:
                    label_mapped = self.label_to_permission.get(label, [])
                    self.labels_all.update(label_mapped)
                       
    def decompile_apk(self):
        count = 0
        print("Starting decompilation process")
        print(f'self.path: {self.path}')
        print(f"Decompiling {self.app_name} ... ")
        
        self.output_dir = os.path.join(project_root, 'apks', 'jadx_results', self.app_name)
        os.makedirs(self.output_dir, exist_ok=True)
    
        command = ["jadx", self.path,  "-d", self.output_dir]
        result = subprocess.run(command)
        
        count = count + 1     
        print(f"Finished Decompiling {count} apps")
    
    def setup(self, app_name, path):
        self.app_name = app_name
        self.path = path
        try:
            result = gp_app(self.app_name, lang='en', country='us')
            self.description = result['description']
            self.description = self.preprocess_text()
            self.sentences = nltk.sent_tokenize(self.description)
            self.decompile_apk()
            self.inference()
            self.get_permissions()
        except NotFoundErr:
            print(f"App {self.app_name} not found in Google Play Store.")
            # Handle the not found error
            return  # Skip further processing for this app
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle any other exceptions
            return
        

    def get_permissions(self):
        try:
            permissions_list = []
            tree = ET.parse(os.path.join(self.output_dir, 'resources', 'AndroidManifest.xml'))
            root = tree.getroot()
            for permission in root.iter('uses-permission'):
                full_permission = permission.attrib.get('{http://schemas.android.com/apk/res/android}name')
                if "android.permission" in full_permission:
                    full_permission = full_permission.replace("android.permission.", "")
                    permissions_list.append(full_permission)
        except Exception as e:
            print(f"Error in permission getter: {e}")
        self.all_permissions = permissions_list
        self.requested_permissions = [permission for permission in permissions_list if any(permission in value for value in self.label_to_permission.values())]
        self.permission_gap = set(self.requested_permissions) - self.labels_all
        
        if len(self.permission_gap) > 0:
            print(f'Permission-description fidelity detected: {self.permission_gap}')
            self.permission_gap_list.append([self.app_name, True])
        else:
            self.permission_gap_list.append([self.app_name, False])
        print(self.permission_gap_list)

git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
project_root = git_repo.git.rev_parse("--show-toplevel")

app_analyzer = PT2()

csv_dir = os.path.join(project_root, 'PTs','apks.csv')
app_analyzer.df = pd.read_csv(csv_dir)
app_analyzer.df.columns =  ['app_name', 'path']
meta_data = []
for index, row in app_analyzer.df.iterrows():
    app_name = row['app_name']
    app_path = row['path']

    app_analyzer.setup(app_name, app_path)
    meta_data.append([app_name, app_analyzer.requested_permissions, app_analyzer.permission_gap, app_analyzer.labels_all, app_analyzer.all_permissions])

    app_analyzer.permission_gap = set()
    app_analyzer.labels_all = set()
    app_analyzer.requested_permissions = set()
 
app_analyzer.sentences_with_predictions_df.to_csv('sentences_with_predictions.csv')
df = pd.DataFrame(app_analyzer.permission_gap_list, columns=['app_name', 'permission_fidelity_detected'])
meta_data_df = pd.DataFrame(meta_data, columns=['app_name', 'filtered_requested_permission', 'predicted_permission','permission_gap','all_requested_permissions'])
df.to_csv('permission_description_fidelity_results.csv')
meta_data_df.to_csv('meta_data.csv')
