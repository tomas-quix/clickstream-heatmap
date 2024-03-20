import os
from quixstreams import Application, State
from dotenv import load_dotenv
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
    
    x = str(math.floor(tile_grid_size * (row["mouse-coordinates"]["x"] / row["window"]["width"])))
    y = str(math.floor(tile_grid_size * (row["mouse-coordinates"]["y"] / row["window"]["height"])))
    
    if x not in state:
        state[x] = {}
        
    if y not in state[x]:
        state[x][y] = 0
    
    state[x][y] += 1
    
    return state
    

sdf = sdf.hopping_window(timedelta(minutes=5), timedelta(seconds=1)) \
        .reduce(heatmap, lambda row: heatmap({}, row))\
        .final()

sdf = sdf.update(lambda row: print(row))
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)