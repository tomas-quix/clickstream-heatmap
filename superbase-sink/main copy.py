from quixstreams import Application

import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

from sink import Supabase

app = Application.Quix()
topic = app.topic(name="qts__purchase_events")


# Configuring the sink app
sink = Supabase(
    "https://kwrouqntpujhrbjttvdc.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3cm91cW50cHVqaHJianR0dmRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA4NDc4NTEsImV4cCI6MjAyNjQyMzg1MX0.LRVeQ8sKheerkBQEtg05iqH4hq_osOTD2MtLwJ01SPs",
    batch_max_messages=100000,    
    broker_address=app._broker_address,
    topic=topic.name,
    consumer_extra_config=app._consumer_extra_config
)

# Running the app
sink.run()
