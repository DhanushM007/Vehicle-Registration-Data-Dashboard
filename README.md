# Vehicle Registrations Data Dashboard

This project is a suite of Python scripts designed to scrape vehicle registration data from the official Vahan portal and visualize it using a Streamlit dashboard.

---

### 📂 File Structure

The project is structured into two main parts: data scraping and data visualization.

- `scraping.py`: The main script to run all the individual data scraping scripts.
- `app.py`: The Streamlit application that provides an interactive dashboard for the scraped data.
- `data_scraping/` (directory): Contains the individual scraping scripts for different data types.
  - `data_manufacturer_monthwise.py`
  - `data_manufacturer.py`
  - `data_vehicle_category_monthwise.py`
  - `data_vehicle_class.py`
- `src/` (directory): This folder will be created automatically to store the HTML files scraped by the Python scripts.

---

### ⚙️ Setup Instructions

To run this project, you'll need Python and a few libraries.

1.  **Install Dependencies:**
    You can install all the required Python libraries at once by running the following command in your terminal:
    ```sh
    pip install -r requirements.txt
    ```
2.  **Install and Set Up ChromeDriver:**
    The scraping scripts use Selenium, which requires a web driver to control a browser. This project is configured to use **ChromeDriver**. You must install it and specify its path in the scraping scripts.
    - Download the correct version of ChromeDriver that matches your Chrome browser version from the official [ChromeDriver website](https://chromedriver.chromium.org/).
    - Extract the downloaded zip file and place the `chromedriver.exe` file in a location of your choice.
    - Open each Python file in the `data_scraping/` directory and update the `service` variable with the path to your downloaded `chromedriver.exe` file.
      ```python
      service = Service("path/to/your/chromedriver.exe")
      ```
3.  **Scrape the Data:**
    Before you can run the dashboard, you need to scrape the data.
    - Run the main scraping script from your terminal:
        ```sh
        python scraping.py
        ```
    - This will create a `src` folder and save the scraped HTML files inside it.
4.  **Run the Dashboard:**
    Once the data is scraped, you can launch the Streamlit dashboard.
    - Run the `app.py` file from your terminal:
        ```sh
        streamlit run app.py
        ```
    - The dashboard will open in your web browser, displaying the data from the HTML files in the `src` folder.

---

### 📊 Data Assumptions

- **Data Source**: The scripts are specifically designed to scrape data from `https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml`
- **HTML Structure**: The scripts assume the HTML structure of the Vahan dashboard remains consistent. Any changes to the website's HTML ids, classes, or general layout may break the scraping functionality.
- **Time Period**: The scraping scripts are currently configured to fetch data for the years 2023, 2024, and 2025. This can be easily modified in the `if __name__ == "__main__":` block of each script.
- **Local Storage**: The scraped data is stored locally as HTML files in the `src` directory.

---

### 🚀 Feature Roadmap

This project can be extended with the following enhancements:

- **Dynamic Scraping**: Modify `app.py` to trigger the scraping scripts on demand, rather than requiring them to be run separately.
- **Database Integration**: Instead of saving to local HTML files, integrate a database (e.g., SQLite, PostgreSQL) to store the data for more efficient querying and scaling.
- **Advanced Visualizations**: Add more complex charts and graphs (e.g., heatmaps, scatter plots) to provide deeper insights into the vehicle registration data.
- **Automated Updates**: Set up a scheduler (e.g., cron job, Windows Task Scheduler) to run the scraping scripts automatically on a daily or weekly basis to keep the data fresh.

---
