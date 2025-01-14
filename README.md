# 

# README - WebSocket Dummy Server for patrobotAPI

## 概要
このプロジェクトは、WebSocketを使用してロボットとサーバー間の通信をシミュレートする**ダミーサーバー**です。Pythonを使用して、TLS(SSL)で保護されたWebSocketサーバーを立ち上げ、ロボットとリアルタイムでメッセージを交換することができます。

このREADMEでは、サーバーの使い方、動作の仕組み、そしてサンプルメッセージの送受信方法について詳しく説明します。

---

## 🛠️ 環境設定
### 必要なパッケージ
以下のパッケージがインストールされていることを確認してください。

- Python 3.10 以上
- websockets
- asyncio
- ssl
- json
- threading

### 依存ライブラリのインストール
仮想環境を作成し、依存ライブラリをインストールします。

```bash
python3 -m venv venv
source venv/bin/activate
pip install websockets
```

---

## 🚀 サーバーの起動
### サーバーの実行
以下のコマンドでサーバーを起動します。

```bash
python3 dummy_server.py
```

### サーバーの起動確認
サーバーが正常に起動すると、以下のメッセージが表示されます：

```
Waiting for initial connection...
Server started at wss://<server address>:5000
```

---

## 📡 WebSocket接続
### 接続されるロボットについて
このサーバーは、特定のパスでWebSocket接続を受け入れます。ロボットが接続する際のURLは次の形式です：

```
wss://127.0.0.1:5000/<user defined path>/robot_name
```

ここで、`robot_name`は接続してくるロボットの名前です。

### 接続確認
ロボットが接続すると、サーバーに次のメッセージが表示されます：

```
Robot '<robot name>' connected.
```

---

## 💬 メッセージの送信
サーバーは、以下の手順でロボットにコマンドを送信できます。

### ステップ 1: 初期接続確認
サーバーは初期接続が完了するまで待機します：

```
Waiting for initial connection...
```

ロボットが接続したら、コマンドを送信することができます。

### ステップ 2: コマンド選択
サーバーの端末に、以下のような入力プロンプトが表示されます：

```
Enter a command number to select the message type (1: Process example, 2: Get Picture Example, 3: Navigation Example):
```

### ステップ 3: コマンド送信
選択したメッセージタイプに応じて、サーバーからコマンドを送信します。

#### 1. **Process メッセージの送信例**
```
Enter a command number to send (1: Start Navigation, 2: Start Make Map, 3: Stop all the running programs):
```

- **1**: ナビゲーション開始
- **2**: マッピング開始
- **3**: すべてのプログラムを停止

#### 2. **Picture メッセージの送信例**
```
Enter a command number to send (1: Get all, 2: Select):
```

- **1**: すべての画像を取得
- **2**: 特定の日付の画像を取得

#### 3. **Navigation メッセージの送信例**
```
Enter a command number to send (1: Set Goal point, 2: Set initial pose, 3: Stop navigation):
```

- **1**: ゴール地点を設定
- **2**: 初期位置を設定
- **3**: ナビゲーションを停止

### ステップ 4: コマンド送信の結果
コマンドが正常に送信されると、次のようなメッセージが表示されます：

```
Command sent successfully.
```

---

## 🛠️ コードの詳細説明
### メイン関数
```python
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
```
この関数は、SSLで保護されたWebSocketサーバーを起動し、ロボットからの接続を待機します。

### handle_connection 関数
```python
async def handle_connection(websocket, path):
    global initial_connection
    robot_name = path.strip('/').split('/')[-1]
    connected_robots[robot_name] = websocket
    print(f"Robot '{robot_name}' connected.")
```
この関数は、ロボットの接続を処理し、ロボットごとのWebSocket接続を管理します。

### send_command_to_robot 関数
```python
async def send_command_to_robot(robot_name, command):
    websocket = connected_robots.get(robot_name)
    if websocket:
        try:
            if isinstance(command, str):
                await websocket.send(command)
            else:
                await websocket.send(json.dumps(command))
            print(f"Sent command to {robot_name}: {command}")
        except Exception as e:
            print(f"Failed to send command to {robot_name}: {e}")
```
この関数は、特定のロボットにコマンドを送信します。コマンドは、JSON形式の文字列として送信されます。

---

## 💡 メッセージフォーマット
ロボットに送信するメッセージは、以下のJSON形式を使用します：

### **Process メッセージ例**
```json
{
  "process": {
    "sender": "DUMMY_SERVER",
    "duration": "120",
    "msgtype": "<message type>",
    "systemctl": "<process commands>"
  }
}
```

### **Picture メッセージ例**
```json
{
  "picture": {
    "sender": "DUMMY_SERVER",
    "duration": "120",
    "msgtype": "picture",
    "command": "get_all"
  }
}
```

---

## 🧪 テスト方法
### サーバーのテスト
1. **サーバーを起動する**
2. **ロボットを接続する**
3. **コマンドを送信し、結果を確認する**

---

## 📄 まとめ


