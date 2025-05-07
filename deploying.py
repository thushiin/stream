import streamlit as st
import pandas as pd
import gspread
from gspread.utils import rowcol_to_a1
import altair as alt

# Set up the app
st.set_page_config(page_title="EV Dashboard", layout="wide")

st.markdown("""
    <style>
    .stMultiSelect > div {
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
    }
    .stMultiSelect label {
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    div[data-baseweb="select"] {
        min-height: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 EV Sales Dashboard")

# Your public sheets configuration
PUBLIC_SHEETS = {
    "trainev": "1f4Jko_EbtwgVhrIA3nwSxzeSMG9C4RhwlaVHWa3Evv0",
    "testev": "1QZAYOIBBjsauY32YXAEDY3i0BbSluSerA7H1O1futv4"
}

def get_public_sheet_data(sheet_id, worksheet_name):
    """Access public sheet without authentication"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    return pd.read_csv(url)

# Sheet selection
selected_sheet = st.selectbox(
    "Select a dataset",
    options=list(PUBLIC_SHEETS.keys()),
    index=0
)

if selected_sheet:
    sheet_id = PUBLIC_SHEETS[selected_sheet]
    
    try:
        # Get worksheet names
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:html"
        html = pd.read_html(url)
        worksheet_names = [ws[0] for ws in html[0].values]
        
        # Worksheet selection
        selected_worksheet = worksheet_names[0]
            
        
        # Display the data
        if selected_worksheet:
            df = get_public_sheet_data(sheet_id, selected_worksheet)
            
            df.columns = df.columns.str.strip()
            
            
            # Optional filters (Multi-select version)
            st.sidebar.header("🔍 Filters")
            if "Region" in df.columns:
                regions = sorted(df["Region"].dropna().unique())
                selected_region = st.sidebar.selectbox("Filter by Region", ["All"] + regions)
                if selected_region != "All":
                    df = df[df["Region"] == selected_region]
        
            if "Brand" in df.columns:
                brands = sorted(df["Brand"].dropna().unique())
                selected_brand = st.sidebar.multiselect("Filter by Brand", brands)
                if selected_brand:
                    df = df[df["Brand"].isin(selected_brand)]

                        
        
            
            col1, col2 = st.columns(2)
            total_entries = df["Region"].count() if "Region" in df.columns else 0
            total_revenue = df["Revenue"].sum() if "Revenue" in df.columns else 0
    
            col1.metric("Region Entries", total_entries)
            col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
            # Revenue by Region Chart
            if "Region" in df.columns and "Revenue" in df.columns:
                region_revenue = df.groupby("Region")["Revenue"].sum().reset_index()
                chart = alt.Chart(region_revenue).mark_bar().encode(
                    x=alt.X("Region:N", sort="-y"),
                    y="Revenue:Q",
                    color="Region:N",
                    tooltip=["Region", "Revenue"]
                ).properties(height=400)
    
                st.subheader("💸 Revenue by Region")
                st.altair_chart(chart, use_container_width=True)
    
  
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the sheet is published and viewable publicly.")


# Footer
st.markdown("---")
st.caption("ℹ️ Read-only view of public Google Sheets - No authentication required")
