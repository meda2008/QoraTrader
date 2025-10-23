# This file provides a service layer interface to the market data functionality
# The actual implementation is in src/market_data/service.py

from src.market_data.service import market_data_service, MarketDataService

# Import the existing market data service to make it available in the services module
market_data_service_instance = MarketDataService()

# You can extend or wrap the functionality here if needed
# For now, we'll simply make the existing implementation available