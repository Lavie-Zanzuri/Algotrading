"""Tests for Portfolio Manager - Written FIRST (TDD approach)"""
import pytest
from src.portfolio_manager import PortfolioManager


class TestPortfolioManagerInitialization:
    """Test portfolio initialization"""
    
    def test_initialize_with_default_cash(self):
        """Portfolio should start with $100,000 by default"""
        portfolio = PortfolioManager()
        assert portfolio.cash == 100000.0
        assert portfolio.initial_cash == 100000.0
    
    def test_initialize_with_custom_cash(self):
        """Portfolio should accept custom initial cash"""
        portfolio = PortfolioManager(initial_cash=50000.0)
        assert portfolio.cash == 50000.0
        assert portfolio.initial_cash == 50000.0
    
    def test_initialize_empty_positions(self):
        """Portfolio should start with no positions"""
        portfolio = PortfolioManager()
        assert portfolio.positions == {}
        assert len(portfolio.positions) == 0


class TestPortfolioValue:
    """Test portfolio value calculation"""
    
    def test_portfolio_value_cash_only(self):
        """Portfolio value with only cash should equal cash"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        assert portfolio.get_portfolio_value() == 100000.0
    
    def test_portfolio_value_with_positions(self):
        """Portfolio value should include positions"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        # Manually add position for testing
        portfolio.positions = {
            'PLTR': {'quantity': 100, 'avg_price': 50.0}
        }
        # Current prices for calculation
        current_prices = {'PLTR': 55.0}
        value = portfolio.get_portfolio_value(current_prices)
        # Cash + (100 shares * $55) = 100000 + 5500 = 105500
        assert value == 105500.0


class TestBuyStock:
    """Test buying stock"""
    
    def test_buy_stock_success(self):
        """Should successfully buy stock"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        result = portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        assert result is True
        assert portfolio.cash == 95000.0  # 100000 - (100 * 50)
        assert 'PLTR' in portfolio.positions
        assert portfolio.positions['PLTR']['quantity'] == 100
        assert portfolio.positions['PLTR']['avg_price'] == 50.0
    
    def test_buy_stock_insufficient_funds(self):
        """Should fail when not enough cash"""
        portfolio = PortfolioManager(initial_cash=1000.0)
        result = portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        assert result is False
        assert portfolio.cash == 1000.0  # Cash unchanged
        assert 'PLTR' not in portfolio.positions
    
    def test_buy_stock_multiple_times_same_symbol(self):
        """Should average cost when buying same stock multiple times"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        
        # First buy: 100 shares at $50
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        # Second buy: 100 shares at $60
        portfolio.buy_stock('PLTR', quantity=100, price=60.0)
        
        # Total: 200 shares at average of $55
        assert portfolio.positions['PLTR']['quantity'] == 200
        assert portfolio.positions['PLTR']['avg_price'] == 55.0
        assert portfolio.cash == 89000.0  # 100000 - 5000 - 6000
    
    def test_buy_stock_invalid_quantity(self):
        """Should fail with invalid quantity"""
        portfolio = PortfolioManager()
        
        assert portfolio.buy_stock('PLTR', quantity=0, price=50.0) is False
        assert portfolio.buy_stock('PLTR', quantity=-10, price=50.0) is False
    
    def test_buy_stock_invalid_price(self):
        """Should fail with invalid price"""
        portfolio = PortfolioManager()
        
        assert portfolio.buy_stock('PLTR', quantity=100, price=0) is False
        assert portfolio.buy_stock('PLTR', quantity=100, price=-50) is False


class TestSellStock:
    """Test selling stock"""
    
    def test_sell_stock_success(self):
        """Should successfully sell stock"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        # First buy some stock
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        # Then sell it
        result = portfolio.sell_stock('PLTR', quantity=50, price=60.0)
        
        assert result is True
        assert portfolio.cash == 98000.0  # 95000 + (50 * 60)
        assert portfolio.positions['PLTR']['quantity'] == 50
    
    def test_sell_stock_all_shares(self):
        """Should remove position when selling all shares"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        result = portfolio.sell_stock('PLTR', quantity=100, price=60.0)
        
        assert result is True
        assert portfolio.cash == 101000.0  # 95000 + (100 * 60)
        assert 'PLTR' not in portfolio.positions
    
    def test_sell_stock_not_owned(self):
        """Should fail when trying to sell stock not owned"""
        portfolio = PortfolioManager()
        result = portfolio.sell_stock('PLTR', quantity=100, price=50.0)
        
        assert result is False
    
    def test_sell_stock_insufficient_quantity(self):
        """Should fail when trying to sell more than owned"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        result = portfolio.sell_stock('PLTR', quantity=200, price=60.0)
        
        assert result is False
        assert portfolio.positions['PLTR']['quantity'] == 100  # Unchanged
    
    def test_sell_stock_invalid_quantity(self):
        """Should fail with invalid quantity"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        assert portfolio.sell_stock('PLTR', quantity=0, price=50.0) is False
        assert portfolio.sell_stock('PLTR', quantity=-10, price=50.0) is False
    
    def test_sell_stock_invalid_price(self):
        """Should fail with invalid price"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        assert portfolio.sell_stock('PLTR', quantity=50, price=0) is False
        assert portfolio.sell_stock('PLTR', quantity=50, price=-50) is False


class TestPortfolioSummary:
    """Test portfolio summary/status"""
    
    def test_get_position_info(self):
        """Should return correct position information"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        
        position = portfolio.get_position('PLTR')
        
        assert position is not None
        assert position['quantity'] == 100
        assert position['avg_price'] == 50.0
    
    def test_get_position_not_exists(self):
        """Should return None for non-existent position"""
        portfolio = PortfolioManager()
        position = portfolio.get_position('PLTR')
        
        assert position is None
    
    def test_get_all_positions(self):
        """Should return all positions"""
        portfolio = PortfolioManager(initial_cash=100000.0)
        portfolio.buy_stock('PLTR', quantity=100, price=50.0)
        portfolio.buy_stock('NFLX', quantity=50, price=100.0)
        
        positions = portfolio.get_all_positions()
        
        assert len(positions) == 2
        assert 'PLTR' in positions
        assert 'NFLX' in positions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])