from monitor import Monitor


class SapDataStatusMonitor(Monitor):
    def monitor(self):
        print(f"Monitoring SAP Data Status: {self.device_id}")

    def stop(self):
        print(f"Stopping SAP Data Status Monitor: {self.device_id}")