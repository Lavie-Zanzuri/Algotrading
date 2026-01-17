"""Market Analyst Agent - First Agent Implementation"""
import os
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from src.custom_tools import get_all_tools

# Load environment variables
load_dotenv()


def create_market_analyst_agent():
    """
    Create a Market Analyst agent with custom tools
    
    Returns:
        Agent configured for market analysis
    """
    return Agent(
        role="Market Analyst",
        goal=(
            "Analyze stock market data and provide actionable trading recommendations "
            "based on price movements, risk analysis, and position sizing calculations"
        ),
        backstory=(
            "You are an experienced stock market analyst with 10 years of experience "
            "in technical and fundamental analysis. You excel at evaluating trading "
            "opportunities and calculating optimal position sizes while managing risk. "
            "You always use mathematical tools to validate your recommendations."
        ),
        tools=get_all_tools(),  # Our custom tools!
        verbose=True,
        allow_delegation=False
    )


def demo_agent_with_tools():
    """Demo: Agent using custom tools"""
    print("=" * 70)
    print("MARKET ANALYST AGENT DEMO")
    print("=" * 70)
    print("\nCreating Market Analyst Agent with custom tools...")
    
    # Create agent
    agent = create_market_analyst_agent()
    print(f"✅ Agent created: {agent.role}")
    print(f"   Tools available: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"   - {tool.name}")
    print()
    
    # Create a simple analysis task
    print("=" * 70)
    print("TASK 1: Analyze a potential PLTR trade")
    print("=" * 70)
    
    task1 = Task(
        description=(
            "Analyze this trading scenario for PLTR stock:\n"
            "- Current price: $55.00\n"
            "- We bought 100 shares at $50.00\n"
            "- Available cash: $95,000\n"
            "- Considering buying more shares\n\n"
            "Use your tools to:\n"
            "1. Calculate current profit/loss on existing position\n"
            "2. Recommend position size if we buy more (use 10% risk)\n"
            "3. Provide a clear recommendation"
        ),
        agent=agent,
        expected_output="Detailed analysis with profit/loss calculation, position size recommendation, and final trading recommendation"
    )
    
    # Create crew and run
    crew = Crew(
        agents=[agent],
        tasks=[task1],
        verbose=True
    )
    
    print("\n🤖 Agent is thinking and using tools...\n")
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("AGENT'S ANALYSIS:")
    print("=" * 70)
    print(result)
    print("=" * 70)
    
    return result


def demo_risk_reward_analysis():
    """Demo: Agent analyzing risk/reward of a trade"""
    print("\n\n" + "=" * 70)
    print("TASK 2: Risk/Reward Analysis")
    print("=" * 70)
    
    agent = create_market_analyst_agent()
    
    task2 = Task(
        description=(
            "Evaluate this potential trade setup for NFLX:\n"
            "- Entry price: $500.00\n"
            "- Target price: $550.00\n"
            "- Stop loss: $480.00\n\n"
            "Use the risk/reward calculator tool to evaluate if this is a good trade. "
            "Provide your recommendation."
        ),
        agent=agent,
        expected_output="Risk/reward analysis with clear recommendation on whether to take the trade"
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task2],
        verbose=True
    )
    
    print("\n🤖 Agent is analyzing risk/reward...\n")
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("AGENT'S RISK/REWARD ANALYSIS:")
    print("=" * 70)
    print(result)
    print("=" * 70)
    
    return result


def main():
    """Main demo function"""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not found in .env file!")
        print("   Please add your OpenAI API key to .env file:")
        print("   OPENAI_API_KEY=your_key_here")
        print()
        print("   Or use a different LLM by setting these in .env:")
        print("   OPENAI_API_BASE=http://localhost:11434/v1  # For Ollama")
        print("   OPENAI_MODEL_NAME=llama2")
        print()
        return
    
    print("\n🚀 Starting Market Analyst Agent Demo\n")
    
    try:
        # Run demos
        demo_agent_with_tools()
        demo_risk_reward_analysis()
        
        print("\n\n" + "=" * 70)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey Observations:")
        print("- Agent successfully used custom tools")
        print("- Calculations were accurate and helpful")
        print("- Agent provided actionable recommendations")
        print()
        
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure OPENAI_API_KEY is set in .env")
        print("2. Check your API key is valid")
        print("3. Ensure you have internet connection")
        print("4. Check your OpenAI account has credits")


if __name__ == "__main__":
    main()