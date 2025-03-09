
#https://richmondcity.perfectmind.com/23650/Clients/BookMe4BookingPages/Classes?calendarId=1af5bfef-def5-4cfc-b9ef-96f1774033fb&widgetId=15f6af07-39c5-473e-b053-96653f77a406&embed=False
#bookEventButton

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

# Initialize ChromeDriver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

destination = input("Enter booking page URL: ")
button_id = "bookEventButton"

try:
    # Open the website
    driver.get(destination)

    # Function to check if it's 12 PM
    def is_12_pm():
        return datetime.now().strftime('%H:%M') == '12:00'

    # Function to calculate time until 12 PM
    def time_until_12_pm():
        now = datetime.now()
        target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)  # If it's already past 12 PM, target next day
        return (target_time - now).total_seconds()

    # Try to find and click the button
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
        print("Button found!")
        button.click()
    except Exception as e:
        print(f"Button not found. Error: {e}")
        print("Waiting until 12 PM to try again...")

        time_to_wait = time_until_12_pm()
        if time_to_wait > 0:
            print(f"Waiting for {time_to_wait:.2f} seconds until 12 PM...")
            time.sleep(time_to_wait)  # Sleep for the exact time difference

       
        driver.refresh()  # Refresh the page

        # Try to find and click the button again after refresh
        try:
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, button_id))
            )
            print("Button found after refresh!")
            button.click()
        except Exception as e:
            print(f"Failed to find the button after refresh. Error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
