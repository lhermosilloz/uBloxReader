from pyubx2 import UBXReader
import serial.tools.list_ports
import socket
import json
import time

def main():
    ports = serial.tools.list_ports.comports()
    print("Available ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")

    # Drones to send GPS data to:
    drones = [
        {'drone_id': 'drone_A', 'local_static_ip': '10.223.0.101', 'receive_port': '5006'},
        {'drone_id': 'drone_B', 'local_static_ip': '10.223.0.102', 'receive_port': '5007'},
        {'drone_id': 'drone_C', 'local_static_ip': '10.223.0.103', 'receive_port': '5008'},
        {'drone_id': 'drone_D', 'local_static_ip': '10.223.0.104', 'receive_port': '5009'},
        {'drone_id': 'drone_E', 'local_static_ip': '10.223.0.105', 'receive_port': '5010'},
        {'drone_id': 'drone_F', 'local_static_ip': '10.223.0.106', 'receive_port': '5011'},
        {'drone_id': 'drone_G', 'local_static_ip': '10.223.0.107', 'receive_port': '5012'},
        {'drone_id': 'drone_Ghadron', 'local_static_ip': '10.223.0.110', 'receive_port': '5020'},
        {'drone_id': 'drone_Sightline', 'local_static_ip': '10.223.0.111', 'receive_port': '5021'},
        {'drone_id': 'ground_Station', 'local_static_ip': '10.223.0.100', 'receive_port': '5005'},
    ]

    # Create the udp socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Open serial connection to F9P
    ser = serial.Serial('COM6', baudrate=9600, timeout=1)

    ubr = UBXReader(ser)
    try:
        while True:
            (raw_data, parsed_data) = ubr.read()
            if parsed_data:
                if parsed_data and parsed_data.identity == 'NAV-POSLLH':
                    gps_data = {
                        'msg_type': 'rover_gps',
                        'lon': parsed_data.lon,
                        'lat': parsed_data.lat
                    }

                    print(gps_data)

                    # Convert to JSON
                    json_data = json.dumps(gps_data).encode('utf-8')

                    # Send to all destinations
                    for drone in drones:
                        try:
                            udp_socket.sendto(json_data, (drone['local_static_ip'], int(drone['receive_port'])))
                        except Exception as e:
                            print(f"Error sending to {drone['drone_id']} at {drone['local_static_ip']}:{drone['receive_port']}: {e}")
                    # Sleep briefly to avoid overwhelming the network (1 second)
                    time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        udp_socket.close()
        ser.close()

if __name__ == "__main__":
    main()