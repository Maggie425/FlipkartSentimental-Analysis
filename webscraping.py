import csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# Open Flipkart's search page for mobiles
url="https://www.flipkart.com/herbnaturo-ice-roller-face-eye/p/itm12d27ddf86f56?pid=KMTH48SARSKRQ8TF&lid=LSTKMTH48SARSKRQ8TFMM3TQ5&marketplace=FLIPKART&q=ice+roller&store=g9b%2Fema%2F5la&srno=s_1_2&otracker=search&otracker1=search&fm=organic&iid=en_r9GdmRR-fscEPTrixIaTlpaWF74VTa84N76zhJsx_-4CA2qJ_D8XSXMryVNVZuoyC4H7hvaFSUvbJI9eYedNkQ%3D%3D&ppt=hp&ppn=homepage&ssid=xv6wqd5b8g0000001731506473841&qH=fed28e11eb6832ed"
driver.get(url)

# Wait for the content to load (adjust the sleep time if necessary)
time.sleep(5)

# Find all mobile titles using their class name
titles = driver.find_elements(By.CLASS_NAME, "VU-ZEz")

# Print each title
for title in titles:
    print(title.text)

# Close the browser


rate=driver.find_element(By.CSS_SELECTOR, ".XQDdHH")

print(rate.text) 

reviews=driver.find_element(By.CLASS_NAME,'Wphh3N')
print(reviews.text)


driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)  # Adjust if necessary to allow full loading

# Find all links on the page
links = driver.find_elements(By.TAG_NAME, "a")

# Extract href attributes that end with "marketplace=FLIPKART"
filtered_links = [link.get_attribute("href") for link in links if link.get_attribute("href") and link.get_attribute("href").endswith("marketplace=FLIPKART")]

for link in filtered_links:
    print(link)

driver.get(link)
with open('flipkart_reviews.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Review"])

    # Loop through each page to get all reviews
    while True:
        # Find all review elements by class name
        comments = driver.find_elements(By.CLASS_NAME, 'z9E0IG')

        for comment in comments:
            writer.writerow([comment.text]) # Write each review to the CSV file

        # Check for the 'Next' button
        try:
            next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
            ActionChains(driver).move_to_element(next_button).click(next_button).perform()
            time.sleep(3)
        except:
            print("No more pages.")
            break


driver.quit()