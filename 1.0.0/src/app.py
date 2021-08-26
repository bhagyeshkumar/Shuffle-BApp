import socket
import asyncio
import time
import random
import json
import requests
import datetime as DT
import re

from walkoff_app_sdk.app_base import AppBase

class ModApp(AppBase):
    __version__ = "1.0.0"
    app_name = "BApp"  # this needs to match "name" in api.yaml
    
    def __init__(self, redis, logger, console_logger=None):
        """
        Each app should have this __init__ to set up Redis and logging.
        :param redis:
        :param logger:
        :param console_logger:
        """
        super().__init__(redis, logger, console_logger)

    async def Normal_Search(self, api_key, search_term, date):
        url = f"https://breachsense.io/api?lic={api_key}&s={search_term}&strict&json"
        if date:
            url = f"https://breachsense.io/api?lic={api_key}&s={search_term}&strict&json&date={date}"   
        try: 
            response = requests.get(url)
            return response.text
        except Exception as e:
            return "Exception occured: %s" % e
            
    #Cheking existing client matching or not
    async def Breach_Checker(self, api_key, Imp_domain, existClient, last_days):
        after_this_date = str(DT.date.today() - DT.timedelta(days=int(last_days)))
        date = after_this_date.replace("-", "")
        domain = str.lower(Imp_domain).strip()
        final_email_list = []

        if domain in existClient:
            url = f"https://breachsense.io/api?lic={api_key}&s={domain}&strict&json&date={date}"         
            try:
                response = requests.get(url)
                if '[]' in response.text:
                    return "There's no data available for this span of time"
                else:
                    values = json.loads(response.text)
                    for itr in values:
                        final_email_list.append(itr['eml'])

                    return final_email_list
            except Exception as e:
                return "Exception occured: %s" % e
        else:
            return "Domain doesn't belongs to you"

    # extracting emails from owa body.content
    async def Get_emails(self, Input_data, Regex):
        if "mailto:" in Input_data:
            rgx = r'(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?[ ]?(at|AT)[ ]?\)?[ ]?)(?<!\.)[\w]+[\w\-\.]*\.[a-zA-Z-]{2,3})(?:[^\w])'
            matches = re.findall(rgx, Input_data)
            get_first_group = lambda y: list(map(lambda x: x[0], y))
            email_list = get_first_group(matches)
            filter_email_list = []
            # removing first char containing \n
            try:
                for item in email_list:
                    filter_email_list.append(item[1::])  
                return filter_email_list
            except Exception as e:
                return "Exception occured: %s" % e            
        else:
            #emails = re.findall("(?<=mailto:).*?(?=:)", Input_data)
            email_list = re.findall("mailto\:(.*?)\:", Input_data)
            if Regex:
                email_list = re.findall(Regex, Input_data)
            try:
                return email_list
            except Exception as e:
                return "Exception occured: %s" % e

    async def Demo(self, url, Imp_domain, existClient):

        domain = str.lower(Imp_domain).strip()
        final_email_list = []

        if domain in existClient:        
            try:
                response = requests.get(url)
                if '[]' in response.text:
                    return "There's no data available for this span of time"
                else:
                    values = json.loads(response.text)
                    for itr in values:
                        final_email_list.append(itr['eml'])

                    return final_email_list
            except Exception as e:
                return "Exception occured: %s" % e
        else:
            return "Domain doesn't belongs to you"

if __name__ == "__main__":
    asyncio.run(ModApp.run(), debug=True)
