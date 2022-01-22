import os
from dataclasses import dataclass
from time import sleep
from typing import Dict


@dataclass
class BluetoothDevice:
    mac_address: str
    name: str = 'Unknown'
    minor_type: str = 'Unknown'
    connected: bool = False


def get_bluetooth_devices() -> Dict[str, BluetoothDevice]:
    devices_dict = dict()
    bluetooth_info = os.popen('system_profiler SPBluetoothDataType').read()
    _, paired_devices_info = bluetooth_info.split('Paired Bluetooth Devices:\n')
    paired_devices_info = paired_devices_info.replace('\n', '')
    device_info_lines = paired_devices_info.split('          ')[1:]
    device_info = dict()
    for line in device_info_lines:
        if line.startswith('    '):
            line = line.replace('    ', '')
            attr, attr_value = line.split(': ', maxsplit=1)
            if attr == 'Minor Type':
                device_info['minor_type'] = attr_value
            elif attr == 'Connected' and attr_value == 'Yes':
                device_info['connected'] = True
            elif attr == 'Address':
                device_info['mac_address'] = attr_value
        else:
            if device_info:
                devices_dict[device_info.get('mac_address')] = BluetoothDevice(**device_info)
                device_info = dict()
            device_info['name'] = line.replace(':', '')
    if device_info:
        devices_dict[device_info.get('mac_address')] = BluetoothDevice(**device_info)
    return devices_dict


def announcer():
    current_bluetooth_state = get_bluetooth_devices()
    while True:
        new_bluetooth_state = get_bluetooth_devices()
        for mac, new_device_state in new_bluetooth_state.items():
            current_device_state = current_bluetooth_state.get(mac, None)
            if not current_device_state or not current_device_state.connected and new_device_state.connected:
                notification_title = f'{new_device_state.minor_type} Connected'
                notification_body = f'{new_device_state.name} has been connected'
                notification_command = f"osascript -e 'display notification \"{notification_body}\" with title" \
                                       f" \"{notification_title}\"'"
                os.system(notification_command)
            elif current_device_state.connected and not new_device_state.connected:
                notification_title = f'{new_device_state.minor_type} Disconnected'
                notification_body = f'{new_device_state.name} has been disconnected'
                notification_command = f"osascript -e 'display notification \"{notification_body}\" with title" \
                                       f" \"{notification_title}\"'"
                os.system(notification_command)
        current_bluetooth_state = new_bluetooth_state
        sleep(1)


if __name__ == '__main__':
    announcer()
