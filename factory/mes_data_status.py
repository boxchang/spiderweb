from database import vnedc_database, scada_database
from monitor import Monitor
from datetime import datetime, timedelta

class MesDataStatusMonitor(Monitor):
    result = {"OKAY": 'S01', "FAIL": 'E01'}

    def monitor(self):
        vnedc_db = vnedc_database()
        scada_db = scada_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            status = self.get_device_status(scada_db, device)
            self.update_device_status(vnedc_db, device.id, status)
            # print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {'OKAY' if str(status) == 'S01' else 'FAIL'}")

    def stop(self):
        # print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")
        return

    def update_device_status(self, db, id, status_id):
        sql = f"""
        update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = '{status_id}', status_update_at = GETDATE() where id = {id}
        """
        db.execute_sql(sql)

    def get_device_status(self, db, device):

        device_name = device.device_name

        try:
            if device_name == 'ThicknessDeviceData':
                sql = f"""
                    SELECT RunCardId, DeviceId UserId, Cdt data_time
                    FROM [PMG_DEVICE].[dbo].[ThicknessDeviceData]
                    WHERE Cdt >= DATEADD(HOUR, -1, GETDATE()) AND Cdt <= GETDATE() AND MES_STATUS = 'E'
                    """
            elif device_name == 'WeightDeviceData':
                sql = f"""
                    SELECT LotNo as RuncardId, UserId, CreationDate as data_time
                    FROM [PMG_DEVICE].[dbo].[WeightDeviceData]
                    where MES_STATUS = 'E' and CreationDate >= DATEADD(HOUR, -1, GETDATE()) AND CreationDate <= GETDATE()
                    """
            rows = db.select_sql_dict(sql)
            if len(rows) == 0:
                result = self.result["OKAY"]
            else:
                comment = [row['RuncardId'] for row in rows]
                result = self.result["FAIL"]
                sql = f"""
                    update [VNEDC].[dbo].[spiderweb_check_log] set comment = '{comment}', update_at = GETDATE() where id = {id} 
                """
                db.execute_sql(sql)
        except:
            result = self.result["FAIL"]
        return result