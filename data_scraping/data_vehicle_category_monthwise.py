from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

def fetch_vehicle_categoty_monthwise_data(year, filename):
    """
    Scrapes vehicle registration data month-wise by vehicle category.
    """
    chrome_options = Options()
    # Use headless mode to run without a visible browser window.
    # chrome_options.add_argument("--headless")
    
    # Path to your chromedriver executable.
    service = Service("C://Users//jaswa//Downloads//chromedriver-win64//chromedriver-win64//chromedriver.exe")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml")
    
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 20)
    
    # Wait for initial page content to load.
    time.sleep(5)
    
    try:
        # Select the desired Year from the dropdown menu.
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@id='selectedYear_label']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[@data-label='{year}']"))).click()
        time.sleep(2)

        # Select "Vehicle Category" in Y-Axis.
        wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@id='yaxisVar_label']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@data-label='Vehicle Category']"))).click()
        time.sleep(2)

        # Select "Month Wise" for the X-Axis.
        wait.until(EC.element_to_be_clickable((By.XPATH,"//label[@id='xaxisVar_label']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[@data-label='Month Wise']"))).click()
        time.sleep(2)
        
        # Click the Refresh button.
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Refresh']"))).click()
        time.sleep(5)

        # Scrape the page content.
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    finally:
        driver.quit()
    
    # Create the 'src' directory if it does not exist.
    os.makedirs("src", exist_ok=True)
    
    file_path = os.path.join("src", filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
        
    print(f"Saved HTML for vehicle category {year} to {filename}")
        
if __name__ == "__main__":
    years = ["2025", "2024","2023"]
    for year in years:
        fname = f"vehicle_category_month_wise_{year}.html"
        fetch_vehicle_categoty_monthwise_data(year, fname)