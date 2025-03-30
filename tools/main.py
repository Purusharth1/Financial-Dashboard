def main():
    """Test all functions in the financial dashboard tools module."""
    import sys
    from pathlib import Path

    # Add the current directory to sys.path to ensure module imports work
    sys.path.append(str(Path(__file__).parent))

    from financial_dashboard_tools import (
        analyze_multiple_assets,
        calculate_investment_return,
        get_crypto_data,
        get_financial_advice,
        get_spending_breakdown,
        get_stock_prices,
    )

    print("\n" + "=" * 50)
    print("FINANCIAL DASHBOARD TOOLS TEST")
    print("=" * 50)

    try:
        # 1. Test spending breakdown
        print("\n1. Testing Spending Breakdown Tool...")
        spending_result = get_spending_breakdown(use_bea=False)  # Use simulated data
        print("Spending breakdown generated successfully")
        print(f"Total spent: ${spending_result['total_spent']:.2f}")
        print(f"Chart saved to: {spending_result['chart_path']}")
        print(f"Categories: {list(spending_result['breakdown'].keys())}")

        # 2. Test stock price checker
        print("\n2. Testing Stock Price Checker...")
        stock_symbol = "AAPL"
        stock_result = get_stock_prices(
            symbol=stock_symbol,
            start_date="2023-01-01",
            end_date="2023-12-31",
        )
        print(f"{stock_symbol} current price: ${stock_result['current_price']:.2f}")
        if stock_result["historical_data"]:
            print(f"Historical data points: {len(stock_result['historical_data'])}")

        # 3. Test investment calculator
        print("\n3. Testing Investment Calculator...")
        investment_result = calculate_investment_return(
            symbol="MSFT",
            initial_amount=10000,
            start_date="2022-01-01",
            end_date="2023-01-01",
        )
        print("Investment result for MSFT:")
        print(f"Initial investment: ${investment_result['initial_amount']:.2f}")
        print(f"Final value: ${investment_result['final_value']:.2f}")
        print(f"Profit/Loss: ${investment_result['profit_loss']:.2f}")
        print(f"Return: {investment_result['percentage_return']:.2f}%")

        # 4. Test crypto tracker
        print("\n4. Testing Crypto Tracker...")
        crypto_result = get_crypto_data("bitcoin")
        print(f"Bitcoin current price: ${crypto_result['current_price']:.2f}")
        print(f"24h price change: {crypto_result['price_change_24h']:.2f}%")

        # print("\n4b. Testing Historical Crypto Tracker (Date Range Comparison)...")
        # historical_result = get_crypto_historical_data(
        #     crypto_id="bitcoin",
        #     from_date="2023-01-01",
        #     to_date="2023-12-31",
        # )
        # print(f"Bitcoin price change from {historical_result['from_date']} to {historical_result['to_date']}:")
        # print(f"Start price: ${historical_result['start_price']:.2f}")
        # print(f"End price: ${historical_result['end_price']:.2f}")
        # print(f"Change: ${historical_result['price_change']:.2f}")
        # print(f"Percentage change: {historical_result['price_change_percentage']:.2f}%")

        # 5. Test financial advice tool
        print("\n5. Testing Financial Advice Tool...")
        portfolio = {
            "AAPL": 0.3,
            "MSFT": 0.2,
            "AMZN": 0.2,
            "GOOGL": 0.15,
            "TSLA": 0.15,
        }
        advice_result = get_financial_advice(portfolio)
        print("Financial advice generated:")
        for suggestion in advice_result["suggestions"]:
            print(f"- {suggestion}")
        print(f"Sector weights: {advice_result['sector_weights']}")

        # 6. Test multi-tool analysis
        print("\n6. Testing Multi-Tool Analysis...")
        assets = [
            {"type": "stock", "id": "AAPL"},
            {"type": "stock", "id": "MSFT"},
            {"type": "crypto", "id": "bitcoin"},
            {"type": "crypto", "id": "ethereum"},
        ]
        analysis_result = analyze_multiple_assets(
            assets=assets,
            initial_amount=1000,
            days=30,
        )
        print("Asset returns:")
        for asset_id, asset_data in analysis_result["assets"].items():
            print(
                f"- {asset_id} ({asset_data['type']}): {asset_data['return_percentage']:.2f}%",
            )
        print(f"Best performing asset: {analysis_result['best_asset']}")

        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        print("\nSome tests failed. See error message above.")


if __name__ == "__main__":
    main()
