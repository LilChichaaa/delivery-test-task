import redis.asyncio as aioredis
import requests

from typing import Union
from .. import settings

redis_client = aioredis.Redis.from_url(settings.REDIS_URL)
