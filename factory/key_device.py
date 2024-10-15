from monitor import Monitor
from database import vnedc_database
import psutil
import random
import socket

class KeyDeviceMonitor(Monitor):
    result = {"OKAY": 'S01', "FAIL": 'E01'}

    def monitor(self):
        vnedc_db = vnedc_database()
        devices = self.get_device_list(vnedc_db, self.device_type)
        for device in devices:
            ip = device.ip_address
            port = device.port
            name = device.device_name
            status = self.get_device_status(ip, port)
            self.update_device_status(vnedc_db, device.id, ip, port, name, status)
            print(f"Monitoring Factory Equipment: {device.device_type} - {device.device_name} - {'OKAY' if str(status) == 'S01' else 'FAIL'}")

    def stop(self):
        print(f"Stopping Key Device Monitor: {self.device_id}")

    def get_device_status(self, client_ip, client_port, message='info'):
        server_port = self.get_port_list()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(("0.0.0.0", server_port))
            print(f"Sending message to {client_ip}:{client_port}")
            server_socket.sendto(message.encode(), (client_ip, client_port))
            try:
                response, client_address = server_socket.recvfrom(4096)  # Buffer size of 4096
                client_message = response.decode()
                server_socket.close()
                print(f"Connection with {client_address} closed.")

                if int(client_message) == 1:
                    result = self.result["OKAY"]
                else:
                    result = self.result["FAIL"]
            except socket.timeout:
                print(f"No response from {client_ip}:{client_port}.")
                result = self.result["FAIL"]
            except Exception as e:
                print(f"Error: {str(e)}")
                result = self.result["FAIL"]
        return result

    def update_device_status(self, db, id, client_ip, client_port, client_name, status_id):
        sql = f"""
           update [VNEDC].[dbo].[spiderweb_monitor_device_list] set status_id = '{status_id}', status_update_at = GETDATE() where id = {id} and ip_address = '{client_ip}' and port = '{client_port}' and device_name = '{client_name}'
           """
        db.execute_sql(sql)

    def get_port_open_list(self):
        connections = psutil.net_connections(kind='inet')
        open_ports = set()
        for conn in connections:
            if conn.status == 'ESTABLISHED' or conn.status == 'LISTEN':
                open_ports.add(conn.laddr.port)
        return sorted(open_ports)

    def get_port_list(self):
        open_ports = self.get_port_open_list()
        while True:
            num = random.randint(7000, 9000)
            if num not in open_ports:
                return num