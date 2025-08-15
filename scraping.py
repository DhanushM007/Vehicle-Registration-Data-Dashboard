import subprocess
import sys

scripts = [
    "data_scraping/data_manufacturer_monthwise.py",
    "data_scraping/data_manufacturer.py",
    "data_scraping/data_vehicle_category_monthwise.py",
    "data_scraping/data_vehicle_class.py"
]

for script in scripts:
    print(f"\n Running: {script}")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f" Errors/Warnings from {script}:\n{result.stderr}")

print("\n All scripts finished running.")
