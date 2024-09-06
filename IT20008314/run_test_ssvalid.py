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
import base64
import io
import cv2
import pytesseract
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np
# Flask setup
app = Flask(__name__)

# Database setup
DATABASE_URL = 'mysql+pymysql://root:root@localhost/phishing_detection'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class ActionLog(Base):
    __tablename__ = 'action_logs'
    id = Column(Integer, primary_key=True)
    domain = Column(String(255))
    result = Column(String(50))
    extracted_text = Column(Text)

Base.metadata.create_all(engine)

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

# Function to check if a domain is blacklisted
def is_blacklisted(domain):
    try:
        cursor.execute("SELECT COUNT(*) FROM blacklisted_domains WHERE domain = %s", (domain,))
        result = cursor.fetchone()
        return result[0] > 0  # Return True if domain is found in blacklist
    except Exception as e:
        print(f"Error querying the database: {e}")
        return False

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

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(domain)

        # Capture screenshot
        screenshot = driver.get_screenshot_as_png()
        driver.quit()

        # Save screenshot to a temporary file
        screenshot_filename = f"screenshots/{hash_domain(domain)}.png"
        os.makedirs(os.path.dirname(screenshot_filename), exist_ok=True)
        with open(screenshot_filename, 'wb') as file:
            file.write(screenshot)

        # Extract text from the webpage
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Extract keywords (simplified)
        keywords = text.split()[:20]  # Only take the first 20 words for simplicity
        print("Extracted text:", text)
       


        # Extract the domain
        extracted_domain = extract_domain_from_url(domain)
        print(f"Extracted domain: {extracted_domain}")

        # Include the domain as a keyword
        keywords.append(extracted_domain)

        return keywords, screenshot_filename
    except Exception as e:
        print(f"Error taking screenshot or extracting keywords: {e}")
        return [], None

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

def log_action(domain, result, extracted_text):
    log_entry = ActionLog(domain=domain, result=result, extracted_text=extracted_text)
    session.add(log_entry)
    session.commit()

@app.route('/validate', methods=['POST'])
def validate_screenshot():
    data = request.json
    image_data = data.get('image')
    domain = data.get('domain')

    try:
        # Decode the image
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(',')[1])))
        image_np = np.array(image)

        # Perform text extraction
        text = pytesseract.image_to_string(image_np)

        # Perform image comparison (placeholder function)
        match_score = compare_screenshots(image_np, domain)

        if match_score > 0.8:  # Threshold for a match (example value)
            log_action(domain, 'safe', text)
            return jsonify({'action': 'none'})
        else:
            log_action(domain, 'policy_violation', text)
            return jsonify({'action': 'restrict'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def compare_screenshots(image, domain):
    # Placeholder function for screenshot comparison
    # Implement image comparison logic here
    return 0.5  # Example score, replace with actual comparison result

# Main function
def check_domain(domain):
    # Step 1: Check the cache
    cached_result = check_cache(domain)
    if cached_result:
        return cached_result

    # Step 2: Check if the domain is blacklisted
    if is_blacklisted(domain):
        return "Warning: Domain is blacklisted"

    # Step 3: Screenshot & Keyword Extraction
    keywords, screenshot_filename = take_screenshot_and_extract_keywords(domain)
    if not keywords:
        return "Unable to extract keywords, potential issue."

    # Step 4: Query Database
    trusted_domains = query_trusted_domains(keywords)
    if not trusted_domains:
        return "No matching domains found in the database."

    # Step 5: Compare Domains
    result = compare_domains(domain, trusted_domains)

    # Step 6: Update Cache and Return Result
    update_cache(domain, result)
    if result == "Warning: Potential Phishing Site":
        add_to_blacklist(domain)
    
    # Optional: Send screenshot to server for further validation
    if screenshot_filename:
        with open(screenshot_filename, 'rb') as file:
            image_base64 = base64.b64encode(file.read()).decode('utf-8')
        send_screenshot_to_server(domain, image_base64)

    return result

def send_screenshot_to_server(domain, image_base64):
    import requests
    response = requests.post('https://yourserver.com/validate', json={'domain': domain, 'image': image_base64})
    if response.ok:
        print("Screenshot sent for validation.")
    else:
        print("Failed to send screenshot.")

# Test with a specific domain
if __name__ == "__main__":
    domain_to_check = "https://www.boc.lk"
    risk_status = check_domain(domain_to_check)
    print(f"The risk status for {domain_to_check} is: {risk_status}")

    # Run Flask server
   # app.run(ssl_context=('cert.pem', 'key.pem'))  # For HTTPS
