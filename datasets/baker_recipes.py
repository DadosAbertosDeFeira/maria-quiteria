from datetime import date

from datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilMinute,
    CityHallBid,
    Gazette,
    GazetteEvent,
)
from model_bakery.recipe import Recipe, foreign_key

CityCouncilAgenda = Recipe(
    CityCouncilAgenda,
    date=date(2020, 3, 18),
    details="PROJETOS DE LEI ORDINÁRIA EM 2ª DISCUSSÃO 017/20",
    event_type="sessao_ordinaria",
    title="ORDEM DO DIA - 18 DE MARÇO DE 2020",
)


CityCouncilAttendanceList = Recipe(
    CityCouncilAttendanceList,
    date=date(2020, 2, 3),
    description="Abertura da 1ª etapa do 4º período da 18ª legislatura",
    council_member="Competente da Silva",
    status="presente",
)


CityCouncilContract = Recipe(CityCouncilContract)


CityCouncilExpense = Recipe(CityCouncilExpense)


CityCouncilMinute = Recipe(CityCouncilMinute)


Gazette = Recipe(Gazette,)


GazetteEvent = Recipe(GazetteEvent, gazette=foreign_key(Gazette))


CityHallBid = Recipe(CityHallBid)
