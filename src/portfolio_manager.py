"""Portfolio Manager - Manages trading portfolio"""
from typing import Dict, Optional


class PortfolioManager:
    """
    Manages a trading portfolio with cash and stock positions.
    
    This class was developed using TDD (Test-Driven Development).
    Tests were written first in test_portfolio_manager.py
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        """
        Initialize portfolio with cash
        
        Args:
            initial_cash: Starting cash amount (default: $100,000)
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Dict[str, float]] = {}
    
    def get_portfolio_value(self, current_prices: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate total portfolio value (cash + positions)
        
        Args:
            current_prices: Dictionary of symbol -> current price
                           If None, uses average purchase prices
        
        Returns:
            Total portfolio value in dollars
        """
        total_value = self.cash
        
        for symbol, position in self.positions.items():
            quantity = position['quantity']
            
            if current_prices and symbol in current_prices:
                price = current_prices[symbol]
            else:
                price = position['avg_price']
            
            total_value += quantity * price
        
        return total_value
    
    def buy_stock(self, symbol: str, quantity: int, price: float) -> bool:
        """
        Buy stock
        
        Args:
            symbol: Stock symbol (e.g., 'PLTR')
            quantity: Number of shares to buy
            price: Price per share
        
        Returns:
            True if purchase successful, False otherwise
        """
        # Validate inputs
        if quantity <= 0:
            return False
        if price <= 0:
            return False
        
        # Calculate total cost
        total_cost = quantity * price
        
        # Check if enough cash
        if total_cost > self.cash:
            return False
        
        # Execute purchase
        self.cash -= total_cost
        
        # Update positions
        if symbol in self.positions:
            # Already own this stock - calculate new average price
            current_position = self.positions[symbol]
            current_quantity = current_position['quantity']
            current_avg_price = current_position['avg_price']
            
            # Calculate new average price
            total_shares = current_quantity + quantity
            total_cost_basis = (current_quantity * current_avg_price) + (quantity * price)
            new_avg_price = total_cost_basis / total_shares
            
            self.positions[symbol] = {
                'quantity': total_shares,
                'avg_price': new_avg_price
            }
        else:
            # New position
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': price
            }
        
        return True
    
    def sell_stock(self, symbol: str, quantity: int, price: float) -> bool:
        """
        Sell stock
        
        Args:
            symbol: Stock symbol (e.g., 'PLTR')
            quantity: Number of shares to sell
            price: Price per share
        
        Returns:
            True if sale successful, False otherwise
        """
        # Validate inputs
        if quantity <= 0:
            return False
        if price <= 0:
            return False
        
        # Check if we own this stock
        if symbol not in self.positions:
            return False
        
        # Check if we have enough shares
        current_quantity = self.positions[symbol]['quantity']
        if quantity > current_quantity:
            return False
        
        # Execute sale
        sale_proceeds = quantity * price
        self.cash += sale_proceeds
        
        # Update positions
        if quantity == current_quantity:
            # Selling all shares - remove position
            del self.positions[symbol]
        else:
            # Selling partial position
            self.positions[symbol]['quantity'] = current_quantity - quantity
        
        return True
    
    def get_position(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get information about a specific position
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with 'quantity' and 'avg_price', or None if not found
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict[str, float]]:
        """
        Get all current positions
        
        Returns:
            Dictionary of all positions
        """
        return self.positions.copy()
    
    def __repr__(self) -> str:
        """String representation of portfolio"""
        return f"PortfolioManager(cash=${self.cash:.2f}, positions={len(self.positions)})"


def main():
    """Demo of Portfolio Manager"""
    print("Portfolio Manager Demo")
    print("=" * 50)
    
    # Create portfolio
    portfolio = PortfolioManager(initial_cash=100000.0)
    print(f"Initial: {portfolio}")
    print(f"Portfolio Value: ${portfolio.get_portfolio_value():,.2f}")
    print()
    
    # Buy some stocks
    print("Buying 100 PLTR at $50...")
    if portfolio.buy_stock('PLTR', quantity=100, price=50.0):
        print("✅ Purchase successful")
    print(f"Cash: ${portfolio.cash:,.2f}")
    print(f"Positions: {portfolio.get_all_positions()}")
    print()
    
    # Buy more of the same stock
    print("Buying 100 more PLTR at $60...")
    if portfolio.buy_stock('PLTR', quantity=100, price=60.0):
        print("✅ Purchase successful")
    pltr_pos = portfolio.get_position('PLTR')
    print(f"PLTR Position: {pltr_pos}")
    print(f"Cash: ${portfolio.cash:,.2f}")
    print()
    
    # Buy different stock
    print("Buying 50 NFLX at $100...")
    if portfolio.buy_stock('NFLX', quantity=50, price=100.0):
        print("✅ Purchase successful")
    print(f"Cash: ${portfolio.cash:,.2f}")
    print()
    
    # Calculate portfolio value with current prices
    current_prices = {'PLTR': 65.0, 'NFLX': 110.0}
    print(f"Current market prices: {current_prices}")
    portfolio_value = portfolio.get_portfolio_value(current_prices)
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    profit = portfolio_value - portfolio.initial_cash
    print(f"Profit/Loss: ${profit:,.2f} ({(profit/portfolio.initial_cash)*100:.2f}%)")
    print()
    
    # Sell some stock
    print("Selling 50 PLTR at $65...")
    if portfolio.sell_stock('PLTR', quantity=50, price=65.0):
        print("✅ Sale successful")
    print(f"Cash: ${portfolio.cash:,.2f}")
    print(f"Positions: {portfolio.get_all_positions()}")
    print()
    
    # Final summary
    print("=" * 50)
    print(f"Final Portfolio: {portfolio}")
    print(f"Final Value: ${portfolio.get_portfolio_value(current_prices):,.2f}")


if __name__ == "__main__":
    main()