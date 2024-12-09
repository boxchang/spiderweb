from datetime import datetime

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
                # 有工單派送 + 檢驗項目有重量 才檢查
                sql = f"""
                SELECT LotNo as RuncardId, UserId, CreationDate as data_time
                FROM [PMG_DEVICE].[dbo].[WeightDeviceData] wd
                JOIN [PMGMES].[dbo].[PMG_MES_RunCard] r on wd.LotNo = r.Id COLLATE SQL_Latin1_General_CP1_CS_AS
                JOIN [PMGMES].[dbo].[PMG_MES_RunCard_IPQCInspectIOptionMapping] m on m.RunCardId = r.Id and GroupType = 'Weight'
                JOIN [PMGMES].[dbo].[PMG_MES_WorkOrder] w on w.Id = r.WorkOrderId and w.StartDate < CreationDate
                where MES_STATUS = 'E' and CreationDate >= DATEADD(HOUR, -2, GETDATE()) AND CreationDate <= DATEADD(HOUR, -1, GETDATE())
                            """
                rows = self.scada_db.select_sql_dict(sql)

                if len(rows) > 0:
                    comment = [row['RuncardId'] for row in rows]
                    status = "E05"
                    msg = ', '.join(comment)

            elif device_name == 'SCRAP_DATA':

                current_hour = datetime.now().hour
                today = datetime.now().strftime('%Y%m%d')

                if current_hour in [10, 11, 12]:

                    sql = f"""
                    WITH machs AS (
                    select * from [PMGMES].[dbo].[PMG_DML_DataModelList] where DataModelTypeId = 'DMT000003'
                    and [Name] not in ('VN_GD_PVC2_L13', 'VN_GD_PVC2_L14', 'VN_GD_PVC2_L15', 
                    'VN_GD_PVC2_L16', 'VN_GD_PVC2_L17', 'VN_GD_PVC2_L18', 'VN_GD_PVC2_L19', 
                    'VN_GD_PVC2_L20', 'VN_GD_PVC2_L21', 'VN_GD_PVC2_L22')
                    ),
                    scrap AS (
                    SELECT r.*
                      FROM [PMGMES].[dbo].[PMG_MES_Scrap] s,  [PMGMES].[dbo].[PMG_MES_RunCard] r
                      where s.CreationTime between CONVERT(DATETIME, '{today} 08:00:00', 120) and CONVERT(DATETIME, '{today} 12:59:59', 120)
                      and s.RunCardId = r.Id and s.ActualQty > 300
                    
                    )
                    
                    select Abbreviation from machs m
                    LEFT JOIN scrap s on m.Name = s.MachineName
                    where s.Id is null order by Abbreviation
                    """

                    rows = self.scada_db.select_sql_dict(sql)

                    if len(rows) > 0:
                        comment = [row['Abbreviation'] for row in rows]
                        status = "E13"
                        msg = ', '.join(comment)


        except Exception as e:
            print(e)
            status = "E99"
            msg = e

        return status, msg