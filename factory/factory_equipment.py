from datetime import datetime, timedelta
from database import vnedc_database, scada_database
from monitor import Monitor
from utils import Log


class CountingDeviceMonitor(Monitor):
    result = {"OKAY": 'S01', "FAIL": 'E01'}

    def monitor(self):
        vnedc_db = vnedc_database()
        scada_db = scada_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            status = self.get_device_status(scada_db, vnedc_db, device)
            self.update_device_status(vnedc_db, device.id, status)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {'OKAY' if str(status) == 'S01' else 'FAIL'}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")

    def update_device_status(self, db, id, status_id):
        sql = f"""
           update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = '{status_id}', status_update_at = GETDATE() where id = {id}
           """
        db.execute_sql(sql)

    def get_device_status(self, scada_db, vnedc_db, device):
        msg = ""
        device_name = device.device_name

        sql = f"""
                   SELECT last_time
                       FROM (
                           SELECT TOP 1 CreationTime as last_time
                           FROM [PMG_DEVICE].[dbo].[COUNTING_DATA]
                           WHERE MachineName = '{device_name}'
                           ORDER BY CreationTime DESC
                       ) AS LatestRow
                       UNION ALL
                       SELECT * 
                       FROM (
                           SELECT TOP 1 CreationTime as last_time
                           FROM [PMG_DEVICE].[dbo].[COUNTING_DATA]
                           WHERE MachineName = '{device_name}'
                             AND Qty2 IS NOT NULL
                           ORDER BY CreationTime DESC
                       ) AS LatestNonNullRow;
           """
        try:
            rows = scada_db.select_sql_dict(sql)
            # print(rows)
            if len(rows) == 2:
                given_time = datetime.strptime(rows[1]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                current_time = datetime.now()
                time_difference = current_time - given_time
                if time_difference > timedelta(minutes=30):
                    result = self.result["FAIL"]
                    msg = f"{device_name} last time is {given_time} already over 30 mins"
                else:
                    last_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                    last_null = datetime.strptime(rows[1]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                    if last_time - last_null > timedelta(minutes=30):
                        result = self.result["FAIL"]
                        msg = f"{device_name} last time is {last_null} already over 30 mins"
                    else:
                        result = self.result["OKAY"]
            else:
                result = self.result["FAIL"]
                msg = f"{device_name} no any data"
        except:
            result = self.result["FAIL"]
        finally:
            if result == self.result["FAIL"]:
                Log.write(vnedc_db, device.device_type, msg, self.result["FAIL"])
        return result


class AOIDeviceMonitor(Monitor):
    result = {"OKAY": 'S01', "FAIL": 'E01', "AOI_Rate": 'E02'}

    def monitor(self):
        vnedc_db = vnedc_database()
        scada_db = scada_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            status = self.get_device_status(scada_db, device)
            self.update_device_status(vnedc_db, device.id, status)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {'OKAY' if status == 'S01' else 'FAIL'}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")

    def update_device_status(self, db, id, status_id):
        sql = f"""
        update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = '{status_id}', status_update_at = GETDATE() where id = {id}
        """
        db.execute_sql(sql)

    def get_device_status(self, db, device):

        device_name = device.device_name
        sql = f"""
            SELECT CONVERT(varchar(30), od.Cdt, 121) AS last_time, od.OKQty, od.NGQty
            FROM [PMG_DEVICE].[dbo].[OpticalDevice] od
            WHERE od.DeviceId = '{device_name}'
            ORDER BY od.Cdt DESC
            OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;
        """
        try:
            rows = db.select_sql_dict(sql)
            # print(rows)

            given_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.now()
            time_difference = current_time - given_time

            if time_difference > timedelta(minutes=30):
                result = self.result["FAIL"]
            else:
                if (float(rows[0]['NGQty']) / (float(rows[0]['NGQty']) + rows[0]['OKQty']))*100 > 3:
                    result = self.result["AOI_Rate"]
                else:
                    result = self.result["OKAY"]
        except:
            result = self.result["FAIL"]
        return result


class ScadaPLCMonitor(Monitor):
    result = {"OKAY": 'S01', "FAIL": 'E01'}

    def monitor(self):
        vnedc_db = vnedc_database()
        scada_db = scada_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            status = self.get_device_status(scada_db, device)
            self.update_device_status(vnedc_db, device.id, status)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {'OKAY' if status == 'S01' else 'FAIL'}")

    def stop(self):
        print(f"Stopping Factory Equipment Monitor: {device.device_type} - {device.device_name}")

    def update_device_status(self, db, id, status_id):
        sql = f"""
        update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = '{status_id}', status_update_at = GETDATE() where id = {id}
        """
        db.execute_sql(sql)

    def get_device_status(self, db, device):

        device_name = device.device_name
        table_name = device.comment

        try:
            if 'NBR' in device_name:
                sql = f"""
                    SELECT CONVERT(varchar(30), max(datetime), 121) AS last_time
                    FROM {table_name}
                """

            elif 'PVC' in device_name:
                sql = f"""
                    SELECT max(CreationTime) as last_time
                    FROM [PMG_DEVICE].[dbo].[PVC_MACHINE_DATA]
                    where MachineName = '{device_name}'
                """
            rows = db.select_sql_dict(sql)
            given_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.now()
            time_difference = current_time - given_time

            if time_difference > timedelta(minutes=30):
                result = self.result["FAIL"]
            else:
                result = self.result["OKAY"]
        except:
            result = self.result["FAIL"]
        return result


