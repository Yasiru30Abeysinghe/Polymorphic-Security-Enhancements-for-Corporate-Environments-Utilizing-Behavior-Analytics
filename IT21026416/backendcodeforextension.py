import subprocess
import logging

def find_extension_id(extension_name):
    """
    Call Puppeteer script via subprocess to find the extension ID by name.
    """
    try:
        # Run the Puppeteer script as a subprocess and wait for it to finish
        result = subprocess.run(['node', 'pupperteer_lookup.js', extension_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            extension_id = result.stdout.strip()  # Get the ID from Puppeteer's output
            if extension_id:
                logging.info(f"Extension ID for '{extension_name}': {extension_id}")
                return extension_id
            else:
                logging.error(f"No extension ID found for '{extension_name}'. Output was empty.")
                return None
        else:
            logging.error(f"Error running Puppeteer script for '{extension_name}': {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logging.error(f"Puppeteer script timed out for '{extension_name}'")
        return None
    except Exception as e:
        logging.error(f"Exception occurred while fetching extension ID for '{extension_name}': {e}")
        return None

def process_extension_whitelist_blacklist(whitelist, blacklist):
    """
    Process the whitelist and blacklist by finding the extension IDs for the given names.
    """
    whitelist_ids = []
    blacklist_ids = []

    # Fetch IDs for whitelist extensions
    for ext_name in whitelist:
        ext_id = find_extension_id(ext_name.strip())
        if ext_id:
            whitelist_ids.append(ext_id)
        else:
            logging.warning(f"Extension '{ext_name}' not found in whitelist.")

    # Fetch IDs for blacklist extensions
    for ext_name in blacklist:
        ext_id = find_extension_id(ext_name.strip())
        if ext_id:
            blacklist_ids.append(ext_id)
        else:
            logging.warning(f"Extension '{ext_name}' not found in blacklist.")

    return whitelist_ids, blacklist_ids
