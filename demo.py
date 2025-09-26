"""
Quick Demo of Startup Valuation Model
Run this script to see the complete analysis in action
"""

from startup_valuation_model import StartupValuation

def main():
    print("🚀 STARTUP VALUATION DEMO")
    print("="*50)
    
    try:
        # Initialize and run the valuation
        valuation = StartupValuation()
        results = valuation.run_complete_analysis()
        
        print("\n✅ Demo completed successfully!")
        print("Check the generated PNG files for visualizations.")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print("Make sure all data files are in the 'data' folder.")

if __name__ == "__main__":
    main()