"""Stock Data Collector - Fetch prices from Alpaca with caching"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

from src.cache import SimpleCache
from src.rate_limiter import RateLimiter

load_dotenv()


class StockDataCollector:
    """
    Collects stock price data from Alpaca with caching and rate limiting
    
    Features:
    - Real-time and historical data
    - Automatic caching to reduce API calls
    - Rate limiting to prevent excessive usage
    - Mock mode for development
    """
    
    # Our 3 allowed stocks
    ALLOWED_SYMBOLS = ['PLTR', 'NFLX', 'PLTK']
    
    def __init__(
        self, 
        use_mock: bool = False,
        cache_ttl: int = 300,  # 5 minutes default
        cache_file: Optional[str] = '.cache/stock_prices.json'
    ):
        """
        Initialize data collector
        
        Args:
            use_mock: Use mock data instead of real API
            cache_ttl: Cache time-to-live in seconds
            cache_file: File path for cache persistence
        """
        self.use_mock = use_mock
        
        # Initialize cache
        self.cache = SimpleCache(ttl_seconds=cache_ttl, cache_file=cache_file)
        
        # Initialize rate limiter (conservative limits)
        self.rate_limiter = RateLimiter(
            per_second=2,    # 2 requests per second
            per_hour=100,    # 100 requests per hour
            per_day=1000     # 1000 requests per day
        )
        
        # Initialize Alpaca client (if not mock)
        if not use_mock:
            api_key = os.getenv('ALPACA_API_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
            
            if not api_key or not secret_key:
                raise ValueError("Alpaca API credentials not found in .env")
            
            self.client = StockHistoricalDataClient(api_key, secret_key)
        else:
            self.client = None
            self._mock_prices = {
                'PLTR': 50.25,
                'NFLX': 485.50,
                'PLTK': 8.75
            }
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Stock symbol (must be in ALLOWED_SYMBOLS)
        
        Returns:
            Current price or None if error
        """
        # Validate symbol
        if symbol not in self.ALLOWED_SYMBOLS:
            raise ValueError(f"Symbol {symbol} not allowed. Use: {self.ALLOWED_SYMBOLS}")
        
        # Check cache first
        cache_key = f"current_price_{symbol}"
        cached_price = self.cache.get(cache_key)
        if cached_price is not None:
            return cached_price
        
        # Mock mode
        if self.use_mock:
            price = self._mock_prices.get(symbol, 0.0)
            self.cache.set(cache_key, price)
            return price
        
        # Real API call - check rate limit
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.get_wait_time()
            raise RuntimeError(
                f"Rate limit exceeded. Wait {wait_time:.1f}s. "
                f"Limit hit: {self.rate_limiter.which_limit_hit()}"
            )
        
        try:
            # Get latest bar (1 minute timeframe)
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                limit=1
            )
            
            bars = self.client.get_stock_bars(request)
            
            if symbol in bars.data and len(bars.data[symbol]) > 0:
                latest_bar = bars.data[symbol][0]
                price = float(latest_bar.close)
                
                # Cache the price
                self.cache.set(cache_key, price)
                
                return price
            
            return None
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbol to price
        """
        prices = {}
        for symbol in symbols:
            try:
                prices[symbol] = self.get_current_price(symbol)
            except Exception as e:
                print(f"Error getting price for {symbol}: {e}")
                prices[symbol] = None
        
        return prices
    
    def get_all_prices(self) -> Dict[str, Optional[float]]:
        """
        Get current prices for all allowed symbols
        
        Returns:
            Dictionary mapping symbol to price
        """
        return self.get_multiple_prices(self.ALLOWED_SYMBOLS)
    
    def get_historical_prices(
        self, 
        symbol: str, 
        days: int = 7
    ) -> List[Dict[str, any]]:
        """
        Get historical prices for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
        
        Returns:
            List of price data dictionaries
        """
        # Validate symbol
        if symbol not in self.ALLOWED_SYMBOLS:
            raise ValueError(f"Symbol {symbol} not allowed")
        
        # Check cache
        cache_key = f"historical_{symbol}_{days}d"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Mock mode
        if self.use_mock:
            base_price = self._mock_prices.get(symbol, 50.0)
            mock_data = []
            
            for i in range(days):
                date = datetime.now() - timedelta(days=days-i)
                # Simulate some price variation
                price = base_price + (i - days/2) * 0.5
                mock_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'close': round(price, 2),
                    'volume': 1000000 + i * 10000
                })
            
            self.cache.set(cache_key, mock_data, ttl=3600)  # Cache for 1 hour
            return mock_data
        
        # Real API call - check rate limit
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.get_wait_time()
            raise RuntimeError(f"Rate limit exceeded. Wait {wait_time:.1f}s")
        
        try:
            # Get historical bars
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.client.get_stock_bars(request)
            
            historical_data = []
            if symbol in bars.data:
                for bar in bars.data[symbol]:
                    historical_data.append({
                        'date': bar.timestamp.strftime('%Y-%m-%d'),
                        'close': float(bar.close),
                        'volume': int(bar.volume)
                    })
            
            # Cache for 1 hour (historical data doesn't change)
            self.cache.set(cache_key, historical_data, ttl=3600)
            
            return historical_data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def get_rate_limit_status(self) -> Dict:
        """Get rate limiter status"""
        return {
            'remaining_second': self.rate_limiter.get_remaining('second'),
            'remaining_hour': self.rate_limiter.get_remaining('hour'),
            'remaining_day': self.rate_limiter.get_remaining('day')
        }
    
    def __repr__(self) -> str:
        """String representation"""
        mode = "MOCK" if self.use_mock else "LIVE"
        return f"StockDataCollector(mode={mode}, symbols={self.ALLOWED_SYMBOLS})"


def main():
    """Demo of Stock Data Collector"""
    print("=" * 70)
    print("STOCK DATA COLLECTOR DEMO")
    print("=" * 70)
    print()
    
    # Create collector in mock mode
    print("Creating collector in MOCK mode (no API needed)...")
    collector = StockDataCollector(use_mock=True)
    print(f"✅ {collector}")
    print()
    
    # Get current prices
    print("Fetching current prices for all stocks...")
    print("-" * 70)
    prices = collector.get_all_prices()
    
    for symbol, price in prices.items():
        if price:
            print(f"  {symbol}: ${price:.2f}")
        else:
            print(f"  {symbol}: Error fetching price")
    print()
    
    # Get historical data
    print("Fetching 7-day historical data for PLTR...")
    print("-" * 70)
    historical = collector.get_historical_prices('PLTR', days=7)
    
    if historical:
        for day_data in historical:
            print(f"  {day_data['date']}: ${day_data['close']:.2f}")
    print()
    
    # Show cache stats
    print("Cache Statistics:")
    print("-" * 70)
    stats = collector.get_cache_stats()
    print(f"  Cached entries: {stats['total_entries']}")
    print(f"  TTL: {stats['ttl_seconds']}s")
    print()
    
    # Show rate limit status
    print("Rate Limit Status:")
    print("-" * 70)
    status = collector.get_rate_limit_status()
    print(f"  Remaining this second: {status['remaining_second']}")
    print(f"  Remaining this hour: {status['remaining_hour']}")
    print(f"  Remaining this day: {status['remaining_day']}")
    print()
    
    # Test caching by fetching again
    print("Fetching PLTR price again (should come from cache)...")
    print("-" * 70)
    price_again = collector.get_current_price('PLTR')
    print(f"  PLTR: ${price_again:.2f} (from cache!)")
    print()
    
    print("=" * 70)
    print("✅ DEMO COMPLETED")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✅ Mock mode for development")
    print("  ✅ Automatic caching")
    print("  ✅ Rate limiting")
    print("  ✅ Multiple stock support")
    print("  ✅ Historical data")
    print()
    print("To use with real Alpaca data:")
    print("  1. Add ALPACA_API_KEY and ALPACA_SECRET_KEY to .env")
    print("  2. Set use_mock=False")
    print()


if __name__ == "__main__":
    main()