import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from scipy.stats import spearmanr

from src.preprocessing.features import FeatureEngineer
from src.model.trainer import get_latest_model_path, FEATURE_COLS

RESULTS_PATH = "results/"


def predict_gp(session_q, year: int, gp_nome: str) -> dict:
    engineer = FeatureEngineer()
    df = engineer.transform(session_q, year)

    salvo = joblib.load(get_latest_model_path())
    model = salvo['model']
    le    = salvo['encoder']

    feature_cols = [c for c in FEATURE_COLS if c in df.columns]
    X = df[feature_cols].copy()
    pu_conhecidos = set(le.classes_)
    X['pu_manufacturer'] = X['pu_manufacturer'].fillna('Unknown').apply(
        lambda x: x if x in pu_conhecidos else le.classes_[0]
    )
    X['pu_manufacturer'] = le.transform(X['pu_manufacturer'])

    print(df[df['pu_manufacturer'].isna()][['Driver', 'TeamName']])

    scores        = model.predict(X)
    df['score']   = scores
    df_sorted     = df.sort_values('score', ascending=False)
    classificacao = df_sorted['Driver'].tolist()

    return {
        'gp':             gp_nome,
        'year':           year,
        'predicted_at':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'classification': classificacao,
        'scores':         dict(zip(df_sorted['Driver'], df_sorted['score'].tolist()))
    }


def save_prediction(prediction: dict, gp_nome: str, year: int) -> None:
    os.makedirs(RESULTS_PATH, exist_ok=True)
    nome_limpo = gp_nome.lower().replace(' ', '_')
    caminho = f"{RESULTS_PATH}pred_{year}_{nome_limpo}.json"
    with open(caminho, 'w') as f:
        json.dump(prediction, f, indent=2, ensure_ascii=False)
    print(f"💾 Predição salva: {caminho}")


def load_prediction(gp_nome: str, year: int) -> dict:
    nome_limpo = gp_nome.lower().replace(' ', '_')
    caminho = f"{RESULTS_PATH}pred_{year}_{nome_limpo}.json"
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Predição não encontrada: {caminho}")
    with open(caminho, 'r') as f:
        return json.load(f)


def evaluate(prediction: dict, session_r) -> dict:
    resultados = session_r.results[['Abbreviation', 'Position']].copy()
    resultados['Position'] = pd.to_numeric(
        resultados['Position'], errors='coerce'
    )
    resultados = session_r.results[['Abbreviation']].copy()
    resultados = resultados.reset_index(drop=True)
    real = resultados['Abbreviation'].tolist()

    predicted = prediction['classification']

    winner_correct = predicted[0] == real[0]

    acertos_top3 = len(set(predicted[:3]) & set(real[:3]))
    top3_accuracy = acertos_top3 / 3

    erros = []
    for piloto in real:
        if piloto in predicted:
            pos_prev = predicted.index(piloto) + 1
            pos_real = real.index(piloto) + 1
            erros.append(abs(pos_prev - pos_real))
    mean_position_error = float(np.mean(erros)) if erros else 0.0

    pilotos_comuns = [p for p in predicted if p in real]
    posicoes_prev  = [predicted.index(p) + 1 for p in pilotos_comuns]
    posicoes_real  = [real.index(p) + 1      for p in pilotos_comuns]
    correlacao, _  = spearmanr(posicoes_prev, posicoes_real)

    return {
        'winner_correct':      winner_correct,
        'top3_accuracy':       round(top3_accuracy, 3),
        'mean_position_error': round(mean_position_error, 2),
        'rank_correlation':    round(float(correlacao), 3)
    }


def run_gp_cycle(session_q, session_r, year: int, gp_nome: str) -> dict:
    prediction = predict_gp(session_q, year, gp_nome)
    save_prediction(prediction, gp_nome, year)

    metrics = evaluate(prediction, session_r)

    vencedor_real = session_r.results.iloc[0]['Abbreviation']
    vencedor_ok   = "✓" if metrics['winner_correct'] else "✗"

    print(f"{'─' * 50}")
    print(f"🏁 {gp_nome} {year}")
    print(f"   Vencedor previsto : {prediction['classification'][0]}")
    print(f"   Vencedor real     : {vencedor_real}")
    print(f"   Acertou vencedor  : {vencedor_ok}")
    print(f"   Acurácia top-3    : {metrics['top3_accuracy']:.1%}")
    print(f"   Erro médio        : {metrics['mean_position_error']:.1f} posições")
    print(f"   Correlação ranking: {metrics['rank_correlation']:.3f}")
    print(f"{'─' * 50}")

    return metrics


if __name__ == "__main__":
    pass