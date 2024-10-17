import os
import requests

def update_log_flag(vnedc_db, id):
    sql = f"""
        update [VNEDC].[dbo].[spiderweb_check_log] set notice_flag = 1 where id = {id}
    """
    vnedc_db.execute_sql(sql)


def send_msg(vnedc_db):
    msg = ""

    sql = f"""
        SELECT * FROM [VNEDC].[dbo].[spiderweb_check_log] where notice_flag = 0
    """
    rows = vnedc_db.select_sql_dict(sql)

    for row in rows:
        msg = f"{row['type_name']}-{row['device_name']}-{row['comment']}"
        send_wecom(msg)
        update_log_flag(vnedc_db, row['id'])


def send_wecom(msg):
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
