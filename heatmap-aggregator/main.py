import os
from quixstreams import Application,State, message_context
from dotenv import load_dotenv
import uuid
import math
from datetime import timedelta

load_dotenv()

app = Application.Quix("heatmap-aggregator-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf[sdf["type"] == "mousemove"]

tile_grid_size = 10

def heatmap(state: dict, row: dict):
    
    if len(state.keys()) == 0:
        print("INIT")
    
    x = str(math.floor(tile_grid_size * (row["mouse-coordinates"]["x"] / row["window"]["width"])))
    y = str(math.floor(tile_grid_size * (row["mouse-coordinates"]["y"] / row["window"]["height"])))
    
    if x not in state:
        state[x] = {}
        
    if y not in state[x]:
        state[x][y] = 0
    
    state[x][y] += 1
    
    return state
    

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html
sdf = sdf.hopping_window(timedelta(minutes=5), timedelta(seconds=1)).reduce(heatmap, lambda row: heatmap({}, row)).final()

sdf = sdf.update(lambda row: print(row))
sdf = sdf.update(lambda row: print(message_context().timestamp.milliseconds))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)