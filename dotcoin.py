import requests
import time
import sys

class Dotcoin:
    def __init__(self):
        self.apikey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impqdm5tb3luY21jZXdudXlreWlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg3MDE5ODIsImV4cCI6MjAyNDI3Nzk4Mn0.oZh_ECA6fA2NlwoUamf1TqF45lrMC0uIdJXvVitDbZ8'

    def get_headers(self, authorization):
        return {
            'Accept': 'application/json',
            'apikey': self.apikey,
            'authorization': f'Bearer {authorization}',
            'Content-Type': 'application/json',
        }

    def http(self, url, headers, data=None):
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            try:
                if data is None:
                    res = requests.get(url, headers=headers)
                else:
                    res = requests.post(url, headers=headers, json=data)
                
                res.raise_for_status()

                if 'application/json' not in res.headers.get('Content-Type', ''):
                    print("Không nhận được phản hồi JSON hợp lệ !")
                    attempts += 1
                    time.sleep(2)
                    continue

                return res.json()

            except requests.RequestException as error:
                attempts += 1
                print(f"Lỗi kết nối (Lần thử {attempts}/{max_attempts}): {error}")
                if attempts < max_attempts:
                    time.sleep(5)
                else:
                    break

        raise Exception('Không thể kết nối sau 3 lần thử')

    def load_credentials(self):
        try:
            with open('query/dotcoin.txt', 'r', encoding='utf-8') as file:
                credentials_list = file.read().split('\n')
            return [cred.strip() for cred in credentials_list]
        except FileNotFoundError:
            print("Không tìm thấy file 'dotcoin.txt'. Đảm bảo file nằm trong cùng thư mục với nhau.")
            return []

    def fetch_task_ids(self, authorization):
        url = 'https://api.dotcoin.bot/rest/v1/rpc/get_filtered_tasks'
        headers = self.get_headers(authorization)
        data = {'platform': 'ios', 'locale': 'en', 'is_premium': False}

        try:
            response = self.http(url, headers, data)
            tasks = response
            return [task['id'] for task in tasks]
        except Exception as error:
            print(f"Lỗi rồi: {error}")
            return []

    def add_attempts(self, lvl, authorization, current_level):
        url = 'https://api.dotcoin.bot/rest/v1/rpc/add_attempts'
        headers = self.get_headers(authorization)

        while True:
            print(f"[ Upgrade ] : Nâng lên cấp độ {lvl}", end='\r')
            try:
                data = {'lvl': lvl}
                response = self.http(url, headers, data)
                if lvl > current_level:
                    return False
                if response['success']:
                    return True
                else:
                    lvl += 1
            except Exception as error:
                print(f"Lỗi khi nâng cấp: {error}")

    def auto_clear_task(self, authorization):
        task_ids = self.fetch_task_ids(authorization)
        url = 'https://api.dotcoin.bot/rest/v1/rpc/complete_task'
        headers = self.get_headers(authorization)
        for task_id in task_ids:
            data = {'oid': str(task_id)}
            try:
                response = self.http(url, headers, data)
                if response['success'] == True:
                    print(f"[ Task {task_id} ] : Hoàn thành")
                else:
                    print(f"[ Task {task_id} ] : Không thành công với mã trạng thái {response['success']}")
            except Exception as error:
                print(f"Lỗi hoàn thành nhiệm vụ {task_id}: {error}")

    def save_coins(self, coins, authorization):
        url = 'https://api.dotcoin.bot/rest/v1/rpc/save_coins'
        headers = self.get_headers(authorization)
        data = {'coins': coins}

        try:
            response = self.http(url, headers, data)
            return response
        except Exception as error:
            print(f"Lỗi khi nhận coin: {error}")
            return False

    def get_user_info(self, authorization):
        url = 'https://api.dotcoin.bot/rest/v1/rpc/get_user_info'
        headers = self.get_headers(authorization)

        try:
            response = self.http(url, headers, {})
            return response
        except Exception as error:
            print(f"Không lấy được thông tin người dùng: {error}")
            print("Thử gọi lại API để lấy thông tin người dùng...")
            try:
                response = self.http(url, headers, {})
                return response
            except Exception as retry_error:
                print(f"Lỗi khi gọi lại API: {retry_error}")
                return None

    def auto_upgrade_daily_attempt(self):
        user_input = 'y'
        if user_input == 'y':
            try:
                n_upgrade = 0
                return 0 if n_upgrade is None else n_upgrade
            except ValueError:
                print("Dữ liệu nhập không hợp lệ, phải là số.")
                return 0
        return 0

    def auto_game(self, authorization, coins):
        url = 'https://api.dotcoin.bot/rest/v1/rpc/try_your_luck'
        headers = self.get_headers(authorization)
        data = {'coins': coins}

        try:
            response = self.http(url, headers, data)
            if response['success'] == True:
                print("[ Game ] : Thắng")
            else:
                print("[ Game ] : Thua")
        except Exception as error:
            print(f"Lỗi rồi: {error}")

    def upgrade_dtc_miner(self, authorization):
        user_info = self.get_user_info(authorization)
        url = 'https://api.dotcoin.bot/functions/v1/upgradeDTCMiner'
        headers = self.get_headers(authorization)
        headers['X-Telegram-User-Id'] = str(user_info['id'])

        try:
            response = self.http(url, headers, {})
            if response['success'] == True:
                print("[ DTC Miner ] : Nâng cấp DTC Miner thành công!")
            else:
                print("[ DTC Miner ] : Hôm nay bạn đã nâng cấp rồi!")
        except Exception as error:
            print(f"[ DTC Miner ] : Lỗi khi nâng cấp: {error}")

    def main(self):
        clear_task = 'y'
        credentials = self.load_credentials()
        n_upgrade = self.auto_upgrade_daily_attempt()
        upgrade_success = {}

        while True:
            for index, authorization in enumerate(credentials):
                info = self.get_user_info(authorization)
                print(f"============== [ Tài khoản {index} | {info['first_name']} ]")

                if not upgrade_success.get(authorization) and n_upgrade > 0:
                    for _ in range(n_upgrade):
                        current_level = info['daily_attempts']
                        success = self.add_attempts(0, authorization, current_level)
                        if success:
                            upgrade_success[authorization] = True
                            print("[ Upgrade ] : Thành công\r")
                            break
                        else:
                            print("[ Upgrade ] : Thất bại\r")

                if info:
                    if clear_task == 'y':
                        self.auto_clear_task(authorization)
                    print(f"[ Level ] : {info['level']}")
                    print(f"[ Balance ] : {info['balance']}")
                    print(f"[ Energy ] : {info['daily_attempts']}")
                    print(f"[ Limit Energy ] : {info['limit_attempts']}")
                    print(f"[ Multitap Level ] : {info['multiple_clicks']}")
                    self.upgrade_dtc_miner(authorization)
                    self.auto_game(authorization, 150000)
                    energy = info['daily_attempts']
                    print(f"[ energy ] : {info['daily_attempts']}")
                    if energy > 0:
                        for _ in range(energy):
                            print("[ Tap ] : Tapping...", end='\r')
                            time.sleep(3)
                            self.save_coins(20000, authorization)
                            print("Thành công")
                    else:
                        print("Năng lượng đã hết. Chờ nạp năng lượng...")
                else:
                    print("Token không hợp lệ, chuyển tài khoản tiếp theo")

            print("==============Tất cả tài khoản đã được xử lý=================")
            sys.exit()

if __name__ == "__main__":
    dotcoin = Dotcoin()
    dotcoin.main()
