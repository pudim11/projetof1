
CIRCUIT_TYPE = {
    # Permanentes
    "Bahrain Grand Prix":            "permanent",
    "Australian Grand Prix":         "permanent",
    "Japanese Grand Prix":           "permanent",
    "Chinese Grand Prix":            "permanent",
    "Emilia Romagna Grand Prix":     "permanent", 
    "Austrian Grand Prix":           "permanent",
    "British Grand Prix":            "permanent",
    "Hungarian Grand Prix":          "permanent",
    "Dutch Grand Prix":              "permanent",
    "Italian Grand Prix":            "permanent",
    "United States Grand Prix":      "permanent",
    "Mexico City Grand Prix":        "permanent",
    "São Paulo Grand Prix":          "permanent",
    "Abu Dhabi Grand Prix":          "permanent",
    "Spanish Grand Prix":            "permanent",
    "Belgian Grand Prix":            "permanent",
    "Qatar Grand Prix":              "permanent",

    "Azerbaijan Grand Prix":         "hybrid",
    "Saudi Arabian Grand Prix":      "hybrid",
    "Las Vegas Grand Prix":          "hybrid",
    "Canadian Grand Prix":           "hybrid",

    "Monaco Grand Prix":             "street",
    "Singapore Grand Prix":          "street",
    "Miami Grand Prix":              "street",

    "Madrid Grand Prix":             "street",
}


HIGH_SPEED_CIRCUIT = {
    "Italian Grand Prix":            True,  
    "Belgian Grand Prix":            True,  
    "British Grand Prix":            True,   
    "Austrian Grand Prix":           True,
    "Dutch Grand Prix":              True, 
    "Bahrain Grand Prix":            True,
    "Spanish Grand Prix":            True,
    "Abu Dhabi Grand Prix":          True,
    "Australian Grand Prix":         False,
    "Monaco Grand Prix":             False,
    "Singapore Grand Prix":          False,
    "Miami Grand Prix":              False,
    "Hungarian Grand Prix":          False,
    "Azerbaijan Grand Prix":         False,
    "Saudi Arabian Grand Prix":      False,
    "Las Vegas Grand Prix":          False,
    "Canadian Grand Prix":           False,
    "Japanese Grand Prix":           False,
    "Chinese Grand Prix":            False,
    "United States Grand Prix":      False,
    "Mexico City Grand Prix":        False,
    "São Paulo Grand Prix":          False,
    "Qatar Grand Prix":              False,
    "Madrid Grand Prix":             False,  
    "Emilia Romagna Grand Prix":     False,
}

SPRINT_WEEKENDS = {
    2025: {
        "Belgian Grand Prix",
        "United States Grand Prix",
        "São Paulo Grand Prix",
        "Qatar Grand Prix",
    },
    2026: {
        "Canadian Grand Prix",
        "British Grand Prix",
        "Dutch Grand Prix",
        "Singapore Grand Prix",
    },
}


NEW_CIRCUITS_2026 = {"Madrid Grand Prix"}

GP_NAME_ALIASES = {
    "Emilia-Romagna Grand Prix": "Emilia Romagna Grand Prix",
    "Brazil Grand Prix":         "São Paulo Grand Prix",
    "Sao Paulo Grand Prix":      "São Paulo Grand Prix",
    "Great Britain Grand Prix":  "British Grand Prix",
    "USA Grand Prix":            "United States Grand Prix",
}

CALENDARIO_INCERTO_2026 = {
    "Bahrain Grand Prix",
    "Saudi Arabian Grand Prix",
    "Abu Dhabi Grand Prix",
}

def get_circuit_info(gp_nome: str, year: int) -> dict:
    """
    Retorna todas as features de circuito para um dado GP.
    Uso: df_gp = df_gp.assign(**get_circuit_info(gp_nome, year))
    """

    nome = GP_NAME_ALIASES.get(gp_nome, gp_nome)

    circuit_type   = CIRCUIT_TYPE.get(nome, "permanent")      
    is_high_speed  = HIGH_SPEED_CIRCUIT.get(nome, False)
    is_sprint      = nome in SPRINT_WEEKENDS.get(year, set())
    is_new_circuit = nome in NEW_CIRCUITS_2026
    is_street      = circuit_type == "street"

    return {
        "circuit_type":       CIRCUIT_TYPE.get(nome, "permanent"),
        "is_street":          int(CIRCUIT_TYPE.get(nome) == "street"),
        "is_high_speed":      int(HIGH_SPEED_CIRCUIT.get(nome, False)),
        "is_sprint_weekend":  int(nome in SPRINT_WEEKENDS.get(year, set())),
        "is_new_circuit":     int(nome in NEW_CIRCUITS_2026),
        "calendar_uncertain": int(year == 2026 and nome in CALENDARIO_INCERTO_2026),
    }