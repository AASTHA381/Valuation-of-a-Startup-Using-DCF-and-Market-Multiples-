"""
Modular Analysis Runner
Choose which parts of the valuation analysis to run
"""

from startup_valuation_model import StartupValuation
import sys

def main():
    print("🚀 MODULAR STARTUP VALUATION ANALYSIS")
    print("="*60)
    
    # Initialize the model
    valuation = StartupValuation()
    
    # Menu options
    print("\nChoose analysis to run:")
    print("1. Historical Analysis Only")
    print("2. Financial Projections Only") 
    print("3. DCF Analysis Only")
    print("4. Market Multiples Only")
    print("5. Complete Analysis")
    print("6. Quick Summary")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter your choice (1-6): ").strip()
    
    try:
        if choice == '1':
            print("\n🔍 Running Historical Analysis...")
            valuation.analyze_historical_performance()
            
        elif choice == '2':
            print("\n📈 Running Financial Projections...")
            valuation.project_financials()
            
        elif choice == '3':
            print("\n💰 Running DCF Analysis...")
            valuation.project_financials()  # Need projections first
            valuation.calculate_dcf_valuation()
            
        elif choice == '4':
            print("\n📊 Running Market Multiples Analysis...")
            valuation.market_multiples_analysis()
            
        elif choice == '5':
            print("\n🎯 Running Complete Analysis...")
            valuation.run_complete_analysis()
            
        elif choice == '6':
            print("\n⚡ Quick Summary Analysis...")
            # Run minimal analysis without charts
            historical = valuation.analyze_historical_performance()
            projections = valuation.project_financials()
            dcf = valuation.calculate_dcf_valuation()
            multiples = valuation.market_multiples_analysis()
            summary = valuation.generate_valuation_summary(dcf, multiples)
            
            print(f"\n🎯 QUICK SUMMARY RESULTS:")
            print(f"Final Valuation: ${summary['weighted_valuation']/1e6:.1f}M")
            print(f"DCF Value: ${summary['dcf_valuation']/1e6:.1f}M")
            print(f"Multiples Value: ${summary['multiples_median']/1e6:.1f}M")
            
        else:
            print("❌ Invalid choice. Please select 1-6.")
            return
            
        print("\n✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()