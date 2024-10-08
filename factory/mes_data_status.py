from monitor import Monitor


class MesDataStatusMonitor(Monitor):
    def monitor(self):
        print(f"Monitoring MES Data Status: {self.device_id}")

    def stop(self):
        print(f"Stopping MES Data Status Monitor: {self.device_id}")