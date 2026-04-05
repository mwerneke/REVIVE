import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="REVIVE",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚽"
)

# ========== PREMIUM STYLING ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Main container */
    [data-testid="stAppViewContainer"] {
        background: #000000;
        color: #ffffff;
    }
    
    /* Sidebar hidden but available */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    
    p, span, label {
        font-family: 'Outfit', sans-serif;
        font-weight: 400;
        color: #ffffff;
    }
    
    /* Input fields - clean and minimal */
    input, select, textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
        font-family: 'Outfit', sans-serif !important;
        padding: 10px 12px !important;
    }
    
    input:focus, select:focus {
        border-color: #ffffff !important;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.1) !important;
    }
    
    /* Buttons - premium look */
    button {
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        cursor: pointer;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 13px;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(255,255,255,0.2) !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #888888 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #888888 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        font-family: 'Outfit', sans-serif !important;
        padding: 12px 0 !important;
        border-radius: 0 !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
        border-bottom-color: #ffffff !important;
        transform: none !important;
    }
    
    button[aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #ffffff !important;
    }
    
    /* Cards and containers */
    [data-testid="stContainer"] {
        background: transparent;
    }
    
    /* Divider */
    hr {
        border-color: #333333 !important;
    }
    
    /* Alerts */
    .stAlert {
        background: rgba(255,255,255,0.05) !important;
        border-left: 3px solid #ffffff !important;
        border-radius: 4px !important;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
if "scenarios" not in st.session_state:
    st.session_state.scenarios = {}
if "orders" not in st.session_state:
    st.session_state.orders = []

# ========== PRICING DATA ==========
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
    available_volumes = sorted(PRICING_DATA.keys())
    if units <= available_volumes[0]:
        return PRICING_DATA[available_volumes[0]]['cost']
    if units >= available_volumes[-1]:
        return PRICING_DATA[available_volumes[-1]]['cost']
    for i in range(len(available_volumes) - 1):
        if available_volumes[i] <= units < available_volumes[i + 1]:
            lower_vol = available_volumes[i]
            upper_vol = available_volumes[i + 1]
            lower_cost = PRICING_DATA[lower_vol]['cost']
            upper_cost = PRICING_DATA[upper_vol]['cost']
            ratio = (units - lower_vol) / (upper_vol - lower_vol)
            return lower_cost + (upper_cost - lower_cost) * ratio
    return PRICING_DATA[available_volumes[-1]]['cost']

def calculate_deal(volume, selling_price, discount_pct=0, payment_days=0, monthly_overhead=0):
    cost_per_unit = interpolate_cost(volume)
    adjusted_price = selling_price * (1 - discount_pct / 100)
    revenue = adjusted_price * volume
    total_cost = cost_per_unit * volume
    gross_profit = revenue - total_cost
    net_profit = gross_profit - monthly_overhead
    gross_margin_pct = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_margin_pct = (net_profit / revenue * 100) if revenue > 0 else 0
    profit_per_unit = adjusted_price - cost_per_unit
    breakeven_units = int((monthly_overhead / profit_per_unit) + 1) if profit_per_unit > 0 else float('inf')
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
    flags = []
    risk_level = "🟢"
    if volume < 5000:
        flags.append("• Small order (less than 5K units)")
        risk_level = "🟡"
    if payment_days >= 60:
        flags.append(f"• Long payment delay ({payment_days} days)")
        if risk_level == "🟢":
            risk_level = "🟡"
    if payment_days >= 90:
        risk_level = "🔴"
    if discount_pct >= 15:
        flags.append(f"• Heavy discount ({discount_pct}%)")
        if risk_level == "🟢":
            risk_level = "🟡"
    if discount_pct >= 25:
        risk_level = "🔴"
    return risk_level, flags

def get_recommendation(result, risk_level):
    profit = result['net_profit']
    margin = result['net_margin_pct']
    if risk_level == "🔴" or profit < 0:
        return "❌ PASS", "Revise terms before proceeding."
    elif risk_level == "🟡":
        return "⚠️ NEGOTIATE", "Better terms or higher volume needed."
    else:
        if margin > 55:
            return "✅ EXCELLENT", "Strong opportunity. Move forward."
        elif margin > 50:
            return "✅ GOOD", "Recommended."
        else:
            return "✅ ACCEPTABLE", "Profitable. Consider negotiating."

# ========== PAGES ==========

def landing_page():
    """Premium landing page with REVIVE logo"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Display logo - centered and auto-fit
        st.image("/mnt/project/white_textlogoname_transparent_background.png", use_column_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <h2 style='text-align: center; font-size: 24px; color: #888888; font-weight: 300; letter-spacing: 0.15em;'>
                PICKLEBALL SKINS MANAGEMENT PLATFORM
            </h2>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Two main options
        col_deal, col_ops = st.columns(2, gap="large")
        
        with col_deal:
            st.markdown("""
                <div style='text-align: center; padding: 40px 20px; border: 1px solid #333333; border-radius: 4px; transition: all 0.3s ease; cursor: pointer;' 
                     onmouseover="this.style.borderColor='#ffffff'; this.style.backgroundColor='rgba(255,255,255,0.02)';"
                     onmouseout="this.style.borderColor='#333333'; this.style.backgroundColor='transparent';">
                    <h3 style='font-size: 20px; margin-bottom: 12px;'>DEAL ANALYZER</h3>
                    <p style='color: #888888; font-size: 13px; line-height: 1.6;'>Instant profitability analysis. Risk assessment. Deal recommendations.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("ENTER ANALYZER", key="btn_analyzer", use_container_width=True):
                st.session_state.current_page = "analyzer"
                st.rerun()
        
        with col_ops:
            st.markdown("""
                <div style='text-align: center; padding: 40px 20px; border: 1px solid #333333; border-radius: 4px; transition: all 0.3s ease; cursor: pointer;'
                     onmouseover="this.style.borderColor='#ffffff'; this.style.backgroundColor='rgba(255,255,255,0.02)';"
                     onmouseout="this.style.borderColor='#333333'; this.style.backgroundColor='transparent';">
                    <h3 style='font-size: 20px; margin-bottom: 12px;'>OPERATIONS</h3>
                    <p style='color: #888888; font-size: 13px; line-height: 1.6;'>Order tracking. Supplier management. Financial overview.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("ENTER OPERATIONS", key="btn_operations", use_container_width=True):
                st.session_state.current_page = "operations"
                st.rerun()
        
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        
        st.markdown("""
            <p style='text-align: center; color: #666666; font-size: 12px; letter-spacing: 0.1em;'>
                REVIVE • RESTORE • REVITALIZE
            </p>
        """, unsafe_allow_html=True)

def analyzer_page():
    """Deal analyzer with sleek interface"""
    
    # Header with navigation
    col_back, col_title, col_empty = st.columns([1, 2, 1])
    with col_back:
        if st.button("← BACK", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
    
    with col_title:
        st.markdown("<h1 style='text-align: center; margin: 0;'>DEAL ANALYZER</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_form, col_result = st.columns([2, 1.5], gap="large")
    
    with col_form:
        st.markdown("<h3 style='margin-top: 0;'>ANALYZE DEAL</h3>", unsafe_allow_html=True)
        
        deal_name = st.text_input("Deal Name", value=f"Deal_{datetime.now().strftime('%m%d_%H%M')}")
        
        st.markdown("<p style='color: #888888; font-size: 12px; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 0.1em;'>Your Baseline</p>", unsafe_allow_html=True)
        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            monthly_overhead = st.number_input("Monthly Overhead ($)", min_value=0, max_value=100000, value=0, step=1000)
        with col_cost2:
            st.metric("Cost Reference (5K)", "$1.80/skin")
        
        st.markdown("<p style='color: #888888; font-size: 12px; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 0.1em;'>Their Order</p>", unsafe_allow_html=True)
        col_vol, col_price = st.columns(2)
        with col_vol:
            order_volume = st.number_input("Volume (units)", min_value=1000, max_value=100000, value=5000, step=500)
        with col_price:
            selling_price = st.number_input("Price ($/unit)", min_value=1.0, max_value=10.0, value=4.50, step=0.05)
        
        st.markdown("<p style='color: #888888; font-size: 12px; margin: 16px 0 8px; text-transform: uppercase; letter-spacing: 0.1em;'>Terms</p>", unsafe_allow_html=True)
        col_discount, col_payment = st.columns(2)
        with col_discount:
            discount_pct = st.slider("Discount (%)", min_value=0, max_value=50, value=0, step=1)
        with col_payment:
            payment_days = st.select_slider("Payment (days)", options=[0, 15, 30, 45, 60, 90], value=0)
        
        st.markdown("---")
        analyze_btn = st.button("ANALYZE", use_container_width=True)
    
    with col_result:
        st.markdown("<h3 style='margin-top: 0;'>RESULT</h3>", unsafe_allow_html=True)
        
        result = calculate_deal(order_volume, selling_price, discount_pct, payment_days, monthly_overhead)
        risk_level, flags = assess_risk(order_volume, payment_days, discount_pct)
        rec_title, rec_detail = get_recommendation(result, risk_level)
        
        st.metric("NET PROFIT", f"${result['net_profit']:,.0f}", f"{result['net_margin_pct']:.1f}% margin")
        st.metric("PER UNIT", f"${result['profit_per_unit']:.2f}")
        st.metric("REVENUE", f"${result['revenue']:,.0f}")
        
        st.markdown(f"<h4>{risk_level} RISK</h4>", unsafe_allow_html=True)
        
        if flags:
            for flag in flags:
                st.warning(flag, icon="⚠️")
        
        st.markdown(f"<h4>{rec_title}</h4>", unsafe_allow_html=True)
        st.info(rec_detail, icon="💡")
    
    # Details section
    st.markdown("---")
    with st.expander("FULL DETAILS"):
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Cost/Unit", f"${result['cost_per_unit']:.2f}")
            st.metric("Gross Profit", f"${result['gross_profit']:,.0f}")
        with col_d2:
            st.metric("Adjusted Price", f"${result['adjusted_price']:.2f}")
            st.metric("Breakeven Vol", f"{result['breakeven_units']:,}")
        with col_d3:
            st.metric("Overhead", f"${monthly_overhead:,.0f}")
            st.metric("Working Capital", f"${result['working_capital']:,.0f}")
    
    # Save scenario
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("SAVE DEAL", use_container_width=True):
            st.session_state.scenarios[deal_name] = {
                "volume": order_volume,
                "price": selling_price,
                "discount": discount_pct,
                "payment_days": payment_days,
                "result": result,
                "risk": risk_level,
                "timestamp": datetime.now().isoformat()
            }
            st.success(f"✅ Saved: {deal_name}")
    
    with col_s2:
        if st.session_state.scenarios and st.button("COMPARE DEALS", use_container_width=True):
            comparison_data = []
            for name, data in st.session_state.scenarios.items():
                comparison_data.append({
                    "Deal": name,
                    "Volume": f"{data['volume']:,}",
                    "Price": f"${data['price']:.2f}",
                    "Profit": f"${data['result']['net_profit']:,.0f}",
                    "Margin": f"{data['result']['net_margin_pct']:.1f}%",
                    "Risk": data['risk']
                })
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def operations_page():
    """Operations dashboard with order tracking and financials"""
    
    # Header with navigation
    col_back, col_title = st.columns([1, 3])
    with col_back:
        if st.button("← BACK", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
    with col_title:
        st.markdown("<h1 style='text-align: center; margin: 0;'>OPERATIONS DASHBOARD</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tab interface
    tab1, tab2, tab3, tab4 = st.tabs(["ORDERS", "SUPPLIERS", "FINANCIALS", "VALUATION"])
    
    with tab1:
        st.markdown("<h3>ORDER MANAGEMENT</h3>", unsafe_allow_html=True)
        
        col_new, col_view = st.columns(2)
        with col_new:
            with st.expander("NEW ORDER"):
                order_date = st.date_input("Order Date")
                order_customer = st.text_input("Customer Name")
                order_volume = st.number_input("Volume", min_value=1000, value=5000, step=500)
                order_price = st.number_input("Price/Unit", min_value=1.0, value=4.50, step=0.05)
                order_status = st.selectbox("Status", ["Pending", "In Production", "Completed", "Delivered", "Paid"])
                
                if st.button("ADD ORDER"):
                    new_order = {
                        "date": order_date.isoformat(),
                        "customer": order_customer,
                        "volume": order_volume,
                        "price": order_price,
                        "status": order_status,
                        "revenue": order_volume * order_price,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.orders.append(new_order)
                    st.success("✅ Order added")
        
        with col_view:
            st.markdown("<h4>Recent Orders</h4>", unsafe_allow_html=True)
            if st.session_state.orders:
                orders_df = pd.DataFrame(st.session_state.orders)
                orders_display = orders_df[["customer", "volume", "price", "status", "revenue"]].copy()
                orders_display["revenue"] = orders_display["revenue"].apply(lambda x: f"${x:,.0f}")
                st.dataframe(orders_display, use_container_width=True, hide_index=True)
            else:
                st.info("No orders yet. Create your first order →")
    
    with tab2:
        st.markdown("<h3>SUPPLIER MANAGEMENT</h3>", unsafe_allow_html=True)
        
        col_sup1, col_sup2 = st.columns(2)
        with col_sup1:
            st.markdown("<h4>Current Suppliers</h4>", unsafe_allow_html=True)
            suppliers = [
                {"name": "Primary Manufacturer", "lead_time": "2-3 weeks", "cost": "$1.42-$1.80/unit", "status": "Active"},
                {"name": "Backup Supplier", "lead_time": "3-4 weeks", "cost": "$1.50-$1.90/unit", "status": "Standby"}
            ]
            suppliers_df = pd.DataFrame(suppliers)
            st.dataframe(suppliers_df, use_container_width=True, hide_index=True)
        
        with col_sup2:
            st.markdown("<h4>Supplier Performance</h4>", unsafe_allow_html=True)
            perf = [
                {"metric": "On-Time Delivery", "score": "98%"},
                {"metric": "Quality (Defect Rate)", "score": "<2%"},
                {"metric": "Cost Efficiency", "score": "Excellent"},
                {"metric": "Communication", "score": "Responsive"}
            ]
            perf_df = pd.DataFrame(perf)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("<h3>FINANCIAL OVERVIEW</h3>", unsafe_allow_html=True)
        
        # Calculate financials from orders
        if st.session_state.orders:
            total_revenue = sum(order["revenue"] for order in st.session_state.orders)
            total_units = sum(order["volume"] for order in st.session_state.orders)
            avg_price = total_revenue / total_units if total_units > 0 else 0
            total_cost = sum(order["volume"] * interpolate_cost(order["volume"]) for order in st.session_state.orders)
            total_profit = total_revenue - total_cost
            margin_pct = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                st.metric("Total Revenue", f"${total_revenue:,.0f}")
            with col_f2:
                st.metric("Total Profit", f"${total_profit:,.0f}")
            with col_f3:
                st.metric("Profit Margin", f"{margin_pct:.1f}%")
            with col_f4:
                st.metric("Total Units", f"{total_units:,}")
            
            st.markdown("---")
            
            # Monthly breakdown
            orders_df = pd.DataFrame(st.session_state.orders)
            orders_df['date'] = pd.to_datetime(orders_df['date'])
            orders_df['month'] = orders_df['date'].dt.to_period('M')
            
            monthly_data = orders_df.groupby('month').agg({
                'revenue': 'sum',
                'volume': 'sum'
            }).reset_index()
            
            if len(monthly_data) > 0:
                st.markdown("<h4>Monthly Revenue Trend</h4>", unsafe_allow_html=True)
                fig = px.bar(monthly_data, x='month', y='revenue', 
                            labels={'revenue': 'Revenue ($)', 'month': 'Month'},
                            color_discrete_sequence=['#ffffff'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title='Month',
                    yaxis_title='Revenue ($)',
                    font=dict(family='Outfit', color='#ffffff'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Create orders to see financial analysis")
    
    with tab4:
        st.markdown("<h3>COMPANY VALUATION</h3>", unsafe_allow_html=True)
        
        # Valuation metrics based on business analysis
        st.markdown("""
            <div style='background: rgba(255,255,255,0.02); border: 1px solid #333333; padding: 24px; border-radius: 4px;'>
                <h4>Valuation Summary</h4>
                <p style='color: #888888; margin: 16px 0;'>Based on your pickleball skins business model with 60% gross margins and growing market demand.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_v1, col_v2, col_v3 = st.columns(3)
        
        with col_v1:
            st.markdown("""
                <div style='text-align: center; padding: 20px; border: 1px solid #333333; border-radius: 4px;'>
                    <p style='color: #888888; font-size: 11px; text-transform: uppercase; margin-bottom: 8px;'>Year 1 Revenue</p>
                    <h3 style='font-size: 24px;'>$2.5M - $10M</h3>
                </div>
            """, unsafe_allow_html=True)
        
        with col_v2:
            st.markdown("""
                <div style='text-align: center; padding: 20px; border: 1px solid #333333; border-radius: 4px;'>
                    <p style='color: #888888; font-size: 11px; text-transform: uppercase; margin-bottom: 8px;'>Year 1 Profit</p>
                    <h3 style='font-size: 24px;'>$1.5M - $6M</h3>
                </div>
            """, unsafe_allow_html=True)
        
        with col_v3:
            st.markdown("""
                <div style='text-align: center; padding: 20px; border: 1px solid #333333; border-radius: 4px;'>
                    <p style='color: #888888; font-size: 11px; text-transform: uppercase; margin-bottom: 8px;'>Profit Margin</p>
                    <h3 style='font-size: 24px;'>60%</h3>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("<h4>Valuation Drivers</h4>", unsafe_allow_html=True)
        
        col_val1, col_val2 = st.columns(2)
        
        with col_val1:
            st.markdown("""
                <h5 style='margin-bottom: 12px;'>Market Fundamentals</h5>
                <ul style='color: #888888; padding-left: 20px; line-height: 2;'>
                    <li>Pickleball growth: +15%/year</li>
                    <li>US market: 5M+ players</li>
                    <li>Addressable market: 1M+ potential customers</li>
                    <li>No major competitors</li>
                </ul>
            """, unsafe_allow_html=True)
        
        with col_val2:
            st.markdown("""
                <h5 style='margin-bottom: 12px;'>Business Strengths</h5>
                <ul style='color: #888888; padding-left: 20px; line-height: 2;'>
                    <li>60% gross margins (top 5% of mfg)</li>
                    <li>Low capital requirements</li>
                    <li>Repeat revenue (skins wear out)</li>
                    <li>Customizable IP protection</li>
                </ul>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("<h4>Conservative Valuation (Year 3)</h4>", unsafe_allow_html=True)
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("Revenue", "$10M - $50M")
        with col_m2:
            st.metric("EBITDA", "$6M - $30M")
        with col_m3:
            st.metric("Multiple", "5-10x EBITDA")
        with col_m4:
            st.metric("Est. Value", "$30M - $300M")
        
        st.markdown("""
            <p style='color: #666666; font-size: 11px; margin-top: 16px;'>
                Valuation based on SaaS/B2B manufacturing comparables (5-10x EBITDA). 
                Conservative estimate assumes 20% of addressable market captured by Year 3.
            </p>
        """, unsafe_allow_html=True)

# ========== MAIN APP ==========

if st.session_state.current_page == "landing":
    landing_page()
elif st.session_state.current_page == "analyzer":
    analyzer_page()
elif st.session_state.current_page == "operations":
    operations_page()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; margin-top: 40px; padding-bottom: 20px;'>
        <p style='color: #666666; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;'>
            REVIVE MANAGEMENT SYSTEM • 2024
        </p>
    </div>
""", unsafe_allow_html=True)
