from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import re
import requests
from time import sleep
# штука, вещь, дело, история,
WORDS = "штука, вещь, дело, история, факт, случай, событие, явление, новость".split(", ")
driver_path = r"C:\chromedriver\chromedriver.exe"
site = r"https://processing.ruscorpora.ru/"


def final_parse_1(html: str):
    TEXT = ""
    soup = BeautifulSoup(html, "html.parser")
    urls = soup.find_all('a', class_="b-kwic-expl")

    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    for url in urls:

        # getting full-loaded text page
        # try:
        #     with Chrome(driver_path, options=chrome_options) as browser:
        #         browser.get(site + url["href"])  # TIME!!!
        #         html_curr = browser.page_source
        # except:
        #     print('lol')
        #     sleep(10)
        try:
            response = requests.get(site + url["href"])
            sleep(1.3)
            if response.status_code == 429:
                # sleep(2)
                response = requests.get(site + url["href"])
                print(response.status_code, "  ..was sleeping")
            html_curr = response.text
        except:
            print("err")
            continue

        # getting text from page
        new_soup = BeautifulSoup(html_curr, "html.parser")
        text_tag = new_soup.find_all("li")
        for phrase in text_tag:
            TEXT += phrase.getText().strip()
    return TEXT


def pretty_text(answer: str):
    answer = re.sub("([\[]).*?([\]])", "", answer)  # deleting all of [**]
    answer = re.sub("[^А-Яа-я0-9,!\.\? \n\-_Ёё―:…\*\@\\ \(\)%\$;\"\'\|]", "", answer)
    # answer = re.sub(r"[\s]", " ", answer)
    # answer = re.sub(r" +", " ", answer)
    return answer


def final_parse(html: str):
    soup = BeautifulSoup(html, "html.parser")
    tabs = soup.find_all("ul")
    answer = ""
    flag = True
    if len(tabs) < 1:
        flag = False
    for tab in tabs:
        answer += tab.get_text()
    return pretty_text(answer), flag


def parser(url: str, word: str, filename: str):
    driver = webdriver.Chrome(driver_path)
    driver.get(url)
    search_bar = driver.find_element_by_name("req")  # finding word bar
    search_bar.send_keys(word)  # entering data in word bar

    search_btn = driver.find_element_by_class_name("button")  # finding enter button and clicking
    search_btn.click()

    driver.switch_to.window(driver.window_handles[-1])  # switching windows

    html = driver.page_source
    text, flag = final_parse(html)
    do_txt(text, filename)

    soup = BeautifulSoup(html, "html.parser")  # finding max_page
    pages = soup.find("p", class_="pager")
    try:
        max_page = int(pages.text.strip("следующая страница").split()[-1])
    except:
        try:
            max_page = int(pages.text.strip("следующая страница").split()[-2])
        except:
            max_page = 1

    st = driver.current_url
    driver.get(st[:st.index("mode=")] + f"p={1}&" + st[st.index("mode="):])
    sleep(1.5)
    html = driver.page_source
    text, flag = final_parse(html)
    do_txt(text, filename)

    for i in range(1, max_page):  # PARSING
        print(f"pages: {i} of {max_page}")
        st = driver.current_url
        before = st[:st.index("mode=") - len(str(int(i))) - 3]
        after = st[st.index("mode="):]
        driver.get(before + f"p={i + 1}&" + after)
        html = driver.page_source
        text, flag = final_parse(html)
        if not flag:
            break
        do_txt(text, filename)
        sleep(1.5)

    driver.close()
    print("almoust done")
    # answer = re.sub("([\[]).*?([\]])", "", answer)  # deleting all of [**]


def do_txt(text: str, filename: str):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text)


def test(word: str):
    text = []
    with open(f"{word}.txt", "r", encoding="utf-8") as f:
        text = f.read().split("\n" * 2)
    with open(f"{word}.txt", "w", encoding="utf-8") as f:
        for line in text:
            if len(re.findall("[А-Яа-я]", line)) != 0:
                f.write(line.strip() + "\n" * 2)


languages = "hy ba be bg bua es it zh lv lit de pl uk fr fin cze sv et".split()

if __name__ == '__main__':
    for word in WORDS:
        # for language in languages:
            # parser(f"https://ruscorpora.ru/new/search-para-{language}.html", word, f"{word}.txt")
        test(word)
