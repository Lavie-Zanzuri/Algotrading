"""Tests for Rate Limiter"""
import pytest
import time
from src.rate_limiter import RateLimiter


class TestRateLimiterInitialization:
    """Test rate limiter initialization"""
    
    def test_initialize_with_default_limits(self):
        """Should initialize with reasonable default limits"""
        limiter = RateLimiter()
        assert limiter.per_second_limit > 0
        assert limiter.per_hour_limit > 0
        assert limiter.per_day_limit > 0
    
    def test_initialize_with_custom_limits(self):
        """Should accept custom limits"""
        limiter = RateLimiter(per_second=5, per_hour=100, per_day=500)
        assert limiter.per_second_limit == 5
        assert limiter.per_hour_limit == 100
        assert limiter.per_day_limit == 500


class TestRateLimiterBasicFunctionality:
    """Test basic rate limiting functionality"""
    
    def test_allow_first_request(self):
        """First request should always be allowed"""
        limiter = RateLimiter(per_second=10, per_hour=100, per_day=1000)
        assert limiter.can_proceed() is True
    
    def test_track_request(self):
        """Should track requests when called"""
        limiter = RateLimiter(per_second=10, per_hour=100, per_day=1000)
        
        # Make 3 requests
        limiter.can_proceed()
        limiter.can_proceed()
        limiter.can_proceed()
        
        # Should have 3 requests tracked
        assert limiter.get_request_count('second') == 3
        assert limiter.get_request_count('hour') == 3
        assert limiter.get_request_count('day') == 3


class TestPerSecondLimit:
    """Test per-second rate limiting"""
    
    def test_respect_per_second_limit(self):
        """Should block when per-second limit reached"""
        limiter = RateLimiter(per_second=3, per_hour=100, per_day=1000)
        
        # First 3 should succeed
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        
        # 4th should fail (within same second)
        assert limiter.can_proceed() is False
    
    def test_reset_after_second(self):
        """Should reset after a second passes"""
        limiter = RateLimiter(per_second=2, per_hour=100, per_day=1000)
        
        # Use up the limit
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is True
        assert limiter.can_proceed() is False  # Blocked
        
        # Wait for new second
        time.sleep(1.1)
        
        # Should work again
        assert limiter.can_proceed() is True


class TestPerHourLimit:
    """Test per-hour rate limiting"""
    
    def test_respect_per_hour_limit(self):
        """Should block when per-hour limit reached"""
        limiter = RateLimiter(per_second=100, per_hour=5, per_day=1000)
        
        # First 5 should succeed
        for i in range(5):
            assert limiter.can_proceed() is True
        
        # 6th should fail
        assert limiter.can_proceed() is False
    
    def test_hour_limit_independent_of_second(self):
        """Hour limit should work even if second limit is higher"""
        limiter = RateLimiter(per_second=10, per_hour=3, per_day=1000)
        
        # Spread over multiple seconds but same hour
        assert limiter.can_proceed() is True
        time.sleep(0.5)
        assert limiter.can_proceed() is True
        time.sleep(0.5)
        assert limiter.can_proceed() is True
        time.sleep(0.5)
        
        # Should still block due to hour limit
        assert limiter.can_proceed() is False


class TestPerDayLimit:
    """Test per-day rate limiting"""
    
    def test_respect_per_day_limit(self):
        """Should block when per-day limit reached"""
        limiter = RateLimiter(per_second=100, per_hour=100, per_day=5)
        
        # First 5 should succeed
        for i in range(5):
            assert limiter.can_proceed() is True
        
        # 6th should fail
        assert limiter.can_proceed() is False


class TestGetRemainingRequests:
    """Test getting remaining request counts"""
    
    def test_get_remaining_per_second(self):
        """Should return correct remaining requests per second"""
        limiter = RateLimiter(per_second=5, per_hour=100, per_day=1000)
        
        assert limiter.get_remaining('second') == 5
        
        limiter.can_proceed()
        assert limiter.get_remaining('second') == 4
        
        limiter.can_proceed()
        assert limiter.get_remaining('second') == 3
    
    def test_get_remaining_per_hour(self):
        """Should return correct remaining requests per hour"""
        limiter = RateLimiter(per_second=100, per_hour=10, per_day=1000)
        
        assert limiter.get_remaining('hour') == 10
        
        for i in range(3):
            limiter.can_proceed()
        
        assert limiter.get_remaining('hour') == 7
    
    def test_get_remaining_per_day(self):
        """Should return correct remaining requests per day"""
        limiter = RateLimiter(per_second=100, per_hour=100, per_day=20)
        
        assert limiter.get_remaining('day') == 20
        
        for i in range(5):
            limiter.can_proceed()
        
        assert limiter.get_remaining('day') == 15


class TestResetCounters:
    """Test resetting counters"""
    
    def test_reset_all_counters(self):
        """Should reset all counters"""
        limiter = RateLimiter(per_second=10, per_hour=100, per_day=1000)
        
        # Make some requests
        for i in range(5):
            limiter.can_proceed()
        
        assert limiter.get_request_count('second') == 5
        
        # Reset
        limiter.reset()
        
        assert limiter.get_request_count('second') == 0
        assert limiter.get_request_count('hour') == 0
        assert limiter.get_request_count('day') == 0


class TestGracefulHandling:
    """Test graceful handling of rate limit violations"""
    
    def test_get_wait_time(self):
        """Should return how long to wait before next request"""
        limiter = RateLimiter(per_second=2, per_hour=100, per_day=1000)
        
        # Use up limit
        limiter.can_proceed()
        limiter.can_proceed()
        
        # Should tell us to wait
        wait_time = limiter.get_wait_time()
        assert wait_time > 0
        assert wait_time <= 1.0  # Should be less than a second
    
    def test_which_limit_hit(self):
        """Should tell us which limit was hit"""
        limiter = RateLimiter(per_second=2, per_hour=100, per_day=1000)
        
        limiter.can_proceed()
        limiter.can_proceed()
        limiter.can_proceed()  # This one should fail and hit the limit
        
        # Should indicate second limit was hit
        assert limiter.which_limit_hit() == 'second'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])