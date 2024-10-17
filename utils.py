from database import vnedc_database
from models import DeviceType


class Log(object):
    def write(self, db, func_name, comment, status_code_id):
        try:
            sql = f"""
            INSERT INTO [dbo].[spiderweb_check_log] (func_name, comment, update_at, status_code_id, notice_flag)
            VALUES ('{func_name}', '{comment}', GETDATE(), '{status_code_id}', 0)
            """
            db.execute_sql(sql)

        except Exception as e:
            print(f"Error while logging: {e}")

class Utils(object):

    def get_device_type_list():
        db = vnedc_database()
        sql = f"""SELECT [type_name]
                      ,[job_frequency]
                      ,[update_at]
                      ,[update_by_id]
                  FROM [VNEDC].[dbo].[spiderweb_device_type]"""
        rows = db.select_sql_dict(sql)

        device_types = [
            DeviceType(type_name=row['type_name'], job_frequency=row['job_frequency'], update_at=row['update_at'], update_by=row['update_by_id']) for
            row in
            rows]

        return device_types