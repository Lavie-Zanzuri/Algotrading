"""Tests for Custom Tools"""
import pytest
from src.custom_tools import (
    CalculateProfitLossTool,
    CalculatePositionSizeTool,
    CalculateRiskRewardTool
)


class TestProfitLossTool:
    """Test profit/loss calculator tool"""
    
    def test_calculate_profit(self):
        """Should calculate profit correctly"""
        tool = CalculateProfitLossTool()
        result = tool._run(buy_price=50.0, current_price=60.0, quantity=100)
        
        assert "$5000.00" in result  # Total invested
        assert "$6000.00" in result  # Current value
        assert "PROFIT" in result
        assert "+20.00%" in result
    
    def test_calculate_loss(self):
        """Should calculate loss correctly"""
        tool = CalculateProfitLossTool()
        result = tool._run(buy_price=60.0, current_price=50.0, quantity=100)
        
        assert "LOSS" in result
        assert "-16.67%" in result or "-16.66%" in result  # Allow for rounding
    
    def test_zero_profit_loss(self):
        """Should handle no change in price"""
        tool = CalculateProfitLossTool()
        result = tool._run(buy_price=50.0, current_price=50.0, quantity=100)
        
        assert "$0.00" in result
        assert "+0.00%" in result


class TestPositionSizeTool:
    """Test position size calculator tool"""
    
    def test_calculate_position_size_10_percent(self):
        """Should calculate position size with 10% risk"""
        tool = CalculatePositionSizeTool()
        result = tool._run(cash_available=100000, stock_price=50.0, risk_percentage=10)
        
        assert "200 shares" in result  # 10% of 100k = 10k / 50 = 200
        assert "$10000.00" in result  # Risk allocation
    
    def test_calculate_position_size_5_percent(self):
        """Should calculate position size with 5% risk"""
        tool = CalculatePositionSizeTool()
        result = tool._run(cash_available=100000, stock_price=50.0, risk_percentage=5)
        
        assert "100 shares" in result  # 5% of 100k = 5k / 50 = 100
    
    def test_invalid_stock_price(self):
        """Should handle invalid stock price"""
        tool = CalculatePositionSizeTool()
        result = tool._run(cash_available=100000, stock_price=0, risk_percentage=10)
        
        assert "Error" in result
    
    def test_invalid_risk_percentage(self):
        """Should handle invalid risk percentage"""
        tool = CalculatePositionSizeTool()
        
        result1 = tool._run(cash_available=100000, stock_price=50.0, risk_percentage=0)
        assert "Error" in result1
        
        result2 = tool._run(cash_available=100000, stock_price=50.0, risk_percentage=150)
        assert "Error" in result2


class TestRiskRewardTool:
    """Test risk/reward calculator tool"""
    
    def test_good_risk_reward(self):
        """Should identify good risk/reward ratio (1:2)"""
        tool = CalculateRiskRewardTool()
        result = tool._run(entry_price=50.0, target_price=60.0, stop_loss=45.0)
        
        assert "1:2.00" in result
        assert "EXCELLENT" in result or "GOOD" in result
    
    def test_poor_risk_reward(self):
        """Should identify poor risk/reward ratio"""
        tool = CalculateRiskRewardTool()
        result = tool._run(entry_price=50.0, target_price=52.0, stop_loss=45.0)
        
        # Reward = 2, Risk = 5, Ratio = 0.4
        assert "POOR" in result or "ACCEPTABLE" in result
    
    def test_equal_risk_reward(self):
        """Should handle equal risk and reward"""
        tool = CalculateRiskRewardTool()
        result = tool._run(entry_price=50.0, target_price=55.0, stop_loss=45.0)
        
        assert "1:1.00" in result
        assert "ACCEPTABLE" in result
    
    def test_invalid_stop_loss(self):
        """Should handle stop loss equal to entry"""
        tool = CalculateRiskRewardTool()
        result = tool._run(entry_price=50.0, target_price=60.0, stop_loss=50.0)
        
        assert "Error" in result


class TestToolNames:
    """Test that tools have correct names for CrewAI"""
    
    def test_profit_loss_tool_name(self):
        """Profit loss tool should have correct name"""
        tool = CalculateProfitLossTool()
        assert tool.name == "calculate_profit_loss"
        assert len(tool.description) > 0
    
    def test_position_size_tool_name(self):
        """Position size tool should have correct name"""
        tool = CalculatePositionSizeTool()
        assert tool.name == "calculate_position_size"
        assert len(tool.description) > 0
    
    def test_risk_reward_tool_name(self):
        """Risk reward tool should have correct name"""
        tool = CalculateRiskRewardTool()
        assert tool.name == "calculate_risk_reward"
        assert len(tool.description) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])