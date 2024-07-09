# GDPR Privacy Threat Test Bed

Welcome to the Privacy Threats Test Bed, a comprehensive environment for evaluating and executing privacy threat detection tools. This test bed is designed to assess and analyze various privacy threats in regards to the General Data Protection Regulation (GDPR).

## Structure
```
|- Project Root
  |- PTs
  |- app_procesor
  |- download_agent
  |- apks
```

1) *PTs*: Provides code and detailed instructions for each privacy threat detection tool in their respective README.md files located in the `/Pts/PT x` directories. There is a overall README.md located in `./PTs` that gives a short overview of each privacy threat.
2) *app_processor*: Provides code to find new medical health (mhealth) apps using a [fine-tuned deBERTa model](https://huggingface.co/etham13/MHealth_app_classifier)
3) *download_agent*: Provides scripts to automatically download apks though a rooted android devices google play store.
4) *apks*: Directory where all application APK files are to be placed. 

## Instructions for Executing Privacy Threat Detection Tools

Navigate to the specific README.md file in the corresponding `./Pts/PT x` directory to find comprehensive instructions on executing each privacy threat detection tool. 
