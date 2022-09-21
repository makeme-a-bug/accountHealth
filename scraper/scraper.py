import random
import time
from typing import Dict,List,Any,Union
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from .utils import solve_captch
from rich.console import Console
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException , NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from dateutil.parser import parse
import pandas as pd

class Scraper(webdriver.Remote):

    def __init__(self,profile_name:str,profile_uuid:str, url:List[str], command_executor:str, destroy_browser:bool = False , tracker:List = [] ) -> None:
        self.command_executor = command_executor
        # self.capabilities = desired_capabilities
        self.profile_name = profile_name
        self.profile_uuid = profile_uuid
        self.url = url
        self.destroy_browser = destroy_browser
        self.console = Console()
        self.tracker = tracker
        self.current_page = 1

        super(Scraper,self).__init__(self.command_executor,desired_capabilities={})
        self.set_page_load_timeout(120)
        self.implicitly_wait(120)
        try:
            self.maximize_window()
        except:
            pass


    def get_data(self):
        """
        Starts reporting for the urls and profile given in the initial
        """
        data = []
        if self.get_page(self.url):
            if self.wait_for_table():
                while True:
                    temp_data = self.get_table()
                    data.extend(temp_data)
                    if not self.get_next_page():
                        break
                    
        return data
        # self.quit()


    def get_table(self):
        rows = self.find_elements_by_class_name("ahd-product-policy-table-row-wrapper")
        table = []
        if rows:
            for row in rows:
                cols = row.find_elements(By.CSS_SELECTOR,"[class*='kat-col']")
                reason = None
                action = None
                date = None
                what_was_impacted = None
                next_step = None
                asin = None
                for i,col in enumerate(cols):
                    if i==0:
                        reason = col.find_element(By.TAG_NAME,'a').text
                    elif i==1:
                        date = col.find_element(By.TAG_NAME,'span').text
                    elif i==2:
                        eles = col.find_elements(By.TAG_NAME,'span')
                        what_was_impacted = eles[0].text
                        asin = eles[1].text.replace('ASIN: ','')
                    elif i==3:
                        action = col.find_element(By.TAG_NAME,'span').text
                    else:
                        next_step = col.find_element(By.TAG_NAME,'kat-button').get_attribute("label")
                table.append({
                    "Reason":reason,
                    "Date":parse(date).strftime("%m/%d/%Y"),
                    "ASIN":asin,
                    "Product Title":what_was_impacted,
                    "Action Taken":action,
                    "Status":next_step,
                })

        return table
    
    def wait_for_table(self):
        table_loaded = False
        for i in range(2):
            try:
                self.implicitly_wait(20)
                WebDriverWait(self, 20).until(EC.presence_of_element_located((By.CLASS_NAME,"ahd-product-policy-table-row-wrapper")))
                self.console.log(f"table for page:{self.current_page}",style="blue")
                table_loaded = True
                self.implicitly_wait(120)
                break
            except TimeoutException:
                continue
        self.implicitly_wait(120)
        return table_loaded

    def get_page(self,url:str) -> None:
        """
        gets the url in the browser.\n
        parameters:\n
        url:<str>
        returns:\n
        None
        """
        url_open = False
        self.get(url)
        time.sleep(3)
        for i in range(3):
            try:
                captcha = self.solve_captcha()
                logged_in = self.is_profile_logged_in()
                if captcha and logged_in:
                    WebDriverWait(self, 60).until(EC.presence_of_element_located((By.ID,"ahd-product-policy-title")))
                    url_open = True
                else:
                    pass
                break
            except TimeoutException:
                self.get(url)
        return url_open

    def solve_captcha(self) -> bool:
        """
        Checks if captcha appreared on the page.if appeared will try to solve it.
        return:
        True  : if captcha was solved
        False : if captcha was not solved
        """

        if "Try different image" in self.page_source:
            print(f"Captcha appear for profile [{self.profile_uuid}]")
            if not solve_captch(self):
                print(self.profile_name, "CAPTCHA not solved")
                return False
        return True
    
    def is_profile_logged_in(self) -> bool:
        """
        Checks if the multilogin is logged into amazon \n
        returns:\n
        True  : if the profile is logged in
        False : if the profile is not logged in
        """
        time.sleep(10)
        if "By continuing, you agree to Amazon's" not in self.page_source:
            return True
        self.console.log(f"{self.profile_name}:Profile not logged in into Amazon account",style='red')
        return False

    
    def get_next_page(self):
        while True:
            elements = self.execute_script("""return document.getElementById('ahd-pp-pagination-katal-control').shadowRoot.querySelector('[data-page="page_num"]')""".replace("page_num",str(self.current_page+1)))
            time.sleep(2)
            if elements:
                elements.click()
                time.sleep(5)
                clicked = self.execute_script("""return document.getElementById('ahd-pp-pagination-katal-control').shadowRoot.querySelector('[data-page="page_num"]')""".replace("page_num",str(self.current_page+1)))
                if clicked.get_attribute("aria-current"):
                    self.current_page += 1
                    self.wait_for_table() 
                    return True
                else:
                    self.console.log("next page button clicked but table was not updated. if you see this message multiple times. bring the browser to the front so it is loaded correctly",style="yellow")
                    try:
                        self.minimize_window()
                    except:
                        pass
                    try:
                        self.maximize_window()
                    except:
                        pass
                    time.sleep(10)
                    try:
                        self.minimize_window()
                    except:
                        pass
                    continue
            else:
                self.console.log("end of table",style="blue")
                return False



    def __exit__(self, *args) -> None:
        if self.destroy_browser:
            self.quit()
            time.sleep(5)


