from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
import re

class Engine:

    def __init__(self, url):
        self.url = url
        # Initialize the Chrome WebDriver with options to optimize performance
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')  # Run in headless mode
        firefox_options.add_argument('--no-sandbox')  # Bypass OS security model
        firefox_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        # self.driver = webdriver.Remote(
        # command_executor='http://localhost:4444/wd/hub',
        # options=firefox_options
        # )
        self.driver = webdriver.Chrome()
        #self.driver = driver = webdriver.Firefox()

    def page_switch(self,mode='main'):
        try:
            if mode == "main":
                url = self.url
            else:
                url = self.driver.current_url             

            pattern = r"page-(\d+)"
            match = re.search(pattern, url)
            if match:
                current_page = int(match.group(1))
                new_page = current_page + 1
                new_url = re.sub(pattern, f"page-{new_page}", url)
            else:
                if mode == "forum":
                    new_url = url+"page-2#replies"
            if mode == 'forum':
                #print(f"in {new_url}")
                sleep(1)
                self.driver.get(new_url)
            if mode == 'main':
                self.url = new_url
                self.driver.get(new_url)
        except Exception as e:
            print(f"An error occurred: {e}")


    def scrape_link(self):
        # Navigate to the URL
        self.driver.get(self.url)
        link_replies = []
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class=" thread-title--gtm"]')))
            # Find all matching anchor elements
            link_elements = self.driver.find_elements(By.XPATH, '//a[@class=" thread-title--gtm"]')
            # Loop through each found link and print the href attribute
            for link in link_elements:
                href = link.get_attribute("href")
                # link_replies.append(f"{href}page-1#replies")
                link_replies.append(f"{href}")
                #print(f"{href}page-1#replies")

        except TimeoutException:
            print("Timeout while waiting for links to load.")
        except Exception as e:
            print(f"An error occurred in scrape_link: {e}")
        finally:
            return link_replies
        
    def peek_forum(self, link):
        """Navigates to a specific forum thread."""
        try:
            print(f"Peeking forum link: {link}")
            self.driver.get(link)
            sleep(2)
        except Exception as e:
            print(f"An error occurred in peek_forum: {e}")

    def pop_forum(self):
        """Navigates back to the main forum URL."""
        try:
            self.driver.get(self.url)
            sleep(2)
        except Exception as e:
            print(f"An error occurred in pop_forum: {e}")

    def peek_forum_page(self):
        try:
            max_page_number = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,'//a[@class="button pageNav-jump"]')))
            return int(max_page_number.text)
        except (TimeoutException, NoSuchElementException):
            return 1  # Default to 1 if no pagination is found
        except Exception as e:
            print(f"An error occurred in peek_forum_page: {e}")
            return 
    
    def scrape_data_in_forum(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="js-quickEditTarget message-cell-content-wrapper"]/div/div')))
                # Find all matching anchor elements
            texts = self.driver.find_elements(By.XPATH, '//div[@class="js-quickEditTarget message-cell-content-wrapper"]/div/div')
        except TimeoutException:
            return 0 
        except TimeoutException:
            print("Timeout while waiting for forum data to load.")
        except StaleElementReferenceException:
            print("Stale element reference error.")
        except Exception as e:
            print(f"An error occurred in scrape_data_in_forum: {e}")
        finally:
            return texts
        
    def close(self):
        """Closes the WebDriver."""
        self.driver.quit()

datas = []

try:
    engine = Engine("https://www.personalitycafe.com/threads/you-know-youre-a-perceiver-when.38412/")
    engine.driver.get(engine.url)
    max_page = engine.peek_forum_page()
    for j in range(1,max_page):
        texts = engine.scrape_data_in_forum()
        for text in texts:
            datas.append(text.text.strip())
        if(max_page-1):
            engine.page_switch("forum")
 
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    engine.close()
    df = pd.DataFrame(datas, columns=["text"])
    df.to_csv("perceiver.csv", index=False)
    print("Data collected:", datas)

