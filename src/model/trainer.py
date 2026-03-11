import pandas as pd
import numpy as np
import joblib
import os

MODEL_DIR  = "models/"
DATA_PATH  = "data/f1_master_dataset.csv"

FEATURE_COLS = [
    "quali_position",
    "quali_gap_to_pole",
    "intra_team_rank",
    "intra_team_gap",
    "is_street",
    "is_high_speed",
    "is_sprint_weekend",
    "is_new_circuit",
    "pu_manufacturer",
    "mid_season_team_change",
]

TARGET_COL = "relevance"


def compute_sample_weights(df: pd.DataFrame) -> np.ndarray:
    pesos_por_ano = {2026: 1.0, 2025: 0.05, 2024: 0.08, 2023: 0.05}
    pesos = df['year'].map(pesos_por_ano).fillna(0.02)
    return pesos.values


def get_groups(df: pd.DataFrame) -> np.ndarray:
    grupos = df.groupby('gp_id', sort=False).size().values
    return grupos


def load_data() -> tuple:
    from sklearn.preprocessing import LabelEncoder

    df = pd.read_csv(DATA_PATH)
    df = df.sort_values('gp_id').reset_index(drop=True)

    le = LabelEncoder()
    df['pu_manufacturer'] = le.fit_transform(df['pu_manufacturer'].fillna('Unknown'))

    feature_cols_disponiveis = [c for c in FEATURE_COLS if c in df.columns]
    X = df[feature_cols_disponiveis]
    y = df[TARGET_COL]

    return X, y, df, le 


def train() -> None:
    import lightgbm as lgb

    X, y, df, le = load_data()  
    pesos  = compute_sample_weights(df)
    grupos = get_groups(df)

    ranker = lgb.LGBMRanker(
        objective='lambdarank',
        metric='ndcg',
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=15,
        importance_type='gain'
    )

    ranker.fit(X, y, group=grupos, sample_weight=pesos)

    os.makedirs(MODEL_DIR, exist_ok=True)
    versao = len([f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]) + 1
    model_path = f"{MODEL_DIR}model_v{versao}.pkl"


    joblib.dump({'model': ranker, 'encoder': le}, model_path)

    print(f"Modelo v{versao} treinado com sucesso!")
    print(f"Amostras: {len(df)} | GPs Únicos: {df['gp_id'].nunique()}")
    print(f"Salvo em: {model_path}")


def retrain(novo_gp_nome: str) -> None:
    print(f"🔄 Retreinando após: {novo_gp_nome}")
    train()


def get_latest_model_path() -> str:
    arquivos = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]
    if not arquivos:
        raise FileNotFoundError("Nenhum modelo treinado encontrado. Rode train() primeiro.")
    arquivos.sort()
    return os.path.join(MODEL_DIR, arquivos[-1])


if __name__ == "__main__":
    train()