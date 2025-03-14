import os
import json
import redis
from ..logs.logs import logger
from ..database.db import DbInstance
from sqlalchemy.orm import sessionmaker

logger = logger.getLogger("RATES")

class RatesService:
    def __init__(self, db: DbInstance, test:bool=False):
        self.db = db
        self.test = test
        self.redis_host = os.environ.get("REDIS_HOST", "project_redis") 
        self.redis_port = int(os.environ.get("REDIS_PORT", 6379))
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port)

    def get_rates(self, account_id:int=None, session:sessionmaker=None) -> dict:
        """
        Get the rates for the account.
        Args:
            account_id: Id of the account to get the rates.
        Returns:
            rates (dict): Rates for the account.
        """
        if not self.test:
            session = self.db.get_session()

        cache_key = f"rates:{account_id}"
        
        if self.redis_client.exists(cache_key):
            cached_rates = self.redis_client.get(cache_key)
            return json.loads(cached_rates.decode('utf-8'))

        rates = self.db.get_rates(account_id, session)
        self.redis_client.set(cache_key, json.dumps(rates))

        self.db.close_session(session)
        logger.info(f"Rates for Account ID #{account_id}: {rates}")

        return rates
    
    def create_update_rates(self, account_id:int=None, national_rate:int=None, international_rate:int=None, session:sessionmaker=None) -> dict:
        """
        Update the rates for the account.
        Args:
            account_id: Id of the account to update the rates.
            national_rate: New national rate.
            international_rate: New international rate.
            update_create: Defines if the rates will be updated or created.
        Returns:
            rates (dict): Updated rates for the account.
        """
        if not self.test:
            session = self.db.get_session()
        
        data = {
            self.db.get_shipment_type_id("NATIONAL"): national_rate, 
            self.db.get_shipment_type_id("INTERNATIONAL"): international_rate
            }

        for key, value in data.items():
            if value:
                self.db.create_update_rates(account_id, key, value, session)
        
        rates = self.db.get_rates(account_id, session)
        cache_key = f"rates:{account_id}"
        self.redis_client.set(cache_key, json.dumps(rates), ex=3600)

        self.db.close_session(session)
        logger.info(f"Rates for Account ID #{account_id}: {rates}")

        return rates