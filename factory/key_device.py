from monitor import Monitor


class KeyDeviceMonitor(Monitor):
    def monitor(self):
        print(f"Monitoring Key Device: {self.device_id}")

    def stop(self):
        print(f"Stopping Key Device Monitor: {self.device_id}")