from datetime import datetime, timedelta
import re

class CountingDeviceAction():
    vnedc_db = None
    scada_db = None
    status = None
    MACHINE_MAPPING = {}

    def __init__(self, obj):
        self.vnedc_db = obj.vnedc_db
        self.scada_db = obj.scada_db
        self.status = obj.status
        self.MACHINE_MAPPING = obj.MACHINE_MAPPING

    # Check if there is no data for a long time
    def IsOverTime(self, device):
        msg = ""
        status = "S01"
        speed = 220
        device_name = device.device_name
        today = datetime.today().strftime('%Y-%m-%d')
        wo_sql = f"""
            SELECT mach_id
            FROM [VNEDC].[dbo].[collection_daily_prod_info_head]
            where data_date = '{today}'
        """
        condition = self.vnedc_db.select_sql_dict(wo_sql)
        # mach_list = sorted(list(set([f"NBR_CountingMachine_{int(mach['mach_id'][-2:])}" if (mach['mach_id'][-2:]) is not None else print(mach['mach_id']) for mach in condition])))
        mach_list = sorted(list(set([f"NBR_CountingMachine_{int(re.sub('[^0-9]', '',  str(mach['mach_id'])))}" for mach in condition if (mach['mach_id'][-2:])])))
        match_name = any(device_name[:-1] == mach for mach in mach_list)

        if match_name == True:
            sql = f"""
               SELECT last_time, Speed
                   FROM (
                       SELECT TOP 1 CreationTime as last_time, Speed
                       FROM [PMG_DEVICE].[dbo].[COUNTING_DATA]
                       WHERE MachineName = '{device_name}'
                       ORDER BY CreationTime DESC
                   ) AS LatestRow
                   UNION ALL
                   SELECT * 
                   FROM (
                       SELECT TOP 1 CreationTime as last_time, Speed
                       FROM [PMG_DEVICE].[dbo].[COUNTING_DATA]
                       WHERE MachineName = '{device_name}'
                         AND Qty2 IS NOT NULL
                       ORDER BY CreationTime DESC
                   ) AS LatestNonNullRow;
                       """
            try:

                rows = self.scada_db.select_sql_dict(sql)

                if len(rows) == 2:
                    given_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                    current_time = datetime.now()
                    time_difference = current_time - given_time
                    if time_difference > timedelta(minutes=30):
                        status = "E01"
                        given_time = given_time.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
                        msg = f"The last time is {given_time} already over 30 mins"
                    else:
                        last_time = datetime.strptime(rows[0]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                        last_null = datetime.strptime(rows[1]['last_time'][:-1], '%Y-%m-%d %H:%M:%S.%f')
                        if last_time - last_null > timedelta(minutes=30):
                            status = "E01"
                            last_null = last_null.replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
                            msg = f"NULL from {last_null}"
                        else:
                            if rows[0]['Speed'] is None:
                                # status = "E10"
                                # msg = f"{device_name} speed is None"
                                pass
                            elif int(rows[0]['Speed']) > speed:
                                status = "E01"
                                msg = f"{device_name} speed is > 220"
                else:
                    status = "E03"
                    msg = f"No any data"
            except Exception as e:
                print(e)
                status = "E99"
                msg = e

        else:
            status = 'S01'
            msg = 'Machine stop'

        return status, msg

    def NoIPQC(self, device):
        msg = "Success"
        status = "S01"  # Default to "Success"
        # VN_GD_NBR1_L03
        device_name = device.device_name

        machine_name = self.MACHINE_MAPPING[device_name]

        # Return True if has QC check gloves in every hour
        try:
            sql_counting = f"""
                SELECT SUM(Qty2) as qty
                FROM [PMG_DEVICE].[dbo].[COUNTING_DATA] where MachineName = '{device.device_name}'
                and CreationTime between CONVERT(DATETIME, CONVERT(VARCHAR, GETDATE(), 112) + ' ' + RIGHT('00' + CAST(DATEPART(HOUR, GETDATE()) AS VARCHAR), 2) + ':00:00', 120)
                      AND CONVERT(DATETIME, CONVERT(VARCHAR, GETDATE(), 112) + ' ' + RIGHT('00' + CAST(DATEPART(HOUR, GETDATE()) AS VARCHAR), 2) + ':59:59', 120)
                and Qty2 is not null
                """
            counting_data = self.scada_db.select_sql_dict(sql_counting)

            sql_check_ipqc = f"""
                WITH CheckData AS (
                    -- Lọc dữ liệu thực tế từ bảng dựa trên giờ trước đó
                    SELECT 
                        COUNT(*) AS ValidDataCount
                    FROM [PMGMES].[dbo].[PMG_MES_IPQCInspectingRecord] ipqc
                    JOIN [PMGMES].[dbo].[PMG_MES_RunCard] r
                        ON ipqc.RunCardId = r.Id
                    WHERE r.InspectionDate = CONVERT(date, GETDATE())  -- Chỉ kiểm tra ngày hiện tại
                        AND Period = DATEPART(HOUR, DATEADD(hour, -1, GETDATE()))  -- Kiểm tra giờ trước đó
                        AND OptionName = 'Weight'
                        AND MachineName = '{machine_name}'
                        --AND LineName = 'B2'
                )
                -- So sánh dữ liệu thực tế với Period của giờ trước đó
                SELECT 
                    DATEPART(HOUR, DATEADD(hour, -1, GETDATE())) AS ExpectedPeriod,
                    CASE 
                        WHEN cd.ValidDataCount IS NULL OR cd.ValidDataCount = 0 THEN 'Missing data'  -- Nếu không có dữ liệu
                        ELSE 'Data exists'  -- Nếu có dữ liệu
                    END AS Status
                FROM CheckData cd;
                """
            qc = self.scada_db.select_sql_dict(sql_check_ipqc)
            temp = ""
            # current_hour = int(datetime.now().hour - timedelta(hours=1))
            if str(qc[0]["Status"]) == "Missing data" and int(counting_data[0]["qty"]) > 0:
                status = "E99"
                msg = "Not exited the IPQC but have Machine online"
                print('OK')
            else:
                print("Normal")
        except Exception as e:
            status = "E99"
            msg = f"Error while checking IPQC for {device.device_name}: {str(e)}"
        return status, msg
