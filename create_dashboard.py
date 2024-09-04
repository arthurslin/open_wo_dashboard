import pandas as pd
from merge_datasets import return_all_dfs
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st

df = return_all_dfs()

st.set_page_config(page_title="Work Order Dashboard",
                   page_icon=":bar_chart", layout="wide")

st.sidebar.header("Filters: ")

# Function to create multiselect widget
def create_multiselect(name, options, default=None):
    if default is None:
        default = options
    return st.sidebar.multiselect(f"Select {name}", options=options, default=default)

# Function to build query condition
def build_condition(column, selected_values):
    if len(selected_values) < len(df[column].unique()):
        return f"({column} == {selected_values})"
    return ""

# Function to create query string
def create_query(filters):
    conditions = [build_condition(col, values) for col, values in filters.items()]
    return " & ".join(filter(None, conditions))

# Create filters
filters = {
    "SOURCE_SYSTEM": create_multiselect("Source System", df["SOURCE_SYSTEM"].unique()),
    "Status": create_multiselect("Status", df["Status"].unique()),
    "Org": create_multiselect("Organization", df["Org"].unique()),
    "Job Type": create_multiselect("Job Type", df["Job Type"].unique())
}

query_string = create_query(filters)

if query_string:
    df_selection = df.query(query_string)
else:
    df_selection = df.copy()

def create_age_distribution_plot(df_selection):
    if "WO Age" not in df_selection.columns:
        st.warning("WO Age column not found in the DataFrame.")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add a new category for NaN values
    df_selection['WO Age'] = pd.to_numeric(df_selection['WO Age'], errors='coerce')
    # df_selection.loc[df_selection['WO Age'].isnull(), 'WO Age'] = -999  # Assign a sentinel value
    
    bins = range(0, int(df_selection['WO Age'].max()) + 101, 100)
    df_selection['WO Age_Binned'] = pd.cut(df_selection['WO Age'], bins=bins, right=False)
    
    counts = df_selection['WO Age_Binned'].value_counts().sort_index()
    
    ax.bar(counts.index.astype(str), counts.values)
    ax.set_xlabel('WO Age Range')
    ax.set_ylabel('Count of WO')
    ax.set_title('Distribution of WO Ages')
    plt.xticks(rotation=90)
    
    # Adjust y-axis scale based on maximum count
    max_count = counts.max()
    ax.set_ylim(0, max_count * 1.1)
    
    st.pyplot(fig)

def create_wip_value_distribution_plot(df_selection):
    if "WO Age" not in df_selection.columns or "WIP Value" not in df_selection.columns:
        st.warning("WO Age or WIP Value column not found in the DataFrame.")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add a new category for NaN values
    df_selection['WO Age'] = pd.to_numeric(df_selection['WO Age'], errors='coerce')
    # df_selection.loc[df_selection['WO Age'].isnull(), 'WO Age'] = -999  # Assign a sentinel value
    
    bins = range(0, int(df_selection['WO Age'].max()) + 101, 100)
    df_selection['WO Age_Bucket'] = pd.cut(df_selection['WO Age'], bins=bins, right=False)
    wip_sums = df_selection.groupby('WO Age_Bucket')['WIP Value'].sum().sort_index()
    
    def millions(x, pos):
        return f'${x / 1e6:.1f}M'
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions))
    
    ax.bar(wip_sums.index.astype(str), wip_sums.values)
    ax.set_xlabel('WO Age Range')
    ax.set_ylabel('Sum of WIP Value (in Millions)')
    ax.set_title('Distribution of WO Ages by Sum of WIP Value')
    plt.xticks(rotation=90)
    
    # Adjust y-axis scale based on maximum sum
    max_sum = wip_sums.max()
    ax.set_ylim(0, max_sum * 1.1)
    
    st.pyplot(fig)

st.title("WO Age Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    create_age_distribution_plot(df_selection)

with col2:
    create_wip_value_distribution_plot(df_selection)

st.dataframe(df_selection, hide_index=True)
