# Default values for LogInspector initialization
LOG_DIR, LOG_EXT = 'logs', '.log'
PIILOGID_DIR, PIILOGID_EXT = 'piilogs', '.piilog.id'
JOIN_DIR, JOIN_EXT = 'join', 'join.id'
OUTPUT_DIR = 'results'
ENCODING = 'ISO-8859-1'

"""
Format for join.id entries (delimited by spaces):
line_number pii_type position* date time process_id thread_id level tag message
*Starting from date

Specific false positives and other instance to disregard when looking for PII exposures
Excluded case format: 'pii_type': (index (from join.id file), 'exception_string')
'pii_type' can a substring to cover multiple PII types
"""
EXCLUDED_CASES = {
    # False positive 1: timestamp mistaken for latitude
    'latitude': (4, '51.0'),
}

# List of tags to exclude when looking for PII exposures
# Typically used for tags that are system-related and not app-specific
EXCLUDED_TAGS = [
    'PasspointManager:',
    'A', 
    'SetupWizard:',
    'Monkey',
    'cr_JCR-WEB:',
    'StorageManagerService:',
    'WifiClientModeImpl:',
    'WifiClientModeImpl[wlan0]:',
    'ConnectivityService:',
    'DhcpClient:',
    'WifiScoreReport:',
    'wpa_supplicant:',
    'SupplicantStaIfaceHal:',
    'GnssNetworkConnectivityHandler:',
    'WifiConfigManager:',
    'SupplicantStateTracker[wlan0]:',
]