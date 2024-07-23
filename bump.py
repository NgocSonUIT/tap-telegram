import requests
import time
import json
from pathlib import Path
from itertools import cycle
import random
import sys

# Read the Telegram IDs and proxies
with open('query/bump.txt', 'r') as file:
    telegram_ids = file.read().strip().split('\n')

auth_url = 'https://api.mmbump.pro/v1/loginJwt'
auth_headers = {
    'Accept': 'application/json',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    # 'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'Content-Type': 'application/json',
    # 'Origin': 'https://mmbump.pro',
    # 'Referer': 'https://mmbump.pro/',
    # 'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    # 'Sec-Ch-Ua-Mobile': '?1',
    # 'Sec-Ch-Ua-Platform': '"Android"',
    # 'Sec-Fetch-Dest': 'empty',
    # 'Sec-Fetch-Mode': 'cors',
    # 'Sec-Fetch-Site': 'same-site',
    # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}
error_time = 0
error_farming = 0

def finish_farming_if_needed(farming_data, farming_headers):
    current_time = int(time.time())
    global error_farming
    if error_farming > 5:
        print('Lỗi 5 lần farming, exit bump')
        sys.exit()

    if farming_data['session']['status'] == 'inProgress' and current_time > farming_data['session']['moon_time']:
        try:
            rd_tap_count = random.randint(50000, 150000)
            finish_url = 'https://api.mmbump.pro/v1/farming/finish'
            finish_payload = {'tapCount': rd_tap_count}

            response = requests.post(finish_url, headers=farming_headers, data=json.dumps(finish_payload))

            print(response)

            if response.status_code == 200:
                print('Đã hoàn thành farming')
                start_url = 'https://api.mmbump.pro/v1/farming/start'
                start_payload = {'status': 'inProgress'}
                start_response = requests.post(start_url, headers=farming_headers, data=json.dumps(start_payload))
                if start_response.status_code == 200:
                    print('Bắt đầu farming...')
                else:
                    print('Lỗi khi bắt đầu farming:', start_response.json())
            else:
                print('Lỗi khi hoàn thành farming:', response.json())
                error_farming += 1
        except Exception as error:
            print('Lỗi khi hoàn thành farming:', str(error))
            error_farming += 1
            if response := error.response:
                print('Response data:', json.dumps(response.json(), indent=2))
    else:
        print('Đang trong trạng thái farming')

def xuly(telegram_id):
    auth_payload = {'initData': telegram_id}
    global error_time
    if error_time > 5:
        print('Lỗi 5 lần, exit bump')
        sys.exit()

    try:
        auth_response = requests.post(auth_url, headers=auth_headers, data=json.dumps(auth_payload))
        if auth_response.status_code == 200:
            access_token = auth_response.json()['access_token']
            farming_url = 'https://api.mmbump.pro/v1/farming'
            farming_headers = {**auth_headers, 'Authorization': f'Bearer {access_token}'}
            farming_data = None
            attempts = 0
            max_attempts = 5
            while attempts < max_attempts:
                farming_response = requests.post(farming_url, headers=farming_headers)

                if farming_response.status_code == 200:
                    farming_data = farming_response.json()
                    if 'telegram_id' in farming_data and 'balance' in farming_data:
                        break
                attempts += 1
                print(f'Thử lại lần {attempts} để lấy dữ liệu farming...')
            if farming_data and 'telegram_id' in farming_data and 'balance' in farming_data:
                print('ID:', farming_data['telegram_id'])
                print('Balance:', farming_data['balance'])
                current_time = int(time.time())
                try:
                    if farming_data['day_grant_first'] is None or (current_time - farming_data['day_grant_first']) >= 86400:
                        grant_day_claim_url = 'https://api.mmbump.pro/v1/grant-day/claim'
                        requests.post(grant_day_claim_url, headers=farming_headers)
                        print('Điểm danh hàng ngày')
                    else:
                        print('Đã điểm danh hàng ngày')
                except requests.HTTPError as grant_error:
                    if grant_error.response.status_code == 400:
                        print('Đã điểm danh hàng ngày')
                    else:
                        raise grant_error
                if farming_data['session']['status'] == 'await':
                    farming_start_url = 'https://api.mmbump.pro/v1/farming/start'
                    farming_start_payload = {'status': 'inProgress'}
                    requests.post(farming_start_url, headers=farming_headers, data=json.dumps(farming_start_payload))
                    print('Bắt đầu farming...')
                elif farming_data['session']['status'] == 'inProgress' and farming_data['session']['moon_time'] > current_time:
                    print('Đang trong trạng thái farming')
                    sys.exit()
                else:
                    finish_farming_if_needed(farming_data, farming_headers)
            else:
                print('Không thể lấy dữ liệu farming hợp lệ sau nhiều lần thử')
                sys.exit()
        else:
            raise Exception('Không thể xác thực')
    except Exception as error:
        print('Lỗi rồi:', str(error))
        error_time += 1

def main():
    while True:
        for telegram_id in telegram_ids:
            xuly(telegram_id)

if __name__ == "__main__":
    main()
