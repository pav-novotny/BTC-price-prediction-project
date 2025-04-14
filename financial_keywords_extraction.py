from playwright.sync_api import sync_playwright
import time
import pandas as pd

with sync_playwright() as p:

    print("Loading page...")

    browser = p.chromium.launch(headless=True)

    browser = browser.new_context(
    user_agent= "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36")

    page = browser.new_page()

    page.goto("https://keywordseverywhere.com/ctl/top/economics-keywords", wait_until="domcontentloaded", timeout=20000)

    print("Page loaded")

    time.sleep(1)

    loc = page.locator("table > tbody > tr > td:nth-child(2)").all_inner_texts()

    loc.extend(["inflation", "government"])

    pd.Series(loc).to_csv("Data/Articles/financial_keywords.csv",index=False)

    browser.close()
