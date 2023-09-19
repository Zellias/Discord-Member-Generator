import tls_client, base64, json
import requests, re, time, random
import websocket, os, threading
import ctypes
from json import dumps
from datetime import timedelta, datetime
from colorama import Fore
from libs.eazyui import Colors, Colorate, Center
from libs.solver import Solver

res = requests.get("https://discord.com/login").text
file_with_build_num = 'https://discord.com/assets/' + \
    re.compile(r'assets/+([a-z0-9]+)\.js').findall(res)[-2]+'.js'
req_file_build = requests.get(file_with_build_num).text
index_of_build_num = req_file_build.find('buildNumber')+24
buildNumb = int(req_file_build[index_of_build_num:index_of_build_num+6])

names = open('input/names.txt', "r", encoding="utf-8").read().splitlines()
proxies = open('input/proxies.txt', "r", encoding="utf-8").read().splitlines()
config = json.loads(open('config.json', 'r').read())
locked, unlocked, total = 0, 0, 0


def updateTitle():
    global total, locked, unlocked
    genStartedAs = time.time()
    while True:
        try:
            delta = timedelta(seconds=round(time.time()-genStartedAs))
            result = ""
            if delta.days > 0:
                result += f"{delta.days}d "
            if delta.seconds // 3600 > 0:
                result += f"{delta.seconds // 3600}h "
            if delta.seconds // 60 % 60 > 0:
                result += f"{delta.seconds // 60 % 60}m "
            if delta.seconds % 60 > 0 or result == "":
                result += f"{delta.seconds % 60}s"
            ctypes.windll.kernel32.SetConsoleTitleW(f'[Token Generator] - Unlocked: {unlocked} | Locked: {locked} | Unlock Rate: {round(unlocked/total*100,2)}% | Speed: {round(unlocked / ((time.time() - genStartedAs) / 60))}/min - {round(unlocked / ((time.time() - genStartedAs) / 60)*60)}/hour | Time Elapsed: {result}')
        except Exception:
            pass
        time.sleep(1)

class Output:
    def __init__(this, level):
        this.level = level
        this.color_map = {
            "INFO": (Fore.LIGHTBLUE_EX, "*"),
            "INFO2": (Fore.LIGHTCYAN_EX, "^"),
            "CAPTCHA": (Fore.LIGHTMAGENTA_EX, "C"),
            "ERROR": (Fore.LIGHTRED_EX, "!"),
            "SUCCESS": (Fore.LIGHTGREEN_EX, "$")
        }

    def log(this, *args, **kwargs):
        color, text = this.color_map.get(this.level, (Fore.LIGHTWHITE_EX, this.level))
        time_now = datetime.now().strftime("%H:%M:%S")[:-5]

        base = f"[{Fore.LIGHTBLACK_EX}{time_now}{Fore.RESET}] ({color}{text.upper()}{Fore.RESET})"
        for arg in args:
            base += f"{Fore.RESET} {arg}"
        if kwargs:
            base += f"{Fore.RESET} {arg}"
        print(base)

class Discord():
    def __init__(self) -> None:
        self.session = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )

        self.session.headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'fr-BE,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-track': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImZyLUJFIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjk5OTksImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9',
        }


        self.prop = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": 'fr-FR',
            "browser_user_agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            "browser_version": '112.0.0',
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": buildNumb,
            "client_event_source": None,
            "design_id": 0
        }
        self.super = base64.b64encode(json.dumps(self.prop, separators=(',', ':')).encode()).decode()

        self.sessId = str(random.randint(500,10000))
        self.proxy = "http://" + random.choice(proxies).replace('sessionid', self.sessId)
        self.session.proxies = {
            "http": self.proxy,
            "https": self.proxy
        }
    
    def getFingerprint(self) -> str:
        res = self.session.get(
            'https://discord.com/api/v9/experiments'
        )
        self.session.cookies = res.cookies
        return res.json()['fingerprint']
    
    def createAccount(self, captchaKey) -> str:

        payload2 = {
            "consent": True,
            "fingerprint": self.fingerprint,
            "global_name": random.choice(names),
            "gift_code_sku_id": None,
            "invite": config["invite"],
            "unique_username_registration":True
        }
        headers3 = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB',
            'Connection': 'keep-alive',
            'content-length': str(len(dumps(payload2))),
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com',
            'Referer': 'https://discord.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/609.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/609.1.15',
            'X-Fingerprint': self.fingerprint,
            'X-Captcha-Key':captchaKey,
            'X-Track': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTE1LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjIyMTIzNSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
        }
        self.session.headers.update(headers3)
        response = self.session.post(
            'https://discord.com/api/v9/auth/register',
            json=payload2
        ).json()
        if 'token' in response:
            return response['token']
        elif 'retry_after' in response:
            raise Exception(f'Rate Limited For {response["retry_after"]}s')
        else:
            raise Exception(str(response))
    
    def isLocked(self) -> bool:
        return "You need to verify your account in order to perform this action." in self.session.get(
            'https://discord.com/api/v9/users/@me/affinities/users',
        ).text
    
    def generate(self) -> None:
        global total, locked, unlocked
        self.fingerprint = self.getFingerprint()
        self.session.headers.update({
            "origin": "https://discord.com",
            "x-fingerprint": self.fingerprint
        })

        startedSolving = time.time()
        captchaKey = None
        while captchaKey == None:
            solver = Solver(
                proxy=self.proxy,
                siteKey="4c672d35-0701-42b2-88c3-78380b0db560",
                siteUrl="discord.com"
            )
            captchaKey = solver.solveCaptcha()
        #captchaKey = input('CapKey> ')
        Output("INFO").log(f'Solved {captchaKey[:30]} in {round(time.time()-startedSolving)}s')

        self.token = self.createAccount(captchaKey)

        self.session.headers.update({
            "authorization": self.token,
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://discord.com/channels/@me",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": 'fr',
            "x-super-properties": self.super
        })
        self.session.headers.pop("x-track")
        self.session.headers.pop("origin")

        if not self.isLocked():
            self.session.proxies = {
                "http": None,
                "https": None
            }
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=9')
            ws.send(json.dumps({"op": 2, "d": {"token": self.token, "capabilities": 4093, "properties": self.prop, "presence": {"status": "online", "since": 0, "activities": [], "afk": False}, "compress": False, "client_state": {"guild_versions": {}, "highest_last_message_id": "0", "read_state_version": 0, "user_guild_settings_version": -1, "user_settings_version": -1, "private_channels_version": "0", "api_code_version": 0}}}))
            ws.send(json.dumps({"op": 4, "d": {"guild_id": None, "channel_id": None, "self_mute": True, "self_deaf": False,"self_video": False}}))
            added = ""
            
            while True:
                try:
                    #Set birth data + avatar if enabled
                    json_data = {
                        'date_of_birth': '1991-11-12',
                    }
                    if config['avatar']:
                        json_data['avatar']  = 'data:image/png;base64,' + base64.b64encode(open(os.path.join("input/image", random.choice([f for f in os.listdir("input/image") if f.endswith('.jpg') or f.endswith('.png')])), 'rb').read()).decode('utf-8')
                        added += "Avatar, "
                    response = self.session.patch('https://discord.com/api/v9/users/@me', json=json_data)
                    if  response.status_code == 200:
                        added += "BirthDate, "
                    elif response.status_code != 400:
                        ws.close()
                        total += 1
                        locked += 1
                        Output("ERROR").log(f'Locked Av [{self.token[:30]}*************************]')
                        return
                    break
                except Exception:
                    pass

            #HypeSquad
            while True:
                try:
                    if config['hypesquad']:
                        response = self.session.post(
                            'https://discord.com/api/v9/hypesquad/online',
                            json={
                                'house_id': random.randint(1,3),
                            }
                        )
                        if response.status_code == 204:
                            added += "Hypesquad, "
                        elif response.status_code != 400:
                            ws.close()
                            locked += 1
                            total += 1
                            Output("ERROR").log(f'Locked Hp [{self.token[:30]}*************************]')
                            return
                    break
                except Exception:
                    pass

            #Bio
            if config['bio']:
                while True:
                    try:
                        bio = random.choice(open('input/bios.txt', 'r', encoding="utf-8").read().splitlines())

                        response = self.session.patch(
                            'https://discord.com/api/v9/users/%40me/profile',
                            json={
                                'bio': bio,
                            }
                        )
                        if response.status_code == 200:
                            added += "Bio, "
                        elif response.status_code != 400:
                            ws.close()
                            locked += 1
                            total += 1
                            Output("ERROR").log(f'Locked Bio [{self.token[:30]}*************************]')
                            return
                        break
                    except Exception:
                        pass
            total += 1
            unlocked += 1
            open('tokens.txt', 'a').write(f'{self.token}\n')
            Output("SUCCESS").log(f'Unlocked [{self.token[:30]}*************************]')
            ws.close()
            Output("INFO2").log(f'Humanized: {added}')
        else:
            total += 1
            locked += 1
            Output("ERROR").log(f'Locked [{self.token[:30]}*************************]')

def generate():
    global total, locked, unlocked
    while True:
        try:
            discord = Discord()
            discord.generate()
        except Exception as e:
            Output('ERROR').log(str(e))
            pass

if __name__ == "__main__":
    os.system("cls")
    os.system(f"title Token Generator")    


    for i in range(int(input(Center.XCenter('\nThreads <3 ')))):
        threading.Thread(target=generate).start()
    threading.Thread(target=updateTitle).start()