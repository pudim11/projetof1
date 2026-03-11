import pandas as pd
import numpy as np
from src.preprocessing.circuit_metadata import get_circuit_info

POWER_UNIT_MAP = {
    2023: {
        "Red Bull Racing":   "Honda",
        "Mercedes":          "Mercedes",
        "Ferrari":           "Ferrari",
        "McLaren":           "Mercedes",
        "Aston Martin":      "Mercedes", 
        "Alpine F1 Team":    "Renault",  
        "Alpine":            "Renault",   
        "Williams":          "Mercedes",
        "AlphaTauri":        "Honda",    
        "Alfa Romeo":        "Ferrari",   
        "Haas F1 Team":      "Ferrari",
    },
    2024: {
        "Red Bull Racing":   "Honda",
        "Mercedes":          "Mercedes",
        "Ferrari":           "Ferrari",
        "McLaren":           "Mercedes",
        "Aston Martin":      "Honda",    
        "Alpine F1 Team":    "Renault",
        "Alpine":            "Renault",
        "Williams":          "Mercedes",
        "Racing Bulls":      "Honda",
        "RB":                "Honda",     
        "Kick Sauber":       "Ferrari",  
        "Haas F1 Team":      "Ferrari",
    },
    2025: {
        "Red Bull Racing":   "Honda",
        "Mercedes":          "Mercedes",
        "Ferrari":           "Ferrari",
        "McLaren":           "Mercedes",
        "Aston Martin":      "Honda",
        "Alpine F1 Team":    "Renault",
        "Alpine":            "Renault",
        "Williams":          "Mercedes",
        "Racing Bulls":      "Honda",
        "Kick Sauber":       "Ferrari",   
        "Haas F1 Team":      "Ferrari",
    },
    2026: {
        "Red Bull Racing":   "Honda",
        "Mercedes":          "Mercedes",
        "Ferrari":           "Ferrari",
        "McLaren":           "Mercedes",
        "Aston Martin":      "Honda",
        "Alpine F1 Team":    "Renault",
        "Alpine":            "Renault",
        "Williams":          "Mercedes",
        "Racing Bulls":      "Honda",
        "Audi":              "Audi",     
        "Haas F1 Team":      "Ferrari",
        "Cadillac":          "Ferrari",   
    },
}


class FeatureEngineer:

    def transform(self, session_q, year: int) -> pd.DataFrame:
        laps = session_q.laps.pick_quicklaps()
        df = laps.groupby('Driver')['LapTime'].min().reset_index()
        df['LapTime'] = df['LapTime'].dt.total_seconds()

        df['quali_gap_to_pole'] = df['LapTime'] - df['LapTime'].min()
        df['quali_position'] = df['LapTime'].rank(method='first').astype(int)

        results = session_q.results[['Abbreviation', 'TeamName']]
        df = df.merge(results, left_on='Driver', right_on='Abbreviation')
        df = df.drop(columns=['Abbreviation'])

        pu_map = POWER_UNIT_MAP.get(year, POWER_UNIT_MAP[2026])
        df['pu_manufacturer'] = df['TeamName'].map(pu_map)

        df['intra_team_rank'] = df.groupby('TeamName')['quali_position'] \
            .rank(method='first').astype(int)

        df['intra_team_gap'] = df.groupby('TeamName')['quali_gap_to_pole'] \
            .transform(lambda x: x - x.min())

        gp_nome = session_q.event['EventName']
        circuit_info = get_circuit_info(gp_nome, year)
        for key, val in circuit_info.items():
            df[key] = val
        
        if 'mid_season_team_change' not in df.columns:
            df['mid_season_team_change'] = 0
        df['year'] = year
        
        return df