import asyncio
import websockets
import os
from quixstreams import Application
from dotenv import load_dotenv
import uuid
import json
load_dotenv()

class webSocketSource:
    
    def __init__(self) -> None:
        app = Application.Quix(str(uuid.uuid4()), auto_offset_reset="earliest")
        self._topic = app.topic(name=os.environ["input"], value_serializer='json')
        self._consumer = app.get_consumer()
        self._consumer.subscribe([self._topic.name])
        
        self.websocket_connections = {}
        
        # Instead of directly creating a task in the constructor, 
        # we'll start the task from outside to avoid issues with incomplete initialization.
        
    async def consume_messages(self):
        while True:
            message = self._consumer.poll(1)
            
            if message is not None:
                value = json.loads(bytes.decode(message.value()))
                key = bytes.decode(message.key())
                print(value)
                
                if key in self.websocket_connections:
                    await self.websocket_connections[key].send(json.dumps(value)) 
                    print("Send to " + key)
                
            else:
                await asyncio.sleep(1)
                
            
    async def handle_websocket(self, websocket, path):
        print(f"Client connected to socket. Path={path}")
        self.websocket_connections[path] = websocket

        try:
            print("Keep the connection open and wait for messages if needed")
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosedOK:
            print(f"Client {path} disconnected normally.")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Client {path} disconnected with error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            print("Removing client from connection list")
            if path in self.websocket_connections:
                del self.websocket_connections[path]  # Use `del` to remove items from a dictionary

    async def start_websocket_server(self):
        print("listening for websocket connections..")
        server = await websockets.serve(self.handle_websocket, '0.0.0.0', 80)
        await server.wait_closed()

async def main():
    client = webSocketSource()
    # Start consuming messages as a separate task
    asyncio.create_task(client.consume_messages())
    await client.start_websocket_server()

# Run the application with exception handling
try:
    asyncio.run(main())
except Exception as e:
    print(f"An error occurred: {e}")