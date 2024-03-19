import logging
from io import BytesIO
from pathlib import PurePath
from typing import Union, Any, Literal, Optional, Dict

from quixstreams.connectors.sinks.base.sinks import BaseBatchingSink
from quixstreams.connectors.sinks.base.batching import Batch

import os
from supabase import create_client, Client

logger = logging.getLogger("quixstreams")


class Supabase(BaseBatchingSink):
    def __init__(
        self,
        supabase_url,
        supabase_key,
        batch_max_messages: int,
        broker_address:str,
        topic: str,
        consumer_extra_config: Optional[dict] = None,
        batch_max_interval_seconds: float = 0.0,
        consumer_group: str = "quixstreams-supabase-sink-default",
    ):
       
        super().__init__(
            
            consumer_group=consumer_group,
            batch_max_messages=batch_max_messages,
            batch_max_interval_seconds=batch_max_interval_seconds,
        )

        self._supabase: Client = create_client(supabase_key, supabase_url)
        

    def flush(self, batch: Batch):
        print(batch)

