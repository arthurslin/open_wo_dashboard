import pandas as pd
import numpy as np
from merge_datasets import return_all_dfs
from graphwo_freqvalue import plot_wo_age_bucket
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

df = return_all_dfs()

st.set_page_config(page_title="Work Order Dashboard",
                   page_icon=":bar_chart", layout="wide")

st.sidebar.header("Filters: ")

def create_multiselect(name, options, default=None):
    if default is None:
        default = options
    return st.sidebar.multiselect(f"Select {name}", options=options, default=default)

# Modified build_condition function
def build_condition(column, selected_values):
    if len(selected_values) < len(df[column].unique()):
        # Format the column name
        if ' ' in column:
            column_str = f"`{column}`"
        else:
            column_str = column
        
        # Format the selected values
        formatted_values = ', '.join([f"'{value}'" for value in selected_values])
        
        return f"({column_str} in ({formatted_values}))"
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
    "Job Type": create_multiselect("Job Type", df["Job Type"].unique()),
}

# Add WO Age slider
min_age = df['WO Age'].min().astype(int)
max_age = df['WO Age'].max().astype(int)

age_range = st.sidebar.slider(
    "Select WO Age range",
    min_value=min_age,
    max_value=max_age,
    value=(int(0), max_age),
    step=1
)

query_string = create_query(filters)

print(query_string)
if query_string:
    df_selection = df.query(query_string)
else:
    df_selection = df.copy()

# Apply WO Age filter
df_selection = df_selection[(df_selection['WO Age'] >= age_range[0]) & (df_selection['WO Age'] <= age_range[1])]

plot_wo_age_bucket(df_selection)

st.title("Current dataset:")
st.dataframe(df_selection, hide_index=True)
