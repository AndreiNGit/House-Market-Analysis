import pandas as pd

def filterDf(df, column, value):
    
    return df[df[column] == value]