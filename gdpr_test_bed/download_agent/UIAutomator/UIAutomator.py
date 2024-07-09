import re
import subprocess
import time
import xml.etree.ElementTree as ET
import os

# TODO: When integrating this class with some framework, it is recommended to
# load paths, account data, etc. from a config file
ADB_PATH = '/Users/ethanmyers/Library/Android/sdk/platform-tools/adb'
DEVICE = 'emulator-5554'
GOOGLE_USER = 'scholarsmate.ohno@gmail.com'
GOOGLE_PASSWORD = 'Wers101A'

class UIAutomator:
    """Class dedicated to calling uiautomator and parsing XML data
    Attributes:
        MAX_ATTEMPTS: The maximum number of attempts for installing a single package
        PLAYSTORE_WAIT_TIME: Number of seconds to wait for Play Store install
        VERBOSE: The verbosity of the class when printing statements
    """
    MAX_ATTEMPTS = 3
    PLAYSTORE_WAIT_TIME = 60
    VERBOSE = True

    def dump_xml():
        """Call uiautomator and format output into XML data
        Returns:
            xml.etree.ElementTree.Element: The root node of the XML data or None if no XML
        """
        command = [ADB_PATH, '-s', DEVICE, 'exec-out', 'uiautomator', 'dump', '/dev/tty']
        output = subprocess.run(command, capture_output=True, check=True).stdout.decode()
        formatted_output = re.search(r'.*(?=UI hierchary dumped to: /dev/tty)', output)
        if formatted_output is None:
            return None 
        return ET.fromstring(formatted_output.group(0))
    

    def search_xml(root, term, attributes, strict, ignore_case):
        """Search the XML for the specified term
        Args:
            root(xml.etree.ElementTree.Element): The node to analyze for attribute value and children
            term(string): The attribute value to search for
            attribute(list<string>): List of attributes to search
                (default is [], in which case search every attribute)
            strict(bool): Exact match if True, else check if term is in attribute
                (default is True)
            ignore_case(bool): Ignore case if True, else do not
                (default is False)
        Returns:
            list<xml.etree.ElementTree.Element>: A list of matching nodes
        """
        nodes = [root]
        matches = []
        term = term.casefold() if ignore_case else term
        original_attrib = attributes
        for node in nodes:
            attributes = original_attrib
            # Check for children nodes
            if len(list(node)) > 0:
                for child in node:
                    nodes.append(child)
            # Search of specified attribute(s) or all attributes if none are specified
            if len(attributes) == 0:
                attributes = [a for a in node.attrib]
            for attribute in attributes:
                if attribute in node.attrib:
                    tag = node.attrib[attribute]
                    tag = tag.casefold() if ignore_case else tag
                    if strict and term == tag:
                        matches.append(node)
                    elif not strict and term in tag:
                        matches.append(node)
        return matches
    

    def find_button(term, attributes=[], strict=True, ignore_case=False, root=None):
        """Capture the XML data of the screen a search for a specified term within it
        Args:
            All arguments are used for the UIAutomator.search_xml function
            If root is already known (xml.etree.ElementTree.Element), can specify root
            and skip calling dump_xml()
        Returns:
            (float, float): Coordinates of the install button if it is found, else None
        """
        if root is None:
            root = UIAutomator.dump_xml()
        if root is None:
            return None
        matches = UIAutomator.search_xml(root, term, attributes, strict, ignore_case)
        for match in matches:
            if 'bounds' in match.attrib:
                coords = re.findall(r'([0-9]+)', match.attrib['bounds'])
                return ((int(coords[0]) + int(coords[2])) / 2, (int(coords[1]) + int(coords[3])) / 2)
        return None
    

    def tap_button(coords):
        """Input a button tap operation
        Args:
            coords((float, float)): Button coordinates
        """
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'input', 'tap', f'{coords[0]}', f'{coords[1]}']
        subprocess.run(command, capture_output=True, check=True)

    
    def find_package(package):
        """Find package in the package list
        Args:
            package(str): Package name
        Returns:
            bool: True if package is found, else False
        """
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'pm', 'list', 'packages']
        output = subprocess.run(command, capture_output=True, check=True).stdout.decode()
        return re.search(r'package:'+re.escape(package), output) is not None
    

    def playstore_install(package, attempts=MAX_ATTEMPTS, bulk=False):
        """Attempt install from the Google Play Store
        Args:
            package(str): Package name
            attempts(int): Number of remaining attempts to install package
                (default is MAX_ATTEMPTS)
            bulk_install(bool): Indicate whether package installation is part of
                bulk installation of multiple apps
                (default is False)
        Returns:
            (bool, float): (True if package was installed else False, time to install package (0 if False returned))
        """
        print(f'Attempting to install {package} from Play Store' + f', {attempts} attempts remaining'
              if UIAutomator.VERBOSE else '')
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', f'market://details?id={package}']
        subprocess.run(command, capture_output=True, check=True)
        coords = UIAutomator.find_button('Install', ['text', 'content-desc'], strict=True, ignore_case=True)
        if coords is None:
            if attempts > 1:
                print(f'Error: Could not locate install button, {attempts - 1} attempts remaining\n'
                      if UIAutomator.VERBOSE else '', end='')
                return UIAutomator.playstore_install(package, attempts - 1, bulk)
            print(f'Error: could not install {package}, skipping ...')
            return False, 0.0
        UIAutomator.tap_button(coords)

        # If bulk, should send installation info back to bulk_playstore_install
        if bulk:
            return True, time.time()

        start_time, end_time = time.time(), 0.0
        while end_time <= UIAutomator.PLAYSTORE_WAIT_TIME:
            if UIAutomator.find_package(package):
                print(f'{package} successfully installed')
                return True, end_time
            end_time = time.time() - start_time
        
        # If packages are installed one at a time, can attempt to retry installation
        if attempts > 1:
            print(f'Error: Could not install in maximum amount of time, {attempts - 1} attempts remaining\n'
                  if UIAutomator.VERBOSE else '', end='')
            coords = UIAutomator.find_button('Cancel', ['content-desc'])
            if coords is not None:
                UIAutomator.tap_button(coords)
            else:
                UIAutomator.uninstall_package(package)
            return UIAutomator.playstore_install(package, attempts - 1, bulk)
        print(f'Error: could not install {package}, skipping ...')
        return False, 0.0
    

    def bulk_playstore_install(packages, attempts=MAX_ATTEMPTS, max_batch=10, uninstall=True):
        """Manages the concurrent installation of multiple packages from the Google Play Store
        Args:
            packages(list(str)): A list of packages to install
            attempts(int): Number of remaining attempts to install package
                (default is MAX_ATTEMPTS)
            max_batch(int): The maximum number of packages to install concurrently
                If len(packages) > max_batch, split packages into multiple batches
            uninstall(bool): Indicates whether to uninstall apps after installation
                (default is True as to avoid filling up devices with large amounts of package data)
        Returns:
            {package: (bool, float)}: A dictionary with package name as the key and the outcome of
                the installation as the value (success, time_to_install)
        """
        installation_report = dict()
        current_installations, failed_installations = [], []

        # Split batch if the list of packges is too long
        if len(packages) > max_batch:
            batches = [packages[i:i+max_batch] for i in range(0, len(packages), max_batch)]
            batch_num = 1
            for batch in batches:
                print(f'Installing batch {batch_num}')
                installation_report.update(UIAutomator.bulk_playstore_install(
                    batch, attempts, max_batch, uninstall))
            return installation_report

        # Start the installation process for all packages
        for package in packages:
            install_started, start_time = UIAutomator.playstore_install(package, attempts, bulk=True)
            if install_started:
                current_installations.append((package, start_time))
            else:
                installation_report[package] = (False, 0.0)
        
        # Cycle through each package's install progress until all packages are installed (or until time runs out)
        installed_apks = []
        start_time, end_time = time.time(), 0.0
        while len(current_installations) > 0 and end_time <= UIAutomator.PLAYSTORE_WAIT_TIME:
            concluded_packages = []
            for package in current_installations:
                package_name, package_start = package
                package_time = end_time + (start_time - package_start)
                # Case: Package successfully installed, mark as success
                if UIAutomator.find_package(package_name):
                    print(f'{package_name} successfully installed')
                    installed_apks.append(package_name)
                    concluded_packages.append(package)
                    installation_report[package_name] = (True, package_time)
                # Case: Package could not be installed in alloted time, mark as failure
                elif package_time > UIAutomator.PLAYSTORE_WAIT_TIME:
                    print(f'Error: could not install {package_name}, skipping ...')
                    failed_installations.append(package_name)
                    concluded_packages.append(package)
                    installation_report[package_name] = (False, 0.0)
            # Stop iterating through any packages that have concluded (success or failure)
            for package in concluded_packages:
                current_installations.remove(package)
            end_time = time.time() - start_time

        # Return to the pages for packages marked as "failed installations" and cancel their installation
        for failed_install in failed_installations:
            command = [ADB_PATH, '-s', DEVICE, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', f'market://details?id={failed_install}']
            subprocess.run(command, capture_output=True, check=True)
            coords = UIAutomator.find_button('Cancel', ['content-desc'])
            if coords is not None:
                UIAutomator.tap_button(coords)
            else:
                UIAutomator.uninstall_package(failed_install)
        print(installed_apks)
        # for package_name, _ in current_installations:
        #     apk_filename = f"{package_name}.apk"
        #     source_apk_path = os.path.join(ADB_PATH, f"data/app/{package_name}/base.apk")
        #     destination_apk_path = os.path.join('./apks', apk_filename)

        #     # Pull the APK from the device to the server
        #     pull_command = [ADB_PATH, '-s', DEVICE, 'pull', source_apk_path, destination_apk_path]
        #     subprocess.run(pull_command, capture_output=True, check=True)

        # Uninstall successfully installed apps if set True
        # if uninstall:
        #     for package in packages:
        #             UIAutomator.uninstall_package(package)

        return installation_report

    
    def uninstall_package(package):
        """Uninstall a package installed from the Google Play Store
        Args:
            package(str): Package name
        """
        try:
            command = [ADB_PATH, '-s', DEVICE, 'uninstall', package]
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f'Error: {package} already uninstalled\n'
                  if UIAutomator.VERBOSE else '', end='')


    def google_login_scan():
        """Scan the XML dump to detect any Google login forms within apps
        Returns:
            (float, float): Coordinates of the install button if it is found, else None
        """
        return UIAutomator.find_button('Google', strict=False, ignore_case=True)


    def google_login(coords=None):
        """Attempt login into Google Account within apps
        Args:
            coords((float, float)): Button coordinates
                (Default is None, will call google_login_scan() first)
        Returns:
            bool: True on login success, else False
        """
        if coords is None:
            coords = UIAutomator.google_login_scan()
        if coords is None:
            return False
        
        UIAutomator.tap_button(coords)
        coords = UIAutomator.find_button(GOOGLE_USER, strict=True, ignore_case=False)
        if coords is not None:
            UIAutomator.tap_button(coords)
            return True
        return False


    def playstore_login():
        """Login into Google Play Store
        Returns:
            bool: True on login success, else False
        """
        def playstore_go_to(term, attempts=10):
            """Helper method specific to navigating the Google Play Store login pages
            Args:
                term(str): The search term to use when searching a page's XML data
                attempts(int): Number of attempts in finding an element with the specified term
                    (default is 10)
            Returns:
                bool: True if term is found in XML data, else False
            """
            for i in range(attempts):
                coords = UIAutomator.find_button(term, ignore_case=True)
                if coords is not None:
                    UIAutomator.tap_button(coords)
                    return True
                #print(f'Attempt {i + 1}/{attempts}: No button detected yet')
            return False
        
        print(f'Opening Play Store app\n' if UIAutomator.VERBOSE else '', end='')
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'am', 'start', '-a', 
                'android.intent.action.VIEW', '-d', 'market://details']
        subprocess.run(command, capture_output=True, check=True)

        print(f'Searching for sign in button\n' if UIAutomator.VERBOSE else '', end='')
        if not playstore_go_to('Sign in'):
            print(f'Error: Sign in button not detected, exiting')
            return False
        
        print(f'Searching for gmail input form\n' if UIAutomator.VERBOSE else '', end='')
        if not playstore_go_to('android.widget.EditText'):
            print(f'Error: Gmail input form not detected, exiting')
            return False
        print(f'Submitting gmail information\n' if UIAutomator.VERBOSE else '', end='')
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'input', 'text', GOOGLE_USER]
        subprocess.run(command, capture_output=True, check=True)
        if not playstore_go_to('Next'):
            print(f'Error: Failure in submitting gmail information, exiting')
            return False
        
        print(f'Searching for password input form\n' if UIAutomator.VERBOSE else '', end='')
        if not playstore_go_to('android.widget.EditText'):
            print(f'Error: Password input form not detected, exiting')
            return False
        print(f'Submitting password information\n' if UIAutomator.VERBOSE else '', end='')
        command = [ADB_PATH, '-s', DEVICE, 'shell', 'input', 'text', GOOGLE_PASSWORD]
        subprocess.run(command, capture_output=True, check=True)
        if not playstore_go_to('Next'):
            print(f'Error: Failure in submitting gmail information, exiting')
            return False
        
        print(f'Finalizing logins, agreements, etc.\n' if UIAutomator.VERBOSE else '', end='')
        if not playstore_go_to('I agree'):
            print(f'Error: Failed to agree to terms of service, exiting')
            return False
        
        return True
