import hashlib
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import os
from urllib.parse import urlparse
from PIL import Image
import pyautogui
import time

# In-memory cache setup
cache = {}

db = mysql.connector.connect(
   host="localhost",
   user="root",      
   password="root",  
   database="phishing_detection"  
)

cursor = db.cursor()

# Function to calculate hash of the domain for cache key
def hash_domain(domain):
    return hashlib.md5(domain.encode()).hexdigest()

# Function to check the cache
def check_cache(domain):
    hashed_domain = hash_domain(domain)
    if hashed_domain in cache:
        print(f"Cache hit for {domain}")
        return cache[hashed_domain]
    print(f"Cache miss for {domain}")
    return None


# Function to update the cache
def update_cache(domain, result):
    hashed_domain = hash_domain(domain)
    cache[hashed_domain] = result
    if result == "Warning: Potential Phishing Site":
        cache[hashed_domain] = "Blacklisted"
    print(f"Cache updated for {domain} with result: {result}")

# Function to extract the domain from the URL (using urllib.parse)
def extract_domain_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Extract the domain part of the URL
    return domain

# Function to take a screenshot, extract keywords, and capture the domain
def take_screenshot_and_extract_keywords(domain):
    try:
        # Setup Chrome WebDriver in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Enable headless mode
        #chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
        #chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (for Linux)
        #chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems (for Linux)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(domain)

        # Capture the screenshot
        #screenshot_filename = f"screenshots/{hash_domain(domain)}.png"
        #os.makedirs(os.path.dirname(screenshot_filename), exist_ok=True)
        #driver.save_screenshot(screenshot_filename)
        #print(f"Screenshot saved at: {screenshot_filename}")

        

        # Extract text from the webpage
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Extract keywords (simplified)
        keywords = text.split()[:20]  # Only take the first 20 words for simplicity

        # Extract the domain
        extracted_domain = extract_domain_from_url(domain)
        print(f"Extracted domain: {extracted_domain}")

        # Include the domain as a keyword
        keywords.append(extracted_domain)

        driver.quit()
        return keywords
    except Exception as e:
        print(f"Error taking screenshot or extracting keywords: {e}")
        return []

# Function to query the database for trusted domains
def query_trusted_domains(keywords):
    trusted_domains = []
    try:
        for keyword in keywords:
            cursor.execute("SELECT domain FROM trusted_domains WHERE domain LIKE %s", (f'%{keyword}%',))
            results = cursor.fetchall()
            for result in results:
                trusted_domains.append(result[0])
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error querying the database: {e}")
    return trusted_domains

def add_to_blacklist(domain):
    try:
        cursor.execute("INSERT INTO blacklisted_domains (domain) VALUES (%s)", (domain,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")



# Function to compare domains
def compare_domains(target_domain, trusted_domains):
    if target_domain in trusted_domains:
        return "No Risk"
    else:
        return "Warning: Potential Phishing Site"
    
def check_domain(domain):
    # Check the blacklist first
    cursor.execute("SELECT domain FROM blacklisted_domains WHERE domain = %s", (domain,))
    if cursor.fetchone():
        return "Blacklisted"

# Main function
def check_domain(domain):
    # Step 1: Check the cache
    cached_result = check_cache(domain)
    if cached_result:
        return cached_result

    # Step 2: Screenshot & Keyword Extraction
    keywords = take_screenshot_and_extract_keywords(domain)
    if not keywords:
        return "Unable to extract keywords, potential issue."

    # Step 3: Query Database
    trusted_domains = query_trusted_domains(keywords)
    if not trusted_domains:
        return "No matching domains found in the database."

    # Step 4: Compare Domains
    result = compare_domains(domain, trusted_domains)
    
    # Step 5: Update Cache and Return Result

        # Update Cache and Database
    update_cache(domain, result)
    if result == "Warning: Potential Phishing Site":
        add_to_blacklist(domain)
    return result

#Test with a specific domain
domain_to_check = "https://www.BOC.lk"  
risk_status = check_domain(domain_to_check)
print(f"The risk status for {domain_to_check} is: {risk_status}")
