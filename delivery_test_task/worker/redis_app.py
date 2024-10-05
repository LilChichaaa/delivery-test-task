import redis
import requests

from typing import Union
from .. import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)
