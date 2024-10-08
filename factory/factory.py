from factory.factory_equipment import CountingDeviceMonitor, AOIDeviceMonitor
from factory.key_device import KeyDeviceMonitor


class MonitorFactory:
    @staticmethod
    def create_monitor(device_type):
        if device_type == "COUNTING DEVICE":
            return CountingDeviceMonitor(device_type)
        elif device_type == "AOI DEVICE":
            return AOIDeviceMonitor(device_type)
        else:
            raise ValueError(f"Unknown device type: {device_type}")
