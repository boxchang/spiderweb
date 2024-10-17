from monitor import Monitor
from wecom.send_message import send_msg, send_wecom


class WecomMonitor(Monitor):
    def monitor(self):
        send_msg(self.vnedc_db)
        print(f"Start WeCom message")

    def stop(self):
        print(f"Stopping WeCom message")