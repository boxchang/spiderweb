from monitor import Monitor
from utils import Log
import os
import requests
import time

class WecomMonitor(Monitor):
    def monitor(self):
        time.sleep(40)
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
            "msgtype": "markdown",
            "markdown": {
                "content": '',
                # "mentioned_list": ["@all"],
            }
        }
        data["markdown"]["content"] = msg
        r = requests.post(url, headers=headers, json=data)
        return r.json()

    def send_msg(self, vnedc_db):
        comment = ""

        sql = f"""
                SELECT smdlog.id, smdlog.func_name, smdlog.comment, smdlist.device_name,
                smdlog.status_code_id error_status, smdlist.status_id current_status, smdlog.notice_flag, smdlog.recover_msg,
                case 
                    when smdlog.status_code_id = smdlist.status_id then 1
                    else 0
                end as code
                FROM [VNEDC].[dbo].[spiderweb_monitor_device_log] smdlog
                JOIN [VNEDC].[dbo].[spiderweb_monitor_device_list] smdlist
                on smdlog.device_id = smdlist.id
                where smdlog.recover_msg is NULL                
                """
        try:
            rows = vnedc_db.select_sql_dict(sql)
            num = len(rows)
            if len(rows) > 0:
                for row in rows:
                    msg = """{icon_mode}[Issue #{row_id}]\nType: **{device_type}**\nDevice: **{device_name}**\n{comment}"""
                    if str(row['notice_flag']) == 'False':
                        Log.update_log_flag(vnedc_db, row['id'])
                        icon_mode = '\u26A0'
                        comment = row['comment']
                    elif str(row['notice_flag']) == 'True':
                        if 's' in str(row['current_status']).lower():
                            comment = "already recover !"
                            icon_mode = '\u2705'
                        elif str(row['error_status']).lower() != str(row['current_status']).lower():
                            comment = f"now change to {row['comment']}"
                            icon_mode = '\u26A0'

                        Log.update_msg_flag(vnedc_db, row['id'])
                    msg = msg.format(icon_mode=icon_mode, row_id=row['id'], device_type=row['func_name'], device_name=row['device_name'], comment=comment)

                    self.send_wecom(msg)
        except Exception as e:
            print(f"Wecom {e}")

