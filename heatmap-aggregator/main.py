import os
from quixstreams import Application, State
from dotenv import load_dotenv
import uuid
import math
import json
from datetime import timedelta

load_dotenv()

app = Application(consumer_group="heatmap-aggregator-v1.1", auto_offset_reset="latest", use_changelog_topics=True, loglevel="DEBUG")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"], key_serializer="json")

sdf = app.dataframe(input_topic)

sdf = sdf[["tile-coordinates", "relative_path", "grid-size"]]

sdf = sdf.group_by(lambda row: row, name="group_by") \
    .hopping_window(timedelta(minutes=5), 1000, 1000).count().final()

sdf = sdf.update(lambda row, key, _: print(f"{key}:{row}"), metadata=True)
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)