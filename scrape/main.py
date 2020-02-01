from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from datetime import datetime

s=["start"]
while s:
    quote_page = "https://wpilib.org/blog/machine-learning-technology-preview-coming-soon"
    page = urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    s = soup.find_all("p", string="Check back in the coming days for more details!")
    print("Probably not updated yet")
    time.sleep(900)
print("Update @ {}".format(datetime.now()))