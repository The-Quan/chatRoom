import sqlite3
import asyncio
import websockets
import json
import firebase_admin
from firebase_admin import credentials, db

# Firebase setup
cred = credentials.Certificate('../firebaseConfig.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fptaptech-3a611-default-rtdb.firebaseio.com/'
})

# SQLite setup for local message storage
conn = sqlite3.connect('chat.db')
c = conn.cursor()

# Create table if not exists for messages in SQLite
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              room_id TEXT,
              username TEXT,
              message TEXT)''')
conn.commit()

# Function to save message to SQLite
def save_message_to_sqlite(room_id, username, message):
    c.execute("INSERT INTO messages (room_id, username, message) VALUES (?, ?, ?)", (room_id, username, message))
    conn.commit()

# Function to save message to Firebase
def save_message_to_firebase(room_id, username, message):
    data = {"username": username, "message": message}
    db.reference(f"rooms/{room_id}/messages").push(data)

# Connected rooms dictionary
rooms = {}

# WebSocket server handler to manage chat rooms and clients
async def handle_client(websocket, path):
    room_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            room_id = data.get('room_id')
            username = data.get('username')
            msg_content = data.get('message')

            # Check if the room exists
            if room_id not in rooms:
                rooms[room_id] = set()

            # Limit room to 2 users
            if len(rooms[room_id]) >= 2 and websocket not in rooms[room_id]:
                await websocket.send(json.dumps({"error": "Room is full"}))
                continue

            # Add client to the room
            rooms[room_id].add(websocket)

            # Save message to SQLite and Firebase
            save_message_to_sqlite(room_id, username, msg_content)
            save_message_to_firebase(room_id, username, msg_content)

            # Broadcast message to all users in the room
            for client in rooms[room_id]:
                await client.send(json.dumps({"username": username, "message": msg_content}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected from room {room_id}")
    finally:
        if room_id and websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)

# Start WebSocket server
async def main():
    async with websockets.serve(handle_client, "localhost", 6789):
        print("WebSocket server running at ws://localhost:6789")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
