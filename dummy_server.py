import asyncio
import websockets
import json
import ssl
import pathlib
import os
import threading
from time import sleep
import messages.message_config as msgs
# ロボットごとの接続を管理するための辞書
connected_robots = {}
initial_connection = False
STATION_NAME = "DUMMY_SERVER"
SERVER_ADDRESS = "192.168.0.104"


async def handle_connection(websocket, path):
    global initial_connection
    robot_name = path.strip('/').split('/')[-1]
    connected_robots[robot_name] = websocket
    print(f"Robot '{robot_name}' connected.")

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                await handle_binary_message(robot_name, message)
            else:
                await handle_text_message(robot_name, message)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Robot '{robot_name}' disconnected.")
    finally:
        del connected_robots[robot_name]

async def handle_text_message(robot_name, message):
    # print(f"Received text message from {robot_name}: {message}")
    data = json.loads(message)
    
    # Get the 'message' dictionary
    message_data = data.get('message')
    msgtype = message_data.get('msgtype')
    print(msgtype)
    # メッセージタイプに応じた処理を行う
    if msgtype == "INITIAL_CONNECTION":
        await handle_initial_connection(robot_name, data)
    elif msgtype == "NAVIGATION_RESPONSE":
        await handle_navigation_response(robot_name, data)
    elif msgtype == "PARAM":
        await handle_param_response(robot_name, data)
    elif msgtype == "MESSAGE":
        await handle_message(robot_name, data)
    elif msgtype == "ROSBAG":
        await handle_rosbag_response(robot_name, data)
    else:
        print(f"Unknown msgtype '{msgtype}' from {robot_name}")
        print(f"The message content is {message_data}")

async def handle_binary_message(robot_name, message):
    print(f"Received binary message from {robot_name}")
    sections = message.split(b'\0')
    header = sections[0].decode('utf-8')
    type_, name = header.split(':')
    filename = sections[1].decode('utf-8')
    detail = sections[2].decode('utf-8')
    data = sections[3]
    file_path = os.path.join("save_folder", type_, detail, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(data)
    print(f"Saved file '{filename}' from {robot_name}")

async def handle_initial_connection(robot_name, data):
    global initial_connection
    print(f"Handling initial connection from {robot_name}")
    if not initial_connection:
        initial_connection = True

async def handle_navigation_response(robot_name, data):
    result = data.get('result')
    command_id = data.get('command_id')
    print(f"Navigation response from {robot_name}: result={result}, command_id={command_id}")

async def handle_param_response(robot_name, data):
    params = data.get('msg')
    print(f"Updated parameters from {robot_name}: {params}")

async def handle_message(robot_name, data):
    print(f"Message from {robot_name}")
    print(f"The content is {data}")

async def handle_rosbag_response(robot_name, data):
    rosbag_list = data.get('msg')
    print(f"Received rosbag list from {robot_name}: {rosbag_list}")

async def send_command_to_robot(robot_name, command):
    websocket = connected_robots.get(robot_name)
    if websocket:
        try:
            if isinstance(command, str):
                # Send directly if it's already a string
                await websocket.send(command)
            else:
                # Convert to JSON string if it's a dictionary
                await websocket.send(json.dumps(command))

            print(f"Sent command to {robot_name}: {command}")
        except Exception as e:
            print(f"Failed to send command to {robot_name}: {e}")
    else:
        print(f"Robot '{robot_name}' is not connected.")

def user_input_thread(loop):
    asyncio.set_event_loop(loop)  # Set the main event loop
    global initial_connection

    while True:
        if initial_connection:
            command_input = input("Enter a command number to selcect the message type(1: Process example, 2: Get Picture Example , 3: Navigation Example): ").strip()
            if command_input in {'1', '2', '3'}:
                if command_input == '1':
                    command_input = input("Enter a command number to send (1: Start Navigation, 2: Start Make Map , 3: Stop all the running programs): ").strip()
                    if command_input == '1':
                        message = msgs.ProcessMessage(STATION_NAME, "process", "120", "start_navigation").create_message()
                    elif command_input == '2':
                        message = msgs.ProcessMessage(STATION_NAME, "process", "120", "start_make_map").create_message()
                    elif command_input == '3':
                        message = msgs.ProcessMessage(STATION_NAME, "process", "120", "killall").create_message()
                elif command_input == '2':
                    command_input = input("Enter a command number to send (1: Get all, 2: select): ").strip()
                    if command_input == '1':
                        message = msgs.PictureMessage(STATION_NAME, "picture", "120", "get_all").create_message()
                    elif command_input == '2':
                        message = msgs.PictureMessage(STATION_NAME, "picture", "120", "selected", "20250101").create_message()
                elif command_input == '3':
                    command_input = input("Enter a command number to send (1: Set Goal point, 2: set intiial pose, 3: Stop navigation): ").strip()
                    if command_input == '1':
                        message = msgs.NavigationMessage(STATION_NAME, "NAVIGATION", "120", 12.0, 12.0, 0.157).create_message()
                    elif command_input == '2':
                        message = msgs.NavigationMessage(STATION_NAME, "INITPOSE", "120", 0.0, 0.0, 0.0).create_message()
                    elif command_input == '3':
                        message = msgs.NavigationMessage(STATION_NAME, "QUIT", "120", 0.0, 0.0, 0.0).create_message()
                if connected_robots:
                    robot_name = list(connected_robots.keys())[0]
                    future = asyncio.run_coroutine_threadsafe(
                        send_command_to_robot(robot_name, message), loop
                    )
                    try:
                        future.result()  # Wait for the coroutine to complete
                        print("Command sent successfully.")
                    except Exception as e:
                        print(f"Error sending command: {e}")
                else:
                    print("No robots connected.")
        else:
            print("Waiting for initial connection...")
            sleep(1)

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    certfile = pathlib.Path(__file__).parent / 'dummy_ssl' / 'cert.pem'
    keyfile = pathlib.Path(__file__).parent / 'dummy_ssl' / 'key.pem'
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    server_address = SERVER_ADDRESS

    # Start the WebSocket server
    server = await websockets.serve(
        handle_connection, server_address, 5000, ssl=ssl_context
    )
    print(f"Server started at wss://{server_address}:5000")

    loop = asyncio.get_event_loop()  # Get the main event loop
    threading.Thread(target=user_input_thread, args=(loop,), daemon=True).start()

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
