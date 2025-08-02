#!/usr/bin/env python3
"""
fetch_financial_news_yearly.py

Fetches financial news articles from NewsAPI daily and saves data into yearly Excel files.
Includes debug logging and saves each year’s data as soon as it’s collected.
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

# --- Configuration ---
API_KEY = "fefaefccad444b73a4585d1899d9df22"
DOMAINS = "bloomberg.com,reuters.com,ft.com,cnbc.com,wsj.com,marketwatch.com,forbes.com"
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 26)  # Update as needed

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def fetch_daily_articles(from_date, to_date, page=1):
    """Fetch articles from NewsAPI for one day."""
    logging.debug(f"Fetching articles from {from_date} to {to_date}, page {page}")
    params = {
        "q": "",
        "domains": DOMAINS,
        "from": from_date,
        "to": to_date,
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "pageSize": 100,
        "page": page
    }
    response = requests.get("https://newsapi.org/v2/everything", params=params)
    if response.status_code != 200:
        logging.error(f"Error fetching page {page}: {response.status_code} {response.text}")
        return []
    data = response.json()
    articles = data.get("articles", [])
    logging.debug(f"Received {len(articles)} articles")
    return articles

def save_yearly_data(year, records):
    """Save list of article records to an Excel file for the given year."""
    if not records:
        logging.info(f"No records for year {year}, skipping save.")
        return
    df = pd.DataFrame(records)
    filename = f"financial_news_{year}.xlsx"
    df.to_excel(filename, index=False)
    logging.info(f"Saved {len(df)} articles to {filename}")

def main():
    logging.info("Starting fetch of financial news")
    current_year = START_DATE.year
    year_records = []

    current_date = START_DATE
    while current_date <= END_DATE:
        from_str = current_date.strftime("%Y-%m-%d")
        to_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        page = 1
        daily_articles_count = 0

        while True:
            articles = fetch_daily_articles(from_str, to_str, page)
            if not articles:
                break
            daily_articles_count += len(articles)
            for art in articles:
                published = art.get("publishedAt", "")
                source_name = art.get("source", {}).get("name", "")
                title = art.get("title") or ""
                description = art.get("description") or ""
                content = art.get("content") or ""
                new_text = f"{title}\\n{description}\\n{content}"
                source_field = f"{source_name} {published}"
                year_records.append({
                    "Date": published,
                    "Source": source_field,
                    "New_text": new_text
                })
            page += 1

        logging.debug(f"Date {from_str}: fetched total {daily_articles_count} articles")

        # Year rollover: if next day is new year, save previous year
        next_day = current_date + timedelta(days=1)
        if next_day.year != current_year:
            save_yearly_data(current_year, year_records)
            year_records = []
            current_year = next_day.year

        current_date = next_day

    # Save the last year's data
    save_yearly_data(current_year, year_records)
    logging.info("Fetch complete.")

if __name__ == "__main__":
    main()
