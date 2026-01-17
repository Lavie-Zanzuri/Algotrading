"""Simple Caching System for API Calls"""
import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict


class SimpleCache:
    """
    Simple in-memory cache with optional disk persistence.
    
    Features:
    - TTL (Time To Live) support
    - Automatic expiration of old entries
    - Optional file-based persistence
    - Key hashing for complex inputs
    """
    
    def __init__(self, ttl_seconds: int = 3600, cache_file: Optional[str] = None):
        """
        Initialize cache
        
        Args:
            ttl_seconds: Time to live for cached entries (default: 1 hour)
            cache_file: Optional file path for persistence
        """
        self.ttl_seconds = ttl_seconds
        self.cache_file = cache_file
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Load from file if exists
        if cache_file:
            self._load_from_file()
    
    def _make_key(self, key: Any) -> str:
        """
        Convert any key to a string hash
        
        Args:
            key: Any hashable object (string, tuple, etc.)
        
        Returns:
            String hash of the key
        """
        if isinstance(key, str):
            return key
        
        # Convert to JSON string and hash it
        key_str = json.dumps(key, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._make_key(key)
        
        if cache_key not in self._cache:
            return None
        
        entry = self._cache[cache_key]
        
        # Check if expired
        if time.time() > entry['expires_at']:
            del self._cache[cache_key]
            return None
        
        return entry['value']
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL (overrides default)
        """
        cache_key = self._make_key(key)
        ttl_to_use = ttl if ttl is not None else self.ttl_seconds
        
        self._cache[cache_key] = {
            'value': value,
            'expires_at': time.time() + ttl_to_use,
            'created_at': time.time()
        }
        
        # Save to file if configured
        if self.cache_file:
            self._save_to_file()
    
    def has(self, key: Any) -> bool:
        """
        Check if key exists in cache (and not expired)
        
        Args:
            key: Cache key
        
        Returns:
            True if key exists and not expired
        """
        return self.get(key) is not None
    
    def delete(self, key: Any):
        """
        Delete key from cache
        
        Args:
            key: Cache key
        """
        cache_key = self._make_key(key)
        if cache_key in self._cache:
            del self._cache[cache_key]
            
            if self.cache_file:
                self._save_to_file()
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        
        if self.cache_file:
            self._save_to_file()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys and self.cache_file:
            self._save_to_file()
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        self.cleanup_expired()
        
        return {
            'total_entries': len(self._cache),
            'ttl_seconds': self.ttl_seconds,
            'cache_file': self.cache_file,
            'memory_size_bytes': len(json.dumps(self._cache))
        }
    
    def _save_to_file(self):
        """Save cache to file"""
        if not self.cache_file:
            return
        
        cache_path = Path(self.cache_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(self._cache, f, indent=2)
    
    def _load_from_file(self):
        """Load cache from file"""
        if not self.cache_file:
            return
        
        cache_path = Path(self.cache_file)
        if not cache_path.exists():
            return
        
        try:
            with open(cache_path, 'r') as f:
                self._cache = json.load(f)
            
            # Clean up expired entries after loading
            self.cleanup_expired()
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, start fresh
            self._cache = {}
    
    def __repr__(self) -> str:
        """String representation"""
        stats = self.get_stats()
        return f"SimpleCache(entries={stats['total_entries']}, ttl={stats['ttl_seconds']}s)"


def main():
    """Demo of caching system"""
    print("Caching System Demo")
    print("=" * 50)
    
    # Create cache with 5 second TTL for demo
    cache = SimpleCache(ttl_seconds=5, cache_file='.cache/demo_cache.json')
    print(f"Created: {cache}")
    print()
    
    # Store some data
    print("Storing data...")
    cache.set('PLTR_price_2024-01-15', 50.25)
    cache.set('NFLX_price_2024-01-15', 485.50)
    cache.set(('PLTR', '2024-01-15', 'close'), 50.25)  # Complex key
    print("✅ Stored 3 items")
    print(f"Stats: {cache.get_stats()}")
    print()
    
    # Retrieve data
    print("Retrieving data...")
    price = cache.get('PLTR_price_2024-01-15')
    print(f"  PLTR price: ${price}")
    
    complex_price = cache.get(('PLTR', '2024-01-15', 'close'))
    print(f"  PLTR (complex key): ${complex_price}")
    print()
    
    # Check existence
    print("Checking existence...")
    print(f"  Has 'PLTR_price_2024-01-15': {cache.has('PLTR_price_2024-01-15')}")
    print(f"  Has 'AAPL_price': {cache.has('AAPL_price')}")
    print()
    
    # Wait for expiration
    print("Waiting 6 seconds for TTL to expire...")
    time.sleep(6)
    print()
    
    # Try to retrieve expired data
    print("Trying to retrieve expired data...")
    expired_price = cache.get('PLTR_price_2024-01-15')
    print(f"  Result: {expired_price} (expired!)")
    print()
    
    # Demonstrate persistence
    print("Adding new data and saving to file...")
    cache.set('TSLA_price', 250.00)
    print(f"  Saved to: {cache.cache_file}")
    print()
    
    # Load from file in new cache instance
    print("Creating new cache instance and loading from file...")
    cache2 = SimpleCache(ttl_seconds=5, cache_file='.cache/demo_cache.json')
    tsla_price = cache2.get('TSLA_price')
    print(f"  Loaded TSLA price: ${tsla_price}")
    print(f"  Stats: {cache2.get_stats()}")
    print()
    
    # Cleanup
    print("Cleaning up...")
    cache.clear()
    print("✅ Cache cleared")


if __name__ == "__main__":
    main()