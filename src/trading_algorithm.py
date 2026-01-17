"""Trading Algorithm - Makes buy/sell decisions using agents"""
from typing import Dict, Optional, List
from src.stock_data_collector import StockDataCollector
from src.portfolio_manager import PortfolioManager
from src.trading_crew import create_trading_crew
from crewai import Task, Crew


class TradingAlgorithm:
    """
    Trading algorithm that uses AI agents to make decisions
    
    Combines:
    - Stock data collection
    - Portfolio management
    - AI agents for analysis
    """
    
    def __init__(
        self, 
        portfolio: PortfolioManager,
        data_collector: StockDataCollector,
        use_agents: bool = False
    ):
        """
        Initialize trading algorithm
        
        Args:
            portfolio: Portfolio manager instance
            data_collector: Stock data collector instance
            use_agents: Whether to use AI agents (requires API key)
        """
        self.portfolio = portfolio
        self.data_collector = data_collector
        self.use_agents = use_agents
        
        # Create agents if enabled
        if use_agents:
            crew_data = create_trading_crew()
            self.agents = crew_data['agents']
        else:
            self.agents = None
    
    def analyze_stock(self, symbol: str) -> Dict:
        """
        Analyze a stock and provide recommendation
        
        Args:
            symbol: Stock symbol to analyze
        
        Returns:
            Dictionary with analysis results
        """
        # Get current price
        current_price = self.data_collector.get_current_price(symbol)
        
        if current_price is None:
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'reason': 'Could not fetch price',
                'confidence': 0
            }
        
        # Get current position
        position = self.portfolio.get_position(symbol)
        
        # Simple rule-based analysis (if not using agents)
        if not self.use_agents:
            return self._simple_analysis(symbol, current_price, position)
        
        # Agent-based analysis
        return self._agent_analysis(symbol, current_price, position)
    
    def _simple_analysis(
        self, 
        symbol: str, 
        current_price: float,
        position: Optional[Dict]
    ) -> Dict:
        """
        Simple rule-based analysis
        
        Rules:
        1. If we don't own it and portfolio < 90% invested: BUY
        2. If we own it and profit > 15%: SELL
        3. Otherwise: HOLD
        """
        portfolio_value = self.portfolio.get_portfolio_value()
        cash_ratio = self.portfolio.cash / portfolio_value
        
        # Rule 1: Buy if we have cash and don't own much of it
        if position is None or position['quantity'] < 100:
            if cash_ratio > 0.1:  # Have at least 10% cash
                # Calculate position size (10% of portfolio)
                max_investment = portfolio_value * 0.10
                shares = int(max_investment / current_price)
                
                if shares > 0:
                    return {
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': shares,
                        'price': current_price,
                        'reason': f'Diversification - investing 10% of portfolio',
                        'confidence': 0.7
                    }
        
        # Rule 2: Sell if we have good profit
        if position is not None:
            avg_price = position['avg_price']
            profit_pct = ((current_price - avg_price) / avg_price) * 100
            
            if profit_pct > 15:
                return {
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': position['quantity'],
                    'price': current_price,
                    'reason': f'Take profit - up {profit_pct:.1f}%',
                    'confidence': 0.8
                }
            
            if profit_pct < -10:
                return {
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': position['quantity'] // 2,  # Sell half
                    'price': current_price,
                    'reason': f'Stop loss - down {profit_pct:.1f}%',
                    'confidence': 0.6
                }
        
        # Rule 3: Hold
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'reason': 'No strong signal',
            'confidence': 0.5
        }
    
    def _agent_analysis(
        self,
        symbol: str,
        current_price: float,
        position: Optional[Dict]
    ) -> Dict:
        """
        Agent-based analysis (requires API key)
        
        Uses the trading crew to make decision
        """
        if not self.agents:
            return self._simple_analysis(symbol, current_price, position)
        
        # Prepare context
        context = f"""
        Stock: {symbol}
        Current Price: ${current_price:.2f}
        Cash Available: ${self.portfolio.cash:.2f}
        """
        
        if position:
            context += f"""
        Current Position: {position['quantity']} shares @ ${position['avg_price']:.2f}
        """
        else:
            context += "\nCurrent Position: None"
        
        # Create analysis task for Market Analyst
        task = Task(
            description=f"{context}\n\nAnalyze {symbol} and recommend BUY, SELL, or HOLD.",
            agent=self.agents['market_analyst'],
            expected_output="Clear BUY/SELL/HOLD recommendation with reasoning"
        )
        
        try:
            # Run the crew
            crew = Crew(
                agents=[self.agents['market_analyst']],
                tasks=[task],
                verbose=False
            )
            
            result = crew.kickoff()
            
            # Parse result (simplified - in reality would need better parsing)
            result_str = str(result).upper()
            
            if 'BUY' in result_str:
                action = 'BUY'
            elif 'SELL' in result_str:
                action = 'SELL'
            else:
                action = 'HOLD'
            
            return {
                'symbol': symbol,
                'action': action,
                'reason': str(result)[:200],  # First 200 chars
                'confidence': 0.75
            }
            
        except Exception as e:
            print(f"Agent analysis failed: {e}")
            return self._simple_analysis(symbol, current_price, position)
    
    def analyze_all_stocks(self) -> List[Dict]:
        """
        Analyze all allowed stocks
        
        Returns:
            List of analysis results for each stock
        """
        results = []
        
        for symbol in self.data_collector.ALLOWED_SYMBOLS:
            analysis = self.analyze_stock(symbol)
            results.append(analysis)
        
        return results
    
    def execute_recommendation(self, recommendation: Dict) -> bool:
        """
        Execute a trading recommendation
        
        Args:
            recommendation: Analysis result with action
        
        Returns:
            True if executed successfully
        """
        action = recommendation.get('action')
        symbol = recommendation.get('symbol')
        
        if action == 'HOLD':
            print(f"  {symbol}: HOLD - {recommendation.get('reason', 'No action')}")
            return True
        
        price = recommendation.get('price')
        quantity = recommendation.get('quantity', 0)
        
        if action == 'BUY' and quantity > 0:
            success = self.portfolio.buy_stock(symbol, quantity, price)
            if success:
                print(f"  ✅ BUY {quantity} {symbol} @ ${price:.2f}")
                print(f"     Reason: {recommendation.get('reason', 'N/A')}")
                return True
            else:
                print(f"  ❌ BUY {symbol} failed (insufficient funds)")
                return False
        
        elif action == 'SELL' and quantity > 0:
            success = self.portfolio.sell_stock(symbol, quantity, price)
            if success:
                print(f"  ✅ SELL {quantity} {symbol} @ ${price:.2f}")
                print(f"     Reason: {recommendation.get('reason', 'N/A')}")
                return True
            else:
                print(f"  ❌ SELL {symbol} failed")
                return False
        
        return False
    
    def run_trading_cycle(self) -> Dict:
        """
        Run one complete trading cycle
        
        Returns:
            Summary of actions taken
        """
        print("\n" + "=" * 70)
        print("TRADING CYCLE")
        print("=" * 70)
        
        # Get portfolio status
        current_prices = self.data_collector.get_all_prices()
        portfolio_value = self.portfolio.get_portfolio_value(current_prices)
        
        print(f"\nPortfolio Status:")
        print(f"  Cash: ${self.portfolio.cash:,.2f}")
        print(f"  Total Value: ${portfolio_value:,.2f}")
        print(f"  Positions: {len(self.portfolio.positions)}")
        
        # Analyze all stocks
        print(f"\nAnalyzing stocks...")
        analyses = self.analyze_all_stocks()
        
        # Execute recommendations
        print(f"\nExecuting recommendations:")
        executed = []
        
        for analysis in analyses:
            if analysis['action'] != 'HOLD':
                success = self.execute_recommendation(analysis)
                if success:
                    executed.append(analysis)
            else:
                self.execute_recommendation(analysis)
        
        # Summary
        new_portfolio_value = self.portfolio.get_portfolio_value(current_prices)
        change = new_portfolio_value - portfolio_value
        
        print(f"\nCycle Summary:")
        print(f"  Actions Taken: {len(executed)}")
        print(f"  New Portfolio Value: ${new_portfolio_value:,.2f}")
        print(f"  Change: ${change:,.2f} ({(change/portfolio_value)*100:+.2f}%)")
        print("=" * 70)
        
        return {
            'actions': len(executed),
            'portfolio_value': new_portfolio_value,
            'change': change
        }


def main():
    """Demo of trading algorithm"""
    print("=" * 70)
    print("TRADING ALGORITHM DEMO")
    print("=" * 70)
    print()
    
    # Initialize components
    print("Initializing components...")
    portfolio = PortfolioManager(initial_cash=100000.0)
    data_collector = StockDataCollector(use_mock=True)
    
    # Create algorithm (without agents - no API key needed for demo)
    algorithm = TradingAlgorithm(
        portfolio=portfolio,
        data_collector=data_collector,
        use_agents=False  # Set to True if you have OpenAI API key
    )
    
    print("✅ Trading algorithm initialized (rule-based mode)")
    print()
    
    # Run 3 trading cycles
    for cycle in range(1, 4):
        print(f"\n{'='*70}")
        print(f"CYCLE {cycle}")
        print(f"{'='*70}")
        
        result = algorithm.run_trading_cycle()
        
        # Show current positions
        if algorithm.portfolio.positions:
            print("\nCurrent Positions:")
            for symbol, pos in algorithm.portfolio.positions.items():
                print(f"  {symbol}: {pos['quantity']} shares @ ${pos['avg_price']:.2f}")
        
        print("\n")
    
    # Final summary
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    final_prices = data_collector.get_all_prices()
    final_value = portfolio.get_portfolio_value(final_prices)
    profit = final_value - portfolio.initial_cash
    profit_pct = (profit / portfolio.initial_cash) * 100
    
    print(f"\nStarting Capital: ${portfolio.initial_cash:,.2f}")
    print(f"Final Value: ${final_value:,.2f}")
    print(f"Profit/Loss: ${profit:,.2f} ({profit_pct:+.2f}%)")
    print()
    
    print("Algorithm Features:")
    print("  ✅ Rule-based decision making")
    print("  ✅ Portfolio management")
    print("  ✅ Automatic diversification")
    print("  ✅ Profit taking (>15%)")
    print("  ✅ Stop loss (<-10%)")
    print()
    
    print("To use with AI agents:")
    print("  1. Add OPENAI_API_KEY to .env")
    print("  2. Set use_agents=True")
    print()


if __name__ == "__main__":
    main()