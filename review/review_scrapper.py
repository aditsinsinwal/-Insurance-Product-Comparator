import requests
from bs4 import BeautifulSoup

def scrape_trustpilot_reviews(insurer_name):

    search_url = f"https://www.trustpilot.com/search?query={insurer_name.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    reviews = []
    for block in soup.find_all("p", class_="typography_body-l__KUYFJ"):
        reviews.append(block.text.strip())
        if len(reviews) >= 5:  # Limit for speed
            break
    return reviews
