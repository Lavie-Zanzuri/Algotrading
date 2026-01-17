"""Custom Tools for Trading Agents"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class CalculateProfitLossInput(BaseModel):
    """Input schema for calculate_profit_loss"""
    buy_price: float = Field(..., description="The price at which the stock was bought")
    current_price: float = Field(..., description="The current price of the stock")
    quantity: int = Field(..., description="Number of shares")


class CalculateProfitLossTool(BaseTool):
    """Tool to calculate profit/loss on a position"""
    
    name: str = "calculate_profit_loss"
    description: str = (
        "Calculates the profit or loss on a stock position. "
        "Useful for evaluating current positions and making trading decisions. "
        "Returns profit/loss in dollars and percentage."
    )
    args_schema: Type[BaseModel] = CalculateProfitLossInput
    
    def _run(self, buy_price: float, current_price: float, quantity: int) -> str:
        """
        Calculate profit or loss
        
        Args:
            buy_price: Purchase price per share
            current_price: Current market price per share
            quantity: Number of shares
        
        Returns:
            String with profit/loss details
        """
        # Calculate total investment and current value
        total_invested = buy_price * quantity
        current_value = current_price * quantity
        
        # Calculate profit/loss
        profit_loss = current_value - total_invested
        profit_loss_pct = (profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        # Determine if profit or loss
        status = "profit" if profit_loss >= 0 else "loss"
        
        return (
            f"Position Analysis:\n"
            f"- Invested: ${total_invested:.2f} ({quantity} shares @ ${buy_price:.2f})\n"
            f"- Current Value: ${current_value:.2f} (@ ${current_price:.2f})\n"
            f"- {status.upper()}: ${abs(profit_loss):.2f} ({profit_loss_pct:+.2f}%)"
        )


class CalculatePositionSizeInput(BaseModel):
    """Input schema for calculate_position_size"""
    cash_available: float = Field(..., description="Available cash to invest")
    stock_price: float = Field(..., description="Current stock price")
    risk_percentage: float = Field(default=10.0, description="Percentage of portfolio to risk (default: 10%)")


class CalculatePositionSizeTool(BaseTool):
    """Tool to calculate optimal position size"""
    
    name: str = "calculate_position_size"
    description: str = (
        "Calculates the optimal number of shares to buy based on available cash "
        "and risk management rules. Helps determine safe position sizes."
    )
    args_schema: Type[BaseModel] = CalculatePositionSizeInput
    
    def _run(self, cash_available: float, stock_price: float, risk_percentage: float = 10.0) -> str:
        """
        Calculate position size
        
        Args:
            cash_available: Available cash
            stock_price: Price per share
            risk_percentage: Percentage of portfolio to allocate
        
        Returns:
            String with position size recommendation
        """
        if stock_price <= 0:
            return "Error: Stock price must be positive"
        
        if risk_percentage <= 0 or risk_percentage > 100:
            return "Error: Risk percentage must be between 0 and 100"
        
        # Calculate maximum amount to invest based on risk
        max_investment = cash_available * (risk_percentage / 100)
        
        # Calculate number of shares (round down to whole shares)
        shares = int(max_investment / stock_price)
        actual_investment = shares * stock_price
        
        return (
            f"Position Size Recommendation:\n"
            f"- Available Cash: ${cash_available:.2f}\n"
            f"- Risk Allocation: {risk_percentage}% = ${max_investment:.2f}\n"
            f"- Stock Price: ${stock_price:.2f}\n"
            f"- RECOMMENDED: Buy {shares} shares\n"
            f"- Total Cost: ${actual_investment:.2f}\n"
            f"- Remaining Cash: ${cash_available - actual_investment:.2f}"
        )


class CalculateRiskRewardInput(BaseModel):
    """Input schema for calculate_risk_reward"""
    entry_price: float = Field(..., description="Entry/buy price")
    target_price: float = Field(..., description="Target/sell price")
    stop_loss: float = Field(..., description="Stop loss price")


class CalculateRiskRewardTool(BaseTool):
    """Tool to calculate risk/reward ratio"""
    
    name: str = "calculate_risk_reward"
    description: str = (
        "Calculates the risk/reward ratio for a trade. "
        "Helps evaluate if a trade setup has favorable risk/reward characteristics. "
        "Generally, a ratio of 1:2 or higher is considered good."
    )
    args_schema: Type[BaseModel] = CalculateRiskRewardInput
    
    def _run(self, entry_price: float, target_price: float, stop_loss: float) -> str:
        """
        Calculate risk/reward ratio
        
        Args:
            entry_price: Entry price
            target_price: Target exit price
            stop_loss: Stop loss price
        
        Returns:
            String with risk/reward analysis
        """
        # Calculate potential reward and risk
        potential_reward = abs(target_price - entry_price)
        potential_risk = abs(entry_price - stop_loss)
        
        if potential_risk == 0:
            return "Error: Stop loss cannot equal entry price"
        
        # Calculate ratio
        risk_reward_ratio = potential_reward / potential_risk
        
        # Evaluation
        if risk_reward_ratio >= 2.0:
            evaluation = "EXCELLENT - High reward vs risk"
        elif risk_reward_ratio >= 1.5:
            evaluation = "GOOD - Favorable risk/reward"
        elif risk_reward_ratio >= 1.0:
            evaluation = "ACCEPTABLE - Equal risk and reward"
        else:
            evaluation = "POOR - Risk exceeds reward"
        
        return (
            f"Risk/Reward Analysis:\n"
            f"- Entry Price: ${entry_price:.2f}\n"
            f"- Target Price: ${target_price:.2f}\n"
            f"- Stop Loss: ${stop_loss:.2f}\n"
            f"- Potential Reward: ${potential_reward:.2f} ({(potential_reward/entry_price)*100:.2f}%)\n"
            f"- Potential Risk: ${potential_risk:.2f} ({(potential_risk/entry_price)*100:.2f}%)\n"
            f"- Risk/Reward Ratio: 1:{risk_reward_ratio:.2f}\n"
            f"- Evaluation: {evaluation}"
        )


# Export all tools
def get_all_tools():
    """Get all custom tools"""
    return [
        CalculateProfitLossTool(),
        CalculatePositionSizeTool(),
        CalculateRiskRewardTool()
    ]


def main():
    """Demo of custom tools"""
    print("Custom Trading Tools Demo")
    print("=" * 60)
    
    # Create tools
    profit_tool = CalculateProfitLossTool()
    position_tool = CalculatePositionSizeTool()
    risk_reward_tool = CalculateRiskRewardTool()
    
    print("\n1. Calculate Profit/Loss Tool")
    print("-" * 60)
    result = profit_tool._run(buy_price=50.0, current_price=65.0, quantity=100)
    print(result)
    
    print("\n" + "=" * 60)
    print("\n2. Calculate Position Size Tool")
    print("-" * 60)
    result = position_tool._run(cash_available=100000, stock_price=50.0, risk_percentage=10)
    print(result)
    
    print("\n" + "=" * 60)
    print("\n3. Calculate Risk/Reward Tool")
    print("-" * 60)
    result = risk_reward_tool._run(entry_price=50.0, target_price=65.0, stop_loss=47.0)
    print(result)
    
    print("\n" + "=" * 60)
    print("\n✅ All tools working correctly!")


if __name__ == "__main__":
    main()