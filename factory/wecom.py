from monitor import Monitor
from utils import Utils, Log
import os
import requests


class WecomMonitor(Monitor):
    def monitor(self):
        self.send_msg(self.vnedc_db)
        print(f"Start WeCom message")

    def stop(self):
        print(f"Stopping WeCom message")


    def send_wecom(self, msg):
        print('Send message')
        print(msg)
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        wecom_file = os.path.join(path, "dt_wecom_key.config")
        url = ''  # Add Wecom GD_MES group key
        if os.path.exists(wecom_file):
            with open(wecom_file, 'r') as file:
                url = file.read().strip()

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": '',
                # "mentioned_list": ["@all"],
            }
        }
        data["text"]["content"] = msg
        r = requests.post(url, headers=headers, json=data)
        return r.json()

    def send_msg(self, vnedc_db):
        msg = ""

        sql = f"""
            SELECT * FROM [VNEDC].[dbo].[spiderweb_monitor_device_log] where notice_flag = 0
        """
        rows = vnedc_db.select_sql_dict(sql)
        if len(rows) > 0:
            for row in rows:
                msg = f"{row['func_name']} {row['comment']}"
                self.send_wecom(msg)
                Log.update_log_flag(vnedc_db, row['id'])