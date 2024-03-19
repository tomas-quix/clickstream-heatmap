import asyncio
import websockets

# This code will publish the CSV data to a stream as if the data were being generated in real-time.
import time
import json
import time
import os
from quixstreams import Application
from dotenv import load_dotenv


load_dotenv("./.env")


class webSocketSource:
    
    
    def __init__(self) -> None:
        print("__init__")
        
        app = Application.Quix()
        self._topic = app.topic(name=os.environ["output"], value_serializer='json')

        self._producer = app.get_producer()
        print("Done")
        


    # handle new websocket connections
    async def handle_websocket(self, websocket, path):
        async for message in websocket:
            # Here you could handle incoming messages. This example simply broadcasts them.
            print(str(message))
            self._producer.produce(
                    topic=self._topic.name,
                    key=path.lstrip('/'),
                    value=message)


    # start the server. Listen on port 80
    async def start_websocket_server(self):
        print("listening for websocket connections..")
        server = await websockets.serve(self.handle_websocket, '0.0.0.0', 80)
        await server.wait_closed()


# Main function to run the application
async def main():
    print("Main")

    
    client = webSocketSource()
    
    await client.start_websocket_server()



# Run the application
asyncio.run(main())
