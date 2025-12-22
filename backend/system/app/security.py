from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

SEARCH_RATE_LIMIT = "60/minute"
PRODUCT_RATE_LIMIT = "100/minute"
BATCH_PRODUCTS_RATE_LIMIT = "30/minute"

