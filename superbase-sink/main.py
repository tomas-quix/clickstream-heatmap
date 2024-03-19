import os
from quixstreams import Application, State, message_context
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Supebase():

    def __init__(self, url, key) -> None:
        self._client: Client = create_client(url, key)
        
    def insert_row(self, row:dict):
        data, count = self._client.table('streams') \
            .insert(row) \
            .execute()
        
        print(data)
        print(count)


url = os.environ["SUPERBASE_URL"]
key= os.environ["SUPERBASE_KEY"]

supebase_sink = Supebase(url, key)  

app = Application.Quix("supabase-sink-v2", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf["timestamp"] = sdf.apply(lambda _: message_context().timestamp.milliseconds)
sdf = sdf[["timestamp","session_id", "page_url"]]
sdf = sdf.update(print)

sdf = sdf.update(supebase_sink.insert_row)

if __name__ == "__main__":
    app.run(sdf)