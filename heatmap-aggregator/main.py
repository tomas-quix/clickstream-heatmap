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

# We are only interested in mousemove events.
sdf = sdf[sdf["type"] == "mousemove"]

tile_grid_size = 10

def heatmap(state: dict, row: dict):
    x = str(row["x"])
    y = str(row["y"])
    
    # We store grid in dictionary of dictionaries.
    if x not in state:
        state[x] = {}
        
    if y not in state[x]:
        state[x][y] = 0
    
    state[x][y] += 1
    
    return state

# We calculate relative coordinates of mouse against window size. 
sdf["x-relative"] = sdf["mouse-coordinates"]["x"] / sdf["window"]["width"]
sdf["y-relative"] = sdf["mouse-coordinates"]["y"] / sdf["window"]["height"]

sdf["tile-coordinates"] = sdf.apply(lambda row: {
    "x": math.floor(tile_grid_size * row["x-relative"]),
    "y": math.floor(tile_grid_size * row["y-relative"])
})

# We calculate hopping window of 5 minutes with step every second.
sdf = sdf.apply(lambda row: row["tile-coordinates"]) \
        .hopping_window(timedelta(minutes=5), timedelta(seconds=1)) \
        .reduce(heatmap, lambda row: heatmap({}, row))\
        .final()

sdf = sdf.update(lambda row: print(row))
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)