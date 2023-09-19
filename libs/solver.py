import requests, json
import time
import httpx
keyCap = json.load(open('./config.json', 'r'))['capmonster-key']

def payload(service:str="capmonster.cloud", proxy:str=None, user_agent:str=None) -> None:
    p = {
        "clientKey":keyCap,
        "task": {
            "websiteURL":"https://discord.com/",
            "websiteKey":"4c672d35-0701-42b2-88c3-78380b0db560",
        }
    }
    if service == "capsolver.com": 
        p['appId']="E68E89B1-C5EB-49FE-A57B-FBE32E34A2B4"
        p['task']['type'] = "HCaptchaTurboTask"
        p['task']['proxy'] = proxy 
        p['task']['userAgent'] = user_agent
    if service == "capmonster.cloud": 
        p['task']['type'] = "HCaptchaTask"
        p['task']['proxyType'] = "http"
        p['task']['proxyAddress'] = proxy.split("@")[1].split(":")[0]
        p['task']['proxyPort'] = proxy.split("@")[1].split(":")[1]
        p['task']['proxyLogin'] = proxy.split("@")[0].split(":")[0]
        p['task']['proxyPassword'] = proxy.split("@")[0].split(":")[1]
    return p

class Solver():
    def __init__(self, proxy:str, siteKey:str, siteUrl:str) -> None:
        self.debug = False

        #Requests
        self.proxy = proxy

        self.siteKey = siteKey
        self.siteUrl = siteUrl

        self.log(f'Solving Captcha, SiteKey: {self.siteKey} | SiteUrl: {self.siteUrl}')

    def log(self, txt:str) -> None:
        if self.debug: print(txt)

    def solveCaptcha(self) -> str:
        capmonster_key = keyCap
        
        site_key='4c672d35-0701-42b2-88c3-78380b0db560'
        page_url='https://discord.com/'
        url = "https://api.capmonster.cloud/createTask"
        data = {
            "clientKey": capmonster_key,
            "task":
            {
                "type": "HCaptchaTaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        response = httpx.post(url,json=data)
        if response.json()['errorId'] == 0:
            task_id = response.json()['taskId']
            url = "https://api.capmonster.cloud/getTaskResult"
            data = {
                "clientKey": capmonster_key,
                "taskId": task_id
            }
            response = httpx.post(url,json=data)
            while response.json()['status'] == 'processing':
                time.sleep(3)
                response = httpx.post(url,json=data)
            return response.json()['solution']['gRecaptchaResponse']
        else:
            print('Error: {}'.format(response.json()['errorDescription']))
            return False
