import pandas as pd
import numpy as np

class DataCleaner:
    def __init__(self):
        self.pu_fix = {
            "Haas F1 Team": "Ferrari",
            "Racing Bulls":  "Honda",
            "AlphaTauri":    "Honda",  
        }

    def clean_master_data(self, df: pd.DataFrame) -> pd.DataFrame:

        drop_cols = ['ClassifiedPosition_x', 'ClassifiedPosition_y',
                     'ClassifiedPosition', 'Abbreviation']
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

        if 'final_position' in df.columns:
            df['final_position'] = pd.to_numeric(
                df['final_position'], errors='coerce'
            ).fillna(21).astype(int)

        if 'quali_position' in df.columns:
            df['quali_position'] = df['quali_position'].round().astype(int)

        if 'pu_manufacturer' in df.columns and 'TeamName' in df.columns:
            mask = df['pu_manufacturer'].isna()
            df.loc[mask, 'pu_manufacturer'] = df.loc[mask, 'TeamName'].map(self.pu_fix)

        if 'final_position' in df.columns:
            df['relevance'] = (22 - df['final_position']).clip(lower=0)
            df['dnf'] = (df['final_position'] == 21).astype(int)

        return df