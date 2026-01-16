"""Alpaca API Client Wrapper"""
import os
from typing import Optional, Dict, Any
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from dotenv import load_dotenv


class AlpacaClient:
    """Wrapper for Alpaca Trading API with mock support"""
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize Alpaca client
        
        Args:
            use_mock: If True, use mock data instead of real API calls
        """
        self.use_mock = use_mock
        
        if not use_mock:
            load_dotenv()
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
            
            if not api_key or not secret_key:
                raise ValueError("Missing Alpaca API credentials in .env file")
            
            self.client = TradingClient(api_key, secret_key, paper=True)
        else:
            self.client = None
            self._mock_account = {
                'cash': '100000.00',
                'portfolio_value': '100000.00',
                'buying_power': '100000.00',
                'equity': '100000.00'
            }
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Dictionary with account details
        """
        if self.use_mock:
            return self._mock_account.copy()
        
        account = self.client.get_account()
        return {
            'cash': str(account.cash),
            'portfolio_value': str(account.portfolio_value),
            'buying_power': str(account.buying_power),
            'equity': str(account.equity)
        }
    
    def get_positions(self) -> list:
        """
        Get all open positions
        
        Returns:
            List of positions
        """
        if self.use_mock:
            return []
        
        return self.client.get_all_positions()
    
    def is_market_open(self) -> bool:
        """
        Check if market is currently open
        
        Returns:
            True if market is open, False otherwise
        """
        if self.use_mock:
            return True
        
        clock = self.client.get_clock()
        return clock.is_open


def main():
    """Test the Alpaca client"""
    print("Testing Alpaca Client with MOCK data:")
    print("-" * 50)
    
    # Test with mock
    mock_client = AlpacaClient(use_mock=True)
    account = mock_client.get_account()
    
    print(f"Cash: ${account['cash']}")
    print(f"Portfolio Value: ${account['portfolio_value']}")
    print(f"Buying Power: ${account['buying_power']}")
    print(f"Market Open (mock): {mock_client.is_market_open()}")
    
    print("\n" + "=" * 50)
    print("Testing Alpaca Client with REAL API:")
    print("-" * 50)
    
    try:
        # Test with real API
        real_client = AlpacaClient(use_mock=False)
        account = real_client.get_account()
        
        print(f"Cash: ${account['cash']}")
        print(f"Portfolio Value: ${account['portfolio_value']}")
        print(f"Buying Power: ${account['buying_power']}")
        print(f"Positions: {len(real_client.get_positions())}")
        print(f"Market Open: {real_client.is_market_open()}")
        
        print("\n✅ Successfully connected to Alpaca Paper Trading!")
        
    except Exception as e:
        print(f"\n❌ Error connecting to Alpaca: {e}")
        print("Make sure your .env file has the correct API keys")


if __name__ == "__main__":
    main()