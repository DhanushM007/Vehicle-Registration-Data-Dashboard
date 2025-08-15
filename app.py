import pandas as pd
import streamlit as st
import os
import datetime
import altair as alt

# --- Streamlit Page Configuration ---
# Sets up the basic configuration for the Streamlit page, including layout, title, and sidebar state.
st.set_page_config(layout="wide", page_title="Vahan — Vehicle Registrations", initial_sidebar_state="expanded")

# --- Function to Load HTML Tables ---
# Caches the loaded HTML tables to improve performance.
# This function attempts to read HTML tables from a specified file path.
@st.cache_data
def load_tables(html_path):
    # Checks if the HTML file exists before attempting to load it.
    if not os.path.exists(html_path):
        return []
    try:
        # Uses pandas to read HTML tables, specifically using the 'bs4' (BeautifulSoup) parser for robustness.
        tables = pd.read_html(html_path, header=None, flavor="bs4")
        return tables
    except ValueError:
        # Displays an error if no tables are found within the HTML file.
        st.error("No tables found in the HTML file.")
        return []
    except Exception as e:
        # Catches any other exceptions that might occur during the loading process.
        st.error(f"An error occurred while loading the tables: {e}")
        return []

# --- Main Page Header ---
# Displays the main title and a brief description for the dashboard.
st.title("Vahan — Vehicle Registrations Dashboard")
st.markdown("Explore vehicle registration data with interactive filters and comparisons.")

# --- Sidebar Filters ---
# Creates a sidebar for user selections to filter the data.
st.sidebar.header("Data Filters")

# Defines the types of tables available for selection.
table_type_options = [
    "Vehicle Class",
    "Manufacturer",
    "Vehicle Category Month Wise",
    "Manufacturer Month Wise"
]
# Allows the user to select the type of data table to display.
table_type = st.sidebar.selectbox("Select Table Type", table_type_options, index=0)

# Displays vehicle type selection only if the table type is not month-wise.
if table_type not in ["Vehicle Category Month Wise", "Manufacturer Month Wise"]:
    # Maps user-friendly vehicle type names to their corresponding file path segments.
    vehicle_types = {
        "Four Wheeler": "four_wheeler",
        "Three Wheeler": "three_wheeler",
        "Two Wheeler": "two_wheeler"
    }
    vehicle_type_options = list(vehicle_types.keys())
    # Allows the user to select a specific vehicle type.
    selected_vehicle_type = st.sidebar.selectbox("Select Vehicle Type", vehicle_type_options, index=0)
else:
    selected_vehicle_type = None

# Allows the user to select the year for which to display data.
year_options = ["2025", "2024", "2023"]
selected_year = st.sidebar.selectbox("Select Year", year_options, index=0)

# Month selection, shown only for month-wise tables.
selected_month = None
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
if table_type in ["Vehicle Category Month Wise", "Manufacturer Month Wise"]:
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    # For the current year, only displays months up to the current month.
    if int(selected_year) == current_year:
        available_months = ["All"] + month_names[:current_month]
        selected_month = st.sidebar.selectbox("Select Month", available_months, index=0)
    else:
        # For past years, displays all months.
        selected_month = st.sidebar.selectbox("Select Month", ["All"] + month_names, index=0)

# --- Data Loading Function ---
# Caches the data loading process for efficiency.
# Constructs the file path and loads the appropriate DataFrame based on user selections.
@st.cache_data
def get_data(year, table_type, selected_vehicle_type):
    # Defines mapping for vehicle types to file naming conventions.
    vehicle_types = {
        "Four Wheeler": "four_wheeler",
        "Three Wheeler": "three_wheeler",
        "Two Wheeler": "two_wheeler"
    }

    # Constructs the HTML file path based on selected filters.
    if selected_vehicle_type:
        html_path = f"src/{vehicle_types[selected_vehicle_type]}_{table_type.replace(' ', '_').lower()}_{year}.html"
    else:
        html_path = f"src/{table_type.replace(' ', '_').lower()}_{year}.html"
        
    # Loads tables from the constructed HTML path.
    tables = load_tables(html_path)
    if not tables:
        return pd.DataFrame()
        
    # Selects the appropriate table (typically the last or second to last one) and cleans it.
    idx = 5 if len(tables) > 5 else len(tables) - 1
    df = tables[idx].copy()
    df = df.reset_index(drop=True).iloc[:, 1:]
    
    # Assigns appropriate column names based on the selected table type and vehicle type.
    if table_type == "Manufacturer":
        if selected_vehicle_type == "Two Wheeler":
            df.columns = ["Manufacturer", "2WIC", "2WN", "2WT", "TOTAL"]
        elif selected_vehicle_type == "Three Wheeler":
            df.columns = ["Manufacturer", "3WN", "3WT", "TOTAL"]
        elif selected_vehicle_type == "Four Wheeler":
            df.columns = ["Manufacturer", "4WIC", "LMV", "MMV", "HMV", "TOTAL"]
    elif table_type == "Vehicle Class":
        if selected_vehicle_type == "Two Wheeler":
            df.columns = ["Class", "2WIC", "2WN", "2WT", "TOTAL"]
        elif selected_vehicle_type == "Three Wheeler":
            df.columns = ["Class", "3WN", "3WT", "TOTAL"]
        elif selected_vehicle_type == "Four Wheeler":
            df.columns = ["Class", "4WIC", "LMV", "MMV", "HMV", "TOTAL"]
    elif table_type in ["Vehicle Category Month Wise", "Manufacturer Month Wise"]:
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        key_column_name = "Category" if table_type == "Vehicle Category Month Wise" else "Manufacturer"
        num_months = len(df.columns) - 2
        if num_months > 0:
            month_cols = month_names[:num_months]
            df.columns = [key_column_name] + month_cols + ["TOTAL"]
        else:
            return pd.DataFrame()
    
    # Converts relevant columns to numeric types, handling missing values.
    num_cols = [col for col in df.columns if col not in [df.columns[0]]]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors='coerce').fillna(0).astype(int)
        
    return df

# --- Load and Display Data ---
# Displays a spinner while data is being loaded.
with st.spinner(f"Loading data for {table_type} in {selected_year}..."):
    df = get_data(selected_year, table_type, selected_vehicle_type)

# Checks if the loaded DataFrame is empty and displays an error if so.
if df.empty:
    st.error(f"No data found for the selected options.")
else:
    display_df = df.copy()
    
    # Filters the displayed DataFrame if a specific month is selected for month-wise tables.
    if selected_month and selected_month != "All" and selected_month in df.columns:
        display_df = df[[df.columns[0], selected_month, "TOTAL"]]
        display_df.columns = [df.columns[0], f"{selected_month} Registrations", "TOTAL"]
        st.header(f"{table_type} Data — {selected_month} {selected_year}")
    else:
        st.header(f"{table_type} Data — {selected_year}")
        
    # Displays the data in a Streamlit DataFrame.
    st.dataframe(display_df, use_container_width=True)

    # --- Download Button ---
    # Provides a button to download the displayed data as a CSV file.
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download table as CSV",
        data=csv,
        file_name=f"{table_type.replace(' ', '_').lower()}_{selected_year}_vehicle_data.csv",
        mime="text/csv",
    )
    
    # --- Monthly Comparison (MoM/YoM) Analysis ---
    # This section is specifically for month-wise tables when a single month is selected.
    if selected_month and selected_month != "All":
        with st.expander("📈 Monthly Comparisons"):
            st.write("This section provides a detailed analysis of month-over-month (MoM) and year-over-month (YoM) growth.")
            try:
                current_month_index = month_names.index(selected_month)
                key_col = df.columns[0]

                if current_month_index > 0:
                    # Performs Month-over-Month (MoM) comparison for months other than January.
                    st.subheader("Month-over-Month (MoM) Comparison")
                    prev_month = month_names[current_month_index - 1]
                    
                    if prev_month in df.columns and selected_month in df.columns:
                        comparison_df = df[[key_col, prev_month, selected_month]].copy()
                        comparison_df.columns = [key_col, prev_month, selected_month]
                        
                        # Calculates the percentage change MoM.
                        comparison_df["Change %"] = comparison_df.apply(
                            lambda row: f"{((row[selected_month] - row[prev_month]) / row[prev_month] * 100):.2f}%"
                            if row[prev_month] != 0 else "—",
                            axis=1
                        )
                        
                        st.dataframe(comparison_df, use_container_width=True)

                        # Calculates and displays the overall MoM growth using a Streamlit metric.
                        current_total = comparison_df[selected_month].sum()
                        previous_total = comparison_df[prev_month].sum()
                        overall_change = (current_total - previous_total) / previous_total * 100 if previous_total != 0 else 0
                        
                        st.metric(
                            label=f"Overall MoM Growth ({selected_month} vs {prev_month})",
                            value=f"{current_total:,}",
                            delta=f"{overall_change:.2f}%"
                        )
                        
                        # Generates and displays an Altair bar chart for MoM comparison.
                        chart_df_melted = pd.melt(
                            comparison_df,
                            id_vars=[key_col],
                            value_vars=[selected_month, prev_month],
                            var_name="Month",
                            value_name="Registrations"
                        )
                        
                        chart = alt.Chart(chart_df_melted).mark_bar().encode(
                            x=alt.X(f'{key_col}:N', title=key_col),
                            y=alt.Y('Registrations:Q'),
                            color=alt.Color('Month:N', scale=alt.Scale(range=['#36A2EB', '#FF6384'])),
                            tooltip=[key_col, 'Month', 'Registrations']
                        ).properties(
                            title=f"MoM Registrations: {selected_month} vs {prev_month}"
                        )
                        
                        st.altair_chart(chart, use_container_width=True)

                    else:
                        st.info(f"Data for either {prev_month} or {selected_month} is not available for MoM calculation.")
                
                else: # Handles Year-over-Month (YoM) comparison specifically for January (current Jan vs previous Dec).
                    st.subheader("Year-over-Month (YoM) Comparison (Jan vs Previous Dec)")
                    prev_year = str(int(selected_year) - 1)
                    prev_df = get_data(prev_year, table_type, selected_vehicle_type) # Loads data for the previous year.

                    if "Jan" in df.columns and "Dec" in prev_df.columns:
                        current_jan_df = df[[key_col, "Jan"]].rename(columns={"Jan": f"Jan_{selected_year}"})
                        prev_dec_df = prev_df[[key_col, "Dec"]].rename(columns={"Dec": f"Dec_{prev_year}"})

                        # Merges current January data with previous December data.
                        comparison_df = pd.merge(
                            current_jan_df,
                            prev_dec_df,
                            on=key_col,
                            how="outer"
                        )
                        comparison_df.fillna(0, inplace=True)
                        
                        dec_prev_year_col = f"Dec_{prev_year}"
                        jan_curr_year_col = f"Jan_{selected_year}"
                        
                        # Calculates the percentage change YoM.
                        comparison_df["Change %"] = comparison_df.apply(
                            lambda row: f"{((row[jan_curr_year_col] - row[dec_prev_year_col]) / row[dec_prev_year_col] * 100):.2f}%"
                            if row[dec_prev_year_col] != 0 else "—",
                            axis=1
                        )
                        
                        st.dataframe(comparison_df, use_container_width=True)

                        # Calculates and displays the overall YoM growth using a Streamlit metric.
                        current_total = comparison_df[jan_curr_year_col].sum()
                        previous_total = comparison_df[dec_prev_year_col].sum()
                        overall_change = (current_total - previous_total) / previous_total * 100 if previous_total != 0 else 0
                        
                        st.metric(
                            label=f"Overall YoM Growth (Jan {selected_year} vs Dec {prev_year})",
                            value=f"{current_total:,}",
                            delta=f"{overall_change:.2f}%"
                        )

                        # Generates and displays an Altair bar chart for YoM comparison.
                        chart_df_melted = pd.melt(
                            comparison_df,
                            id_vars=[key_col],
                            value_vars=[jan_curr_year_col, dec_prev_year_col],
                            var_name="Period",
                            value_name="Registrations"
                        )
                        
                        chart = alt.Chart(chart_df_melted).mark_bar().encode(
                            x=alt.X(f'{key_col}:N', title=key_col),
                            y=alt.Y('Registrations:Q'),
                            color=alt.Color('Period:N', scale=alt.Scale(range=['#36A2EB', '#FF6384'])),
                            tooltip=[key_col, 'Period', 'Registrations']
                        ).properties(
                            title=f"YoM Registrations: Jan {selected_year} vs Dec {prev_year}"
                        )
                        
                        st.altair_chart(chart, use_container_width=True)
                    
                    else:
                        st.info(f"Previous year's December data ({prev_year}) or current year's January data not available for Year-over-Month calculation.")

            except Exception as e:
                st.error(f"Error calculating monthly comparison: {e}")
                
    # --- Quarter-over-Quarter (QoQ) Analysis ---
    # This section is displayed only when "All" months are selected for month-wise tables.
    if selected_month == "All":
        with st.expander("🔄 Quarter-over-Quarter (QoQ) Growth"):
            try:
                # Checks if monthly columns are available for QoQ calculation.
                if any(m in df.columns for m in month_names):
                    st.write("View the registration trends and percentage change between quarters.")
                    
                    # Defines the months included in each quarter.
                    quarter_months = {
                        "Q1 (Jan-Mar)": ["Jan", "Feb", "Mar"],
                        "Q2 (Apr-Jun)": ["Apr", "May", "Jun"],
                        "Q3 (Jul-Sep)": ["Jul", "Aug", "Sep"],
                        "Q4 (Oct-Dec)": ["Oct", "Nov", "Dec"]
                    }
                    
                    qoq_df = df[[df.columns[0]]].copy()
                    calculated_quarters = []
                    # Calculates total registrations for each quarter.
                    for quarter_name, months in quarter_months.items():
                        existing_months = [m for m in months if m in df.columns]
                        if existing_months:
                            qoq_df[quarter_name] = df[existing_months].sum(axis=1)
                            calculated_quarters.append(quarter_name)
                    
                    if len(calculated_quarters) > 1:
                        # Calculates Quarter-over-Quarter percentage change.
                        for i in range(1, len(calculated_quarters)):
                            curr_quarter = calculated_quarters[i]
                            prev_quarter = calculated_quarters[i-1]
                            
                            qoq_df[f"{curr_quarter} vs {prev_quarter} QoQ%"] = qoq_df.apply(
                                lambda row: f"{((row[curr_quarter] - row[prev_quarter]) / row[prev_quarter] * 100):.2f}%"
                                if row[prev_quarter] != 0 else "—",
                                axis=1
                            )
                        
                        st.dataframe(qoq_df, use_container_width=True)

                        if len(calculated_quarters) > 0:
                            chart_data = qoq_df[calculated_quarters].sum().reset_index()
                            chart_data.columns = ["Quarter", "Total_Registrations"]
                            
                            # Generates and displays an Altair line chart for quarterly trends.
                            line_chart = alt.Chart(chart_data).mark_line(point=True, strokeWidth=3).encode(
                                x=alt.X('Quarter:N', sort=calculated_quarters, axis=alt.Axis(labelAngle=-45)),
                                y=alt.Y('Total_Registrations:Q', title="Total Registrations"),
                                tooltip=['Quarter', 'Total_Registrations']
                            ).properties(
                                title=f"Quarterly Registration Trend for {selected_year}"
                            )
                            
                            st.altair_chart(line_chart, use_container_width=True)
                            
                            # Displays the latest QoQ growth metric.
                            if len(calculated_quarters) > 1:
                                last_qoq_col = f"{calculated_quarters[-1]} vs {calculated_quarters[-2]} QoQ%"
                                last_qoq_change = qoq_df[last_qoq_col].iloc[0] if not qoq_df.empty and last_qoq_col in qoq_df.columns else "—"
                                st.metric(
                                    label=f"Latest QoQ Growth ({calculated_quarters[-1]} vs {calculated_quarters[-2]})",
                                    value=f"{qoq_df[calculated_quarters[-1]].sum():,}",
                                    delta=last_qoq_change
                                )
                    else:
                        st.info("Not enough quarter data to perform QoQ calculation.")
                else:
                    st.info("Monthly columns not found for QoQ calculation.")
            except Exception as e:
                st.error(f"Error calculating QoQ: {e}")
                
    # --- Year-over-Year (YoY) Analysis ---
    # This section provides a comparison of registration data with the previous year.
    with st.expander("📊 Year-over-Year (YoY) Comparison"):
        st.write("Compare registration numbers for the current and previous years.")
        try:
            prev_year = str(int(selected_year) - 1)
            prev_df = get_data(prev_year, table_type, selected_vehicle_type) # Loads data for the previous year.

            if not prev_df.empty:
                key_col = df.columns[0]
                
                # Determines whether to compare specific months or total annual data.
                if selected_month and selected_month != "All" and selected_month in df.columns and selected_month in prev_df.columns:
                    current_data = df[[key_col, selected_month]].copy()
                    prev_data = prev_df[[key_col, selected_month]].copy()
                    data_col = selected_month
                    period_label = f" for {selected_month}"
                else:
                    current_data = df[[key_col, "TOTAL"]].copy()
                    prev_data = prev_df[[key_col, "TOTAL"]].copy()
                    data_col = "TOTAL"
                    period_label = ""
                    
                # Merges current and previous year's data for comparison.
                merged_df = pd.merge(
                    current_data,
                    prev_data,
                    on=key_col,
                    how="outer",
                    suffixes=(f"_{selected_year}", f"_{prev_year}")
                )
                merged_df.fillna(0, inplace=True)
                
                # Calculates the Year-over-Year percentage change.
                merged_df["YoY %"] = merged_df.apply(
                    lambda row: f"{((row[f'{data_col}_{selected_year}'] - row[f'{data_col}_{prev_year}']) / row[f'{data_col}_{prev_year}'] * 100):.2f}%"
                    if row[f'{data_col}_{prev_year}'] != 0 else "—",
                    axis=1
                )
                
                st.dataframe(merged_df, use_container_width=True)
                
                # Calculates and displays the overall YoY growth using a Streamlit metric.
                current_total = merged_df[f'{data_col}_{selected_year}'].sum()
                previous_total = merged_df[f'{data_col}_{prev_year}'].sum()
                overall_yoy_change = (current_total - previous_total) / previous_total * 100 if previous_total != 0 else 0
                
                st.metric(
                    label=f"Overall YoY Growth ({selected_year} vs {prev_year}){period_label}",
                    value=f"{current_total:,}",
                    delta=f"{overall_yoy_change:.2f}%"
                )
                
                # Generates and displays an Altair bar chart for YoY comparison.
                chart_df_melted = pd.melt(
                    merged_df,
                    id_vars=[key_col],
                    value_vars=[f'{data_col}_{selected_year}', f'{data_col}_{prev_year}'],
                    var_name="Year",
                    value_name="Registrations"
                )

                yoy_chart = alt.Chart(chart_df_melted).mark_bar().encode(
                    x=alt.X(f'{key_col}:N', title=key_col),
                    y=alt.Y('Registrations:Q'),
                    color=alt.Color('Year:N', scale=alt.Scale(range=['#36A2EB', '#FF6384'])),
                    tooltip=[key_col, 'Year', 'Registrations']
                ).properties(
                    title=f"YoY Registrations: {selected_year} vs {prev_year}{period_label}"
                )
                
                st.altair_chart(yoy_chart, use_container_width=True)
                
            else:
                st.warning(f"No previous year ({prev_year}) data available for YoY calculation.")
        except Exception as e:
            st.error(f"Error calculating YoY: {e}")