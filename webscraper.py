from urllib.request import Request, urlopen
import urllib.parse as parse_url
from bs4 import BeautifulSoup
import ssl


baseurl = "https://www.vagonweb.cz/razeni/vlak.php?"


def create_request(operator: str, category: str, number: str, year=2024) -> str:
    url = baseurl
    if operator:
        url = url + "&zeme=" + parse_url.quote(operator)
    if category:
        url = url + "&kategorie=" + category
    if number:
        url = url + "&cislo=" + number
    if year:
        url = url + "&rok=" + str(year)
    return url


def __request_vagonweb__(
    operator: str, category: str, number: str, year=2024
) -> BeautifulSoup:
    url = create_request(operator=operator, category=category, number=number, year=year)
    context = ssl._create_unverified_context()
    # headers = {"User-Agent": "PostmanRuntime/7.42.0", "Connection": "keep-alive"}
    req = Request(url)
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    )
    req.add_header("Connection", "keep-alive")

    try:
        response = urlopen(req, context=context)
        html_bytes = response.read()
        html_content = html_bytes.decode("utf-8")  # Decode bytes to string
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()
    return BeautifulSoup(html_content, "html.parser")


def __extract_train_class__(soup: BeautifulSoup) -> list:
    result = []
    vlacek_table = soup.find("table", class_="vlacek")

    if vlacek_table:
        # Use CSS selector to find the desired span element
        selector_carriages = "tr > td.bunka_vozu"
        carriages = vlacek_table.select(selector_carriages)
        for carriage in carriages:
            selector_class = "div > div > span.tab-radam"
            className = carriage.select_one(selector_class)
            if className:
                result.append(className.get_text(strip=True))
    return result
