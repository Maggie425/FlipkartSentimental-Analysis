from flask import Flask, request, render_template
import pandas as pd
import nltk
import re
import string
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['product_link']  
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 20) 
    
    try:
        driver.get(url)

        title_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "VU-ZEz")))
        title = title_element.text

        rate_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".XQDdHH")))
        rate = rate_element.text

    except TimeoutException:
        print("Error: Timed out waiting for elements to load.")
        title = "N/A"  
        rate = "N/A"   

    except NoSuchElementException:
        print("Error: Element not found on the page.")
        title = "N/A"
        rate = "N/A"

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    links = driver.find_elements(By.TAG_NAME, "a")
    filtered_links = [link.get_attribute("href") for link in links if link.get_attribute("href") and link.get_attribute("href").endswith("marketplace=FLIPKART")]

    
    if filtered_links:
        for link in filtered_links:
            print(link)
            driver.get(link)  
            break  
    else:
        print("No valid links found.")
        return render_template('result.html', title="Error", rate="N/A", sentiment="Error", positive=0, negative=0, neutral=0, image_url=None)

    stars = driver.find_elements(By.XPATH, "//div[contains(@class, 'BArk-j')]")
    ratings = []
    for star in stars:
        ratings.append(star.text)
    ratings = [int(rating.replace(",", "")) for rating in ratings]

    with open('flipkart_reviews.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Review"])
        while True:
            try:
                comments = driver.find_elements(By.CLASS_NAME, '_11pzQk')  

                if not comments:
                    comments = driver.find_elements(By.CLASS_NAME, 'z9E0IG') 
                for comment in comments:
                    writer.writerow([comment.text])
                next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
                ActionChains(driver).move_to_element(next_button).click(next_button).perform()
                time.sleep(3)
            except:
                break

    driver.quit()

    data = pd.read_csv("flipkart_reviews.csv")
    nltk.download('stopwords')
    stemmer = nltk.SnowballStemmer('english')
    from nltk.corpus import stopwords
    stopword = set(stopwords.words('english'))

    def clean(text):
        text = str(text).lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        text = [word for word in text.split(' ') if word not in stopword]
        text = " ".join(text)
        text = [stemmer.stem(word) for word in text.split(' ')]
        text = " ".join(text)
        return text

    data["Review"] = data["Review"].apply(clean)

    labels = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]

    plt.figure(figsize=(8, 8))
    plt.pie(ratings, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title("Distribution of Ratings")

    if not os.path.exists('static'):
        os.makedirs('static')

    plt.savefig('static/ratings_pie_chart.png')

    plt.close()

    nltk.download('vader_lexicon')
    sentiments = SentimentIntensityAnalyzer()
    data["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in data["Review"]]
    data["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in data["Review"]]
    data["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in data["Review"]]

    x = sum(data["Positive"])
    y = sum(data["Negative"])
    z = sum(data["Neutral"])
    if (x > y) and (x > z):
        sentiment = "Positive 😊"
    elif (y > x) and (y > z):
        sentiment = "Negative 😠"
    else:
        sentiment = "Neutral 🙂"

    return render_template(
        'Result.html',
        title=title,
        rate=rate,
        sentiment=sentiment,
        positive=x,
        negative=y,
        neutral=z,
        image_url='static/ratings_pie_chart.png'
    )

if __name__ == '__main__':
    app.run(debug=True)
