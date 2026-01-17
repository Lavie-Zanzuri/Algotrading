"""Tests for Trading Crew"""
import pytest
from src.trading_crew import (
    create_market_analyst,
    create_risk_manager,
    create_news_analyzer,
    create_trade_executor,
    create_trading_crew
)


class TestIndividualAgents:
    """Test each agent is created correctly"""
    
    def test_market_analyst_creation(self):
        """Market Analyst should be created correctly"""
        agent = create_market_analyst()
        
        assert agent.role == "Market Analyst"
        assert len(agent.tools) == 3
        assert agent.allow_delegation is True
    
    def test_risk_manager_creation(self):
        """Risk Manager should be created correctly"""
        agent = create_risk_manager()
        
        assert agent.role == "Risk Manager"
        assert len(agent.tools) == 3
        assert agent.allow_delegation is True
    
    def test_news_analyzer_creation(self):
        """News Analyzer should be created correctly"""
        agent = create_news_analyzer()
        
        assert agent.role == "News Analyzer"
        assert agent.allow_delegation is True
    
    def test_trade_executor_creation(self):
        """Trade Executor should be created correctly"""
        agent = create_trade_executor()
        
        assert agent.role == "Trade Executor"
        assert len(agent.tools) == 3
        assert agent.allow_delegation is False  # Makes final decisions


class TestTradingCrew:
    """Test the complete trading crew"""
    
    def test_crew_creation(self):
        """Should create crew with all 4 agents"""
        crew_data = create_trading_crew()
        agents = crew_data['agents']
        
        assert len(agents) == 4
        assert 'market_analyst' in agents
        assert 'risk_manager' in agents
        assert 'news_analyzer' in agents
        assert 'trade_executor' in agents
    
    def test_all_agents_unique(self):
        """Each agent should be unique"""
        crew_data = create_trading_crew()
        agents = crew_data['agents']
        
        roles = [agent.role for agent in agents.values()]
        
        # All roles should be unique
        assert len(roles) == len(set(roles))
    
    def test_agents_have_correct_delegation(self):
        """Check delegation settings are correct"""
        crew_data = create_trading_crew()
        agents = crew_data['agents']
        
        # Market Analyst, Risk Manager, News Analyzer can delegate
        assert agents['market_analyst'].allow_delegation is True
        assert agents['risk_manager'].allow_delegation is True
        assert agents['news_analyzer'].allow_delegation is True
        
        # Trade Executor makes final decisions - no delegation
        assert agents['trade_executor'].allow_delegation is False
    
    def test_agents_with_tools(self):
        """Check which agents have tools"""
        crew_data = create_trading_crew()
        agents = crew_data['agents']
        
        # Market Analyst should have tools
        assert len(agents['market_analyst'].tools) > 0
        
        # Risk Manager should have tools
        assert len(agents['risk_manager'].tools) > 0
        
        # Trade Executor should have tools
        assert len(agents['trade_executor'].tools) > 0
        
        # News Analyzer might not have tools (could be added later)
        # No assertion for news_analyzer tools


class TestCrewRoles:
    """Test that crew roles are appropriate"""
    
    def test_market_analyst_role(self):
        """Market Analyst should have analysis-focused role"""
        agent = create_market_analyst()
        
        assert "analyst" in agent.role.lower() or "market" in agent.role.lower()
        assert len(agent.goal) > 20  # Has substantial goal
        assert len(agent.backstory) > 50  # Has detailed backstory
    
    def test_risk_manager_role(self):
        """Risk Manager should have risk-focused role"""
        agent = create_risk_manager()
        
        assert "risk" in agent.role.lower()
        assert "risk" in agent.goal.lower() or "safe" in agent.goal.lower()
    
    def test_trade_executor_role(self):
        """Trade Executor should have execution-focused role"""
        agent = create_trade_executor()
        
        assert "executor" in agent.role.lower() or "trade" in agent.role.lower()
        assert "decision" in agent.goal.lower() or "execute" in agent.goal.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])