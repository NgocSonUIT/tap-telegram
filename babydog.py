import requests
import json
import time
import os
import sys
import asyncio
import urllib.parse
import random

class Babydoge:
    def __init__(self):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://babydogepawsbot.com',
            'Referer': 'https://babydogepawsbot.com/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
        self.line = '~' * 50
    
    def http(self, url, headers=None, data=None):
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            try:
                if data is None:
                    res = requests.get(url, headers=headers)
                else:
                    res = requests.post(url, data=data, headers=headers)
                
                # print(res.json())

                # if not isinstance(res.json(), dict):
                #     self.log('Không nhận được phản hồi JSON hợp lệ !')
                #     attempts += 1
                #     time.sleep(2)
                #     continue
                
                return res
            
            except requests.exceptions.RequestException as error:
                attempts += 1
                self.log(f'Lỗi kết nối (Lần thử {attempts}/{max_attempts}): {error}')
                if attempts < max_attempts:
                    time.sleep(5)
                else:
                    break
        
        raise Exception('Không thể kết nối sau 3 lần thử')

    def log(self, msg):
        print(f'[*] {msg}')

    async def dangnhap(self, tgData):
        url = 'https://backend.babydogepawsbot.com/authorize'
        headers = self.headers.copy()

        try:
            res = self.http(url, headers, tgData)
            if res.json():
                self.log('Đăng nhập thành công!')
                data = res.json()
                balance = data.get('balance', '')
                energy = data.get('energy', '')
                max_energy = data.get('max_energy', '')
                access_token = data.get('access_token', '')
                self.log(f'Balance: {balance}')
                self.log(f'Năng lượng: {energy}/{max_energy}')
                return access_token, balance, int(energy)
            else:
                self.log('Đăng nhập thất bại!')
                return None, None
        except Exception as error:
            self.log(f'Lỗi rồi: {error}')
            sys.exit()
            return None, None

    async def daily(self, access_token):
        check_url = 'https://backend.babydogepawsbot.com/getDailyBonuses'
        claim_url = 'https://backend.babydogepawsbot.com/pickDailyBonus'
        headers = {**self.headers, 'X-Api-Key': access_token}

        try:
            check_res = self.http(check_url, headers)
            if check_res.json() and check_res.json().get('has_available'):
                self.log('Điểm danh hàng ngày có sẵn!')
                claim_res = self.http(claim_url, headers, '')
                if claim_res.json():
                    self.log('Điểm danh hàng ngày thành công!')
                else:
                    self.log('Điểm danh hàng ngày thất bại!')
            else:
                self.log('Hôm nay đã điểm danh hàng ngày.')
        except Exception as error:
            self.log(f'Lỗi khi kiểm tra hoặc claim daily bonus: {error}')

    async def get_task(self, access_token):
        url = 'https://backend.babydogepawsbot.com/channels'
        headers = {**self.headers, 'X-Api-Key': access_token}

        try:
            res = self.http(url, headers)
            if res.json() and res.json().get('channels'):
                available_channels = [channel for channel in res.json().get('channels') if channel.get('is_available') and channel.get('type') != 'telegram']
                return available_channels
            else:
                self.log('Không có nhiệm vụ nào có sẵn.')
                return []
        except Exception as error:
            self.log(f'Lỗi rồi: {error}')
            return []

    async def claim_task(self, access_token, channel):
        url = 'https://backend.babydogepawsbot.com/channels'
        headers = {
            **self.headers,
            'X-Api-Key': access_token,
            'Content-Type': 'application/json'
        }
        data = json.dumps({'channel_id': channel.get('id')})

        try:
            res = self.http(url, headers, data)
            if res.json():
                self.log(f'Đang làm nhiệm vụ: {channel.get("title")}... Trạng thái: thành công')
            else:
                self.log(f'Lỗi khi nhận phần thưởng cho nhiệm vụ: {channel.get("title")}')
        except Exception as error:
            self.log(f'Lỗi khi nhận phần thưởng: {error}')

    async def tapdc(self, access_token, initial_energy):
        url = 'https://backend.babydogepawsbot.com/mine'
        headers = {
            **self.headers,
            'X-Api-Key': access_token,
            'Content-Type': 'application/json'
        }
        energy = int(initial_energy)
        try:
            while energy >= 50:
                random_energy = random.randint(10, 50)
                count = (energy - random_energy) // 2

                if count % 2 != 0:
                    count = (count // 2) * 2

                if count <= 0:
                    self.log('Năng lượng không đủ để tiếp tục tap...chuyển tài khoản!')
                    sys.exit()
                    break
                data = json.dumps({'count': random_energy})

                res = self.http(url, headers, data)
                if res.json():
                    print(res.json())
                    balance = res.json().get('balance', '')
                    mined = res.json().get('mined', '')
                    new_energy = res.json().get('newEnergy', '')
                    self.log(f'Đã tap {str(mined)} lần. Balance: {str(balance)} Năng lượng: {str(new_energy)}')

                    energy = int(new_energy)

                    if energy < 50:
                        self.log('Năng lượng quá thấp để tiếp tục tap...chuyển tài khoản!')
                        sys.exit()
                        break
                else:
                    self.log('Lỗi rồi, không thể tap!')
                    sys.exit()
                    break
        except Exception as error:
            sys.exit()
            self.log(f'Lỗi rồi: {error}')

    async def buy_cards(self, access_token, balance):
        list_cards_url = 'https://backend.babydogepawsbot.com/cards/new'
        upgrade_url = 'https://backend.babydogepawsbot.com/cards'
        get_me_url = 'https://backend.babydogepawsbot.com/getMe'
        headers = {
            **self.headers,
            'X-Api-Key': access_token,
            'Content-Type': 'application/json'
        }

        try:
            get_me_res = self.http(get_me_url, headers)
            balance = int(get_me_res.json().get('balance', ''))

            res = self.http(list_cards_url, headers)

            if res.json() and len(res.json()) > 0:
                cards = res.json()
                for card in cards:
                    if balance < int(card.get('upgrade_cost')):
                        self.log('Số dư không đủ để mua thẻ !')
                        return

                    if card.get('cur_level') == 0:
                        upgrade_data = json.dumps({'id': card.get('id')})
                        upgrade_res = self.http(upgrade_url, headers, upgrade_data)
                        if upgrade_res.json():
                            balance = upgrade_res.json().get('balance', '')
                            self.log(f'Đang mua thẻ {card.get("name")}...Trạng thái: {"Thành công"} Balance mới: {str(balance)}')
                        else:
                            self.log(f'Đang mua thẻ {card.get("name")}...Trạng thái: {"Thất bại"}')
            else:
                self.log('Không có thẻ mới nào.')
        except Exception as error:
            self.log(f'Lỗi rồi: {error}')

    async def upgrade_my_cards(self, access_token, balance):
        list_my_cards_url = 'https://backend.babydogepawsbot.com/cards/new'
        upgrade_url = 'https://backend.babydogepawsbot.com/cards'
        get_me_url = 'https://backend.babydogepawsbot.com/getMe'
        headers = {
            **self.headers,
            'X-Api-Key': access_token,
            'Content-Type': 'application/json'
        }

        try:
            get_me_res = self.http(get_me_url, headers)
            balance = get_me_res.json().get('balance', '')
            res = self.http(list_my_cards_url, headers)

            if res.json() and len(res.json()) > 0:
                cards = res.json()
                for card in cards:
                    if balance < int(card.get('upgrade_cost')):
                        self.log('Số dư không đủ để nâng cấp thẻ !')
                        return

                    upgrade_data = json.dumps({'id': card.get('id')})
                    upgrade_res = self.http(upgrade_url, headers, upgrade_data)
                    if upgrade_res.json():
                        balance = upgrade_res.json().get('balance', '')
                        self.log(f'Đang nâng cấp thẻ {card.get("name")}...Trạng thái: {"Thành công"} Balance mới: {str(balance)}')
                    else:
                        self.log(f'Đang nâng cấp thẻ {card.get("name")}...Trạng thái: {"Thất bại"}')
            else:
                self.log('Không có thẻ nào để nâng cấp.')
        except Exception as error:
            self.log(f'Lỗi rồi: {error}')

    async def main(self):
        data_file = os.path.join(os.path.dirname(__file__), 'query/babydoge.txt')

        with open(data_file, 'r', encoding='utf-8') as f:
            data = f.read().replace('\r', '').split('\n')
            data = list(filter(None, data))

        if not data:
            print('No accounts added!')
            return

        buy_cards_decision = True  # Set your decision logic here
        upgrade_my_cards_decision = True  # Set your decision logic here

        while True:
            for index, tgData in enumerate(data, start=1):
                userData = json.loads(
                    urllib.parse.unquote(tgData.split('&')[1].split('=')[1])
                )
                firstName = userData['first_name']
                print(f'========== Tài khoản {index}/{len(data)} | {firstName} ==========')

                result = await self.dangnhap(tgData)

                if result:
                    access_token, balance, energy = result
                    await self.daily(access_token)

                    available_channels = await self.get_task(access_token)
                    for channel in available_channels:
                        await self.claim_task(access_token, channel)

                    if buy_cards_decision:
                        await self.buy_cards(access_token, balance)

                    if upgrade_my_cards_decision:
                        await self.upgrade_my_cards(access_token, balance)

                    await self.tapdc(access_token, energy)

                await asyncio.sleep(5)

            # Uncomment the line below to add a delay between iterations
            # await asyncio.sleep(60)

if __name__ == "__main__":
  babydoge = Babydoge()
  asyncio.run(babydoge.main())
