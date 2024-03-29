GAZETTES_API = "api/datasets/gazettes"
CITY_HALL_API = "api/datasets/city-hall"
CITY_COUNCIL_API = "api/datasets/city-council"

AVAILABLE_ENDPOINTS_BY_PUBLIC_AGENCY = {
    "city-council": {
        "public_agency": "Câmara Municipal",
        "endpoints": [
            {
                "friendly_name": "Agenda dos vereadores",
                "endpoint": f"{CITY_COUNCIL_API}/agenda/",
            },
            {
                "friendly_name": "Atas das sessões",
                "endpoint": f"{CITY_COUNCIL_API}/minute/",
            },
            {
                "friendly_name": "Diário Oficial - Legislativo",
                "endpoint": f"{GAZETTES_API}/?power=legislative",
            },
            {
                "friendly_name": "Lista de presença dos vereadores",
                "endpoint": f"{CITY_COUNCIL_API}/attendance-list/",
            },
        ],
    },
    "city-hall": {
        "public_agency": "Prefeitura",
        "endpoints": [
            {
                "friendly_name": "Diário Oficial - Executivo",
                "endpoint": f"{GAZETTES_API}/?power=executive",
            },
            {
                "friendly_name": "Licitações",
                "endpoint": f"{CITY_HALL_API}/bids/",
            },
        ],
    },
}
