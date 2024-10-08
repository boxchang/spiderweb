from abc import abstractmethod, ABC

from database import vnedc_database
from models import DeviceInfo


class Monitor(ABC):
    def __init__(self, device_type):
        self.device_type = device_type

    @abstractmethod
    def monitor(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def get_device_list(self, db, device_type):

        sql = f"""SELECT c.id, mt.type_name monitor_type, dt.type_name device_type, device_name, ip_address, port,
                    plant, enable, status_name status, status_update_at,comment,job_start_time, dt.job_frequency, c.update_at,c.update_by_id update_by
                    FROM [VNEDC].[dbo].[spiderweb_monitor_device_list] c
                    JOIN [VNEDC].[dbo].[spiderweb_monitor_type] mt on c.monitor_type_id = mt.id
                    JOIN [VNEDC].[dbo].[spiderweb_device_type] dt on c.device_type_id = dt.id
                    JOIN [VNEDC].[dbo].[spiderweb_monitor_status] s on c.status_id = s.id and dt.type_name='{device_type}'"""
        rows = db.select_sql_dict(sql)

        devices = [
            DeviceInfo(id=row['id'], monitor_type=row['monitor_type'], device_type=row['device_type'], device_name=row['device_name'],
                       ip_address=row['ip_address'], port=row['port'], plant=row['plant'], enable=row['enable'],
                       status=row['status'], status_update_at=row['status_update_at'], comment=row['comment'],
                       job_start_time=row['job_start_time'],
                       job_frequency=row['job_frequency'], update_at=row['update_at'], update_by=row['update_by']) for
            row in
            rows]

        return devices
