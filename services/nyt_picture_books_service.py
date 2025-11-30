import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def fetch_nyt_picture_books() -> List[Dict[str, str]]:
    url = "https://www.nytimes.com/books/best-sellers/2024/01/07/picture-books/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for book_item in soup.select("ol[data-testid='topic-list'] li"):
        title_tag = book_item.find("h3")
        author_tag = book_item.find("p", string=lambda s: s and s.lower().startswith("by "))
        if title_tag and author_tag:
            title = title_tag.get_text(strip=True)
            author = author_tag.get_text(strip=True).replace("by ", "")
            books.append({"title": title, "author": author})

    return books
