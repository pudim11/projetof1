import fastf1
import pandas as pd
import os
from src.api.fetcher import F1Fetcher
from src.preprocessing.features import FeatureEngineer
from src.preprocessing.circuit_metadata import get_circuit_info, SPRINT_WEEKENDS

fastf1.Cache.enable_cache("data/fastf1_cache")

OUTPUT_PATH = "data/f1_master_dataset.csv"

PU_MAP_FALLBACK = {
    "Haas F1 Team":   "Ferrari",
    "Racing Bulls":   "Honda",
    "AlphaTauri":     "Honda",
    "Alfa Romeo":     "Ferrari",
    "Alpine F1 Team": "Renault",
}

PILOTOS_EXCLUIR = {"DOO"}

TROCAS_EQUIPE = {
    "TSU": ["Racing Bulls", "Red Bull Racing"],
}

CADILLAC_DRIVERS_2026: set = set()


def limpar_gp(df: pd.DataFrame, gp_id: int, gp_nome: str, year: int) -> pd.DataFrame:
    """Limpeza, enriquecimento e validação de um GP antes de salvar."""

    df = df[~df['Driver'].isin(PILOTOS_EXCLUIR)].copy()

    df['final_position'] = pd.to_numeric(
        df['ClassifiedPosition'], errors='coerce'
    ).fillna(21).astype(int)
    df = df.drop(columns=['ClassifiedPosition', 'Abbreviation'], errors='ignore')

    df['dnf'] = (df['final_position'] == 21).astype(int)

    df['relevance'] = (22 - df['final_position']).clip(lower=0)

    mask = df['pu_manufacturer'].isna()
    df.loc[mask, 'pu_manufacturer'] = df.loc[mask, 'TeamName'].map(PU_MAP_FALLBACK)

    df['mid_season_team_change'] = df['Driver'].isin(TROCAS_EQUIPE).astype(int)

    df['gp_id']   = gp_id
    df['gp_nome'] = gp_nome
    df['year']    = year

    return df


def gps_ja_baixados() -> set:
    if not os.path.exists(OUTPUT_PATH):
        return set()
    df = pd.read_csv(OUTPUT_PATH, usecols=['gp_nome'])
    return set(df['gp_nome'].unique())


def validar_gp(df: pd.DataFrame, gp_nome: str) -> bool:
    ok = True

    unique_pos = df['final_position'].nunique()
    if unique_pos <= 2:
        print(f"final_position com apenas {unique_pos} valor(es) único(s)!")
        ok = False

    decimais = (df['quali_position'] % 1 != 0).sum()
    if decimais > 0:
        print(f"{decimais} posições decimais em quali_position!")
        ok = False

    nulos_pu = df['pu_manufacturer'].isna().sum()
    if nulos_pu > 0:
        print(f"{nulos_pu} nulos em pu_manufacturer!")
        ok = False

    return ok

def baixar_temporada(ano: int):
    fetcher  = F1Fetcher()
    engineer = FeatureEngineer()

    os.makedirs("data/fastf1_cache", exist_ok=True)

    schedule = fastf1.get_event_schedule(ano)
    corridas = schedule[schedule['EventFormat'] != 'testing'].reset_index(drop=True)
    sprint_gps = SPRINT_WEEKENDS.get(ano, set())

    ja_baixados = gps_ja_baixados()
    print(f"Temporada {ano} — {len(corridas)} GPs | {len(sprint_gps)} com Sprint")
    if ja_baixados:
        print(f"{len(ja_baixados)} GPs já no dataset")

    for gp_id, (_, row) in enumerate(corridas.iterrows()):
        gp_nome    = row['EventName']
        is_sprint  = gp_nome in sprint_gps

        if gp_nome in ja_baixados:
            print(f" [{gp_id:02d}] {gp_nome} — já salvo")
            continue

        sprint_label = "🏃 Sprint" if is_sprint else "Normal"
        print(f"\n  [{gp_id:02d}] {gp_nome} ({sprint_label})")

        try:
            q_sess = fetcher.get_race_session(ano, gp_nome, 'Q')
            r_sess = fetcher.get_race_session(ano, gp_nome, 'R')

            if not (q_sess and r_sess):
                print(f"Sessões indisponíveis — GP ainda não ocorreu?")
                continue

            df_gp = engineer.transform(q_sess, ano)

            results = r_sess.results[['Abbreviation', 'ClassifiedPosition']]
            df_gp   = df_gp.merge(results, left_on='Driver', right_on='Abbreviation')

            df_gp = limpar_gp(df_gp, gp_id, gp_nome, ano)

            if not validar_gp(df_gp, gp_nome):
                print(f"GP com dados inválidos — pulando para não corromper o dataset")
                continue

            escrever_header = not os.path.exists(OUTPUT_PATH)
            df_gp.to_csv(OUTPUT_PATH, mode='a', header=escrever_header, index=False)

            pos_str = sorted(df_gp['final_position'].unique())
            print(f"{len(df_gp)} pilotos | posições: {pos_str}")

        except Exception as e:
            print(f"Erro em {gp_nome}: {e}")

    # Resumo final
    if os.path.exists(OUTPUT_PATH):
        df_final = pd.read_csv(OUTPUT_PATH)
        print("\n" + "─" * 50)
        print(f"  Dataset: {OUTPUT_PATH}")
        print(f"  Linhas       : {len(df_final)}")
        print(f"  GPs          : {df_final['gp_nome'].nunique()}")
        print(f"  Anos         : {sorted(df_final['year'].unique())}")
        print(f"  Colunas      : {list(df_final.columns)}")
        print(f"  PU nulos     : {df_final['pu_manufacturer'].isna().sum()}")
        print(f"  Quali dec.   : {(df_final['quali_position'] % 1 != 0).sum()}")
        print(f"  Pos. únicas  : {df_final['final_position'].nunique()} (esperado: ~21)")


if __name__ == "__main__":
    import sys
    ano = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    baixar_temporada(ano)