import os
from quixstreams import Application
import math
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

tile_grid_size = int(os.environ.get("grid_size", 50))

app = Application(consumer_group="transformation-v1.4", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# We calculate relative coordinates of mouse against window size. 
sdf["x-relative"] = sdf["mouse-coordinates"]["x"] / sdf["window"]["width"]
sdf["y-relative"] = sdf["mouse-coordinates"]["y"] / sdf["window"]["height"]

sdf["tile-coordinates"] = sdf.apply(lambda row: {
    "x": math.floor(tile_grid_size * row["x-relative"]),
    "y": math.floor(tile_grid_size * row["y-relative"])
})

sdf["grid-size"] = tile_grid_size

sdf = sdf.update(print)

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)