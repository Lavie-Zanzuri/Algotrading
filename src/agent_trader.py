"""
agent_trader.py - Main Trading Program

This is the main entry point for the algotrading system.
Run this file to start trading!

Usage:
    python agent_trader.py

Press Ctrl+C to stop gracefully.
"""
import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from src.alpaca_client import AlpacaClient
from src.portfolio_manager import PortfolioManager
from src.stock_data_collector import StockDataCollector
from src.trading_algorithm import TradingAlgorithm

# Load environment variables
load_dotenv()


def setup_logging():
    """Configure logging for the trading system"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"logs/trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('agent_trader')


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🤖 AGENT TRADER v1.0 🤖                         ║
    ║                                                              ║
    ║          Automated Trading System with AI Agents            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_portfolio_status(portfolio, data_collector, logger):
    """Print current portfolio status"""
    try:
        current_prices = data_collector.get_all_prices()
        portfolio_value = portfolio.get_portfolio_value(current_prices)
        
        profit = portfolio_value - portfolio.initial_cash
        profit_pct = (profit / portfolio.initial_cash) * 100
        
        logger.info("=" * 70)
        logger.info("PORTFOLIO STATUS")
        logger.info("=" * 70)
        logger.info(f"Cash: ${portfolio.cash:,.2f}")
        logger.info(f"Portfolio Value: ${portfolio_value:,.2f}")
        logger.info(f"Profit/Loss: ${profit:,.2f} ({profit_pct:+.2f}%)")
        logger.info(f"Positions: {len(portfolio.positions)}")
        
        if portfolio.positions:
            logger.info("\nCurrent Positions:")
            for symbol, pos in portfolio.positions.items():
                current_price = current_prices.get(symbol, pos['avg_price'])
                position_value = pos['quantity'] * current_price
                position_pl = (current_price - pos['avg_price']) * pos['quantity']
                position_pl_pct = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
                
                logger.info(
                    f"  {symbol}: {pos['quantity']} shares @ ${pos['avg_price']:.2f} "
                    f"(Current: ${current_price:.2f}, "
                    f"P/L: ${position_pl:,.2f} {position_pl_pct:+.1f}%)"
                )
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error printing portfolio status: {e}")


def main():
    """Main trading loop"""
    logger = setup_logging()
    print_banner()
    
    # Configuration
    USE_MOCK = True  # Set to False for real trading
    USE_AGENTS = False  # Set to True if you have OpenAI API key
    CYCLE_INTERVAL = 60  # seconds between trading cycles
    
    logger.info("Starting Agent Trader...")
    logger.info(f"Mode: {'MOCK' if USE_MOCK else 'LIVE'}")
    logger.info(f"AI Agents: {'ENABLED' if USE_AGENTS else 'DISABLED (rule-based)'}")
    logger.info(f"Cycle Interval: {CYCLE_INTERVAL}s")
    logger.info("")
    
    # Initialize components
    try:
        logger.info("Initializing components...")
        
        # Initialize Alpaca client
        alpaca_client = AlpacaClient(use_mock=USE_MOCK)
        logger.info("✅ Alpaca client initialized")
        
        # Get initial account info
        account = alpaca_client.get_account()
        initial_cash = float(account['cash'])
        
        # Initialize portfolio manager
        portfolio = PortfolioManager(initial_cash=initial_cash)
        logger.info(f"✅ Portfolio initialized with ${initial_cash:,.2f}")
        
        # Initialize data collector
        data_collector = StockDataCollector(use_mock=USE_MOCK)
        logger.info("✅ Data collector initialized")
        
        # Initialize trading algorithm
        algorithm = TradingAlgorithm(
            portfolio=portfolio,
            data_collector=data_collector,
            use_agents=USE_AGENTS
        )
        logger.info("✅ Trading algorithm initialized")
        
        logger.info("")
        logger.info("All systems ready! 🚀")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        logger.error("Please check your configuration and try again.")
        return
    
    # Main trading loop
    cycle_count = 0
    
    try:
        logger.info("Starting main trading loop...")
        logger.info("Press Ctrl+C to stop gracefully")
        logger.info("")
        
        while True:
            cycle_count += 1
            
            logger.info("")
            logger.info("=" * 70)
            logger.info(f"TRADING CYCLE #{cycle_count}")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 70)
            logger.info("")
            
            try:
                # Run trading cycle
                result = algorithm.run_trading_cycle()
                
                # Log results
                logger.info("")
                logger.info(f"Cycle completed: {result['actions']} actions taken")
                logger.info(f"Portfolio change: ${result['change']:,.2f}")
                
                # Print portfolio status
                print_portfolio_status(portfolio, data_collector, logger)
                
                # Check if market is open (if using real API)
                if not USE_MOCK:
                    if not alpaca_client.is_market_open():
                        logger.info("Market is closed. Waiting for next cycle...")
                
                # Cache stats
                cache_stats = data_collector.get_cache_stats()
                logger.info(f"Cache: {cache_stats['total_entries']} entries")
                
                # Rate limit status
                rate_status = data_collector.get_rate_limit_status()
                logger.info(
                    f"Rate limits: {rate_status['remaining_hour']}/hour, "
                    f"{rate_status['remaining_day']}/day remaining"
                )
                
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                logger.error("Continuing to next cycle...")
            
            # Wait before next cycle
            logger.info("")
            logger.info(f"Waiting {CYCLE_INTERVAL} seconds until next cycle...")
            logger.info("(Press Ctrl+C to stop)")
            logger.info("")
            
            time.sleep(CYCLE_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("Shutdown requested by user (Ctrl+C)")
        logger.info("=" * 70)
    
    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error(f"Fatal error: {e}")
        logger.error("=" * 70)
    
    finally:
        # Final summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total cycles run: {cycle_count}")
        
        try:
            print_portfolio_status(portfolio, data_collector, logger)
            
            final_prices = data_collector.get_all_prices()
            final_value = portfolio.get_portfolio_value(final_prices)
            total_profit = final_value - portfolio.initial_cash
            total_profit_pct = (total_profit / portfolio.initial_cash) * 100
            
            logger.info("")
            logger.info("Performance:")
            logger.info(f"  Starting Capital: ${portfolio.initial_cash:,.2f}")
            logger.info(f"  Final Value: ${final_value:,.2f}")
            logger.info(f"  Total Profit/Loss: ${total_profit:,.2f} ({total_profit_pct:+.2f}%)")
            
        except Exception as e:
            logger.error(f"Error generating final summary: {e}")
        
        logger.info("")
        logger.info("Agent Trader stopped.")
        logger.info("Thank you for using Agent Trader! 🤖")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()