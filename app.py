import streamlit as st
import math
import pandas as pd
from scipy.optimize import linprog
import yfinance as yf

# ==========================================
# 1. PAGE SETUP & UI CONFIG
# ==========================================
st.set_page_config(page_title="Commercial Blending Desk", layout="wide")
st.title("🛢️ Refinery Blending & Arbitrage Dashboard")
st.markdown("Dynamic Linear Programming Optimizer for USGC 87 Regular Gasoline")

# ==========================================
# 2. CORE OPTIMIZER FUNCTION (From Section 4)
# ==========================================
def run_blending_optimizer(prices, ron_specs, rvp_idx, inventories, batch_size):
    num_components = len(prices)
    c = prices
    target_rvp_index = 9.0 ** 1.25
    
    A_ub = [[-ron for ron in ron_specs], rvp_idx]
    b_ub = [-87.0, target_rvp_index]
    
    A_eq = [[1.0] * num_components]
    b_eq = [1.0]
    
    bounds = []
    for i in range(num_components):
        max_physical_fraction = inventories[i] / batch_size
        bounds.append((0, min(1.0, max_physical_fraction)))
        
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if result.success:
        return {
            "status": "Success",
            "cost": result.fun,
            "volumes": result.x,
            "shadow_rvp": result.ineqlin.marginals[1],
            "shadow_tanks": result.upper.marginals
        }
    return {"status": "Infeasible", "message": result.message}

# ==========================================
# 3. SIDEBAR: TRADER INPUTS
# ==========================================
st.sidebar.header("Logistics & Supply Chain")
batch_size = st.sidebar.number_input("Target Batch Size (bbls)", min_value=10000, max_value=500000, value=100000, step=10000)

st.sidebar.subheader("Current Tank Inventories")
inv_naphtha = st.sidebar.slider("Naphtha (bbls)", 0, 150000, 80000)
inv_reformate = st.sidebar.slider("Reformate (bbls)", 0, 150000, 40000)
inv_alkylate = st.sidebar.slider("Alkylate (bbls)", 0, 150000, 50000)
inv_butane = st.sidebar.slider("Butane (bbls)", 0, 50000, 15000)

inventories = [inv_naphtha, inv_reformate, inv_alkylate, inv_butane]

# ==========================================
# 4. MAIN DASHBOARD EXECUTION
# ==========================================
components = ["Naphtha", "Reformate", "Alkylate", "Butane"]
# Read the CSV file
lims_db = pd.read_csv(r"C:\Users\...\Quantitative-Refinery-Blending-Commercial-Arbitrage\refinery_lims_data.csv")

# Extract as lists directly from the dataframe
assay_ron = lims_db['RON'].tolist()
assay_rvp_psi = lims_db['RVP_psi'].tolist()

# Linearize RVP dynamically
rvp_indices = [math.pow(rvp, 1.25) for rvp in assay_rvp_psi]

# Fetching Market Data
st.subheader("Live Market Pricing")
with st.spinner("Fetching live futures..."):
    # Using fallback prices in case market is closed/offline
    try:
        live_rbob = float(yf.Ticker("RB=F").history(period="1d")['Close'].iloc[-1] * 42)
        live_wti = float(yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1])
    except:
        live_rbob, live_wti = 122.31, 80.37 # Fallbacks

spot_prices = [live_wti*1.05, live_rbob*1.08, live_rbob*1.12, live_wti*0.60]

col1, col2 = st.columns(2)
col1.metric("WTI Crude Oil", f"${live_wti:.2f}/bbl")
col2.metric("RBOB Gasoline", f"${live_rbob:.2f}/bbl")

st.markdown("---")

# Run Optimizer Button
if st.button("EXECUTE BLEND OPTIMIZATION", type="primary", use_container_width=True):
    mix = run_blending_optimizer(spot_prices, assay_ron, rvp_indices, inventories, batch_size)
    
    if mix["status"] == "Success":
        net_margin = live_rbob - mix["cost"] - 1.50 # $1.50 OPEX
        total_profit = net_margin * batch_size
        
        # Display Terminal-Style Alerts
        if net_margin > 0:
            st.success(f"✅ PROFITABLE TRADE CAPTURED: +${net_margin:.2f}/bbl Margin")
        else:
            st.error(f"❌ COMMERCIAL LOSS: {net_margin:.2f}/bbl Margin. HOLD COMPONENTS.")
            
        # Display Key Financial Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Optimized Blend Cost", f"${mix['cost']:.2f}/bbl")
        m2.metric("Total Batch Profit", f"${total_profit:,.2f}")
        m3.metric("RVP Shadow Price", f"${abs(mix['shadow_rvp']):.2f}/bbl")
        
        # Display Optimal Volume Mix Dataframe
        st.subheader("Optimal Volumetric Recipe")
        df = pd.DataFrame({
            "Component": components,
            "Volume (%)": [round(v*100, 2) for v in mix['volumes']],
            "Barrels Used": [int(v * batch_size) for v in mix['volumes']],
            "Tank Utilization": [f"{int((v * batch_size)/inventories[i] * 100)}%" if inventories[i]>0 else "0%" for i, v in enumerate(mix['volumes'])]
        })
        st.dataframe(df, use_container_width=True)
        
    else:
        st.error(f"⚠️ INFEASIBLE BLEND: {mix['message']}")
        st.warning("Hint: Check your sidebar! You likely don't have enough Reformate to meet the Octane specs.")
