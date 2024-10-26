
import os
import logging
import json
import paramiko
import requests
from datetime import datetime
from backendcodeforextension import process_extension_whitelist_blacklist
import subprocess
import shutil

# Log settings for visibility
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Centralized folder path
REMOTE_FOLDER = r"C:\ProgramData\policy_exec"

def generate_extension_config(specifications):
    logging.info("Generating browser extension configuration")

    # Initialize the blocked_conditions dictionary
    blocked_conditions = {}

    if specifications.get('block_all') == 'yes':
        blocked_conditions['block_all'] = True
    else:
        blocked_conditions['block_all'] = False
        conditions = []
        
        condition_types = specifications.get('conditionType[]', [])
        condition_values = specifications.get('conditionValue[]', [])

        logging.debug(f"Condition Types: {condition_types}")
        logging.debug(f"Condition Values: {condition_values}")

        # Check if condition_types and condition_values are not None and properly matched
        if isinstance(condition_types, str):
            condition_types = [condition_types]
        if isinstance(condition_values, str):
            condition_values = [condition_values]

        if len(condition_types) == len(condition_values):
            for cond_type, cond_value in zip(condition_types, condition_values):
                if cond_type and cond_value:
                    conditions.append({"type": cond_type, "value": cond_value})
            blocked_conditions['conditions'] = conditions
        else:
            logging.warning("Mismatch in condition types and values, or they are empty.")
            logging.debug(f"Condition Types: {condition_types}, Condition Values: {condition_values}")
        
        if not conditions:
            logging.warning("No valid conditions provided for blocking downloads.")

    # Save the blocked_conditions to the JSON file
    extension_config_path = "C:\\policy_exec\\extension_config.json"

    try:
        with open(extension_config_path, 'w') as config_file:
            json.dump(blocked_conditions, config_file, indent=4)
            logging.info(f"Extension configuration saved to {extension_config_path}")
    except Exception as e:
        logging.error(f"Failed to save extension config: {e}")
        return None
    return True  # Indicating success if needed

# Log settings
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def generate_policy_files(specifications):
    """
    Function to generate policy files based on the input specifications
    """
    logging.info(f"Received specifications: {json.dumps(specifications, indent=4)}")

    # Mapping policy keys to registry values
    policy_mappings = {
        # Threat Prevention Policy
        'SafeBrowsingProtectionLevel': 'SafeBrowsingProtectionLevel',
        'BlockObstructiveWebsites': 'SafeSitesFilterBehavior',
        'BlockInjectedCode': 'ThirdPartyBlockingEnabled',
        'BlockExcessiveAds': 'AdsSettingForIntrusiveAdsSites',
        'OverrideCertificateErrors': 'SSLErrorOverrideAllowed',
        'FileDownloads': 'DownloadRestrictions',
        'WhitelistExtensions': 'ExtensionInstallAllowlist',
        'BlacklistExtensions': 'ExtensionInstallBlocklist',
        # Permissions across all websites
        'geolocation': 'DefaultGeolocationSetting',
        'camera': 'VideoCaptureAllowed',
        'sensor': 'DefaultSensorsSetting',
        'notifications': 'DefaultNotificationsSetting',
        'js': 'DefaultJavaScriptSetting',
        'popups': 'DefaultPopupsSetting',
        'usb': 'DefaultWebUsbGuardSetting',

        # DLP (Data Leakage Prevention)
        'PrintWebpage': 'PrintingEnabled',
        'AutomaticBrowserSync': 'BrowserSignin',
        'SaveBrowserHistory': 'SavingBrowserHistoryDisabled',
        'Autofill': 'AutofillAddressEnabled',
        'CaptureScreenshots': 'DisableScreenshots',
        'RememberPasswords': 'PasswordManagerEnabled',
        'SitePerProcess': 'NewTabPagelLocation',
        'SearchSuggestions': 'SearchSuggestEnabled',
        'MetricsReporting': 'MetricsReportingEnabled',
        'PromptDownloadLocation': 'PromptForDownloadLocation',
        'BrowserHistoryDeletion': 'AllowDeletingBrowserHistory',
        'BackgroundProcessing': 'BackgroundModeEnabled',
        'NetworkPredictions': 'NetworkPredictionOptions',
        'ThirdPartyCookies': 'BlockThirdPartyCookies',
        'BrowsingDataLifetime': 'BrowsingDataLifetime',
        'ExemptDomainFileTypePairsFromFileTypeDownloadWarnings': 'ExemptDomainFileTypePairsFromFileTypeDownloadWarnings',

        #is is either dlp or tpp
        'BlockThirdPartyCookies':'BlockThirdPartyCookies',
        'BlockURLs':'URLBlocklist',
        'AllowURLs':'URLAllowlist'

    }

    # Corrected registry paths for Chromium-based browsers
    browser_registry_paths = {
        'Chrome': 'HKEY_LOCAL_MACHINE\\Software\\Policies\\Google\\Chrome',
        'Brave': 'HKEY_LOCAL_MACHINE\\Software\\Policies\\BraveSoftware\\Brave',
        'Edge': 'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Edge',
        'Vivaldi': 'HKEY_LOCAL_MACHINE\\Software\\Policies\\Vivaldi'
    }

    policy_data = {}

    for browser, registry_path in browser_registry_paths.items():
        policy_data[browser] = {"registry_path": registry_path, "policies": {}}

        # Handle blocked conditions
        blocked_conditions = {}
        if specifications.get('block_all') == 'yes':
            policy_data[browser]['policies'][policy_mappings['FileDownloads']] = 3  # Block all downloads
            logging.info(f"Set {policy_mappings['FileDownloads']} to block all downloads for {browser}")
        else:
            blocked_conditions['block_all'] = False
            conditions = []
            condition_types = specifications.get('conditionType[]', [])
            condition_values = specifications.get('conditionValue[]', [])
            if len(condition_types) == len(condition_values):
                for cond_type, cond_value in zip(condition_types, condition_values):
                    if cond_type and cond_value:
                        conditions.append({"type": cond_type, "value": cond_value})
                blocked_conditions['conditions'] = conditions

        # Processing new security policies
        security_policies = ['geolocation', 'camera', 'sensor', 'notifications', 'js', 'popups', 'usb']
        for security_policy in security_policies:
            value = specifications.get(security_policy)
            if value:
                policy_name = policy_mappings[security_policy]
                policy_value = 2 if value == 'block' else 1  # Assuming 'block' = 2 and 'allow' = 1
                policy_data[browser]['policies'][policy_name] = policy_value
                logging.info(f"Set {policy_name} to {policy_value} for {browser}")

        # Process the selected data type and time to live for BrowsingDataLifetime
        data_type = specifications.get('BrowsingDataLifetime[data_type]')
        time_to_live_in_hours = specifications.get('BrowsingDataLifetime[time_to_live_in_hours]', 1)

        if data_type:
            policy_data[browser]['policies']['BrowsingDataLifetime'] = [
                {
                    "data_types": [data_type],
                    "time_to_live_in_hours": int(time_to_live_in_hours)
                }
            ]
            logging.info(f"Added BrowsingDataLifetime settings for {browser}: {policy_data[browser]['policies']['BrowsingDataLifetime']}")
        else:
            logging.info(f"Skipping BrowsingDataLifetime for {browser} as no data type is provided.")
           
        # Processing ExemptDomainFileTypePairsFromFileTypeDownloadWarnings policy
        domains = [domain.strip() for domain in specifications.get('domains', '').split(',')]
        file_extension = specifications.get('file_extension', '').lower()

        if file_extension and domains:
            policy_value = [{
                "domains": domains,
                "file_extension": file_extension
            }]
            policy_data[browser]['policies']['ExemptDomainFileTypePairsFromFileTypeDownloadWarnings'] = policy_value
            logging.info(f"Added download restriction for {file_extension} on domains: {domains} for {browser}")


        # New Policies (BlockThirdPartyCookies, BlockURLs, AllowURLs)
        # Process BlockThirdPartyCookies
        block_third_party_cookies = specifications.get('BlockThirdPartyCookies', 'not_configured')
        if block_third_party_cookies != 'not_configured':
            policy_value = 1 if block_third_party_cookies == 'enable' else 0  # 1 = Block, 0 = Allow
            policy_data[browser]['policies'][policy_mappings['BlockThirdPartyCookies']] = policy_value
            logging.info(f"Set BlockThirdPartyCookies to {policy_value} for {browser}")
                
        
        # Process BlockURLs
        block_urls = specifications.get('BlockURLs')
        if block_urls:
            url_list = [url.strip() for url in block_urls.split(',') if url.strip()]
            if url_list:
                # Correctly map BlockURLs to URLBlocklist using the mapping
                policy_data[browser]['policies'][policy_mappings['BlockURLs']] = url_list
                logging.info(f"Set URLBlocklist for {browser}: {url_list}")

        # Process AllowURLs
        allow_urls = specifications.get('AllowURLs')
        if allow_urls:
            url_list = [url.strip() for url in allow_urls.split(',') if url.strip()]
            if url_list:
                # Correctly map AllowURLs to URLAllowlist using the mapping
                policy_data[browser]['policies'][policy_mappings['AllowURLs']] = url_list
                logging.info(f"Set URLAllowlist for {browser}: {url_list}")

        # Process whitelist and blacklist extension IDs
        whitelist_extensions = [ext.strip() for ext in specifications.get('WhitelistExtensions', '').split(',')]
        blacklist_extensions = [ext.strip() for ext in specifications.get('BlacklistExtensions', '').split(',')]

        # Call backendcodeforextension to get the actual extension IDs
        from backendcodeforextension import process_extension_whitelist_blacklist

        # Skip processing if both extension lists are empty
        if whitelist_extensions or blacklist_extensions:
            # Call backendcodeforextension to get the actual extension IDs
            whitelist_ids, blacklist_ids = process_extension_whitelist_blacklist(whitelist_extensions, blacklist_extensions)
            logging.info(f"Whitelist IDs: {whitelist_ids}")
            logging.info(f"Blacklist IDs: {blacklist_ids}")

            # Update policies with the fetched extension IDs if they exist
            if whitelist_ids:
                policy_data[browser]['policies']['ExtensionInstallAllowlist'] = whitelist_ids
            else:
                policy_data[browser]['policies']['ExtensionInstallAllowlist'] = []  # Empty list if no IDs
            
            if blacklist_ids:
                policy_data[browser]['policies']['ExtensionInstallBlocklist'] = blacklist_ids
            else:
                policy_data[browser]['policies']['ExtensionInstallBlocklist'] = []  # Empty list if no IDs
        else:
            logging.info(f"Skipping extension whitelist/blacklist for {browser} as no extensions are provided.")



                # Process SafeBrowsingProtectionLevel
        safe_browsing_protection_level = specifications.get('SafeBrowsingProtectionLevel')
        if safe_browsing_protection_level:
            policy_value = int(safe_browsing_protection_level)  # Convert the value to an integer
            policy_data[browser]['policies'][policy_mappings['SafeBrowsingProtectionLevel']] = policy_value
            logging.info(f"Set SafeBrowsingProtectionLevel to {policy_value} for {browser}")

        # Process BlockExcessiveAds
        block_excessive_ads = specifications.get('BlockExcessiveAds')
        if block_excessive_ads:
            policy_value = 2 if block_excessive_ads == 'enable' else 1  # Enable = 2, otherwise = 1
            policy_data[browser]['policies'][policy_mappings['BlockExcessiveAds']] = policy_value
            logging.info(f"Set BlockExcessiveAds to {policy_value} for {browser}")


        # Processing other existing policies
        for key, value in specifications.items():
            if key not in ['domains', 'file_extension', 'BrowsingDataLifetime[data_types][]', 'BrowsingDataLifetime[time_to_live_in_hours]', *security_policies, 'BlockURLs', 'AllowURLs', 'WhitelistExtensions', 'BlacklistExtensions']:
                if value != 'not_configured':
                    policy_name = policy_mappings.get(key)
                    if policy_name:
                        try:
                            policy_value = int(value) if value.isdigit() else 1 if value.lower() in ['allow', 'enable', 'yes'] else 0
                        except ValueError:
                            logging.error(f"Error converting {key}: {value} to integer.")
                            continue
                        policy_data[browser]['policies'][policy_name] = policy_value
                        logging.info(f"Set {policy_name} to {policy_value} for {browser}")

            # Generate the browser extension config

    logging.info(f"Final policy data for {browser}: {json.dumps(policy_data[browser], indent=4)}")

    local_json_path = r"D:\NLP\NLPFinal\Main\policies.json"
    with open(local_json_path, 'w') as json_file:
        json.dump(policy_data, json_file, indent=4)
    logging.info(f"Policies saved locally to {local_json_path}")
    
    logging.info("Policy generation completed. Saving execution log.")
    save_execution_log(specifications)  # Ensure this is called

    with open('deployment.json', 'r') as file:
        deployment_data = json.load(file)
    vm = deployment_data['vms'][0]
    vm_ip = vm['ip']
    vm_username = vm['username']
    vm_password = vm['password']
    
    remote_json_path = f"{SECURE_FOLDER}\\policies.json"
    remote_ps_script_path = f"{SECURE_FOLDER}\\generate_policy_reg_files.ps1"

    if upload_file(vm_ip, vm_username, vm_password, local_json_path, remote_json_path):
        # Now upload PowerShell script in the same way
        local_ps_script_path = r"D:\NLP\NLPFinal\Main\generate_policy_reg_files.ps1"
        if upload_file(vm_ip, vm_username, vm_password, local_ps_script_path, remote_ps_script_path):
            # If both files were uploaded successfully, execute the script
            result = execute_on_remote_vm(vm_ip, vm_username, vm_password, remote_json_path, remote_ps_script_path)

            if result.get("status") == "success":
                # Save logs only after successful execution
                save_execution_log(specifications)
                logging.info("Policies executed successfully, logs saved.")
                return result
            else:
                logging.error("Policy execution failed on the VM.")
                return {"status": "error", "details": "Policy execution failed on the VM."}
        else:
            logging.error("Failed to upload PowerShell script to the VM.")
            return {"status": "error", "details": "Failed to upload PowerShell script."}
    else:
        logging.error("Failed to upload JSON file to the VM.")
        return {"status": "error", "details": "Failed to upload JSON file."}

def save_execution_log(specifications):
    """
    Save the received specifications to a JSON log after successful execution.
    """
    print("save_execution_log() function called")  # Debug print

    try:
        logs_folder = r"D:\NLP\NLPFinal\Main\logs"

        # Check if the logs folder exists, and create it if it doesn't
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
            logging.info(f"Created logs folder: {logs_folder}")
        else:
            logging.info(f"Logs folder already exists: {logs_folder}")

        # Generate a timestamp and log file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        policy_category = determine_policy_category(specifications)
        log_file_path = os.path.join(logs_folder, f"{policy_category}_policy_{timestamp}.json")

        logging.info(f"Saving log to: {log_file_path}")

        # Save the log
        with open(log_file_path, 'w') as log_file:
            json.dump(specifications, log_file, indent=4)

        logging.info(f"Execution log saved to {log_file_path}")

    except Exception as e:
        logging.error(f"Failed to save execution log: {e}")

def determine_policy_category(specifications):
    """
    Determine the policy category dynamically based on the specifications.
    """
    if 'PrintWebpage' in specifications:
        return "Data_Leakage_Prevention"
    elif 'SafeBrowsingProtectionLevel' in specifications:
        return "Threat_Prevention"
    else:
        return "Uncategorized"


## Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Define the secure centralized folder path
SECURE_FOLDER = r"C:\ProgramData\policy_exec"

# Step 1: Create and Secure the Folder Automatically
def create_secure_folder():
    try:
        if not os.path.exists(SECURE_FOLDER):
            os.makedirs(SECURE_FOLDER)
            cmd = f'icacls "{SECURE_FOLDER}" /inheritance:r /grant Administrators:F /grant SYSTEM:F'
            subprocess.run(cmd, shell=True, check=True)
            logging.info(f"Folder created and secured: {SECURE_FOLDER}")
        else:
            logging.info(f"Folder already exists: {SECURE_FOLDER}")
    except Exception as e:
        logging.error(f"Failed to create or secure folder: {e}")
        raise


# Step 2: Load Deployment Details from deployment.json
def load_deployment_data():
    try:
        with open('deployment.json', 'r') as file:
            deployment_data = json.load(file)
            logging.info("Deployment data loaded successfully.")
            return deployment_data['vms'][0]
    except Exception as e:
        logging.error(f"Error loading deployment data: {e}")
        raise

# Step 3: Upload Files to Remote VM
def upload_file(ssh_client, local_path, remote_path):
    try:
        sftp = ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        logging.info(f"Uploaded {local_path} to {remote_path}")
        sftp.close()
        return True
    except Exception as e:
        logging.error(f"Failed to upload {local_path}: {e}")
        return False
    

# Step 4: Execute PowerShell Script on Remote VM
def execute_on_remote_vm(vm_ip, vm_username, vm_password, json_file_path, remote_ps_script_path):
    try:
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(vm_ip, username=vm_username, password=vm_password)

        # Execute the PowerShell script
        execute_cmd = f'powershell.exe -ExecutionPolicy Bypass -File "C:\\ProgramData\\policy_exec\\generate_policy_reg_files.ps1" -jsonFilePath "C:\\ProgramData\\policy_exec\\policies.json"'




        logging.info(f"Executing PowerShell script on the VM: {execute_cmd}")

        stdin, stdout, stderr = ssh.exec_command(execute_cmd)
        logging.error(f"StdErr: {stderr.read().decode()}")
        logging.info(f"StdOut: {stdout.read().decode()}")



        # Capture output and errors
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        logging.info(f"Script executed on the remote VM: {stdout_data}")

        if stderr_data:
            logging.error(f"Errors from the remote VM: {stderr_data}")
            return {"policy_file_path": None, "status": "error"}

        ssh.close()
        return {"policy_file_path": json_file_path, "status": "success"}

    except Exception as e:
        logging.error(f"Failed to execute script on remote VM: {e}")
        return {"policy_file_path": None, "status": "error"}

# Main Function: Orchestrates the Process
def main(specifications):
    # Ensure secure folder exists
    create_secure_folder()

    # Load VM credentials
    vm = load_deployment_data()
    vm_ip, vm_username, vm_password = vm['ip'], vm['username'], vm['password']

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip, username=vm_username, password=vm_password)
    # Continue with the upload logic...

    try:
        logging.info(f"Connecting to VM {vm_ip}")
        ssh.connect(vm_ip, username=vm_username, password=vm_password)

        # Define local and remote paths
        local_json_path = r"D:\NLP\NLPFinal\Main\policies.json"
        local_ps_script_path = r"D:\NLP\NLPFinal\Main\generate_policy_reg_files.ps1"
        remote_json_path = f"{SECURE_FOLDER}\\policies.json"
        remote_ps_script_path = f"{SECURE_FOLDER}\\generate_policy_reg_files.ps1"

        # Upload JSON and PowerShell script
        if upload_file(ssh, local_json_path, remote_json_path) and \
           upload_file(ssh, local_ps_script_path, remote_ps_script_path):

            # Execute the script only if both files were uploaded
            if execute_on_remote_vm(ssh, remote_ps_script_path, remote_json_path):
                logging.info("Policy execution completed successfully.")
                save_execution_log(specifications)
                logging.info("Policies executed successfully, logs saved.")
            else:
                logging.error("Policy execution failed on the VM.")
        else:
            logging.error("File upload failed. Execution aborted.")
    except Exception as e:
        logging.error(f"Connection to VM failed: {e}")
    finally:
        ssh.close()

# Example Usage
if __name__ == "__main__":
    sample_specifications = {
        'block_all': 'no',
        'conditionType[]': ['url', 'file_type'],
        'conditionValue[]': ['www.chatgpt.com', 'txt'],
        'BlockThirdPartyCookies': 'enable',
        'BrowsingDataLifetime[data_type]': 'download_history',
        'BrowsingDataLifetime[time_to_live_in_hours]': '3',
    }
    main(sample_specifications)
