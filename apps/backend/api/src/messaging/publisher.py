from messaging_utils.core.connection_params import messaging_params
from messaging_utils.messaging.publishers import Publisher

params = messaging_params
exchange_info = messaging_params.pop("exchange")

publisher = Publisher(params=params, exchange_info=exchange_info)
