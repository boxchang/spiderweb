
class MESDataStatusAction():
    vnedc_db = None
    scada_db = None
    status = None

    def __init__(self, obj):
        self.vnedc_db = obj.vnedc_db
        self.scada_db = obj.scada_db
        self.status = obj.status

    # Check if there is no data for a long time
    def CheckDataStatus(self, device):
        device_name = device.device_name
        msg = ""
        status = "S01"

        try:
            if device_name == 'THICKNESS_DATA':
                sql = f"""
                        SELECT RunCardId, DeviceId UserId, Cdt data_time
                        FROM [PMG_DEVICE].[dbo].[ThicknessDeviceData] td
                        JOIN [PMGMES].[dbo].[PMG_MES_RunCard] r on td.RunCardId = r.Id
                        WHERE Cdt >= DATEADD(HOUR, -2, GETDATE()) AND Cdt <= DATEADD(HOUR, -1, GETDATE()) AND MES_STATUS = 'E'
                            """
                rows = self.scada_db.select_sql_dict(sql)

                if len(rows) > 0:
                    comment = [row['RuncardId'] for row in rows]
                    status = "E04"
                    msg = ', '.join(comment)

            elif device_name == 'WEIGHT_DATA':
                sql = f"""
                            SELECT LotNo as RuncardId, UserId, CreationDate as data_time
                            FROM [PMG_DEVICE].[dbo].[WeightDeviceData] wd
                            JOIN [PMGMES].[dbo].[PMG_MES_RunCard] r on wd.LotNo = r.Id
                            where MES_STATUS = 'E' and CreationDate >= DATEADD(HOUR, -2, GETDATE()) AND CreationDate <= DATEADD(HOUR, -1, GETDATE())
                            """
                rows = self.scada_db.select_sql_dict(sql)

                if len(rows) > 0:
                    comment = [row['RuncardId'] for row in rows]
                    status = "E05"
                    msg = ', '.join(comment)

        except Exception as e:
            print(e)
            status = "E99"
            msg = e

        return status, msg