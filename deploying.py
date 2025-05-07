import streamlit as st
import pandas as pd
import gspread
from gspread.utils import rowcol_to_a1
import altair as alt

# Set up the app
st.set_page_config(page_title="Public Sheets Viewer", layout="wide")

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

st.title("📊 Public Google Sheets Viewer")

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
            col1, col2 = st.columns(2)
            with col1:
                if "Region" in df.columns:
                    all_regions = sorted(df["Region"].dropna().unique().tolist())
                    selected_region = st.selectbox("Filter by Region", options=["All"] + all_regions)
                    if selected_region != "All":
                        df = df[df["Region"] == selected_region]

                        
            with col2:
                if "Brand" in df.columns:
                    all_brands = sorted(df["Brand"].dropna().unique().tolist())
                    selected_brands = st.multiselect("Filter by Brand", options=all_brands, default= None)
                    if selected_brands:
                        df = df[df["Brand"].isin(selected_brands)]
                        
                        
        st.subheader(f"{selected_sheet}")
            
        total_entries = df["Region"].count() if "Region" in df.columns else 0
        st.metric("Total Region Entries", total_entries)
            
            # Sum of Revenue
        revenue_sum = df["Revenue"].sum() if "Revenue" in df.columns else 0
        st.metric("Total Revenue", f"{revenue_sum:,.2f}")
        
                        
        if "Region" in df.columns and "Revenue" in df.columns:
            region_revenue = df.groupby("Region")["Revenue"].sum().reset_index()

    # Altair bar chart
            st.subheader("Total Revenue by Region")
            chart = alt.Chart(region_revenue).mark_bar().encode(
                x="Region:N",  # Categorical axis
                y="Revenue:Q",  # Quantitative axis
                tooltip=["Region", "Revenue"]  # Tooltip on hover
            ).properties(
                width=600,
                height=400,
                
            )
            st.altair_chart(chart, use_container_width=True)
                        
                

        

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the Google Sheet is set to 'Anyone with the link can view'")

# Footer
st.markdown("---")
st.caption("ℹ️ Read-only view of public Google Sheets - No authentication required")
