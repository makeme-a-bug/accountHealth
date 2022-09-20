from typing import Dict,List,Any,Union
import requests
import pandas as pd
from .scraper import Scraper
from rich.console import Console
from googlesheet.core import update_sheet

class Manager:
    
    def __init__(self,inputs:List[List], port:int = 35111):
        
        self.port = port
        self.console = Console()
        self.profiles = self.getProfiles()
        self.inputs = inputs
        self.link = "https://sellercentral.amazon.com/performance/account/health/product-policies"
        
    
    def getProfiles(self) -> Union[Dict,None]:
        """
        Get all profiles from multilogin
        """
        try:
            url = f'http://localhost:{self.port}/api/v2/profile'
            profiles = requests.get(url)
            profiles = profiles.json()
            profiles_map = {}
            for r in profiles:
                profiles_map[r['name']] = r['uuid']

            return profiles_map

        except requests.exceptions.Timeout:
            self.console.log(f"Request to get profiles timeout",style="red")
            return

        except requests.exceptions.ConnectionError as e:
            self.console.log(f"Please make sure multilogin API is running. Failed to make request to the API.",style="red")
            raise SystemExit()

        except requests.exceptions as e:
            self.console.log("Request failed due to",style="red")
            print(e)
            return
   
    
    def start_profile_browser(self, profile_id:str) -> Union[str, None]:
        """
            Starts browser profile for given profile_id        
        """
        try:
            mla_url = (
                f"http://127.0.0.1:{self.port}/api/v1/profile/start?automation=true&profileId=" + profile_id
            )
            resp = requests.get(mla_url)
            json:Dict = resp.json()
            if resp.status_code == 500:
                self.console.log(f"profile with id:{profile_id} not found",style="red")
                return
            

        except requests.exceptions.Timeout as e:
            self.console.log(f"Request to get profile:{profile_id} timeout",style="red")
            return

        except requests.exceptions.ConnectionError as e:
            self.console.log(f"Please make sure multilogin API is running. Failed to make request to the API.",style="red")
            raise SystemExit()

        except requests.exceptions as e:
            self.console.log("Request failed due to",style="red")
            print(e)
            return
        except Exception as e:
            print(e)
            return
        
        return json.get('value',None)

    def gather_data(self):
        for sheet_name , profile_name in self.inputs:
            self.console.log(f"Working on {profile_name}",style="blue")
            profile_uuid:str = self.profiles.get(profile_name,None)
            if not profile_uuid:
                self.console.log(f"profile not found:{profile_name}",style="red")
                continue

            mla_url = self.start_profile_browser(profile_uuid)
            data = []
            if mla_url:
                with Scraper(profile_name , profile_uuid , self.link , mla_url,destroy_browser=True) as scraper:
                    data.extend(scraper.get_data())
                data = pd.DataFrame(data)
                update_sheet(sheet_name,data)
            self.console.log(f"{profile_name} done",style="blue")
            
                
                
                






                

    
                