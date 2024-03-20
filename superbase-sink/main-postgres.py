import os
from quixstreams import Application, State, message_context
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

class PostgresSink():

    def __init__(self, dbname: str, user: str, password, host:str) -> None:
        # Connect to the database
        self._conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        
        # Open a cursor to perform database operations
        self._cur = self._conn.cursor()


        
    def insert_row(self, row:dict):
        
        insert_str = "INSERT INTO streams (timestamp,session_id,page_url) "
        
        insert_str += f"VALUES ({str(row['timestamp'])}, '{row['session_id']}','{row['page_url']}')"
        
        insert_sql = sql.SQL(insert_str)

        self._cur.execute(insert_sql)

        # Commit the changes to the database
        self._conn.commit()
        
        print(insert_str)

postgresSink = PostgresSink(
    dbname="postgres",
    user="postgres.kwrouqntpujhrbjttvdc",
    password="fxk_dey.AHA5yet2tdw",
    host="aws-0-eu-central-1.pooler.supabase.com"
)

app = Application.Quix("supabase-sink-v2", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf["timestamp"] = sdf.apply(lambda _: message_context().timestamp.milliseconds)
sdf = sdf[["timestamp","session_id", "page_url"]]
sdf = sdf.update(print)

sdf = sdf.update(postgresSink.insert_row)

if __name__ == "__main__":
    app.run(sdf)