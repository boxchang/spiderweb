import pyodbc

# 定義員工物件類別
from database import vnedc_database


class DeviceInfo:

    def __init__(self, id, monitor_type, device_type, device_name, ip_address, port, plant, enable, status, status_update_at, comment, update_at, update_by):
        self.id = id
        self.monitor_type = monitor_type
        self.device_type = device_type
        self.device_name = device_name
        self.ip_address = ip_address
        self.port = port
        self.plant = plant
        self.enable = enable
        self.status = status
        self.status_update_at = status_update_at
        self.comment = comment
        self.update_at = update_at
        self.update_by = update_by




class DeviceType:

    def __init__(self, type_name, job_frequency, update_at, update_by):
        self.type_name = type_name
        self.job_frequency = job_frequency
        self.update_at = update_at
        self.update_by = update_by

