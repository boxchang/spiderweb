from datetime import datetime, timedelta
from database import vnedc_database, scada_database
from monitor import Monitor


class CountingDeviceMonitor(Monitor):
    result = {"OKAY": 1, "FAIL": 2}

    def monitor(self):
        vnedc_db = vnedc_database()
        scada_db = scada_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            status = self.get_device_status(scada_db, device)
            self.update_device_status(vnedc_db, device.id, status)
            print(f"Monitoring Factory Equipment: {device.device_name}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_name}")


    def update_device_status(self, db, id, status_id):
        sql = f"""
        update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = {status_id} where id = {id}
        """
        db.execute_sql(sql)


    def get_device_status(self, db, device):

        device_name = device.device_name
        sql = f"""
            SELECT max(d.CreationTime) last_time
          FROM [PMG_DEVICE].[dbo].[COUNTING_DATA] d
          JOIN [PMG_DEVICE].[dbo].[COUNTING_DATA_MACHINE] dm on d.MachineName = dm.COUNTING_MACHINE
          where dm.MES_MACHINE = '{device_name}'
        """
        rows = db.select_sql_dict(sql)
        print(rows)

        given_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
        current_time = datetime.now()
        time_difference = current_time - given_time

        if time_difference > timedelta(minutes=30):
            result = self.result["FAIL"]
        else:
            result = self.result["OKAY"]
        return result

class AOIDeviceMonitor(Monitor):
    def monitor(self):
        print(f"Monitoring Factory Equipment: {self.device_type}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {self.device_type}")