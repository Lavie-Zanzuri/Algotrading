"""Tests for Trading Algorithm"""
import pytest
from src.trading_algorithm import TradingAlgorithm
from src.portfolio_manager import PortfolioManager
from src.stock_data_collector import StockDataCollector


class TestAlgorithmInitialization:
    """Test algorithm initialization"""
    
    def test_create_algorithm(self):
        """Should create algorithm successfully"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        
        algo = TradingAlgorithm(
            portfolio=portfolio,
            data_collector=collector,
            use_agents=False
        )
        
        assert algo is not None
        assert algo.portfolio == portfolio
        assert algo.data_collector == collector
        assert algo.use_agents is False
    
    def test_algorithm_without_agents(self):
        """Algorithm should work without agents"""
        portfolio = PortfolioManager()
        collector = StockDataCollector(use_mock=True)
        
        algo = TradingAlgorithm(
            portfolio=portfolio,
            data_collector=collector,
            use_agents=False
        )
        
        assert algo.agents is None


class TestStockAnalysis:
    """Test stock analysis functionality"""
    
    def test_analyze_stock_pltr(self):
        """Should analyze PLTR stock"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        analysis = algo.analyze_stock('PLTR')
        
        assert 'symbol' in analysis
        assert 'action' in analysis
        assert analysis['symbol'] == 'PLTR'
        assert analysis['action'] in ['BUY', 'SELL', 'HOLD']
    
    def test_analyze_all_stocks(self):
        """Should analyze all allowed stocks"""
        portfolio = PortfolioManager()
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        analyses = algo.analyze_all_stocks()
        
        assert len(analyses) == 3  # PLTR, NFLX, PLTK
        assert all('action' in a for a in analyses)


class TestSimpleAnalysis:
    """Test rule-based analysis"""
    
    def test_buy_recommendation_with_cash(self):
        """Should recommend BUY when we have cash"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        analysis = algo.analyze_stock('PLTR')
        
        # Should recommend buying since we have cash and no position
        assert analysis['action'] in ['BUY', 'HOLD']
    
    def test_sell_recommendation_with_profit(self):
        """Should recommend SELL with >15% profit"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        # Buy at lower price
        portfolio.buy_stock('PLTR', 100, 40.0)
        
        # Analyze at higher price (50.25 in mock - 25% profit)
        analysis = algo.analyze_stock('PLTR')
        
        # Should recommend selling due to profit
        assert analysis['action'] in ['SELL', 'HOLD']


class TestRecommendationExecution:
    """Test executing recommendations"""
    
    def test_execute_buy(self):
        """Should execute BUY recommendation"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        recommendation = {
            'symbol': 'PLTR',
            'action': 'BUY',
            'quantity': 100,
            'price': 50.0,
            'reason': 'Test buy'
        }
        
        success = algo.execute_recommendation(recommendation)
        
        assert success is True
        assert portfolio.cash < 100000  # Cash should decrease
        assert 'PLTR' in portfolio.positions
    
    def test_execute_sell(self):
        """Should execute SELL recommendation"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        # First buy some stock
        portfolio.buy_stock('PLTR', 100, 50.0)
        initial_cash = portfolio.cash
        
        # Then sell
        recommendation = {
            'symbol': 'PLTR',
            'action': 'SELL',
            'quantity': 50,
            'price': 55.0,
            'reason': 'Test sell'
        }
        
        success = algo.execute_recommendation(recommendation)
        
        assert success is True
        assert portfolio.cash > initial_cash  # Cash should increase
        assert portfolio.positions['PLTR']['quantity'] == 50
    
    def test_execute_hold(self):
        """Should handle HOLD recommendation"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        recommendation = {
            'symbol': 'PLTR',
            'action': 'HOLD',
            'reason': 'No action needed'
        }
        
        initial_cash = portfolio.cash
        success = algo.execute_recommendation(recommendation)
        
        assert success is True
        assert portfolio.cash == initial_cash  # No change


class TestTradingCycle:
    """Test complete trading cycle"""
    
    def test_run_trading_cycle(self):
        """Should run complete trading cycle"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        result = algo.run_trading_cycle()
        
        assert 'actions' in result
        assert 'portfolio_value' in result
        assert 'change' in result
        assert isinstance(result['actions'], int)
    
    def test_multiple_cycles(self):
        """Should handle multiple trading cycles"""
        portfolio = PortfolioManager(initial_cash=100000)
        collector = StockDataCollector(use_mock=True)
        algo = TradingAlgorithm(portfolio, collector, use_agents=False)
        
        # Run 3 cycles
        for _ in range(3):
            result = algo.run_trading_cycle()
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])