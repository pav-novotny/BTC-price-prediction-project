import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import pandas as pd
import numpy as np
import os

os.makedirs("Data/Articles", exist_ok=True)

def get_articles(n_articles: int = 100, csv_save: bool = False):
    
    # a method extracts links of articles from bbc.com economy news.
    # n_articles: determines maximum number of articles to be extracted
    # csv_save: if True, links will be saved in csv in the file directory
    # returns a list links to articles

    url = "https://www.bbc.com/news/topics/c1038wnxypvt"

    if n_articles < 1:
        n_articles = 9999
        

    with sync_playwright() as p:

        print("Loading page...")

        browser = p.chromium.launch(headless=True)

        browser = browser.new_context(
        user_agent= "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36"
        )

        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=20000)

        print("Page loaded")

        time.sleep(1)

        articles = []

        first_it = True
        while len(articles) < n_articles:

            if first_it:
                article_list = page.locator("div[data-testid = 'alaska-grid'] a").all()
                articles = ["https://www.bbc.com/" + a.get_attribute("href") for a in article_list]
                first_it = False
            else:
                try:
                    page.locator("button[data-testid = 'pagination-next-button']").click(delay=200)
                except:
                    print("All available articles have been extracted!")
                    break
                time.sleep(1)
                article_list = page.locator("div[data-testid = 'alaska-grid'] a").all()
                article_list = ["https://www.bbc.com/" + a.get_attribute("href") for a in article_list]
                articles = articles + article_list
            
            print(f"Number of articles extracted: {len(articles)}")
        page.close()

        articles = articles[:n_articles]

        if csv_save:

            df = pd.DataFrame({"Link": articles})

            df.to_csv("Data/Articles/article_links.csv", index = False)

        return articles



def extract_articles(articles: list, save_csv: bool = False):

    article_dates = []
    article_titles = []
    article_content = []

    number_of_articles = len(articles)
    
    for i, article in enumerate(articles):

        print(article)

        response = requests.get(article)

        print(response.status_code)

        if response.status_code != 200:
            print("Article was not loaded correctly, skipping iteration...")
            continue

        page = BeautifulSoup(response.content, "html.parser")

        try:
            article_dates.append(page.find("time").attrs["datetime"][:10]) # find a time element and extracts date from datetime attribute in format YYYY-MM-DD (10 characters) and append to the list
        except:
            print("An error occured extracting the Date, skipping...")
            article_dates.append(None)

        try:
            article_titles.append(page.find("div", attrs={"data-component": "headline-block"}).get_text()) # find a title text and append to the list
        except AttributeError:
            try:
                article_titles.append(page.find("h1", attrs={"id": "main-heading"}).get_text())
            except AttributeError:
                print("An error occured extracting the Title, skipping...")
                article_titles.append(None)

        text = ""

        try:
            text_elements = page.find_all("div", attrs={"data-component": "text-block"}) # finds all text elements, extracts the text and transforms it to a single string
            for el in text_elements:
                text += el.get_text()
        except:
            print("An error occured extracting the content, skipping...")
            text = None

        article_content.append(text)

        print(f"Extracted articles: {i+1} from {number_of_articles}.")
    
    df = pd.DataFrame({"Date": article_dates, "Title": article_titles, "Content": article_content})

    if save_csv:
        df.to_csv("Data/Articles/articles_content.csv", index=False)
    
    return df


def scrape_news(n_articles: int = 100, save_links: bool = False, save_articles: bool = True):

    articles = get_articles(n_articles, save_links)

    df = extract_articles(articles, save_articles)

    return df

df = scrape_news(n_articles=0, save_links=False, save_articles=True)

