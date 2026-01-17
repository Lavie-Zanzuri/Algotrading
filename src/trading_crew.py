"""Trading Crew - 4 Agents Working Together"""
from crewai import Agent, Task, Crew, Process
from src.custom_tools import get_all_tools


def create_market_analyst():
    """
    Market Analyst - Analyzes stock prices and trends
    """
    return Agent(
        role="Market Analyst",
        goal="Analyze stock market data and identify profitable trading opportunities",
        backstory=(
            "You are a senior market analyst with 15 years of experience in technical "
            "and fundamental analysis. You excel at spotting trends and patterns in "
            "stock prices. You always use data and calculations to support your analysis."
        ),
        tools=get_all_tools(),
        verbose=True,
        allow_delegation=True  # Can ask other agents for help
    )


def create_risk_manager():
    """
    Risk Manager - Evaluates and manages trading risks
    """
    return Agent(
        role="Risk Manager",
        goal="Evaluate trading risks and ensure portfolio safety through proper position sizing",
        backstory=(
            "You are a cautious risk management expert with 12 years of experience. "
            "Your primary concern is protecting capital. You calculate risk/reward ratios, "
            "recommend position sizes, and ensure we never risk too much on a single trade. "
            "You're known for saying 'no' to risky trades."
        ),
        tools=get_all_tools(),
        verbose=True,
        allow_delegation=True
    )


def create_news_analyzer():
    """
    News Analyzer - Analyzes market news and sentiment
    """
    return Agent(
        role="News Analyzer",
        goal="Analyze market news and sentiment to inform trading decisions",
        backstory=(
            "You are a sharp news analyst who reads between the lines. With 8 years "
            "of experience tracking market news, you understand how news affects stock "
            "prices. You identify potential catalysts and risks from news events."
        ),
        tools=[],  # Could add news API tools later
        verbose=True,
        allow_delegation=True
    )


def create_trade_executor():
    """
    Trade Executor - Makes final trading decisions and executes
    """
    return Agent(
        role="Trade Executor",
        goal="Make final trading decisions and execute trades based on team analysis",
        backstory=(
            "You are the decisive trade executor with 10 years of trading experience. "
            "You synthesize input from the analyst, risk manager, and news analyst to "
            "make the final call. You're responsible for the actual buy/sell decisions "
            "and ensure trades align with our $100,000 portfolio strategy."
        ),
        tools=get_all_tools(),
        verbose=True,
        allow_delegation=False  # Makes final decisions
    )


def create_trading_crew():
    """
    Create the full trading crew with all 4 agents
    
    Returns:
        Configured crew ready to analyze trades
    """
    # Create all agents
    market_analyst = create_market_analyst()
    risk_manager = create_risk_manager()
    news_analyzer = create_news_analyzer()
    trade_executor = create_trade_executor()
    
    return {
        'agents': {
            'market_analyst': market_analyst,
            'risk_manager': risk_manager,
            'news_analyzer': news_analyzer,
            'trade_executor': trade_executor
        }
    }


def demo_crew_structure():
    """Demo: Show crew structure without running LLM"""
    print("=" * 70)
    print("TRADING CREW - 4 AGENTS STRUCTURE")
    print("=" * 70)
    print()
    
    crew_data = create_trading_crew()
    agents = crew_data['agents']
    
    print("Creating Trading Crew...")
    print(f"✅ {len(agents)} Agents Created\n")
    
    # Show each agent
    for i, (name, agent) in enumerate(agents.items(), 1):
        print(f"{i}. {agent.role}")
        print(f"   Goal: {agent.goal[:60]}...")
        print(f"   Tools: {len(agent.tools)}")
        print(f"   Can delegate: {agent.allow_delegation}")
        print()
    
    print("=" * 70)
    print("HOW THEY WORK TOGETHER:")
    print("=" * 70)
    print()
    print("📊 Workflow for 'Should we buy PLTR?' question:")
    print()
    print("1. 📈 MARKET ANALYST")
    print("   - Analyzes PLTR price: $55")
    print("   - Uses calculate_profit_loss tool")
    print("   - Reports: 'PLTR up 10%, trend is positive'")
    print()
    print("2. 🛡️  RISK MANAGER")
    print("   - Evaluates risk of buying more")
    print("   - Uses calculate_position_size & risk_reward tools")
    print("   - Reports: 'Safe to buy 200 shares (10% portfolio risk)'")
    print()
    print("3. 📰 NEWS ANALYZER")
    print("   - Checks recent PLTR news")
    print("   - Reports: 'Positive earnings report released yesterday'")
    print()
    print("4. ✅ TRADE EXECUTOR")
    print("   - Reviews all inputs")
    print("   - Makes final decision")
    print("   - Output: 'BUY 200 shares of PLTR at $55'")
    print()
    
    print("=" * 70)
    print("KEY FEATURES:")
    print("=" * 70)
    print()
    print("✅ Collaboration: Agents can ask each other for help")
    print("✅ Specialization: Each agent has specific expertise")
    print("✅ Tools: Market Analyst & Risk Manager use our custom tools")
    print("✅ Final Decision: Trade Executor makes the call")
    print()
    
    print("=" * 70)
    print("CREW COORDINATION:")
    print("=" * 70)
    print()
    print("Sequential Process:")
    print("  Market Analyst → Risk Manager → News Analyzer → Trade Executor")
    print()
    print("Each agent builds on previous agent's work!")
    print()


def demo_task_example():
    """Show example of how tasks would be structured"""
    print("=" * 70)
    print("EXAMPLE TASK STRUCTURE (Conceptual)")
    print("=" * 70)
    print()
    
    print("Task 1: Market Analysis (for Market Analyst)")
    print("-" * 70)
    print("Description:")
    print("  'Analyze PLTR stock. Current price: $55, we own 100 shares")
    print("   bought at $50. Calculate profit/loss and assess trend.'")
    print()
    print("Expected Output:")
    print("  - Current profit/loss calculation")
    print("  - Price trend analysis")
    print("  - Recommendation (buy/sell/hold)")
    print()
    
    print("Task 2: Risk Assessment (for Risk Manager)")
    print("-" * 70)
    print("Description:")
    print("  'Based on Market Analyst's findings, evaluate the risk of")
    print("   buying more PLTR. We have $95,000 cash available.'")
    print()
    print("Expected Output:")
    print("  - Risk/reward ratio")
    print("  - Recommended position size")
    print("  - Risk level assessment")
    print()
    
    print("Task 3: News Check (for News Analyzer)")
    print("-" * 70)
    print("Description:")
    print("  'Check recent news about PLTR. Any catalysts or risks?'")
    print()
    print("Expected Output:")
    print("  - Summary of recent news")
    print("  - Sentiment analysis")
    print("  - Potential impacts")
    print()
    
    print("Task 4: Final Decision (for Trade Executor)")
    print("-" * 70)
    print("Description:")
    print("  'Review all analysis and make final trading decision for PLTR.'")
    print()
    print("Expected Output:")
    print("  - Clear BUY/SELL/HOLD decision")
    print("  - Number of shares")
    print("  - Price target")
    print("  - Rationale")
    print()


def main():
    """Main demo"""
    print("\n🚀 TRADING CREW DEMO - 4 AGENTS\n")
    
    demo_crew_structure()
    print("\n")
    demo_task_example()
    
    print("=" * 70)
    print("✅ CREW STRUCTURE READY!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Add OPENAI_API_KEY to .env to run with real AI")
    print("2. Create specific tasks for your trading scenario")
    print("3. Let the crew analyze and make decisions!")
    print()
    print("The crew is ready to:")
    print("  - Analyze any of the 3 stocks (PLTR, NFLX, PLTK)")
    print("  - Use custom tools for calculations")
    print("  - Coordinate between agents")
    print("  - Make informed trading decisions")
    print()


if __name__ == "__main__":
    main()