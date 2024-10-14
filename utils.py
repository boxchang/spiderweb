class Log(object):
    def write(db, func_name, comment, status_code_id):
        try:
            sql = f"""
            INSERT INTO [dbo].[spiderweb_check_log] (func_name, comment, update_at, status_code_id)
            VALUES ('{func_name}', '{comment}', GETDATE(), '{status_code_id}')
            """
            db.execute_sql(sql)

        except Exception as e:
            print(f"Error while logging: {e}")
