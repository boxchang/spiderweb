import threading
import time

from database import vnedc_database
from factory.factory import MonitorFactory
from models import DeviceInfo, DeviceType
from wecom.send_message import send_message, prepare_msg

class MonitorThread(threading.Thread):
    def __init__(self, monitor, frequency):
        super().__init__()
        self.monitor = monitor
        self.frequency = frequency
        self._stop_event = threading.Event()

    def run(self):
        frequency = int(self.frequency)
        while not self._stop_event.is_set():
            self.monitor.monitor()
            time.sleep(frequency)  # Monitor periodically, can adjust as needed

    def stop(self):
        self.monitor.stop()
        self._stop_event.set()

def get_device_list():
    db = vnedc_database()
    sql = f"""SELECT [type_name]
                  ,[job_frequency]
                  ,[update_at]
                  ,[update_by_id]
              FROM [VNEDC].[dbo].[spiderweb_device_type]"""
    rows = db.select_sql_dict(sql)

    device_types = [
        DeviceType(type_name=row['type_name'], job_frequency=row['job_frequency'], update_at=row['update_at'], update_by=row['update_by_id']) for
        row in
        rows]

    return device_types


def main():
    device_type_list = get_device_list()

    threads = []

    # Create and start threads for each device type
    for device_type in device_type_list:
        monitor = MonitorFactory.create_monitor(device_type.type_name)
        job_frequency = device_type.job_frequency
        thread = MonitorThread(monitor, job_frequency)
        threads.append(thread)
        thread.start()

if __name__ == "__main__":
    main()