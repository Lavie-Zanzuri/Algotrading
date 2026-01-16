"""Rate Limiter - Limits API calls per second/hour/day"""
import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Rate limiter to prevent excessive API calls.
    
    Tracks requests per second, hour, and day and blocks when limits are reached.
    This is crucial for:
    - Preventing excessive charges from paid APIs
    - Complying with API provider limits
    - Protecting against bugs that cause infinite loops
    """
    
    def __init__(
        self,
        per_second: int = 10,
        per_hour: int = 500,
        per_day: int = 5000
    ):
        """
        Initialize rate limiter with limits
        
        Args:
            per_second: Maximum requests per second (default: 10)
            per_hour: Maximum requests per hour (default: 500)
            per_day: Maximum requests per day (default: 5000)
        """
        self.per_second_limit = per_second
        self.per_hour_limit = per_hour
        self.per_day_limit = per_day
        
        # Store timestamps of requests
        # Using deque for efficient removal of old entries
        self.second_requests = deque()
        self.hour_requests = deque()
        self.day_requests = deque()
        
        self._last_limit_hit: Optional[str] = None
    
    def _clean_old_requests(self):
        """Remove requests that are outside the time windows"""
        current_time = time.time()
        
        # Clean requests older than 1 second
        while self.second_requests and current_time - self.second_requests[0] > 1:
            self.second_requests.popleft()
        
        # Clean requests older than 1 hour
        while self.hour_requests and current_time - self.hour_requests[0] > 3600:
            self.hour_requests.popleft()
        
        # Clean requests older than 1 day
        while self.day_requests and current_time - self.day_requests[0] > 86400:
            self.day_requests.popleft()
    
    def can_proceed(self) -> bool:
        """
        Check if a new request can proceed
        
        Returns:
            True if request can proceed, False if rate limit reached
        """
        self._clean_old_requests()
        
        # Check all limits
        if len(self.second_requests) >= self.per_second_limit:
            self._last_limit_hit = 'second'
            return False
        
        if len(self.hour_requests) >= self.per_hour_limit:
            self._last_limit_hit = 'hour'
            return False
        
        if len(self.day_requests) >= self.per_day_limit:
            self._last_limit_hit = 'day'
            return False
        
        # All limits OK - record the request
        current_time = time.time()
        self.second_requests.append(current_time)
        self.hour_requests.append(current_time)
        self.day_requests.append(current_time)
        
        self._last_limit_hit = None
        return True
    
    def get_request_count(self, period: str) -> int:
        """
        Get number of requests in the given period
        
        Args:
            period: 'second', 'hour', or 'day'
        
        Returns:
            Number of requests in that period
        """
        self._clean_old_requests()
        
        if period == 'second':
            return len(self.second_requests)
        elif period == 'hour':
            return len(self.hour_requests)
        elif period == 'day':
            return len(self.day_requests)
        else:
            raise ValueError(f"Invalid period: {period}")
    
    def get_remaining(self, period: str) -> int:
        """
        Get remaining requests for the given period
        
        Args:
            period: 'second', 'hour', or 'day'
        
        Returns:
            Number of remaining requests
        """
        self._clean_old_requests()
        
        if period == 'second':
            return max(0, self.per_second_limit - len(self.second_requests))
        elif period == 'hour':
            return max(0, self.per_hour_limit - len(self.hour_requests))
        elif period == 'day':
            return max(0, self.per_day_limit - len(self.day_requests))
        else:
            raise ValueError(f"Invalid period: {period}")
    
    def get_wait_time(self) -> float:
        """
        Get how long to wait before next request can proceed
        
        Returns:
            Wait time in seconds, or 0 if can proceed now
        """
        self._clean_old_requests()
        
        if self.can_proceed():
            return 0.0
        
        # Find the oldest request in the limiting period
        current_time = time.time()
        
        if self._last_limit_hit == 'second' and self.second_requests:
            oldest = self.second_requests[0]
            return max(0, 1.0 - (current_time - oldest))
        
        if self._last_limit_hit == 'hour' and self.hour_requests:
            oldest = self.hour_requests[0]
            return max(0, 3600.0 - (current_time - oldest))
        
        if self._last_limit_hit == 'day' and self.day_requests:
            oldest = self.day_requests[0]
            return max(0, 86400.0 - (current_time - oldest))
        
        return 0.0
    
    def which_limit_hit(self) -> Optional[str]:
        """
        Get which limit was hit on last can_proceed() call
        
        Returns:
            'second', 'hour', 'day', or None if no limit hit
        """
        return self._last_limit_hit
    
    def reset(self):
        """Reset all counters (useful for testing)"""
        self.second_requests.clear()
        self.hour_requests.clear()
        self.day_requests.clear()
        self._last_limit_hit = None
    
    def __repr__(self) -> str:
        """String representation"""
        self._clean_old_requests()
        return (
            f"RateLimiter("
            f"second: {len(self.second_requests)}/{self.per_second_limit}, "
            f"hour: {len(self.hour_requests)}/{self.per_hour_limit}, "
            f"day: {len(self.day_requests)}/{self.per_day_limit})"
        )


def main():
    """Demo of Rate Limiter"""
    print("Rate Limiter Demo")
    print("=" * 50)
    
    # Create a strict limiter
    limiter = RateLimiter(per_second=3, per_hour=10, per_day=50)
    print(f"Limits: 3/sec, 10/hour, 50/day")
    print(limiter)
    print()
    
    # Make some requests
    print("Making 5 rapid requests...")
    for i in range(5):
        if limiter.can_proceed():
            print(f"  Request {i+1}: ✅ Allowed")
        else:
            print(f"  Request {i+1}: ❌ Blocked ({limiter.which_limit_hit()} limit hit)")
            wait = limiter.get_wait_time()
            print(f"    Need to wait: {wait:.2f} seconds")
    
    print()
    print(f"Current state: {limiter}")
    print(f"Remaining this second: {limiter.get_remaining('second')}")
    print(f"Remaining this hour: {limiter.get_remaining('hour')}")
    print(f"Remaining today: {limiter.get_remaining('day')}")
    print()
    
    # Wait and try again
    print("Waiting 1.5 seconds...")
    time.sleep(1.5)
    print()
    
    print("Trying again after waiting...")
    if limiter.can_proceed():
        print("  ✅ Allowed - second limit reset!")
    else:
        print("  ❌ Still blocked")
    
    print()
    print(f"Final state: {limiter}")


if __name__ == "__main__":
    main()