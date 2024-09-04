import pandas as pd
import numpy as np
import math
import datetime
import glob
import os


def load_data(dirs):
    to_return = []
    for i in dirs:
        paths = glob.glob(os.path.join(i, "*xlsx"))
        if not paths:
            raise FileNotFoundError(i, "File not found")
        for path in paths:
            xl = pd.ExcelFile(path)
            new_df = pd.read_excel(path, sheet_name=xl.sheet_names[0])

            while np.nan in new_df.columns or "Unnamed" in new_df.columns[1]:
                new_df.columns = new_df.iloc[0]
                new_df = new_df.iloc[1:].reset_index(drop=True)
            to_return.append(new_df)
    return to_return


def clean_sap(data):
    for df in data:
        df.rename(columns={"Plant": "Org", "Order": "Job", "Material": "Item", "Material description": "Item Description",
                  "Order Type": "Job Type", "Order quantity (GMEIN)": "Start Quantity", "Delivered quantity (GMEIN)": "Quantity Completed", "Release date (actual)": "Release Date", "Basic start date": "Actual Start Date", "Basic finish date": "Expected Completion Date"}, inplace=True)
        nan_items = ['Status', 'WIP Labor', 'WIP Material', 'WIP Value']
        for i in nan_items:
            df[i] = np.nan
        
        df["Quantity Due"] = df["Start Quantity"] - df["Quantity Completed"]
        df["SOURCE_SYSTEM"] = "SAP"


def clean_syspro(data):
    for df in data:
        nan_items = ["Start Quantity", "Quantity Completed",
           "Quantity Due", "Release Date", "Actual Start Date", "Expected Completion Date"]
        for i in nan_items:
            df[i] = np.nan
        df["Org"] = "Wilmington"
        df["Status"] = "Released"
        df.dropna(subset="Stock Code",inplace=True)
        df.rename(columns={"Stock Code": "Item", "Job Description": "Item Description","Labor Cost":"WIP Labor","Materia lCost":"WIP Material"},inplace=True)
        df["SOURCE_SYSTEM"] = "Syspro"


def clean_oracle(data):
    for df in data:
        nan_items = ["Org","Job Type","Release Date"]
        for i in nan_items:
            df[i] = np.nan
        df.rename(columns={"Job Name":"Job","Item  Description": "Item Description","Total Labor Cost":"WIP Labor","Total Material Cost":"WIP Material","Job Start Date":"Actual Start Date"},inplace=True)
        df["WIP Value"] = df["WIP Labor"] + df["WIP Material"]
        df["SOURCE_SYSTEM"] = "Oracle"


default_names = ["SOURCE_SYSTEM","Org", "Job", "Item", "Item Description", "Status", "Job Type", "Start Quantity", "Quantity Completed",
                 "Quantity Due", "Release Date", "Actual Start Date", "Expected Completion Date", "WIP Labor", "WIP Material", "WIP Value",]

def return_all_dfs():
    oracle_items = load_data(["oracle"])
    sap_items = load_data(["sap"])
    syspro_items = load_data(["syspro"])
    clean_sap(sap_items)
    clean_syspro(syspro_items)
    clean_oracle(oracle_items)

    all_dfs = oracle_items + sap_items + syspro_items
    all_dfs_clean = []
    for df in all_dfs:
        all_dfs_clean.append(df[default_names])

    new_df = pd.concat(all_dfs_clean)

    new_df["Actual Start Date"] = pd.to_datetime(new_df["Actual Start Date"], errors='coerce')

    new_df["WO Age"] = new_df["Actual Start Date"].apply(lambda x: 
        datetime.date.today() - x.date() if not pd.isnull(x) else pd.NaT
    )

    new_df["WO Age"] = new_df["WO Age"].dt.days
    new_df["WIP Value"] = new_df["WIP Value"].fillna(0)
    new_df[["Status", "Org","Job Type"]] = new_df[["Status", "Org","Job Type"]].fillna("EMPTY_VALUE")
    return new_df

end_dataframe = return_all_dfs()

end_dataframe.to_excel("merged_items.xlsx",index=False)
