
import os
import logging
import json
import paramiko
import requests
from datetime import datetime
from backendcodeforextension import process_extension_whitelist_blacklist
import subprocess

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

        #new from WFP
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
                

        # Processing other existing policies
        for key, value in specifications.items():
            if key not in ['domains', 'file_extension', 'BrowsingDataLifetime[data_types][]', 'BrowsingDataLifetime[time_to_live_in_hours]', *security_policies, 'BlockURLs', 'AllowURLs', 'WhitelistExtensions', 'BlacklistExtensions']:
                if value != 'not_configured':
                    policy_name = policy_mappings.get(key)
                    if policy_name:
                        # Convert SafeBrowsingProtectionLevel and other numeric settings to integers
                        if key == 'SafeBrowsingProtectionLevel':
                            policy_value = int(value)
                        elif key == 'BlockExcessiveAds':  # Ensure handling of this key
                            policy_value = 2 if value == 'enable' else 1
                        else:
                            # Convert values to integers where necessary
                            try:
                                policy_value = int(value) if value.isdigit() else 1 if value.lower() in ['allow', 'enable', 'yes'] else 0
                            except ValueError:
                                logging.error(f"Error converting {key}: {value} to integer.")
                                continue
                            policy_data[browser]['policies'][policy_name] = policy_value
                            logging.info(f"Set {policy_name} to {policy_value} for {browser}")
        
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
        whitelist_ids, blacklist_ids = process_extension_whitelist_blacklist(whitelist_extensions, blacklist_extensions)
        logging.info(f"Whitelist IDs: {whitelist_ids}")
        logging.info(f"Blacklist IDs: {blacklist_ids}")

        # Update policies with the fetched extension IDs
        if whitelist_ids:
            logging.debug(f"Whitelist IDs to be written: {whitelist_ids}")
            policy_data[browser]['policies']['ExtensionInstallAllowlist'] = whitelist_ids
        else:
            policy_data[browser]['policies']['ExtensionInstallAllowlist'] = []  # If no IDs, assign empty list

        if blacklist_ids:
            logging.debug(f"Blacklist IDs to be written: {blacklist_ids}")
            policy_data[browser]['policies']['ExtensionInstallBlocklist'] = blacklist_ids
        else:
            policy_data[browser]['policies']['ExtensionInstallBlocklist'] = []  # If no IDs, assign empty list


    # Generate the browser extension config


    logging.info(f"Final policy data for {browser}: {json.dumps(policy_data[browser], indent=4)}")

    local_json_path = r"D:\NLP\NLPFinal\Main\policies.json"
    with open(local_json_path, 'w') as json_file:
        json.dump(policy_data, json_file, indent=4)
    logging.info(f"Policies saved locally to {local_json_path}")

    with open('deployment.json', 'r') as file:
        deployment_data = json.load(file)
    vm = deployment_data['vms'][0]
    vm_ip = vm['ip']
    vm_username = vm['username']
    vm_password = vm['password']
    
    remote_json_path = r"C:\policy_exec\policies.json"

    remote_ps_script_path = r"C:\policy_exec\generate_policy_reg_files.ps1"

    # Ensure we handle JSON and PowerShell script in the same manner
    if upload_json_to_vm(vm_ip, vm_username, vm_password, local_json_path, remote_json_path):
        # Now upload PowerShell script in the same way
        local_ps_script_path = r"D:\NLP\NLPFinal\Main\generate_policy_reg_files.ps1"
        if upload_ps_script_to_vm(vm_ip, vm_username, vm_password, local_ps_script_path, remote_ps_script_path):
            # If both files were uploaded successfully, execute the script
            result = execute_on_remote_vm(vm_ip, vm_username, vm_password, remote_json_path, remote_ps_script_path)
            return result
        else:
            logging.error("Failed to upload PowerShell script to the VM.")
            return {"status": "error", "details": "Failed to upload PowerShell script."}
    else:
        logging.error("Failed to upload JSON file to the VM.")
        return {"status": "error", "details": "Failed to upload JSON file."}

def upload_ps_script_to_vm(vm_ip, vm_username, vm_password, local_ps_script_path, remote_ps_script_path):
    try:
        logging.info(f"Connecting to VM {vm_ip} to upload PowerShell script.")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip, username=vm_username, password=vm_password)

        sftp = ssh.open_sftp()

        # Ensure remote directory exists
        remote_dir = os.path.dirname(remote_ps_script_path)
        logging.info(f"Checking if remote directory {remote_dir} exists.")
        try:
            sftp.stat(remote_dir)
            logging.info(f"Directory {remote_dir} already exists.")
        except FileNotFoundError:
            logging.info(f"Creating remote directory {remote_dir}.")
            sftp.mkdir(remote_dir)

        # Upload the PowerShell script
        logging.info(f"Attempting to upload PowerShell script {local_ps_script_path} to {remote_ps_script_path}")
        sftp.put(local_ps_script_path, remote_ps_script_path)
        logging.info(f"PowerShell script uploaded successfully to {remote_ps_script_path}")
        
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logging.error(f"Error during PowerShell script upload or SSH connection: {e}")
        return False
    

def upload_json_to_vm(vm_ip, vm_username, vm_password, local_json_path, remote_json_path):
    try:
        logging.info(f"Connecting to VM {vm_ip} for file upload.")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip, username=vm_username, password=vm_password)

        # Ensure remote directory exists
        sftp = ssh.open_sftp()
        remote_dir = os.path.dirname(remote_json_path)
        logging.info(f"Checking if remote directory {remote_dir} exists.")
        
        try:
            sftp.stat(remote_dir)
            logging.info(f"Directory {remote_dir} already exists.")
        except FileNotFoundError:
            logging.info(f"Creating remote directory {remote_dir}.")
            sftp.mkdir(remote_dir)

        # Attempt to upload the file
        logging.info(f"Attempting to upload {local_json_path} to {remote_json_path}")
        sftp.put(local_json_path, remote_json_path)
        logging.info(f"File uploaded successfully to {remote_json_path}")
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        logging.error(f"Error during file upload or SSH connection: {e}")
        return False

def execute_on_remote_vm(vm_ip, vm_username, vm_password, json_file_path, remote_ps_script_path):
    """
    Connects to the remote VM, uploads the PowerShell script, and executes it.
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip, username=vm_username, password=vm_password)

        # Execute the PowerShell script on the VM
        execute_cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{remote_ps_script_path}" -jsonFilePath "{json_file_path}"'
        logging.info(f"Executing PowerShell script on the VM: {execute_cmd}")
        stdin, stdout, stderr = ssh.exec_command(execute_cmd)

        # Capture and log the command output and error
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
if __name__ == "__main__":
    specifications = {
        'block_all': 'no',  # Change to 'yes' for testing blocking all downloads
        'conditionType[]': ['url', 'file_type'],
        'conditionValue[]': ['www.chatgpt.com', 'txt'],
        'BlockThirdPartyCookies': 'enable',
        'BrowsingDataLifetime[data_type]': 'download_history',
        'BrowsingDataLifetime[time_to_live_in_hours]': '3',
    }
    result = generate_policy_files(specifications)

    if result:
        logging.info(f"Policy generation result: {result}")
    else:
        logging.error("Policy generation failed.")

    
    # Add logging to inspect the result object
    if result is None:
        logging.error("Failed to generate policy files: Result is None")
        exit(1)  # Exit or handle error appropriately

    logging.info(f"Result from generate_policy_files: {result}")

    if result.get("status") == "success":
        # Define the local path of the PowerShell script
        local_ps_script_path = r"D:\NLP\NLPFinal\Main\generate_policy_reg_files.ps1"
        # Define the remote path where the PowerShell script should be uploaded on the VM
        remote_ps_script_path = r"C:\policy_exec\generate_policy_reg_files.ps1"

        # Add logging to verify the function call arguments
        logging.info(f"Calling execute_on_remote_vm with: vm_ip={result['vm_ip']}, "
                     f"vm_username={result['vm_username']}, vm_password={result['vm_password']}, "
                     f"policy_file_path={result['policy_file_path']}, "
                     f"local_ps_script_path={local_ps_script_path}, "
                     f"remote_ps_script_path={remote_ps_script_path}")
        
        # Execute the script on the remote VM
        try:
            ps_result = execute_on_remote_vm(
                result["vm_ip"], 
                result["vm_username"], 
                result["vm_password"], 
                result["policy_file_path"], 
                local_ps_script_path, 
                remote_ps_script_path
            )
            
            # Log and print the result from the function
            logging.info(f"Result from execute_on_remote_vm: {ps_result}")
            print(ps_result)
        
        except Exception as e:
            logging.error(f"Failed to execute PowerShell script on the VM: {e}")
            print(f"Failed to execute PowerShell script: {e}")
    else:
        logging.error(f"Error in generating policies: {result.get('details', 'Unknown error')}")
