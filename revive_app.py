import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import BytesIO

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="REVIVE Deal Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="⚽"
)

# ========== CUSTOM STYLING ==========
st.markdown("""
    <style>
    /* REVIVE Color Scheme: Dark navy/teal with bright accents */
    :root {
        --revive-dark: #1a2332;
        --revive-blue: #0066cc;
        --revive-teal: #00a8a8;
        --revive-accent: #ff6b6b;
    }
    
    /* Main app background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2332 0%, #2c3e50 100%);
    }
    
    /* Text colors */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #00a8a8 !important;
        font-size: 32px !important;
    }
    
    /* Buttons */
    button {
        background: linear-gradient(135deg, #0066cc, #00a8a8) !important;
        color: white !important;
    }
    
    /* Input fields */
    input, select {
        background-color: #3a4a60 !important;
        color: #ffffff !important;
        border: 1px solid #0066cc !important;
    }
    
    /* Success/Warning/Error colors */
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}

# ========== PRICING DATA (from your spreadsheet) ==========
PRICING_DATA = {
    5000: {'cost': 1.80, 'charge': 4.50, 'total_cost': 9010},
    10000: {'cost': 1.70, 'charge': 4.25, 'total_cost': 17020},
    15000: {'cost': 1.65, 'charge': 4.125, 'total_cost': 24780},
    20000: {'cost': 1.58, 'charge': 3.95, 'total_cost': 31680},
    25000: {'cost': 1.56, 'charge': 3.90, 'total_cost': 39100},
    30000: {'cost': 1.50, 'charge': 3.75, 'total_cost': 44880},
    35000: {'cost': 1.48, 'charge': 3.70, 'total_cost': 51660},
    40000: {'cost': 1.46, 'charge': 3.65, 'total_cost': 58240},
    45000: {'cost': 1.44, 'charge': 3.60, 'total_cost': 64620},
    50000: {'cost': 1.42, 'charge': 3.55, 'total_cost': 70800},
}

# ========== HELPER FUNCTIONS ==========
def interpolate_cost(units):
    """Interpolate cost for units between standard tiers."""
    available_volumes = sorted(PRICING_DATA.keys())
    
    if units <= available_volumes[0]:
        return PRICING_DATA[available_volumes[0]]['cost']
    if units >= available_volumes[-1]:
        return PRICING_DATA[available_volumes[-1]]['cost']
    
    # Find surrounding volumes
    for i in range(len(available_volumes) - 1):
        if available_volumes[i] <= units < available_volumes[i + 1]:
            lower_vol = available_volumes[i]
            upper_vol = available_volumes[i + 1]
            lower_cost = PRICING_DATA[lower_vol]['cost']
            upper_cost = PRICING_DATA[upper_vol]['cost']
            
            # Linear interpolation
            ratio = (units - lower_vol) / (upper_vol - lower_vol)
            return lower_cost + (upper_cost - lower_cost) * ratio
    
    return PRICING_DATA[available_volumes[-1]]['cost']

def calculate_deal(volume, selling_price, discount_pct=0, payment_days=0, monthly_overhead=0):
    """Calculate deal profitability."""
    cost_per_unit = interpolate_cost(volume)
    
    # Adjusted price for discount
    adjusted_price = selling_price * (1 - discount_pct / 100)
    
    # Revenue and costs
    revenue = adjusted_price * volume
    total_cost = cost_per_unit * volume
    gross_profit = revenue - total_cost
    
    # Net profit (accounting for monthly overhead)
    net_profit = gross_profit - monthly_overhead
    
    # Margins
    gross_margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin_pct = (net_profit / revenue * 100) if revenue > 0 else 0
    profit_per_unit = adjusted_price - cost_per_unit
    
    # Break-even
    breakeven_units = int((monthly_overhead / profit_per_unit) + 1) if profit_per_unit > 0 else float('inf')
    
    # Working capital impact
    working_capital = (revenue * payment_days / 30) if payment_days > 0 else 0
    
    return {
        "revenue": revenue,
        "cost_per_unit": cost_per_unit,
        "total_cost": total_cost,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "gross_margin_pct": gross_margin_pct,
        "net_margin_pct": net_margin_pct,
        "profit_per_unit": profit_per_unit,
        "breakeven_units": breakeven_units,
        "working_capital": working_capital,
        "adjusted_price": adjusted_price
    }

def assess_risk(volume, payment_days, discount_pct):
    """Assess deal risk and provide flags."""
    flags = []
    risk_level = "🟢"
    
    # Volume risk
    if volume < 5000:
        flags.append("• Small order (less than 5K units)")
        risk_level = "🟡"
    
    # Payment risk
    if payment_days >= 60:
        flags.append(f"• Long payment delay ({payment_days} days) ties up cash")
        if risk_level == "🟢":
            risk_level = "🟡"
    
    if payment_days >= 90:
        flags.append("• ⚠️ Very long payment terms—major cash flow impact")
        risk_level = "🔴"
    
    # Discount risk
    if discount_pct >= 15:
        flags.append(f"• Heavy discount ({discount_pct}%) reduces margin")
        if risk_level == "🟢":
            risk_level = "🟡"
    
    if discount_pct >= 25:
        flags.append("• ⚠️ Discount too high—may not be worth it")
        risk_level = "🔴"
    
    return risk_level, flags

def get_recommendation(result, risk_level):
    """Get actionable recommendation."""
    profit = result['net_profit']
    margin = result['net_margin_pct']
    
    if risk_level == "🔴" or profit < 0:
        return "❌ DO NOT TAKE THIS DEAL", "Revise terms before proceeding."
    elif risk_level == "🟡":
        return "⚠️ PROCEED WITH CAUTION", "Negotiate better terms or higher volume."
    else:
        if margin > 55:
            return "✅ EXCELLENT DEAL", "This is a great opportunity. Move forward."
        elif margin > 50:
            return "✅ GOOD DEAL", "Strong profitability. Recommended."
        else:
            return "✅ ACCEPTABLE", "Profitable but thin margin. Consider negotiating."

# ========== HEADER ==========
col_logo, col_title = st.columns([1, 3])

with col_logo:
    st.markdown("### ⚽ REVIVE")

with col_title:
    st.title("Deal Analyzer")

st.markdown("---")

# ========== MAIN INTERFACE ==========
col_form, col_result = st.columns([2, 1.5], gap="large")

with col_form:
    st.subheader("📋 Quick Deal Analysis")
    
    # Deal name
    deal_name = st.text_input(
        "Deal Name",
        value=f"Deal_{datetime.now().strftime('%m%d_%H%M')}",
        help="Give this deal a memorable name (e.g., 'Retailer ABC - Q2')"
    )
    
    st.markdown("**Your Baseline Costs**")
    col_cost1, col_cost2 = st.columns(2)
    
    with col_cost1:
        monthly_overhead = st.number_input(
            "Monthly Overhead ($)",
            min_value=0,
            max_value=100000,
            value=0,
            step=1000,
            help="Rent, staff, utilities, etc. (Leave at 0 if you only want gross profit)"
        )
    
    with col_cost2:
        st.metric("Cost Reference (5K units)", "$1.80/skin")
    
    st.markdown("**Their Offer**")
    col_vol, col_price = st.columns(2)
    
    with col_vol:
        order_volume = st.number_input(
            "Order Volume (units)",
            min_value=1000,
            max_value=100000,
            value=5000,
            step=500,
            help="How many skins are they ordering?"
        )
    
    with col_price:
        selling_price = st.number_input(
            "Your Selling Price ($/unit)",
            min_value=1.0,
            max_value=10.0,
            value=4.50,
            step=0.05,
            help="What are you charging per skin?"
        )
    
    st.markdown("**Terms**")
    col_discount, col_payment = st.columns(2)
    
    with col_discount:
        discount_pct = st.slider(
            "Discount (%)",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
            help="Bulk discount from your asking price (0% = no discount)"
        )
    
    with col_payment:
        payment_days = st.select_slider(
            "Payment Terms",
            options=[0, 15, 30, 45, 60, 90],
            value=0,
            help="When do they pay you? (0 = upfront, 30 = Net 30, etc.)"
        )
    
    st.markdown("---")
    analyze_btn = st.button("🔍 ANALYZE DEAL", use_container_width=True, type="primary")

with col_result:
    st.subheader("💰 Result")
    
    if analyze_btn or True:  # Always show result
        result = calculate_deal(order_volume, selling_price, discount_pct, payment_days, monthly_overhead)
        risk_level, flags = assess_risk(order_volume, payment_days, discount_pct)
        rec_title, rec_detail = get_recommendation(result, risk_level)
        
        # KPI Cards
        st.metric(
            "💵 Net Profit",
            f"${result['net_profit']:,.0f}",
            f"{result['net_margin_pct']:.1f}% margin"
        )
        
        st.metric(
            "💸 Per Skin Profit",
            f"${result['profit_per_unit']:.2f}"
        )
        
        st.metric(
            "📊 Gross Revenue",
            f"${result['revenue']:,.0f}"
        )
        
        # Risk and recommendation
        st.markdown(f"### {risk_level} Risk Level")
        
        if flags:
            for flag in flags:
                st.warning(flag, icon="⚠️")
        
        st.markdown(f"### {rec_title}")
        st.info(rec_detail, icon="💡")

# ========== DETAILS SECTION ==========
st.markdown("---")

with st.expander("📈 Full Financial Details", expanded=False):
    col_det1, col_det2, col_det3 = st.columns(3)
    
    with col_det1:
        st.metric("Cost per Unit", f"${result['cost_per_unit']:.2f}")
        st.metric("Adjusted Price", f"${result['adjusted_price']:.2f}")
    
    with col_det2:
        st.metric("Total Manufactured Cost", f"${result['total_cost']:,.0f}")
        st.metric("Gross Profit", f"${result['gross_profit']:,.0f}")
    
    with col_det3:
        st.metric("Monthly Overhead", f"${monthly_overhead:,.0f}")
        st.metric("Net Profit", f"${result['net_profit']:,.0f}")
    
    st.markdown("---")
    
    col_break, col_wc = st.columns(2)
    
    with col_break:
        st.metric("Break-Even Volume", f"{result['breakeven_units']:,} units")
        st.caption(f"vs. ordering {order_volume:,} units")
    
    with col_wc:
        st.metric("Working Capital (tied up)", f"${result['working_capital']:,.0f}")
        st.caption(f"For {payment_days} days")

# ========== SCENARIO COMPARISON ==========
st.markdown("---")

col_save, col_compare, col_export = st.columns([1, 2, 1])

with col_save:
    if st.button("💾 Save This Deal", use_container_width=True):
        st.session_state.scenarios[deal_name] = {
            "volume": order_volume,
            "price": selling_price,
            "discount": discount_pct,
            "payment_days": payment_days,
            "monthly_overhead": monthly_overhead,
            "result": result,
            "risk": risk_level,
            "timestamp": datetime.now().isoformat()
        }
        st.success(f"✅ Saved: {deal_name}")

with col_compare:
    if st.session_state.scenarios:
        st.markdown("### 📊 Saved Deals")
        
        # Create comparison dataframe
        comparison_data = []
        for name, data in st.session_state.scenarios.items():
            comparison_data.append({
                "Deal": name,
                "Volume": f"{data['volume']:,}",
                "Price/Unit": f"${data['price']:.2f}",
                "Profit": f"${data['result']['net_profit']:,.0f}",
                "Margin": f"{data['result']['net_margin_pct']:.1f}%",
                "Risk": data['risk']
            })
        
        df_compare = pd.DataFrame(comparison_data)
        st.dataframe(df_compare, use_container_width=True, hide_index=True)
        
        # Clear all scenarios
        if st.button("🗑️ Clear All Saved Deals", use_container_width=False):
            st.session_state.scenarios = {}
            st.rerun()

with col_export:
    if st.button("📄 Export as JSON", use_container_width=True):
        json_str = json.dumps(st.session_state.scenarios, indent=2, default=str)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"revive_deals_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px; margin-top: 30px;'>
        <p><strong>REVIVE Pickleball Skins Deal Analyzer</strong></p>
        <p>Smart decisions for paddle skin deals • Built for your business</p>
    </div>
""", unsafe_allow_html=True)
