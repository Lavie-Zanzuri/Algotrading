"""Tests for Agent Creation"""
import pytest
from src.market_analyst_agent import create_market_analyst_agent


class TestAgentCreation:
    """Test that agent is created correctly"""
    
    def test_create_agent(self):
        """Should create agent successfully"""
        agent = create_market_analyst_agent()
        
        assert agent is not None
        assert agent.role == "Market Analyst"
        assert len(agent.tools) == 3  # We have 3 custom tools
    
    def test_agent_has_tools(self):
        """Agent should have our custom tools"""
        agent = create_market_analyst_agent()
        
        tool_names = [tool.name for tool in agent.tools]
        
        assert "calculate_profit_loss" in tool_names
        assert "calculate_position_size" in tool_names
        assert "calculate_risk_reward" in tool_names
    
    def test_agent_configuration(self):
        """Agent should be configured correctly"""
        agent = create_market_analyst_agent()
        
        assert agent.verbose is True
        assert agent.allow_delegation is False
        assert len(agent.goal) > 0
        assert len(agent.backstory) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])