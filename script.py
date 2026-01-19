from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import sys

n8n_webhook_url = "https://scripbox-businessinsights.app.n8n.cloud/webhook/3fa39e91-415b-4ac1-b919-c38ba54d449b"

# Reference for month names
all_months = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]

args = sys.argv[1:]
if len(args) < 2:
    print("Usage: python3 script.py YEAR1 [YEAR2 ...] MONTH1 [MONTH2 ...] [PM_NAME]")
    print("Example: python3 script.py 2023 2024 July August September")
    sys.exit(1)

# Separate years and months
years = [arg for arg in args if arg.isdigit()]
rest = [arg for arg in args if not arg.isdigit()]

# If the last non-numeric argument looks like a PM name (not a month), treat it as PM name
pm_name = "DEZERV INVESTMENTS PRIVATE LIMITED"
months = rest
if rest and rest[-1] not in all_months:
    pm_name = rest[-1]
    months = rest[:-1]

print(f"Years: {years}, Months: {months}, Portfolio Manager: {pm_name}")

for year in years:
    for month in months:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get("https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doPmr=yes")
            wait = WebDriverWait(driver, 50)

            Select(wait.until(EC.presence_of_element_located((By.NAME, "pmrId")))).select_by_visible_text(pm_name)
            Select(driver.find_element(By.NAME, "year")).select_by_visible_text(year)
            Select(driver.find_element(By.NAME, "month")).select_by_visible_text(month)

            driver.execute_script("getPMR();")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            result = ""
            for tr in soup.find_all("tr"):
                if "No. of clients" in tr.text:
                    result = tr.text.strip()
                    break

            payload = {
                "month": month,
                "year": year,
                "pm_name": pm_name,
                "result": result if result else "Not Found"
            }
            response = requests.post(n8n_webhook_url, json=payload)
            print(f"Sent {month} {year}: status {response.status_code}")

        finally:
            driver.quit()
            time.sleep(2)
