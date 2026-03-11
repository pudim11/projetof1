import fastf1


class F1Fetcher:

    def get_race_session(self, year: int, gp_nome: str, session_type: str):
        """
        Carrega uma sessão do FastF1.

        session_type:
          'Q'  = Qualifying (qualificação do GP)
          'R'  = Race (corrida principal)
          'SQ' = Sprint Qualifying
          'S'  = Sprint Race

        Retorna a sessão carregada ou None se não estiver disponível.
        """
        try:
            session = fastf1.get_session(year, gp_nome, session_type)
            session.load()
            return session
        except Exception as e:
            print(f"Sessão {session_type} indisponível para {gp_nome} {year}: {e}")
            return None