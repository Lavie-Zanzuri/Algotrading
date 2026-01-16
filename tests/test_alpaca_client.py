"""Tests for Alpaca Client"""
import pytest
from src.alpaca_client import AlpacaClient


def test_mock_client_initialization():
    """Test that mock client initializes correctly"""
    client = AlpacaClient(use_mock=True)
    assert client.use_mock is True
    assert client.client is None


def test_mock_get_account():
    """Test getting account info with mock"""
    client = AlpacaClient(use_mock=True)
    account = client.get_account()
    
    assert 'cash' in account
    assert 'portfolio_value' in account
    assert account['cash'] == '100000.00'
    assert account['portfolio_value'] == '100000.00'


def test_mock_get_positions():
    """Test getting positions with mock returns empty list"""
    client = AlpacaClient(use_mock=True)
    positions = client.get_positions()
    
    assert isinstance(positions, list)
    assert len(positions) == 0


def test_mock_is_market_open():
    """Test market status with mock always returns True"""
    client = AlpacaClient(use_mock=True)
    assert client.is_market_open() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])