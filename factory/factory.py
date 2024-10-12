from factory.factory_equipment import CountingDeviceMonitor, AOIDeviceMonitor, ScadaPLCMonitor
from factory.mes_data_status import MesDataStatusMonitor
# from factory.key_device import KeyDeviceMonitor


class MonitorFactory:
    @staticmethod
    def create_monitor(device_type):
        if device_type == "COUNTING DEVICE":
            return CountingDeviceMonitor(device_type)
        elif device_type == "AOI DEVICE":
            return AOIDeviceMonitor(device_type)
        elif device_type == "PLC SCADA":
            return ScadaPLCMonitor(device_type)
        elif device_type == 'MES JOB':
            return MesDataStatusMonitor(device_type)
        else:
            raise ValueError(f"Unknown device type: {device_type}")
