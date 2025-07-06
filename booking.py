from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
from datetime import datetime, timedelta
import requests
import time
import os
import re

# Path to your Chrome profile
# Path to your Chrome profile (OS dependent)
if os.name == 'nt':  # Windows
    chrome_profile_path = "C:\\Users\\cleme\\AppData\\Local\\Google\\Chrome\\User Data"
else:  # macOS
    chrome_profile_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")


def get_chrome_version():
    """Get the installed version of Chrome browser"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            version = re.search(r'version\s+REG_SZ\s+([\d.]+)', result.stdout)
            if version:
                return version.group(1)
        else:  # Mac or Linux
            result = subprocess.run(
                ['google-chrome', '--version'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            version = re.search(r'([\d.]+)', result.stdout)
            if version:
                return version.group(1)
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
    return None

def get_webdriver_version(driver_path):
    """Get the version of the installed ChromeDriver"""
    try:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service)
        version = driver.capabilities['browserVersion']
        driver.quit()
        return version
    except Exception as e:
        print(f"Error getting WebDriver version: {e}")
        return None

def download_latest_webdriver(chrome_version):
    """Download the latest compatible ChromeDriver using webdriver-manager"""
    try:
        # Use webdriver_manager to handle the download and installation
        driver_path = ChromeDriverManager().install()
        print(f"Successfully updated ChromeDriver to match Chrome version {chrome_version}")
        return driver_path
    except Exception as e:
        print(f"Error updating ChromeDriver: {e}")
        return None

def check_and_update_webdriver(current_driver_path=None):
    """Check if WebDriver is up to date and update if needed"""
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Could not determine Chrome browser version")
        return None
    
    print(f"Installed Chrome version: {chrome_version}")
    
    if current_driver_path and os.path.exists(current_driver_path):
        driver_version = get_webdriver_version(current_driver_path)
        if driver_version:
            print(f"Current WebDriver version: {driver_version}")
            
            # Compare major versions (the number before the first dot)
            chrome_major = chrome_version.split('.')[0]
            driver_major = driver_version.split('.')[0]
            
            if chrome_major == driver_major:
                print("WebDriver is up to date")
                return current_driver_path
    
    print("WebDriver is outdated or not found, updating...")
    new_driver_path = download_latest_webdriver(chrome_version)
    return new_driver_path


def initialize_driver(service=None, destination=None):
    """Initialize Chrome driver with profile or fallback to guest mode"""
    chrome_options = webdriver.ChromeOptions()
    
    # Performance optimizations
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-restore-session-state")
    chrome_options.add_argument("--no-startup-window")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    
    # Try to use the existing profile first
    chrome_options.add_argument(f"--user-data-dir={chrome_profile_path}")
    
    try:
        print("Attempting to start Chrome with user profile...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        if destination:
            driver.get(destination)
        return driver
    except Exception as e:
        print(f"Failed to start with user profile (might be in use): {e}")
        print("Falling back to guest mode...")
        
        # Create new options for guest mode
        guest_options = webdriver.ChromeOptions()
        
        # Performance optimizations
        guest_options.add_argument("--no-sandbox")
        guest_options.add_argument("--disable-dev-shm-usage")
        guest_options.add_argument("--disable-gpu")
        guest_options.add_argument("--disable-extensions")
        guest_options.add_argument("--disable-plugins")
        guest_options.add_argument("--disable-images")
        
        # Guest mode settings
        guest_options.add_argument("--guest")
        guest_options.add_argument("--incognito")
        
        try:
            driver = webdriver.Chrome(service=service, options=guest_options)
            if destination:
                driver.get(destination)

            return driver
        except Exception as e:
            print(f"Failed to start in guest mode: {e}")
            raise Exception("Could not start Chrome in either profile or guest mode")
        

def is_12_pm():
    """Check if the current time is 12:00 PM."""
    return datetime.now().strftime('%H:%M') == '12:00'

def time_until_12_pm():
    """Calculate time in seconds until 12:00 PM."""
    now = datetime.now()
    target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
    if now >= target_time:
        return 0
    return (target_time - now).total_seconds()

def fast_click_attempt(driver, button_id):
    """Attempt to click button as fast as possible using multiple methods"""
    
    # Method 1: Direct find_element (fastest)
    try:
        button = driver.find_element(By.ID, button_id)
        if button.is_enabled():
            button.click()
            return True
    except (NoSuchElementException, Exception):
        pass
    
    # Method 2: JavaScript click (often faster than Selenium click)
    try:
        driver.execute_script(f"document.getElementById('{button_id}').click();")
        return True
    except Exception:
        pass
    
    # Method 3: WebDriverWait with very short timeout
    try:
        button = WebDriverWait(driver, 0.1).until(
            EC.element_to_be_clickable((By.ID, button_id))
        )
        button.click()
        return True
    except TimeoutException:
        pass
    
    return False

def main():
    destination = input("Enter booking page URL: ")
    current_driver_path = "chromedriver.exe"

    updated_driver_path = check_and_update_webdriver(current_driver_path)

    service = Service(current_driver_path) if os.path.exists(current_driver_path) else None
    if updated_driver_path:
        print(f"Using WebDriver at: {updated_driver_path}")
        service = Service(updated_driver_path)
    else:
        print("Failed to update WebDriver. Exiting.")
        return
    

        

    button_id = "bookEventButton"
    
    # Initialize the driver
    driver = initialize_driver(service, destination)
    
    # Navigate to the destination
    
    # Manual login time if needed
    print("\n" + "="*50)
    print("Please log in manually if necessary.")
    print("The script will wait for 60 seconds to allow you to log in.")
    print("="*50 + "\n")
    time.sleep(60)
    print("Continuing with booking process...")
    
    try:
        while True:
            print("Waiting until 12 PM...")
            
            # Wait until 12 PM with more precise timing
            while not is_12_pm():
                wait_time = time_until_12_pm()
                if wait_time > 60:  # If more than 1 minute, wait in chunks
                    print(f"Waiting {wait_time:.0f} seconds until 12 PM...")
                    time.sleep(30)  # Check every 30 seconds
                elif wait_time > 5:  # If less than 1 minute but more than 5 seconds
                    print(f"Almost time! {wait_time:.1f} seconds remaining...")
                    time.sleep(1)
                else:

                    time.sleep(max(0, wait_time))
                    break
            
            
            # Refresh the page
            driver.refresh()
            
            # Rapid-fire clicking attempts for first few seconds
            start_time = time.time()
            clicked = False
            attempt_count = 0
            
            while time.time() - start_time < 10 and not clicked:  # Try for 10 seconds
                clicked = fast_click_attempt(driver, button_id)
                attempt_count += 1
                
                if clicked:
                    print(f"SUCCESS! Button clicked after {attempt_count} attempts in {time.time() - start_time:.2f} seconds!")
                    break
                
                # Very short delay between attempts
             
            if clicked:
                break
            else:
                print(f"No button found after {attempt_count} attempts. Waiting for next 12 PM...")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Keep the browser open for 11 minutes after completion
    if clicked:
        print("Keeping browser open for 11 minutes...")
        time.sleep(660)
    
    # Close the driver
    driver.quit()

if __name__ == "__main__":
    main()