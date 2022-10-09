import json
import os
from dataclasses import dataclass
from time import sleep
from typing import Dict, List


@dataclass
class BluetoothDevice:
    mac_address: str
    name: str = 'Unknown'
    minor_type: str = 'Unknown'
    connected: bool = False
    battery_level: int = 0


def get_bluetooth_devices() -> Dict[str, BluetoothDevice]:
    devices_dict = dict()
    bluetooth_info = os.popen('system_profiler SPBluetoothDataType -json').read()
    bluetooth_info_dict: Dict = json.loads(bluetooth_info)

    connected_devices: List[Dict[str, Dict[str, str]]] = bluetooth_info_dict.get('SPBluetoothDataType')[0] \
        .get('device_connected')
    not_connected_devices: List[Dict[str, Dict[str, str]]] = bluetooth_info_dict.get('SPBluetoothDataType')[0] \
        .get('device_not_connected')

    if connected_devices is not None:
        for device in connected_devices:
            for device_name, device_info in device.items():
                battery_level = int(device_info.get('device_batteryLevelMain', '100%').replace('%', ''))
                devices_dict[device_name] = BluetoothDevice(mac_address=device_info.get('device_address'),
                                                            name=device_name,
                                                            minor_type=device_info.get('device_minorType'),
                                                            connected=True,
                                                            battery_level=battery_level)

    if not_connected_devices is not None:
        for device in not_connected_devices:
            for device_name, device_info in device.items():
                devices_dict[device_name] = BluetoothDevice(mac_address=device_info.get('device_address', 'Unknown'),
                                                            name=device_name,
                                                            minor_type=device_info.get('device_minorType', 'Unknown'),
                                                            connected=False)

    return devices_dict


def announcer():
    current_bluetooth_state = get_bluetooth_devices()
    while True:
        new_bluetooth_state = get_bluetooth_devices()
        for name, new_device_state in new_bluetooth_state.items():
            current_device_state = current_bluetooth_state.get(name, None)
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

            if current_device_state.connected and new_device_state.battery_level <= 10 and \
                    new_device_state.battery_level < current_device_state.battery_level:
                notification_title = f'{new_device_state.minor_type} has Low Battery'
                notification_body = f'{new_device_state.name} has only {new_device_state.battery_level} % Battery left'
                notification_command = f"osascript -e 'display notification \"{notification_body}\" with title" \
                                       f" \"{notification_title}\"'"
                os.system(notification_command)

        current_bluetooth_state = new_bluetooth_state
        sleep(0.5)


if __name__ == '__main__':
    announcer()
