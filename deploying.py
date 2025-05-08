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
    "testev": "1QZAYOIBBjsauY32YXAEDY3i0BbSluSerA7H1O1futv4",
    "sale": "19tMDrq-SQtxh6TIe_6iu_M-BD8GQ-bgJ0bgw7y4Cwl8"
}

def get_public_sheet_data(sheet_id, worksheet_name):
    """Access public sheet without authentication"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    return pd.read_csv(url)

# Sheet selection (manual combination of 1 or 2)
selected_sheets = st.multiselect(
    "Select more than 1 dataset to combine",
    options=list(PUBLIC_SHEETS.keys()),
    default=["trainev"],
    max_selections=4
)

if selected_sheets:
    combined_df = pd.DataFrame()

    for sheet_name in selected_sheets:
        sheet_id = PUBLIC_SHEETS[sheet_name]
        try:
            # Get worksheet name
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:html"
            html = pd.read_html(url)
            worksheet_name = html[0].values[0][0]

            # Load data
            df = get_public_sheet_data(sheet_id, worksheet_name)
            df.columns = df.columns.str.strip()
            df["Source"] = sheet_name  # Optional: Tag data origin

            combined_df = pd.concat([combined_df, df], ignore_index=True)

        except Exception as e:
            st.error(f"Error loading {sheet_name}: {str(e)}")

    if not combined_df.empty:
        df = combined_df

        # Sidebar Filters
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

        # Metrics
        st.markdown("<div style='padding-top: 3rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Region Entries", df["Region"].count() if "Region" in df.columns else 0)
        col2.metric("Total Revenue", f"₹{df['Revenue'].sum():,.2f}" if "Revenue" in df.columns else "₹0")

        # Show region with most revenue
        if "Region" in df.columns and "Revenue" in df.columns:
            top_region = df.groupby("Region")["Revenue"].sum().idxmax()
            top_value = df.groupby("Region")["Revenue"].sum().max()
            st.info(f"🏆 Highest Revenue Region: **{top_region}** with ₹{top_value:,.2f}")
        
        st.markdown("<div style='padding-top: 3rem;'></div>", unsafe_allow_html=True)
        # Revenue by Region Chart
        if "Region" in df.columns and "Revenue" in df.columns:
            region_revenue = df.groupby("Region")["Revenue"].sum().reset_index()
            chart = alt.Chart(region_revenue).mark_bar().encode(
                x=alt.X("Region:N", sort="-y"),
                y="Revenue:Q",
                color=alt.Color("Region:N", legend=None),
                tooltip=["Region", "Revenue"]
            ).properties(height=400, width=600)
            st.subheader("💸 Revenue by Region")
            st.altair_chart(chart, use_container_width=True)

        # Pie Chart: Units Sold by Brand
        if "Brand" in df.columns and "Units_Sold" in df.columns:
            brand_units = df.groupby("Brand")["Units_Sold"].sum().reset_index()
            brand_units = brand_units[brand_units["Units_Sold"] > 0]

            pie_chart = alt.Chart(brand_units).mark_arc(innerRadius=40).encode(
                theta=alt.Theta("Units_Sold:Q"),
                color=alt.Color("Brand:N", legend=alt.Legend(title="Brand")),
                tooltip=["Brand", "Units_Sold"]
            ).properties(width=400, height=400)
            st.subheader("🔄 Units Sold by Brand")
            st.altair_chart(pie_chart, use_container_width=True)
            
            

    

# Footer
st.markdown("---")
st.caption("ℹ️ Read-only view of public Google Sheets - No authentication required")
