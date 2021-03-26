from datetime import date

from model_bakery.recipe import Recipe, foreign_key
from web.datasets.models import (
    CityCouncilAgenda,
    CityCouncilAttendanceList,
    CityCouncilBid,
    CityCouncilContract,
    CityCouncilExpense,
    CityCouncilMinute,
    CityCouncilRevenue,
    CityHallBid,
    File,
    Gazette,
    GazetteEvent,
    SyncInformation,
)

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


CityCouncilBid = Recipe(CityCouncilBid)


CityCouncilContract = Recipe(CityCouncilContract)


CityCouncilExpense = Recipe(CityCouncilExpense)


CityCouncilMinute = Recipe(CityCouncilMinute)


CityCouncilRevenue = Recipe(CityCouncilRevenue)


CityHallBid = Recipe(CityHallBid)


Gazette = Recipe(
    Gazette,
)


GazetteEvent = Recipe(GazetteEvent, gazette=foreign_key(Gazette))


File = Recipe(
    File,
)


SyncInformation = Recipe(
    SyncInformation,
)
