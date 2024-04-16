import os
from quixstreams import Application
import uuid
import json
from datetime import timedelta

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group=str(uuid.uuid4()), auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"])
#output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)


sdf = sdf.update(lambda row: print(json.dumps(row, indent=4)))

#sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)