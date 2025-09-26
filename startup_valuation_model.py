"""
Startup Valuation Model using DCF and Market Multiples
This comprehensive model values a startup using both DCF analysis and comparable company multiples.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class StartupValuation:
    def __init__(self):
        """Initialize the valuation model with data loading."""
        self.load_data()
        self.setup_styling()
    
    def load_data(self):
        """Load all required data files."""
        try:
            self.historical_data = pd.read_csv('data/startup_financials.csv')
            self.comparable_data = pd.read_csv('data/comparable_companies.csv')
            self.parameters = pd.read_csv('data/valuation_parameters.csv')
            
            # Convert parameters to dictionary for easy access
            self.params = dict(zip(self.parameters['Parameter'], self.parameters['Value']))
            
            print("✓ Data loaded successfully")
            
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            raise
    
    def setup_styling(self):
        """Setup matplotlib and seaborn styling."""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def analyze_historical_performance(self):
        """Analyze historical financial performance."""
        print("\n" + "="*60)
        print("HISTORICAL FINANCIAL ANALYSIS")
        print("="*60)
        
        # Calculate growth rates
        revenue_growth = self.historical_data['Revenue'].pct_change().fillna(0)
        ebitda_growth = self.historical_data['EBITDA'].pct_change().fillna(0)
        
        # Calculate margins
        gross_margin = (self.historical_data['Revenue'] - self.historical_data['COGS']) / self.historical_data['Revenue']
        ebitda_margin = self.historical_data['EBITDA'] / self.historical_data['Revenue']
        
        # Display key metrics
        print(f"Revenue CAGR (2020-2024): {((self.historical_data['Revenue'].iloc[-1]/self.historical_data['Revenue'].iloc[0])**(1/4)-1)*100:.1f}%")
        print(f"Average Revenue Growth: {revenue_growth[1:].mean()*100:.1f}%")
        print(f"Average EBITDA Margin: {ebitda_margin.mean()*100:.1f}%")
        print(f"Average Gross Margin: {gross_margin.mean()*100:.1f}%")
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Revenue and EBITDA trend
        ax1.plot(self.historical_data['Year'], self.historical_data['Revenue']/1e6, marker='o', linewidth=2, label='Revenue')
        ax1.bar(self.historical_data['Year'], self.historical_data['EBITDA']/1e6, alpha=0.7, label='EBITDA')
        ax1.set_title('Revenue & EBITDA Trend', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Amount ($M)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Growth rates
        ax2.bar(self.historical_data['Year'][1:], revenue_growth[1:]*100, alpha=0.8, color='green')
        ax2.set_title('Year-over-Year Revenue Growth', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Growth Rate (%)')
        ax2.grid(True, alpha=0.3)
        
        # Margins trend
        ax3.plot(self.historical_data['Year'], gross_margin*100, marker='s', label='Gross Margin', linewidth=2)
        ax3.plot(self.historical_data['Year'], ebitda_margin*100, marker='^', label='EBITDA Margin', linewidth=2)
        ax3.set_title('Profitability Margins', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Margin (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Cash flow analysis
        ax4.bar(self.historical_data['Year'], self.historical_data['Free_Cash_Flow']/1e6, 
                color=['red' if x < 0 else 'blue' for x in self.historical_data['Free_Cash_Flow']])
        ax4.set_title('Free Cash Flow', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Free Cash Flow ($M)')
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('historical_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close figure to free memory
        
        return {
            'revenue_cagr': ((self.historical_data['Revenue'].iloc[-1]/self.historical_data['Revenue'].iloc[0])**(1/4)-1),
            'avg_revenue_growth': revenue_growth[1:].mean(),
            'avg_ebitda_margin': ebitda_margin.mean(),
            'avg_gross_margin': gross_margin.mean()
        }
    
    def project_financials(self, years=5):
        """Project future financial statements."""
        print("\n" + "="*60)
        print("FINANCIAL PROJECTIONS")
        print("="*60)
        
        # Get base year (2024) data
        base_year = self.historical_data.iloc[-1]
        
        # Projection assumptions
        revenue_growth_rates = [0.35, 0.30, 0.25, 0.20, 0.15]  # Declining growth
        ebitda_margin_improvement = [0.02, 0.015, 0.01, 0.005, 0.005]  # Margin expansion
        
        projections = []
        
        for i in range(years):
            year = 2025 + i
            
            if i == 0:
                prev_revenue = base_year['Revenue']
                prev_ebitda_margin = base_year['EBITDA'] / base_year['Revenue']
            else:
                prev_revenue = projections[i-1]['Revenue']
                prev_ebitda_margin = projections[i-1]['EBITDA'] / projections[i-1]['Revenue']
            
            # Project revenue
            revenue = prev_revenue * (1 + revenue_growth_rates[i])
            
            # Project EBITDA with margin improvement
            ebitda_margin = prev_ebitda_margin + ebitda_margin_improvement[i]
            ebitda = revenue * ebitda_margin
            
            # Project other items as % of revenue
            depreciation = revenue * 0.025  # 2.5% of revenue
            ebit = ebitda - depreciation
            interest_expense = revenue * 0.005  # 0.5% of revenue
            
            # Calculate taxes and net income
            ebt = ebit - interest_expense
            taxes = ebt * self.params['Tax_Rate']
            net_income = ebt - taxes
            
            # Calculate free cash flow
            capex = revenue * 0.03  # 3% of revenue
            working_capital_change = revenue * 0.02  # 2% of revenue increase
            free_cash_flow = net_income + depreciation - capex - working_capital_change
            
            projections.append({
                'Year': year,
                'Revenue': revenue,
                'EBITDA': ebitda,
                'EBITDA_Margin': ebitda_margin,
                'Depreciation': depreciation,
                'EBIT': ebit,
                'Interest_Expense': interest_expense,
                'Net_Income': net_income,
                'CapEx': capex,
                'Working_Capital_Change': working_capital_change,
                'Free_Cash_Flow': free_cash_flow
            })
        
        self.projections_df = pd.DataFrame(projections)
        
        # Display projections
        print("\nProjected Financial Statements (in $M):")
        display_df = self.projections_df.copy()
        for col in ['Revenue', 'EBITDA', 'EBIT', 'Net_Income', 'Free_Cash_Flow']:
            display_df[col] = display_df[col] / 1e6
        
        print(display_df[['Year', 'Revenue', 'EBITDA', 'EBITDA_Margin', 'Free_Cash_Flow']].round(2).to_string(index=False))
        
        return self.projections_df
    
    def calculate_dcf_valuation(self):
        """Calculate DCF valuation."""
        print("\n" + "="*60)
        print("DCF VALUATION ANALYSIS")
        print("="*60)
        
        # Get projected free cash flows
        fcf_projections = self.projections_df['Free_Cash_Flow'].values
        wacc = self.params['WACC']
        terminal_growth = self.params['Terminal_Growth_Rate']
        
        # Calculate present value of projected cash flows
        pv_fcf = []
        for i, fcf in enumerate(fcf_projections):
            pv = fcf / ((1 + wacc) ** (i + 1))
            pv_fcf.append(pv)
        
        # Calculate terminal value
        terminal_fcf = fcf_projections[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcf_projections))
        
        # Calculate enterprise value
        enterprise_value = sum(pv_fcf) + pv_terminal_value
        
        # Calculate equity value (assuming minimal debt and cash)
        net_debt = 0  # Assume no net debt for startup
        equity_value = enterprise_value - net_debt
        
        # Display results
        print(f"WACC: {wacc*100:.1f}%")
        print(f"Terminal Growth Rate: {terminal_growth*100:.1f}%")
        print(f"\nCash Flow Valuation:")
        print(f"PV of Projected FCF (5 years): ${sum(pv_fcf)/1e6:.1f}M")
        print(f"PV of Terminal Value: ${pv_terminal_value/1e6:.1f}M")
        print(f"Enterprise Value: ${enterprise_value/1e6:.1f}M")
        print(f"Equity Value: ${equity_value/1e6:.1f}M")
        
        # Sensitivity analysis
        self.sensitivity_analysis(fcf_projections, terminal_growth, wacc)
        
        return {
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'pv_fcf': sum(pv_fcf),
            'pv_terminal_value': pv_terminal_value,
            'terminal_value': terminal_value
        }
    
    def sensitivity_analysis(self, fcf_projections, base_terminal_growth, base_wacc):
        """Perform sensitivity analysis on key valuation drivers."""
        # Define ranges for sensitivity
        wacc_range = np.arange(base_wacc - 0.02, base_wacc + 0.03, 0.005)
        terminal_growth_range = np.arange(base_terminal_growth - 0.01, base_terminal_growth + 0.015, 0.0025)
        
        # Create sensitivity matrix
        sensitivity_matrix = np.zeros((len(wacc_range), len(terminal_growth_range)))
        
        for i, wacc in enumerate(wacc_range):
            for j, terminal_growth in enumerate(terminal_growth_range):
                # Calculate PV of projected FCF
                pv_fcf = sum([fcf / ((1 + wacc) ** (k + 1)) for k, fcf in enumerate(fcf_projections)])
                
                # Calculate terminal value
                terminal_fcf = fcf_projections[-1] * (1 + terminal_growth)
                terminal_value = terminal_fcf / (wacc - terminal_growth)
                pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcf_projections))
                
                # Total equity value
                equity_value = pv_fcf + pv_terminal_value
                sensitivity_matrix[i, j] = equity_value / 1e6  # Convert to millions
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(sensitivity_matrix, 
                    xticklabels=[f"{x:.1%}" for x in terminal_growth_range],
                    yticklabels=[f"{x:.1%}" for x in wacc_range],
                    annot=True, fmt='.0f', cmap='RdYlGn',
                    cbar_kws={'label': 'Equity Value ($M)'})
        plt.title('DCF Sensitivity Analysis\nEquity Value ($M)', fontsize=16, fontweight='bold')
        plt.xlabel('Terminal Growth Rate', fontsize=12)
        plt.ylabel('WACC', fontsize=12)
        plt.tight_layout()
        plt.savefig('dcf_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def market_multiples_analysis(self):
        """Perform market multiples valuation analysis."""
        print("\n" + "="*60)
        print("MARKET MULTIPLES ANALYSIS")
        print("="*60)
        
        # Calculate multiples for comparable companies
        public_comps = self.comparable_data[self.comparable_data['Stage'] == 'Public']
        private_comps = self.comparable_data[self.comparable_data['Stage'] == 'Private']
        
        # Current year metrics for our startup
        current_revenue = self.historical_data['Revenue'].iloc[-1]
        current_ebitda = self.historical_data['EBITDA'].iloc[-1]
        projected_revenue = self.projections_df['Revenue'].iloc[0]  # 2025 projection
        projected_ebitda = self.projections_df['EBITDA'].iloc[0]
        
        print("Comparable Company Analysis:")
        print(f"\nPublic Companies (n={len(public_comps)}):")
        print(f"Median EV/Revenue: {public_comps['EV_Revenue'].median():.1f}x")
        print(f"Median EV/EBITDA: {public_comps['EV_EBITDA'].median():.1f}x")
        
        print(f"\nPrivate Companies (n={len(private_comps)}):")
        print(f"Median EV/Revenue: {private_comps['EV_Revenue'].median():.1f}x")
        print(f"Median EV/EBITDA: {private_comps['EV_EBITDA'].median():.1f}x")
        
        # Calculate valuations using different multiples
        valuations = {}
        
        # Using public company multiples
        valuations['Public_EV_Revenue_Current'] = current_revenue * public_comps['EV_Revenue'].median()
        valuations['Public_EV_Revenue_Forward'] = projected_revenue * public_comps['EV_Revenue'].median()
        valuations['Public_EV_EBITDA_Current'] = current_ebitda * public_comps['EV_EBITDA'].median()
        valuations['Public_EV_EBITDA_Forward'] = projected_ebitda * public_comps['EV_EBITDA'].median()
        
        # Using private company multiples (more relevant for startup)
        valuations['Private_EV_Revenue_Current'] = current_revenue * private_comps['EV_Revenue'].median()
        valuations['Private_EV_Revenue_Forward'] = projected_revenue * private_comps['EV_Revenue'].median()
        valuations['Private_EV_EBITDA_Current'] = current_ebitda * private_comps['EV_EBITDA'].median()
        valuations['Private_EV_EBITDA_Forward'] = projected_ebitda * private_comps['EV_EBITDA'].median()
        
        print(f"\nValuation Results (Enterprise Value in $M):")
        print("-" * 50)
        
        for method, value in valuations.items():
            method_clean = method.replace('_', ' ').title()
            print(f"{method_clean}: ${value/1e6:.1f}M")
        
        # Create visualization
        self.plot_multiples_analysis(valuations, public_comps, private_comps)
        
        return valuations
    
    def plot_multiples_analysis(self, valuations, public_comps, private_comps):
        """Create visualizations for multiples analysis."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Multiples comparison
        ax1.boxplot([public_comps['EV_Revenue'], private_comps['EV_Revenue']], 
                   labels=['Public', 'Private'])
        ax1.set_title('EV/Revenue Multiples Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('EV/Revenue Multiple')
        ax1.grid(True, alpha=0.3)
        
        ax2.boxplot([public_comps['EV_EBITDA'], private_comps['EV_EBITDA']], 
                   labels=['Public', 'Private'])
        ax2.set_title('EV/EBITDA Multiples Comparison', fontsize=14, fontweight='bold')
        ax2.set_ylabel('EV/EBITDA Multiple')
        ax2.grid(True, alpha=0.3)
        
        # Valuation range
        methods = ['Public Rev Current', 'Public Rev Forward', 'Private Rev Current', 'Private Rev Forward']
        values = [valuations['Public_EV_Revenue_Current'], valuations['Public_EV_Revenue_Forward'],
                 valuations['Private_EV_Revenue_Current'], valuations['Private_EV_Revenue_Forward']]
        values_m = [v/1e6 for v in values]
        
        bars = ax3.bar(range(len(methods)), values_m, color=['lightblue', 'blue', 'lightcoral', 'red'])
        ax3.set_title('Revenue-Based Valuations', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Enterprise Value ($M)')
        ax3.set_xticks(range(len(methods)))
        ax3.set_xticklabels(methods, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values_m):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${value:.0f}M', ha='center', va='bottom', fontweight='bold')
        
        # EBITDA-based valuations
        methods_ebitda = ['Public EBITDA Current', 'Public EBITDA Forward', 'Private EBITDA Current', 'Private EBITDA Forward']
        values_ebitda = [valuations['Public_EV_EBITDA_Current'], valuations['Public_EV_EBITDA_Forward'],
                        valuations['Private_EV_EBITDA_Current'], valuations['Private_EV_EBITDA_Forward']]
        values_ebitda_m = [v/1e6 for v in values_ebitda]
        
        bars2 = ax4.bar(range(len(methods_ebitda)), values_ebitda_m, color=['lightgreen', 'green', 'lightyellow', 'orange'])
        ax4.set_title('EBITDA-Based Valuations', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Enterprise Value ($M)')
        ax4.set_xticks(range(len(methods_ebitda)))
        ax4.set_xticklabels(methods_ebitda, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars2, values_ebitda_m):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${value:.0f}M', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('multiples_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_valuation_summary(self, dcf_results, multiples_results):
        """Generate comprehensive valuation summary."""
        print("\n" + "="*80)
        print("COMPREHENSIVE VALUATION SUMMARY")
        print("="*80)
        
        # DCF Valuation
        dcf_equity_value = dcf_results['equity_value']
        
        # Market Multiples - focus on most relevant (private company multiples)
        relevant_multiples = {
            'Revenue (Current)': multiples_results['Private_EV_Revenue_Current'],
            'Revenue (Forward)': multiples_results['Private_EV_Revenue_Forward'],
            'EBITDA (Current)': multiples_results['Private_EV_EBITDA_Current'],
            'EBITDA (Forward)': multiples_results['Private_EV_EBITDA_Forward']
        }
        
        # Calculate statistics
        multiples_values = list(relevant_multiples.values())
        multiples_median = np.median(multiples_values)
        multiples_mean = np.mean(multiples_values)
        
        print(f"DCF Valuation: ${dcf_equity_value/1e6:.1f}M")
        print(f"\nMarket Multiples Valuation:")
        for method, value in relevant_multiples.items():
            print(f"  {method}: ${value/1e6:.1f}M")
        
        print(f"\nMultiples Statistics:")
        print(f"  Mean: ${multiples_mean/1e6:.1f}M")
        print(f"  Median: ${multiples_median/1e6:.1f}M")
        print(f"  Range: ${min(multiples_values)/1e6:.1f}M - ${max(multiples_values)/1e6:.1f}M")
        
        # Weighted average valuation
        dcf_weight = 0.6  # Give DCF higher weight for fundamental analysis
        multiples_weight = 0.4
        
        weighted_valuation = (dcf_equity_value * dcf_weight) + (multiples_median * multiples_weight)
        
        print(f"\n" + "="*50)
        print(f"FINAL VALUATION RECOMMENDATION")
        print("="*50)
        print(f"Weighted Average Valuation: ${weighted_valuation/1e6:.1f}M")
        print(f"  - DCF (60% weight): ${dcf_equity_value/1e6:.1f}M")
        print(f"  - Market Multiples (40% weight): ${multiples_median/1e6:.1f}M")
        
        print(f"\nValuation Range: ${min(min(multiples_values), dcf_equity_value)/1e6:.1f}M - ${max(max(multiples_values), dcf_equity_value)/1e6:.1f}M")
        
        # Create final summary visualization
        self.plot_valuation_summary(dcf_equity_value, relevant_multiples, weighted_valuation)
        
        return {
            'dcf_valuation': dcf_equity_value,
            'multiples_median': multiples_median,
            'weighted_valuation': weighted_valuation,
            'valuation_range': (min(min(multiples_values), dcf_equity_value), max(max(multiples_values), dcf_equity_value))
        }
    
    def plot_valuation_summary(self, dcf_value, multiples_results, weighted_value):
        """Create final valuation summary visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Valuation methods comparison
        methods = ['DCF'] + list(multiples_results.keys()) + ['Weighted Average']
        values = [dcf_value] + list(multiples_results.values()) + [weighted_value]
        values_m = [v/1e6 for v in values]
        
        colors = ['navy'] + ['lightcoral']*4 + ['gold']
        bars = ax1.bar(range(len(methods)), values_m, color=colors, alpha=0.8)
        ax1.set_title('Valuation Methods Comparison', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Enterprise Value ($M)', fontsize=12)
        ax1.set_xticks(range(len(methods)))
        ax1.set_xticklabels(methods, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, value in zip(bars, values_m):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${value:.0f}M', ha='center', va='bottom', fontweight='bold')
        
        # Valuation distribution
        ax2.hist(values_m[1:5], bins=8, alpha=0.7, color='lightcoral', label='Market Multiples')
        ax2.axvline(dcf_value/1e6, color='navy', linestyle='--', linewidth=3, label=f'DCF: ${dcf_value/1e6:.0f}M')
        ax2.axvline(weighted_value/1e6, color='gold', linestyle='-', linewidth=3, label=f'Weighted Avg: ${weighted_value/1e6:.0f}M')
        ax2.set_title('Valuation Distribution', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Enterprise Value ($M)', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('valuation_summary.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_complete_analysis(self):
        """Run the complete valuation analysis."""
        print("🚀 STARTUP VALUATION ANALYSIS")
        print("Comprehensive DCF and Market Multiples Valuation")
        print(f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}")
        
        # Step 1: Historical Analysis
        historical_metrics = self.analyze_historical_performance()
        
        # Step 2: Financial Projections
        projections = self.project_financials()
        
        # Step 3: DCF Valuation
        dcf_results = self.calculate_dcf_valuation()
        
        # Step 4: Market Multiples
        multiples_results = self.market_multiples_analysis()
        
        # Step 5: Final Summary
        final_results = self.generate_valuation_summary(dcf_results, multiples_results)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE ✅")
        print("="*80)
        print("Charts saved:")
        print("  - historical_analysis.png")
        print("  - dcf_sensitivity_analysis.png") 
        print("  - multiples_analysis.png")
        print("  - valuation_summary.png")
        
        return final_results

# Example usage and execution
if __name__ == "__main__":
    try:
        # Initialize the valuation model
        valuation_model = StartupValuation()
        
        # Run complete analysis
        results = valuation_model.run_complete_analysis()
        
        print(f"\n🎯 INVESTMENT RECOMMENDATION:")
        print(f"Target Valuation: ${results['weighted_valuation']/1e6:.1f}M")
        print(f"Valuation Range: ${results['valuation_range'][0]/1e6:.1f}M - ${results['valuation_range'][1]/1e6:.1f}M")
        
    except Exception as e:
        print(f"Error in analysis: {e}")
        import traceback
        traceback.print_exc()