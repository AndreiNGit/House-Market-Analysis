import pandas as pd
from eurostatapiclient import EurostatAPIClient

def get_eurostat_data(indicators: dict) -> pd.DataFrame:
    """
    Obține date de la Eurostat API și le preprocesează conform filtrelor specificate.
    
    :param indicators: Dicționar cu definiția datelor și filtre. Fiecare cheie este un indicator,
                       iar valoarea este un alt dicționar ce conține filtre (ex: 'geo', 'time', etc.)
                       și opțional o etichetă sub cheia "label" pentru identificare.
    :return: DataFrame pandas pivotat și filtrat.
    """
    df = pd.DataFrame()
    # Configurarea clientului Eurostat
    VERSION = '1.0'
    FORMAT = 'json'
    LANGUAGE = 'en'
    eurostat = EurostatAPIClient(VERSION, FORMAT, LANGUAGE)

    for indicator, params in indicators.items():
        data_df = eurostat.get_dataset(indicator).to_dataframe()
        
        # Aplică filtrele specificate, sărim peste cheia "label" indiferent de modul în care este scrisă
        for filter_key, value in params.items():
            if filter_key.strip().lower() == "label":
                continue
            if filter_key in data_df.columns:
                if isinstance(value, list):
                    if(filter_key == 'time' and data_df["freq"].iloc[0] == 'M'):
                        data_df = data_df[data_df[filter_key].astype(str).apply(lambda x: any(x.startswith(str(v)) for v in value))]
                    else:
                        data_df = data_df[data_df[filter_key].isin(value)]
                else:
                    data_df = data_df[data_df[filter_key] == value]
        
        if params.get("label") is not None:
            data_df["indicator"] = params["label"]
        else:
            data_df["indicator"] = indicator

        # Agregare: convertim datele lunare la date anuale folosind media pe cele 12 luni
        if 'freq' in data_df.columns and not data_df.empty and data_df['freq'].iloc[0] == 'M':
            data_df['time'] = pd.to_datetime(data_df['time']).dt.year
            data_df["freq"] = "A"
            group_columns = [col for col in data_df.columns if col not in ['values']]
            data_df = data_df.groupby(group_columns, as_index=False)['values'].mean()
            data_df["time"] = data_df["time"].astype(str)
            
        
        search_cols_list = [col for col in data_df.columns if col != 'indicator']
        for col in search_cols_list:
            if data_df[col].nunique() == 1:
                data_df.drop(col, axis=1, inplace=True)

        df = pd.concat([df, data_df], ignore_index=True)
    

    cols_of_interest = ['geo', 'time', 'indicator', 'values']
    df = df[cols_of_interest]

    df_pivot = df.pivot(index=['geo','time'], columns='indicator', values='values')
    df_pivot.reset_index(inplace=True)
    return df_pivot
