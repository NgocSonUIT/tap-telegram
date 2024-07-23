import json
import requests
import random
import time
import os
import sys

random_number = random.randint(50, 200)
post_data = json.dumps(random_number)
post_url = 'https://api.yescoin.gold/game/collectCoin'
get_url = 'https://api.yescoin.gold/account/getAccountInfo'
get_game_info_url = 'https://api.yescoin.gold/game/getGameInfo'
token_file_path = 'query/yescoin.txt'
current_index = 0

def get_game_info_and_log(headers):
    try:
        response = requests.get(get_game_info_url, headers=headers)

        if response.status_code == 200:
            data = response.json()['data']
            coin_pool_total_count = data['coinPoolTotalCount']
            coin_pool_left_count = data['coinPoolLeftCount']
            print(f"Năng Lượng: {coin_pool_left_count}/{coin_pool_total_count}")
            return coin_pool_left_count
        else:
            print(f"Nhận thông tin không thành công với mã trạng thái: {response.status_code}")
            return -1
    except Exception as e:
        print(f"Lỗi rồi: {e}")
        return -1

def claim_for_token(token):
    try:
        headers = {
            'Content-Type': 'application/json',
            # 'Accept': 'application/json',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            # 'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            # 'Origin': 'https://www.yescoin.gold',
            # 'Referer': 'https://www.yescoin.gold/',
            # 'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            # 'Sec-Ch-Ua-Mobile': '?0',
            # 'Sec-Ch-Ua-Platform': '"Windows"',
            # 'Sec-Fetch-Dest': 'empty',
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-site',
            'Token': token,
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

        coin_pool_left_count = get_game_info_and_log(headers)
        if coin_pool_left_count < 500:
            print(f"Energy nhỏ hơn 500 token {token[:35]}... Claim token tiếp theo")
            sys.exit()
            return True

        post_response = requests.post(post_url, data=post_data, headers=headers, timeout=20)
        if post_response.status_code == 200:
            get_response = requests.get(get_url, headers=headers)
            if get_response.status_code == 200:
                data = get_response.json()['data']
                total_amount = data['totalAmount']
                user_level = data['userLevel']
                rank = data['rank']
                print(f"Claim thành công cho token {token[:35]}...: Balance: {total_amount}, User Level: {user_level}, Rank: {rank}")
            else:
                print(f"Nhận Thông tin tài khoản không thành công với mã trạng thái {get_response.status_code}")
                sys.exit()
        else:
            print(f"Yêu cầu không thành công với mã trạng thái {post_response.status_code}")
            sys.exit()
        return False
    except Exception as e:
        print(f"Lỗi rồi: {e}")
        return False

def claim_and_reset_interval():
    global current_index
    try:
        with open(token_file_path, 'r') as file:
          authorization_list = file.read().splitlines()
          claim_for_token(authorization_list[current_index])
        # if current_index < len(authorization_list):
        #     should_switch_token = claim_for_token(authorization_list[current_index])
        #     if should_switch_token:
        #         current_index += 1
        # else:
        #     print('Đã hoàn tất claim tất cả token, nghỉ 10 phút rồi tiếp tục!')
        #     current_index = 0
        #     print('Yescoin Tasks completed.')
        #     sys.exit()
            # time.sleep(600)  # nghỉ 10 phút
    except Exception as e:
        print(f"Lỗi đọc tệp: {e}")

# while True:
#     claim_and_reset_interval()
#     time.sleep(1)
def main():
    while True:
        claim_and_reset_interval()

if __name__ == "__main__":
    main()