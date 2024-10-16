from action.MESDataStatusAction import MESDataStatusAction
from monitor import Monitor


class MesDataStatusMonitor(Monitor):
    DEVICE_TYPE = "MES JOB"

    def monitor(self):
        devices = self.get_device_list(self.DEVICE_TYPE)
        for device in devices:
            action = MESDataStatusAction(self).CheckDataStatus
            status, msg = self.execute(action, device)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {self.status[status]}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")


