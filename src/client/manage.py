from realsense import RealSenseClient
from seek_thermal import SeekThermalClient
from drone import DroneClient


class ManageClient:
    def __init__(self):
        self.rs_client = RealSenseClient()
        self.seek_thermal_client = SeekThermalClient()
        self.drone_client = DroneClient()

    def run(self):
        self.rs_client.run()                # start realsense socket client thread
        self.seek_thermal_client.run()      # start seek thermal socket client thread
        self.drone_client.run()             # start drone data socket client thread


if __name__ == '__main__':
    client_manager = ManageClient()
    client_manager.run()                    # start client thread manager