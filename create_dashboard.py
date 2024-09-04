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

def build_condition(column, selected_values):
    if len(selected_values) < len(df[column].unique()):
        return f"({column} == {selected_values})"
    return ""

def create_query(filters):
    conditions = [build_condition(col, values) for col, values in filters.items()]
    return " & ".join(filter(None, conditions))

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

plot_wo_age_bucket(df_selection)

st.title("Current dataset:")
st.dataframe(df_selection, hide_index=True)
