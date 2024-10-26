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
        comment = ""
        msg = """
        [Issue #{row_id}]
        Type: {device_type}
        Device: {device_name}
        {comment}
        """

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
                where smdlog.recover_msg is null                   
                """
        rows = vnedc_db.select_sql_dict(sql)
        if len(rows) > 0:
            for row in rows:

                if int(row['notice_flag']) == 0:
                    comment = row['comment']
                    Log.update_log_flag(vnedc_db, row['id'])
                elif int(row['notice_flag']) == 1:
                    if str(row['error_status'])[0] == 'E'  and str(row['current_status']) == 'S':
                        comment = "already recover !"
                    elif str(row['error_status'])[0] == 'E' and str(row['current_status']) == 'E':
                        comment = f"now change to {row['comment']}"
                    Log.update_msg_flag(vnedc_db, row['id'])
                msg.format(row_id=row['id'], device_type=row['func_name'], device_name=row['device_name'], comment=comment)
                self.send_wecom(msg)


