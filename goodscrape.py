from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

async def scrape(book_search="Wizard of Earthsea"):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('log-level=3')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options)


    driver.get("https://www.goodreads.com/search")
    driver.find_element(By.ID, "search_query_main").send_keys(book_search)
    driver.find_element(By.CLASS_NAME, "searchBox__button").click()

    book_info = {}

    # handle popup
    try:
        # try to click on the booktitle
        driver.find_element(By.CLASS_NAME, "bookTitle").click()
    except:
        # closes pop-up that may occur
        driver.find_element(By.CLASS_NAME, "gr-h3--noMargin").click()
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        driver.find_element(By.CLASS_NAME, "bookTitle").click()


    print("Printing info on book")
    print("============================")

    title = driver.find_element(By.CLASS_NAME, "Text__title1")
    print("Title: ", title.text)
    book_info["title"] = title.text

    author = driver.find_element(By.CLASS_NAME, "ContributorLink__name")
    print("Author: ", author.text)
    book_info["author"] = author.text

    rating = driver.find_element(By.CLASS_NAME, "RatingStatistics__rating")
    print("Rating: ", rating.text)
    book_info["rating"] = rating.text

    page_count = driver.find_element(By.CLASS_NAME, "FeaturedDetails").find_element(By.TAG_NAME, "p")
    print("Page count: ", page_count.text)
    book_info["page_count"] = page_count.text

    link = driver.current_url.split("?")[0]
    print("Link: ", link)
    book_info["link"] = link

    print(book_info)

    if len(book_info) != 5:
        raise Exception("Error: incorrect number of info found on book")

    return book_info

