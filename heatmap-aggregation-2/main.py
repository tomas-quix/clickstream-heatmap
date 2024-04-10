import os
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()
import math
import json
from datetime import timedelta

app = Application.Quix("heatmap-v2", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

grid_size = 4

sdf = app.dataframe(input_topic)

sdf = sdf[sdf["type"] == "mousemove"]


sdf = sdf[["window", "mouse-coordinates"]]

sdf["mouse-relative-x"] = sdf["mouse-coordinates"]["x"] / sdf["window"]["width"]
sdf["mouse-relative-y"] = sdf["mouse-coordinates"]["y"] / sdf["window"]["height"]

sdf["tile-x"] = sdf["mouse-relative-x"] * grid_size
sdf["tile-y"] = sdf["mouse-relative-y"] * grid_size

sdf = sdf.apply(lambda row: {
    "tile-x" : math.floor(row["tile-x"]),
    "tile-y" : math.floor(row["tile-y"]),
})

def heatmap(state:dict, row: dict):
    
    tile_x = str(row["tile-x"])
    tile_y = str(row["tile-y"])
    
    if tile_x not in state:
        state[tile_x] = {}
    
    if tile_y not in state[tile_x]:
        state[tile_x][tile_y] = 0
        
    state[tile_x][tile_y] += 1
    
    return state

sdf = sdf.hopping_window(timedelta(minutes=1), 250) \
    .reduce(heatmap, lambda row: heatmap({}, row)).final()
    
sdf["grid-size"] = grid_size


sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)