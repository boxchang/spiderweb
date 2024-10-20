from action.AOIDeviceAction import AOIDeviceAction
from action.CountingDeviceAction import CountingDeviceAction
from action.ScadaPLCAction import ScadaPLCAction
from monitor import Monitor


class CountingDeviceMonitor(Monitor):
    DEVICE_TYPE = "COUNTING DEVICE"

    def monitor(self):

        devices = self.get_device_list(self.DEVICE_TYPE)
        for device in devices:
            action = CountingDeviceAction(self).IsOverTime
            status, msg = self.execute(action, device)

            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {self.status[status]}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")


class AOIDeviceMonitor(Monitor):
    DEVICE_TYPE = "AOI DEVICE"

    def monitor(self):

        devices = self.get_device_list(self.DEVICE_TYPE)
        for device in devices:
            action = AOIDeviceAction(self).IsOverTime
            status, msg = self.execute(action, device)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {self.status[status]}")

            action = AOIDeviceAction(self).Over_AOI_NG_Rate
            status, msg = self.execute(action, device)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {self.status[status]}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")


class ScadaPLCMonitor(Monitor):
    DEVICE_TYPE = "PLC SCADA"

    def monitor(self):
        devices = self.get_device_list(self.DEVICE_TYPE)
        for device in devices:
            action = ScadaPLCAction(self).IsOverTime
            status, msg = self.execute(action, device)

            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {self.status[status]}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")




