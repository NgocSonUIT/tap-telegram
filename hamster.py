import requests
import json
import time
import asyncio


with open('query/hamster.txt', 'r') as file:
    authorization_list = file.read().splitlines()
print('Authorization:', authorization_list)


def click_with_api(authorization):
    try:
        payload = {
            'count': 1,
            'availableTaps': 1500,
            'timestamp': int(time.time() * 1000)
        }
        headers = {
            'Authorization': f'Bearer {authorization}',
            'Content-Type': 'application/json'
        }
        response = requests.post('https://api.hamsterkombat.io/clicker/tap', data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            data = response.json()
            clicker_user = data['clickerUser']
            required_fields = {
                'Balance': clicker_user['balanceCoins'],
                'Level': clicker_user['level'],
                'availableTaps': clicker_user['availableTaps'],
                'maxTaps': clicker_user['maxTaps']
            }
            print('Đang tap:', required_fields)
            return required_fields
        else:
            print(f'Không bấm được. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')
    return None

def run_for_authorization(authorization):
    while True:
        click_data = click_with_api(authorization)
        if click_data and click_data['availableTaps'] < 10:
            print(f'Token {authorization} có năng lượng nhỏ hơn 10. Chuyển token tiếp theo...')
            return

def main():
    while True:
        for authorization in authorization_list:
            run_for_authorization(authorization)
        print('Hamster Tasks completed.')
        return

if __name__ == "__main__":
    main()