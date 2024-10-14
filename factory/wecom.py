from monitor import Monitor
from wecom.send_message import prepare_msg, send_message


class WecomMonitor(Monitor):
    def monitor(self):
        code, msg = prepare_msg()
        send_message(code, msg)
        print(f"Start WeCom message")

    def stop(self):
        print(f"Stopping WeCom message")