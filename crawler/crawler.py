"crawler.py"

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

URL_LINK = "https://boardgamegeek.com/boardgame/167355/nemesis/ratings?pageid=2"


# def get_url_content(url):
#     "return"

#     content = requests.get(url).text
#     soup = BeautifulSoup(content, "html.parser")

#     text = soup.find("div", {"class": "game-secondary"}).text
#     print(text)


# get_url_content(URL_LINK)

PATH = r"F:/Programmierung/Chromedriver/chromedriver.exe"
driver = webdriver.Chrome(PATH)
# opts = Options()
# opts.binary_location = r"C:/ProgramFiles(x86)/Google/Chrome/Application"


# # Instantiate options
# opts = Options()
# # opts.add_argument(" — headless") # Uncomment if the headless version needed
# opts.binary_location = "<path to Chrome executable>"

# # Set the location of the webdriver
# chrome_driver = os.getcwd() + "<Chrome webdriver filename>"

# # Instantiate a webdriver
# driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

# # Load the HTML page
# driver.get(os.getcwd() + "/test.html")

# # Parse processed webpage with BeautifulSoup
# soup = BeautifulSoup(driver.page_source)
# print(soup.find(id="test").get_text())
