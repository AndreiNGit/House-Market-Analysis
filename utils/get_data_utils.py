import pandas as pd
from eurostatapiclient import EurostatAPIClient

def get_eurostat_data(indicators: dict, columnRenamingMapping: dict = None) -> pd.DataFrame:
    """
    Get data from Eurostat API
    :param data_def: dictionary with data definition and filters
    :param columnRenamingMapping: dictionary with column renaming mapping for indicator columns
    :return: pandas DataFrame with pivotated and filtered data
    """
    df = pd.DataFrame()
    # Choose service version: only 1.0 is currently available
    VERSION = '1.0'
    # Only json is currently available
    FORMAT = 'json'
    # Specify language: en, fr, de
    LANGUAGE = 'en'

    eurostat = EurostatAPIClient(VERSION, FORMAT, LANGUAGE)

    for indicator, params in indicators.items():
        data_df = eurostat.get_dataset(indicator).to_dataframe()
        
        for filter_key, value in params.items():
            if isinstance(value, list):
                data_df = data_df[data_df[filter_key].isin(value)]
            else:
                data_df = data_df[data_df[filter_key] == value]

        if columnRenamingMapping is not None and indicator in columnRenamingMapping:
            data_df["indicator"] = columnRenamingMapping[indicator]
        else:
            data_df["indicator"] = indicator

        search_cols_list = [col for col in data_df.columns if col != 'indicator']
        for col in search_cols_list:  
            if data_df[col].nunique() == 1:
                data_df.drop(col, axis=1, inplace=True)
        df = pd.concat([df, data_df], ignore_index=True)
    
    index_cols = [col for col in df.columns if col not in ['indicator', 'values']]
    df_pivot = df.pivot(index=index_cols, columns='indicator', values='values')
    df_pivot.reset_index(inplace=True)
    return df_pivot