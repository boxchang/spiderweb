from datetime import datetime, timedelta


class CountingDeviceAction():
    vnedc_db = None
    scada_db = None
    status = None

    def __init__(self, obj):
        self.vnedc_db = obj.vnedc_db
        self.scada_db = obj.scada_db
        self.status = obj.status

    # Check if there is no data for a long time
    def IsOverTime(self, device):
        msg = ""
        status = "S01"
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
            rows = self.scada_db.select_sql_dict(sql)

            if len(rows) == 2:
                given_time = datetime.strptime(rows[1]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                current_time = datetime.now()
                time_difference = current_time - given_time
                if time_difference > timedelta(minutes=30):
                    status = "E01"
                    msg = f"The last time is {given_time} already over 30 mins"
                else:
                    last_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                    last_null = datetime.strptime(rows[1]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                    if last_time - last_null > timedelta(minutes=30):
                        status = "E01"
                        msg = f"The last time is {given_time} already over 30 mins"
            else:
                status = "E03"
                msg = f"No any data"
        except Exception as e:
            print(e)
            status = "E99"
            msg = e

        return status, msg