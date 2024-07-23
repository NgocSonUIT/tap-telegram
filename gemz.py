import os
import json
import base64
import random
import time
import asyncio
import aiohttp
from urllib.parse import parse_qs, unquote
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from pathlib import Path
import re

def tao_sid():
    return base64.b64encode(os.urandom(6)).decode('utf-8')[:9]

def check_energy(energy):
    return energy > 30

async def xuly(query_id, session):

    queryParams = parse_qs(query_id)

    # Decode and parse the user parameter
    user = json.loads(unquote(queryParams.get('user')[0]))

    first_name = user.get('first_name')
    last_name = user.get('last_name')

    # Extract user ID using regular expression
    user_id_match = re.search(r'"id":(\d+)', queryParams.get('user')[0])
    user_id = user_id_match.group(1) if user_id_match else None

    if not user_id:
        print(f"Không tìm thấy user id: {query_id}")
        return

    payload1 = {
        "sid": tao_sid(),
        "id": str(user_id),
        "auth": query_id.replace('&', '\n')
        # "auth": 'auth_date=1721271658\nhash=230dc4ea24a1d295868e440f1f530374f3f6316d94ef058ebf0bd56a1be7ea4d\nquery_id=AAGyt2pDAAAAALK3akOO1kIr\nuser=%7B%22id%22%3A1131067314%2C%22first_name%22%3A%22S%C6%A1n%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22lufgfy%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D'
    }
    print(payload1)
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Content-Type': 'application/json',
        # 'Origin': 'https://ff.notgemz.gemz.fun',
        # 'Referer': 'https://ff.notgemz.gemz.fun/',
        # 'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        # 'Sec-Ch-Ua-Mobile': '?1',
        # 'Sec-Ch-Ua-Platform': '"Android"',
        # 'Sec-Fetch-Dest': 'empty',
        # 'Sec-Fetch-Mode': 'cors',
        # 'Sec-Fetch-Site': 'cross-site',
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    }

    url1 = 'https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.44.0/loginOrCreate'

    try:
        async with session.post(url1, data=json.dumps(payload1), headers=headers) as response1:
            response1_data = await response1.json()
            data = response1_data['data']

            if not data or not data.get('state') or not data.get('token'):
                print(f"Dữ liệu phản hồi không hợp lệ: {response1_data}")
                return

            print(f"Username: {data['state']['username']}, Balance: {data['state']['balance']}, Energy: {data['state']['energy']}")

            rev = data['rev']
            current_energy = 6000

            while check_energy(current_energy):
                print(f"Năng lượng hiện tại {current_energy}")
                queue_length = random.randint(50, 200)
                queue = [{"fn": "tap", "async": False, "meta": {"now": int(time.time() * 1000)}} for _ in range(queue_length)]
                payload2 = {
                    "abTestsDynamicConfig": {
                        "0002_invite_drawer": {"active": True, "rollOut": 1},
                        "0003_invite_url": {"active": True, "rollOut": 1},
                        "0004_invite_copy": {"active": True, "rollOut": 1},
                        "0010_localization": {"active": True, "rollOut": 1},
                        "0006_daily_reward": {"active": False, "rollOut": 0},
                        "0011_earn_page_buttons": {"active": True, "rollOut": 1},
                        "0005_invite_message": {"active": True, "rollOut": 1},
                        "0008_retention_with_points": {"active": True, "rollOut": 1},
                        "0018_earn_page_button_2_friends": {"active": True, "rollOut": 1},
                        "0012_rewards_summary": {"active": True, "rollOut": 1},
                        "0022_localization": {"active": True, "rollOut": 1},
                        "0025_earn_page_button_connect_wallet": {"active": True, "rollOut": 1},
                        "0016_throttling": {"active": True, "rollOut": 1},
                        "0024_rewards_summary2": {"active": True, "rollOut": 1},
                        "0016_throttling_v2": {"active": True, "rollOut": 1},
                        "0014_gift_airdrop": {"active": True, "rollOut": 1}
                    },
                    "queue": queue,
                    "rev": rev,
                    "requestedProfileIds": [],
                    "consistentFetchIds": [],
                    "sid": tao_sid(),
                    "clientRandomSeed": 0,
                    "crqid": tao_sid(),
                    "id": str(user_id),
                    "auth": data['token']
                }

                url2 = 'https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.44.0/replicate'

                try:
                    async with session.post(url2, data=json.dumps(payload2), headers=headers) as response2:
                        response_data = await response2.json()
                        response2_data = response_data['data']

                        if not response_data or not response_data.get('state'):
                            print(f"Đang tap...rev {response2_data['rev']}")
                        rev = response2_data['rev']
                        current_energy -= queue_length

                except ClientError as error:
                    print(f"Lỗi rồi: {str(error)}")
                    break

            if data['state']['unclaimed_rewards'] == 0:
                payload3 = {
                    "abTestsDynamicConfig": {
                        "0002_invite_drawer": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0003_invite_url": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0004_invite_copy": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0010_localization": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0006_daily_reward": {
                            "active": False,
                            "rollOut": 0
                        },
                        "0011_earn_page_buttons": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0005_invite_message": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0008_retention_with_points": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0018_earn_page_button_2_friends": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0012_rewards_summary": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0022_localization": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0023_earn_page_button_connect_wallet": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0016_throttling": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0024_rewards_summary2": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0016_throttling_v2": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0014_gift_airdrop": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0007_game_preview": {
                            "active": False,
                            "rollOut": 0
                        },
                        "0015_dao_card": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0028_mining_page_route": {
                            "active": False,
                            "rollOut": 0
                        },
                        "0029_mining_special_initial_tab": {
                            "active": False,
                            "rollOut": 0
                        },
                        "0031_free_gift_modal": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0025_invite_btn_locked_cards": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0035_elim_reengage_msgs": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0020_mining_page_badge": {
                            "active": False,
                            "rollOut": 0
                        },
                        "0030_earn_page2": {
                            "active": True,
                            "rollOut": 1
                        },
                        "0032_early_invite_prompt": {
                            "active": True,
                            "rollOut": 1
                        }
                    },
                    "queue": [
                        {
                            "fn": "_heartbeat",
                            "async": False,
                            "args": []
                        }
                    ],
                    "rev": data['rev'],
                    "requestedProfileIds": [],
                    "consistentFetchIds": [],
                    "sid": tao_sid(),
                    "clientRandomSeed": 0,
                    "crqid": tao_sid(),
                    "id": str(user_id),
                    "auth": data['token']
                }

                url3 = 'https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.44.0/replicate'

                try:
                    async with session.post(url3, data=json.dumps(payload3), headers=headers) as response3:
                        print(response3)
                        response3_data = await response3.json()
                        print("Đã gọi API claimDailyReward")
                except ClientError as error:
                    print(f"Lỗi khi gọi API claimDailyReward: {str(error)}")

    except ClientError as error:
        print(f"Lỗi: {str(error)}")

async def run_tasks():
    with open('query/gemz.txt', 'r', encoding='utf-8') as file:
        xuly_query = file.read()
    query_ids = [line.strip() for line in xuly_query.split('\n') if line.strip()]

    async with ClientSession() as session:
        tasks = []
        for query_id in query_ids:
            tasks.append(xuly(query_id, session))
        await asyncio.gather(*tasks)

async def main():
    while True:
        await run_tasks()
        print('Gemz Tasks completed.')
        return
        # await asyncio.sleep(15 * 60)  # Wait for 15 minutes (15 * 60 seconds)

if __name__ == "__main__":
    asyncio.run(main())


