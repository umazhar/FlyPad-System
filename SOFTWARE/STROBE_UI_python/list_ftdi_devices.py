from pyftdi.ftdi import Ftdi

def list_ftdi_devices():
    devices = Ftdi.list_devices()
    if not devices:
        print("No FTDI devices found.")
        return

    for device in devices:
        device_info, interface_number = device
        print(f"device_info: {device_info}")
        print(f"Type of device_info: {type(device_info)}")
        vid = device_info.vid
        pid = device_info.pid
        bus = device_info.bus
        address = device_info.address
        serial_number = device_info.sn
        index = device_info.index
        description = device_info.description

        # device URL
        url = f'ftdi://{vid:04x}:{pid:04x}:{serial_number}/{interface_number}'
        print(f"Device URL    : {url}")
        print(f"  Description : {description}")
        print(f"  Serial      : {serial_number}")
        print(f"  Vendor ID   : 0x{vid:04X}")
        print(f"  Product ID  : 0x{pid:04X}")
        print(f"  Bus         : {bus}")
        print(f"  Address     : {address}")
        print(f"  Interface   : {interface_number}")
        print('-' * 40)

if __name__ == "__main__":
    list_ftdi_devices()
