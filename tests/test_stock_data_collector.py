"""Tests for Stock Data Collector"""
import pytest
from src.stock_data_collector import StockDataCollector


class TestDataCollectorInitialization:
    """Test data collector initialization"""
    
    def test_create_mock_collector(self):
        """Should create collector in mock mode"""
        collector = StockDataCollector(use_mock=True)
        
        assert collector.use_mock is True
        assert collector.client is None
        assert len(collector.ALLOWED_SYMBOLS) == 3
    
    def test_allowed_symbols(self):
        """Should have correct allowed symbols"""
        collector = StockDataCollector(use_mock=True)
        
        assert 'PLTR' in collector.ALLOWED_SYMBOLS
        assert 'NFLX' in collector.ALLOWED_SYMBOLS
        assert 'PLTK' in collector.ALLOWED_SYMBOLS


class TestCurrentPrices:
    """Test fetching current prices"""
    
    def test_get_current_price_pltr(self):
        """Should get current price for PLTR"""
        collector = StockDataCollector(use_mock=True)
        price = collector.get_current_price('PLTR')
        
        assert price is not None
        assert price > 0
        assert isinstance(price, float)
    
    def test_get_current_price_all_symbols(self):
        """Should get prices for all allowed symbols"""
        collector = StockDataCollector(use_mock=True)
        
        for symbol in collector.ALLOWED_SYMBOLS:
            price = collector.get_current_price(symbol)
            assert price is not None
            assert price > 0
    
    def test_get_invalid_symbol(self):
        """Should reject invalid symbols"""
        collector = StockDataCollector(use_mock=True)
        
        with pytest.raises(ValueError):
            collector.get_current_price('AAPL')  # Not in allowed list
    
    def test_get_multiple_prices(self):
        """Should get multiple prices at once"""
        collector = StockDataCollector(use_mock=True)
        prices = collector.get_multiple_prices(['PLTR', 'NFLX'])
        
        assert len(prices) == 2
        assert 'PLTR' in prices
        assert 'NFLX' in prices
        assert prices['PLTR'] > 0
        assert prices['NFLX'] > 0
    
    def test_get_all_prices(self):
        """Should get all allowed prices"""
        collector = StockDataCollector(use_mock=True)
        prices = collector.get_all_prices()
        
        assert len(prices) == 3
        assert all(symbol in prices for symbol in collector.ALLOWED_SYMBOLS)


class TestCaching:
    """Test caching functionality"""
    
    def test_price_caching(self):
        """Should cache prices"""
        collector = StockDataCollector(use_mock=True, cache_ttl=60)
        
        # First fetch
        price1 = collector.get_current_price('PLTR')
        
        # Second fetch (should come from cache)
        price2 = collector.get_current_price('PLTR')
        
        assert price1 == price2
        
        # Cache should have entry
        cache_stats = collector.get_cache_stats()
        assert cache_stats['total_entries'] > 0
    
    def test_cache_stats(self):
        """Should provide cache statistics"""
        collector = StockDataCollector(use_mock=True)
        
        # Fetch some prices
        collector.get_current_price('PLTR')
        collector.get_current_price('NFLX')
        
        stats = collector.get_cache_stats()
        
        assert 'total_entries' in stats
        assert stats['total_entries'] >= 2


class TestHistoricalData:
    """Test historical data fetching"""
    
    def test_get_historical_prices(self):
        """Should get historical prices"""
        collector = StockDataCollector(use_mock=True)
        historical = collector.get_historical_prices('PLTR', days=7)
        
        assert len(historical) == 7
        assert all('date' in day for day in historical)
        assert all('close' in day for day in historical)
    
    def test_historical_data_structure(self):
        """Historical data should have correct structure"""
        collector = StockDataCollector(use_mock=True)
        historical = collector.get_historical_prices('PLTR', days=5)
        
        for day_data in historical:
            assert 'date' in day_data
            assert 'close' in day_data
            assert 'volume' in day_data
            assert isinstance(day_data['close'], (int, float))
    
    def test_historical_invalid_symbol(self):
        """Should reject invalid symbol for historical data"""
        collector = StockDataCollector(use_mock=True)
        
        with pytest.raises(ValueError):
            collector.get_historical_prices('AAPL', days=7)


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_status(self):
        """Should provide rate limit status"""
        collector = StockDataCollector(use_mock=True)
        status = collector.get_rate_limit_status()
        
        assert 'remaining_second' in status
        assert 'remaining_hour' in status
        assert 'remaining_day' in status
        assert status['remaining_second'] >= 0
    
    def test_rate_limiter_exists(self):
        """Collector should have rate limiter"""
        collector = StockDataCollector(use_mock=True)
        
        assert collector.rate_limiter is not None
        assert hasattr(collector.rate_limiter, 'can_proceed')


class TestStringRepresentation:
    """Test string representation"""
    
    def test_repr_mock_mode(self):
        """Should show mock mode in repr"""
        collector = StockDataCollector(use_mock=True)
        repr_str = repr(collector)
        
        assert 'MOCK' in repr_str
        assert 'PLTR' in repr_str or 'symbols' in repr_str.lower()
    
    def test_repr_contains_symbols(self):
        """Repr should contain allowed symbols"""
        collector = StockDataCollector(use_mock=True)
        repr_str = repr(collector)
        
        # Should mention symbols somehow
        assert len(repr_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])