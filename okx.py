import os
import time
import requests
import random
from colorama import Fore, init
import sys
init(autoreset=True)

class OKX:
    def headers(self):
        return {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'App-Type': 'web',
            'Content-Type': 'application/json',
            'Origin': 'https://www.okx.com',
            'Referer': 'https://www.okx.com/mini-app/racer?tgWebAppStartParam=linkCode_85298986',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'X-Cdn': 'https://www.okx.com',
            'X-Locale': 'en_US',
            'X-Utc': '7',
            'X-Zkdex-Env': '0',
        }
    def post_to_okx_api(self, ext_user_id, ext_user_name, query_id):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/info?t={int(time.time() * 1000)}'
        headers = self.headers()
        headers = {**headers, 'X-Telegram-Init-Data': query_id}
        payload = {
            'extUserId': ext_user_id,
            'extUserName': ext_user_name,
            'gameId': 1,
            'linkCode': '85298986'
        }

        return requests.post(url, json=payload, headers=headers)

    def assess_prediction(self, ext_user_id, predict, query_id):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/assess?t={int(time.time() * 1000)}'
        headers = self.headers()
        headers = {**headers, 'X-Telegram-Init-Data': query_id}
        payload = {
            'extUserId': ext_user_id,
            'predict': predict,
            'gameId': 1
        }

        return requests.post(url, json=payload, headers=headers)

    def check_daily_rewards(self, ext_user_id, query_id):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/tasks?extUserId={ext_user_id}&t={int(time.time() * 1000)}'
        headers = self.headers()
        headers = {**headers, 'X-Telegram-Init-Data': query_id}

        try:
            response = requests.get(url, headers=headers)
            tasks = response.json().get('data', [])
            daily_check_in_task = next((task for task in tasks if task['id'] == 4), None)
            if daily_check_in_task:
                if daily_check_in_task['state'] == 0:
                    self.log('Bắt đầu checkin...')
                    self.perform_check_in(ext_user_id, daily_check_in_task['id'])
                else:
                    self.log('Hôm nay bạn đã điểm danh rồi!')
        except Exception as error:
            self.log(f'Lỗi kiểm tra phần thưởng hàng ngày: {error}')

    def perform_check_in(self, ext_user_id, task_id, query_id):
        url = f'https://www.okx.com/priapi/v1/affiliate/game/racer/task?t={int(time.time() * 1000)}'
        headers = self.headers()
        headers = {**headers, 'X-Telegram-Init-Data': query_id}
        payload = {
            'extUserId': ext_user_id,
            'id': task_id
        }

        try:
            requests.post(url, json=payload, headers=headers)
            self.log('Điểm danh hàng ngày thành công!')
        except Exception as error:
            self.log(f'Lỗi rồi: {error}')

    def log(self, msg):
        print(f'[*] {msg}')

    def sleep(self, ms):
        time.sleep(ms / 1000.0)

    def wait_with_countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f'===== Đã hoàn thành tất cả tài khoản, chờ {i} giây để tiếp tục vòng lặp =====', end='\r')
            self.sleep(1000)
        print('')

    def countdown(self, seconds):
        for i in range(seconds, -1, -1):
            print(f'[*] Chờ {i} giây để tiếp tục...', end='\r')
            self.sleep(1000)
        print('')

    def main(self):
        data_file = os.path.join(os.path.dirname(__file__), 'query/okx.txt')
        with open(data_file, 'r', encoding='utf-8') as f:
            user_data = [line.strip() for line in f if line.strip()]

        while True:
            for i, line in enumerate(user_data):
                ext_user_id, ext_user_name, query_id = line.split('|')
                try:
                    print(Fore.BLUE + f'========== Tài khoản {i + 1} | {ext_user_name} ==========')
                    self.check_daily_rewards(ext_user_id, query_id)
                    for j in range(20):
                        response = self.post_to_okx_api(ext_user_id, ext_user_name, query_id)
                        balance_points = response.json()['data']['balancePoints']
                        self.log(Fore.GREEN + f'Balance Points: {balance_points}')

                        predict = 0 if random.random() < 0.5 else 1
                        assess_response = self.assess_prediction(ext_user_id, predict, query_id)
                        assess_data = assess_response.json()['data']
                        result = Fore.GREEN + 'Win' if assess_data['won'] else Fore.RED + 'Thua'
                        calculated_value = assess_data['basePoint'] * assess_data['multiplier']
                        self.log(Fore.MAGENTA + f'Kết quả: {result} x {assess_data["multiplier"]}! Balance: {assess_data["balancePoints"]}, Nhận được: {calculated_value}, Giá cũ: {assess_data["prevPrice"]}, Giá hiện tại: {assess_data["currentPrice"]}')
                        if assess_data['numChance'] > 1:
                            self.countdown(5)
                            continue
                        elif assess_data['secondToRefresh'] > 0:
                            continue 
                            # self.countdown(assess_data['secondToRefresh'] + 5)
                        else:
                            sys.exit()
                except Exception as error:
                    self.log(Fore.RED + f'Lỗi rồi: {error}')
            sys.exit()

if __name__ == '__main__':
    okx = OKX()
    okx.main()
