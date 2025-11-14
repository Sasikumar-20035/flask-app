from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_sebi(month, year, pm_name):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doPmr=yes")
        wait = WebDriverWait(driver, 10)

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

        return result if result else "Not Found"

    finally:
        driver.quit()

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    month = data.get("month", "September")
    year = data.get("year", "2025")
    pm_name = data.get("pm_name", "DEZERV INVESTMENTS PRIVATE LIMITED")
    result = scrape_sebi(month, year, pm_name)
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)