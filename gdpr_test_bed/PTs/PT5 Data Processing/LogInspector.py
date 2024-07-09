from LogConfig import *
import csv
import numpy as np
import os
import re

class LogInspector():
    """Class dedicated to analyzing Android log data for PII exposure incidents """

    class LogAnalysisException(Exception):
        """Class dedicated for log analysis related errors"""
        def __init__(self, message='ERROR: Analysis-related error occured'):
            super().__init__(message)


    def __init__(self, log_dir=LOG_DIR, piilogid_dir=PIILOGID_DIR, join_dir=JOIN_DIR,
                 output_dir=OUTPUT_DIR, encoding=ENCODING, verbose=True):
        """Initialize an instnace of LogInspector, create necessary directories, and collect pii types
        Args:
            log_dir(str): The folder containing .log files to analyze
            piilogid_dir(str): The folder containing .piilog.id files to analyze
            join_dir(str): The directory to be used for joining log and piilog.id files
                (See log_piilog_id join for more details)
            output_dir(str): The directory in which csv result files will be recorded
            encoding(str): The type of encoding to use when reading/writing to files
            verbose(bool): Display additional information
        By default, arguments use information specified in LogConfig
        """
        self.log_dir = log_dir
        self.piilogid_dir = piilogid_dir
        self.join_dir = join_dir
        self.output_dir = output_dir
        self.encoding = encoding
        self.verbose = verbose

        def make_dir(dir):
            try:
                os.mkdir(dir)
            except FileExistsError:
                pass

        print(f'INFO: Generating directories: {self.join_dir}, {self.output_dir}\n'
              if self.verbose else '', end='')
        make_dir(self.join_dir)
        make_dir(self.output_dir)
        print(f'INFO: Retrieving PII types from: {self.piilogid_dir}\n'
              if self.verbose else '', end='')
        self.pii_types = set()
        self.get_pii_types()


    def get_pii_types(self, update=True):
        """Compile a list of pii types that may have been exposed within logs
        Args:
            update(bool): If True, add PII types to the current set (pii_types)
            If False, generate a new set of PII types
        """
        if not update:
            self.pii_types = set()
        piilogid_files = os.listdir(self.piilogid_dir)
        for piilogid_file in piilogid_files:
            path = os.path.join(self.piilogid_dir, piilogid_file)
            with open(path, 'r', encoding=self.encoding) as f:
                for line in f.readlines():
                    line_split = line.split(',')
                    if len(line_split) >= 8:
                        self.pii_types.add(line_split[7])
                f.close()
        self.pii_types = sorted(self.pii_types, key=str.casefold)


    def __analysis_sanity_check(self, log_files, piilogid_files):
        """Ensure that there is a log file for each piilog.id file, and vice-versa
        Args:
            log_files(list(str)): list of log files
            piilogid_files(list(str)): list of piilog.id files
        Raises:
            LogAnalysisException
        """
        
        # TODO: add doc to this, most poeple will not understand this 
        
        log_files = set([file[:(-1 * len(LOG_EXT))] for file in log_files])
        piilogid_files = set([file[:(-1 * len(PIILOGID_EXT))] for file in piilogid_files])
        if len(log_files - piilogid_files) != 0:
            raise self.LogAnalysisException(
                f'ERROR: {", ".join(app for app in (log_files - piilogid_files))} present in {self.log_dir} but not {self.piilogid_dir}')
        if len(piilogid_files - log_files) != 0:
            raise self.LogAnalysisException(
                f'ERROR: {", ".join(app for app in (piilogid_files - log_files))} present in {self.piilogid_dir} but not {self.log_dir}')


    def log_piilogid_join(self, log_path, piilogid_path, override=False):
        """Create a new file (filename.join.id) in the join directory
        This new file is an inner join between each piilog.id entry and its corresponding log (based on line number)
        Args:
            log_path(str): The file path to the log file
            piilogid_path(str): The file path to the piilog.id file
            override(bool): If False and the join file already exists and has data,
                do not perform a join nor overwrite the existing file
        Returns:
            bool: Indicates if join was performed 
        """
        join_path = os.path.join(self.join_dir, os.path.split(log_path)[1].replace(LOG_EXT, '.join.id'))
        #print(f'INFO: Joining {log_path}, {piilogid_path} to {join_path}\n'
        #      if self.verbose else '', end='')
        if not override and os.path.exists(join_path) and os.path.getsize(join_path) > 0:
            #print(f'INFO: {join_path} already constructed, skipping\n'
            #    if self.verbose else '', end='')
            return False
        
        #TODO: only for python 3.9 and up
        with (open(log_path, 'r', encoding=self.encoding) as log_f,
              open(piilogid_path, 'r', encoding=self.encoding) as piilogid_f,
              open(join_path, 'w', encoding=self.encoding) as join_f):
            log_lines = [line for line in log_f.readlines() if re.match(r'^\d{2}\-\d{2}|^\-|^\[', line)]
            for piilogid_entry in piilogid_f.readlines():
                entry_split = piilogid_entry.split(',')
                if len(entry_split) >= 9 and entry_split[0].isnumeric():
                    line_number, pii_type, position = int(entry_split[0]), entry_split[7], entry_split[8]
                    join_f.write(f'{line_number} {pii_type} {position} {log_lines[line_number - 1]}')
            log_f.close(), piilogid_f.close(), join_f.close()
        return True
    

    def log_pid_tracking(self, log_path):
        """Parse through the given log file and record process ID's (PIDs) based on origin (Activity Manager vs. other/system)
        Args:
            log_path(str): The file path to the log file
        Returns:
            spawned_pids: A dictionary with the format {'pid': 'package.name'},
            unspawned_pids: A list of pids not spawned by the Activity Manager,
            total_pids: A list of all pids in the log file
        """
        spawned_pids = {}
        unspawned_pids, total_pids =[], []
        with open(log_path, 'r', encoding=self.encoding) as f:
            for log in f.readlines():
                # Check: line is valid log
                if not re.match(r'^\d{2}-\d{2}', log):
                    continue
                split = log.split()
                if len(split) < 7:
                    continue
                pid, tag, message = split[2], split[5], ' '.join(split[6:])
                # If PID appears before ActivityManager, it is considered as a system PID
                if pid not in total_pids:
                    total_pids.append(pid)
                    if pid not in spawned_pids:
                        unspawned_pids.append(pid)
                if tag == 'ActivityManager:' and 'Start proc' in message:
                    search = re.search(r'(\d+):((?:\w+\.)*\w+)', message)
                    try:
                        spawned_pid = search.group(1)
                        package_name = search.group(2)
                        if spawned_pid not in total_pids and spawned_pid not in unspawned_pids:
                            total_pids.append(spawned_pid)
                            spawned_pids[spawned_pid] = package_name
                    except (AttributeError, IndexError):
                        continue
            f.close()
        return spawned_pids, unspawned_pids, total_pids


    def log_pii_analysis(self, csv_file, override=False, filter_excluded_cases=False, filter_excluded_tags=False,
                              activity_manager_only=False, app_package_only=False):
        """Method of analyzing log files for PII information, writes results to csv file in the form of a matrix
        Args:
            csv_file(str): The name of the csv_file to write to
            override(bool): Used for join operation (If False, do not overwrite existing data)
            filter_excluded_cases(bool): Flag for filtering excluded cases (i.e. false positives)
            filter_excluded_tags(bool): Flag for filtering excluded tags (listed in LogConfig)
            activity_manager_only(bool): Flag to only consider logs with PID's from the Activity Manager
            app_package_only(bool): Flag to only consider logs attributed to the app's package name
                (Note: this will only have an effect is activity_manager_only is also True)
        """
        def is_false_positive(split, pii_type):
            cases = [key for key in EXCLUDED_CASES.keys() if key in pii_type]
            for case in cases:
                index, false_match = EXCLUDED_CASES[case]
                if false_match in split[index]:
                    return True
            return False
        
        def pid_in_scope(pid, package_name, pid_scope):
            if pid in pid_scope:
                if app_package_only:
                    return pid_scope[pid] == package_name
                return True
            return False

        # Establish log/piilog.id files and ensure that they match up (There is a log file and piilog.id file for each app)
        log_files = sorted([file for file in os.listdir(self.log_dir) if file.endswith(LOG_EXT)],
                           key=str.casefold)
        piilogid_files = sorted([file for file in os.listdir(self.piilogid_dir) if file.endswith(PIILOGID_EXT)],
                                key=str.casefold)
        try:
            self.__analysis_sanity_check(log_files, piilogid_files)
        except self.LogAnalysisException as err:
            print(err)
            return
        
        # Set up and display runtime information
        packages = [file[:(-1 * len(LOG_EXT))].split('-')[0] for file in log_files]
        pii_exposure_matrix = np.zeros((len(packages), len(self.pii_types)), dtype=int)
        am_pids = {}
        print(f'Analyzing PII exposure within logs from {self.log_dir} and {self.piilogid_dir}')
        print(f'Settings Enabled:')
        print(f'-Filter by excluded cases\n' if filter_excluded_cases else '', end='')
        print(f'-Filter by excluded tags\n' if filter_excluded_tags else '', end='')
        print(f'-Only analyze logs from Activity Manager processes\n' if activity_manager_only else '', end='')
        print(f'-Only analyze logs from the app package\n' if activity_manager_only and app_package_only else '', end='')
        print(f'INFO: May take some time due to the large number of log files\n'
                if len(log_files) > 100 and self.verbose else '', end='')

        # Perform an inner join between log and piilog.id file for each app
        print(f'INFO: Joining piilog.id entries with log messages')
        for i in range(len(log_files)):
            log_path = os.path.join(self.log_dir, log_files[i])
            piilogid_path = os.path.join(self.piilogid_dir, piilogid_files[i])
            self.log_piilogid_join(log_path, piilogid_path, override)

        # Track the PIDs associated with each package
        if activity_manager_only:
            print(f'INFO: Tracking PID entries from the ActivityManager\n'
                  if self.verbose else '', end='')
            for i in range(len(log_files)):
                log_path = os.path.join(self.log_dir, log_files[i])
                am_pids[packages[i]] = self.log_pid_tracking(log_path)[0]

        # Analyze each newly created join.id file for PII data (using toggled filters)
        print(f'INFO: Compiling PII exposure data')
        join_files = sorted([file for file in os.listdir(self.join_dir) if file.endswith(JOIN_EXT)],
                            key=str.casefold)
        for i in range(len(join_files)):
            with open(os.path.join(self.join_dir, join_files[i]), 'r', encoding=self.encoding) as f:
                for line in f.readlines():
                    split = line.split()
                    if len(split) < 10:
                        continue
                    pii_type, pid, tag = split[1], split[5], split[8]
                    if filter_excluded_cases and is_false_positive(split, pii_type):
                        continue
                    if filter_excluded_tags and tag in EXCLUDED_TAGS:
                        continue
                    if activity_manager_only and not pid_in_scope(
                        pid, packages[i], am_pids[packages[i]]):
                        continue
                    column = self.pii_types.index(pii_type)
                    pii_exposure_matrix[i][column] += 1
                f.close()

        # Record results
        self.__write_app_pii_matrix(csv_file, packages, pii_exposure_matrix)


    def __write_app_pii_matrix(self, csv_file, packages, pii_exposure_matrix):
        """Writes app-PII matrix, meant to only be called by log_pii_analysis
        Args:
            csv_file(str): The name of the csv_file to write to
            packages(list(str)): The list of package names
            pii_exposure_matrix(ndarray): A matrix of size (# packages) x (# pii_types)
                Example: pii_exposure_matrix[0][1] is the number of times in which
                the 1st package in the package list exposed the 2nd pii_type in pii_types
        """
        output_path = os.path.join(self.output_dir, csv_file)
        print(f'Writing results to {output_path}')
        with open(output_path, 'w', newline='') as f:
            csvwriter= csv.writer(f)
            csvwriter.writerow(['Within matrix, values = number of logs that expose PII', '', 'PII Category'] + self.pii_types)
            csvwriter.writerow(['', '', 'Total Exposing Logs per PII'] + list(np.sum(pii_exposure_matrix, axis=0)))
            csvwriter.writerow(['App', 'Total Exposing Logs per App', 'Total Exposing Apps per PII (Right),\nTotal Types PII Exposed per App (Below)'] + 
                               list(np.sum(pii_exposure_matrix > 0, axis=0)))
            for i in range(len(packages)):
                csvwriter.writerow([packages[i], np.sum(pii_exposure_matrix[i]), np.sum(pii_exposure_matrix[i] > 0)] + 
                                   [val if val > 0 else "" for val in pii_exposure_matrix[i]])
            f.close()


    def log_tag_analysis(self, csv_file):
        """Method for analyzing tag data (frequency, etc.) within the log files
        Args:
            csv_file(str): The name of the csv_file to write to
        """
        tag_data = {} # (count of logs, set of log files, count of piilog.id entries, set of piilog.id files)
        log_files = sorted([file for file in os.listdir(self.log_dir) if file.endswith(LOG_EXT)],
                           key=str.casefold)
        piilogid_files = sorted([file for file in os.listdir(self.piilogid_dir) if file.endswith(PIILOGID_EXT)],
                                key=str.casefold)
        output_path = os.path.join(self.output_dir, csv_file)
        print(f'Analyzing tags in log files')
        # Analyze log files
        for file in log_files:
            with open(os.path.join(self.log_dir, file), 'r', encoding=self.encoding) as log_f:
                log_lines = [line for line in log_f.readlines() if re.match(r'^\d{2}\-\d{2}', line)]
                for log in log_lines:
                    split = log.split()
                    if len(split) < 6:
                        continue
                    tag = split[5]
                    if tag not in tag_data:
                        tag_data[tag] = [1, {file}, 0, set()]
                    else:
                        tag_data[tag][0] += 1
                        tag_data[tag][1].add(file)
                log_f.close()
        # Analyze piilog.id files
        for file in piilogid_files:
            with open(os.path.join(self.piilogid_dir, file), 'r', encoding=self.encoding) as piilogid_f:
                for line in piilogid_f.readlines():
                    split = line.split(',')
                    if len(split) < 9:
                        continue
                    tag = split[1]
                    if tag not in tag_data:
                        tag_data[tag] = [0, set(), 1, {file}]
                    else:
                        tag_data[tag][2] += 1
                        tag_data[tag][3].add(file)
                piilogid_f.close()
        # Record results 
        print(f'Writing results to {output_path}')
        with open(output_path, 'w', newline='') as out_f:
            csvwriter= csv.writer(out_f)
            csvwriter.writerow(['Tag', '# logs with tag', '# log files with tag', '# piilog.id entries with tag', '# piilog.id files with tag'])
            for tag, data in tag_data.items():
                csvwriter.writerow([tag, data[0], len(data[1]), data[2], len(data[3])])
            out_f.close()


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