import os
import requests
from database import vnedc_database

def prepare_msg():
    message = ""
    db = vnedc_database()
    sql = f"""
        SELECT sdt.type_name, smdl.device_name, sms.[desc]
        FROM [VNEDC].[dbo].[spiderweb_monitor_device_list] smdl
        JOIN [VNEDC].[dbo].[spiderweb_monitor_status] sms on sms.status_code = smdl.status_id
        JOIN [VNEDC].[dbo].[spiderweb_device_type] sdt on sdt.id = smdl.device_type_id
        WHERE status_id = 'E01' and enable = 'Y'
        order by sdt.type_name, smdl.device_name
    """
    rows = db.select_sql_dict(sql)
    send = 0
    if len(rows) > 0:
        message_list = [f"{row['type_name']}-{row['device_name']}" for row in rows]
        message = '\n+'.join(message_list)
        send = 1
    return send, message

def send_message(send_code, msg):
    if send_code == 0:
        pass
    elif send_code == 1:
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
