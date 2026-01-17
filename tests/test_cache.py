"""Tests for Cache System"""
import pytest
import time
import tempfile
from pathlib import Path
from src.cache import SimpleCache


class TestCacheBasics:
    """Test basic cache functionality"""
    
    def test_store_and_retrieve(self):
        """Should store and retrieve values"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
    
    def test_retrieve_nonexistent(self):
        """Should return None for nonexistent key"""
        cache = SimpleCache()
        assert cache.get('nonexistent') is None
    
    def test_has_key(self):
        """Should check if key exists"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set('existing_key', 'value')
        assert cache.has('existing_key') is True
        assert cache.has('nonexistent_key') is False
    
    def test_delete_key(self):
        """Should delete keys"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set('test_key', 'test_value')
        assert cache.has('test_key') is True
        
        cache.delete('test_key')
        assert cache.has('test_key') is False
    
    def test_clear_cache(self):
        """Should clear all entries"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None


class TestCacheTTL:
    """Test TTL (Time To Live) functionality"""
    
    def test_ttl_expiration(self):
        """Should expire entries after TTL"""
        cache = SimpleCache(ttl_seconds=1)  # 1 second TTL
        
        cache.set('temp_key', 'temp_value')
        assert cache.get('temp_key') == 'temp_value'
        
        # Wait for expiration
        time.sleep(1.5)
        
        assert cache.get('temp_key') is None
    
    def test_custom_ttl(self):
        """Should allow custom TTL per entry"""
        cache = SimpleCache(ttl_seconds=60)  # Default: 60 seconds
        
        cache.set('short_lived', 'value', ttl=1)  # Custom: 1 second
        cache.set('long_lived', 'value', ttl=60)  # Custom: 60 seconds
        
        time.sleep(1.5)
        
        assert cache.get('short_lived') is None  # Expired
        assert cache.get('long_lived') == 'value'  # Still valid
    
    def test_cleanup_expired(self):
        """Should remove expired entries"""
        cache = SimpleCache(ttl_seconds=1)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        time.sleep(1.5)
        
        removed = cache.cleanup_expired()
        assert removed == 2


class TestComplexKeys:
    """Test caching with complex keys"""
    
    def test_tuple_key(self):
        """Should handle tuple keys"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set(('PLTR', '2024-01-15', 'close'), 50.25)
        assert cache.get(('PLTR', '2024-01-15', 'close')) == 50.25
    
    def test_dict_key(self):
        """Should handle dict keys (converted to hash)"""
        cache = SimpleCache(ttl_seconds=60)
        
        key = {'symbol': 'PLTR', 'date': '2024-01-15'}
        cache.set(key, 50.25)
        assert cache.get(key) == 50.25
    
    def test_key_consistency(self):
        """Same key should return same value"""
        cache = SimpleCache(ttl_seconds=60)
        
        key1 = {'symbol': 'PLTR', 'date': '2024-01-15'}
        key2 = {'date': '2024-01-15', 'symbol': 'PLTR'}  # Different order
        
        cache.set(key1, 50.25)
        # Keys with same content should be treated as same
        assert cache.get(key2) == 50.25


class TestPersistence:
    """Test file-based persistence"""
    
    def test_save_to_file(self):
        """Should save cache to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / 'test_cache.json'
            
            cache = SimpleCache(ttl_seconds=60, cache_file=str(cache_file))
            cache.set('test_key', 'test_value')
            
            # Check file exists
            assert cache_file.exists()
    
    def test_load_from_file(self):
        """Should load cache from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / 'test_cache.json'
            
            # Create cache and save data
            cache1 = SimpleCache(ttl_seconds=60, cache_file=str(cache_file))
            cache1.set('persistent_key', 'persistent_value')
            
            # Create new cache instance and load
            cache2 = SimpleCache(ttl_seconds=60, cache_file=str(cache_file))
            assert cache2.get('persistent_key') == 'persistent_value'
    
    def test_expired_entries_not_loaded(self):
        """Should not load expired entries from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / 'test_cache.json'
            
            # Create cache with short TTL
            cache1 = SimpleCache(ttl_seconds=1, cache_file=str(cache_file))
            cache1.set('short_lived', 'value')
            
            # Wait for expiration
            time.sleep(1.5)
            
            # Load in new cache - should be cleaned
            cache2 = SimpleCache(ttl_seconds=1, cache_file=str(cache_file))
            assert cache2.get('short_lived') is None


class TestCacheStats:
    """Test cache statistics"""
    
    def test_get_stats(self):
        """Should return cache statistics"""
        cache = SimpleCache(ttl_seconds=60)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        stats = cache.get_stats()
        
        assert stats['total_entries'] == 2
        assert stats['ttl_seconds'] == 60
        assert 'memory_size_bytes' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])