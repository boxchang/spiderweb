from monitor import Monitor
from utils import Log
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
                SELECT smdlog.id, smdlog.func_name, smdlog.comment, 
                smdlog.status_code_id error_status, smdlist.status_id current_status, smdlog.notice_flag, smdlog.recover_msg,
                case 
                    when smdlog.status_code_id = smdlist.status_id then 1
                    else 0
                end as code
                FROM [VNEDC].[dbo].[spiderweb_monitor_device_log] smdlog
                JOIN [VNEDC].[dbo].[spiderweb_monitor_device_list] smdlist
                on smdlog.device_id = smdlist.id
                where smdlog.recover_msg != 1                   
                """
        rows = vnedc_db.select_sql_dict(sql)
        if len(rows) > 0:
            for row in rows:
                if int(row['notice_flag']) == 0:
                    msg = f"[Issue #{row['id']}] {row['func_name']} {row['comment']}"
                    self.send_wecom(msg)
                    Log.update_log_flag(vnedc_db, row['id'])
                elif int(row['notice_flag']) == 1:
                    if str(row['error_status'])[0] == 'E'  and str(row['current_status']) == 'S':
                        msg = f"[Issue #{row['id']}] {row['func_name']} already recover !"
                    elif str(row['error_status'])[0] == 'E' and str(row['current_status']) == 'E':
                        msg = f"[Issue #{row['id']}] now change to {row['comment']}"
                    self.send_wecom(msg)
                    Log.update_msg_flag(vnedc_db, row['id'])

