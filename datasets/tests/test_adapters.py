from datetime import date, datetime

from datasets.adapters import to_bid, to_contract, to_expense, to_revenue


def test_save_expense_from_csv():
    item = {
        "CODARQUIVO": "253",
        "CODETAPA": "EMP",
        "CODLINHA": "2",
        "CODUNIDORCAM": "101",
        "DSDESPESA": "IMPORTE DESTINADO A PAGAMENTO DE SUBSIDIOS DURANTE O "
        "PERIODO.                                         ",
        "DSFONTEREC": "0000 - " "TESOURO                                          ",
        "DSFUNCAO": "01 - " "LEGISLATIVA                                      ",
        "DSNATUREZA": "319011010000000000 - V.Vant.Fixas P.Civil(Ve.Base "
        "Folha)                            2003 - Administracao da acao "
        "legislativa                          ",
        "DSSUBFUNCAO": "031 - " "ACAO                                             ",
        "DTPUBLICACAO": "2/1/2014",
        "DTREGISTRO": "2/1/2014",
        "EXCLUIDO": "N",
        "MODALIDADE": "ISENTO                        ",
        "NMCREDOR": "VEREADORES                           ",
        "NUCPFCNPJ": "14.488.415/0001-60",
        "NUMETAPA": "14000001                      ",
        "NUMPROCADM": "001/2014                      ",
        "NUMPROCLIC": "                              ",
        "VALOR": "3790000,00",
    }

    expected_expense = {
        "phase": "empenho",
        "budget_unit": "101",
        "summary": "IMPORTE DESTINADO A PAGAMENTO DE SUBSIDIOS DURANTE O PERIODO.",
        "resource": "0000 - TESOURO",
        "function": "01 - LEGISLATIVA",
        "legal_status": "319011010000000000 - V.Vant.Fixas P.Civil(Ve.Base "
        "Folha)                            2003 - Administracao da acao "
        "legislativa",
        "subfunction": "031 - ACAO",
        "published_at": date(2014, 1, 2),
        "date": date(2014, 1, 2),
        "excluded": False,
        "modality": "isento",
        "company_or_person": "VEREADORES",
        "document": "14.488.415/0001-60",
        "phase_code": "14000001",
        "number": "001/2014",
        "process_number": "",
        "value": 3790000.00,
        "external_file_code": "253",
        "external_file_line": "2",
    }
    expense_obj = to_expense(item)
    assert expense_obj.phase == expected_expense["phase"]
    assert expense_obj.budget_unit == expected_expense["budget_unit"]
    assert expense_obj.resource == expected_expense["resource"]
    assert expense_obj.function == expected_expense["function"]
    assert expense_obj.legal_status == expected_expense["legal_status"]
    assert expense_obj.subfunction == expected_expense["subfunction"]
    assert expense_obj.published_at == expected_expense["published_at"]
    assert expense_obj.excluded == expected_expense["excluded"]
    assert expense_obj.modality == expected_expense["modality"]
    assert expense_obj.company_or_person == expected_expense["company_or_person"]
    assert expense_obj.document == expected_expense["document"]
    assert expense_obj.phase_code == expected_expense["phase_code"]
    assert expense_obj.number == expected_expense["number"]
    assert expense_obj.process_number == expected_expense["process_number"]
    assert expense_obj.value == expected_expense["value"]


def test_save_contract_from_csv():
    item = {
        "CODCON": "43",
        "DSCON": "CONTRATO Nº 004/2014 - PRESTAÇÃO DE SERVIÇO",
        "OBJETOCON": "Contratação conforme Licitação 01/2014, Pregão 01/2014.",
        "CPFCNPJCON": "92.559.830/0001-71",
        "NMCON": "GREEN CARD S/A REFEIÇÕES COMÉRCIO E SERVIÇOS",
        "VALORCON": "1157115,96",
        "DTCON": "28/3/2014",
        "DTCONFIM": "27/3/2015",
        "EXCLUIDO": "N",
    }

    expected_expense = {
        "external_code": "43",
        "description": "CONTRATO Nº 004/2014 - PRESTAÇÃO DE SERVIÇO",
        "details": "Contratação conforme Licitação 01/2014, Pregão 01/2014.",
        "company_or_person_document": "92.559.830/0001-71",
        "company_or_person": "GREEN CARD S/A REFEIÇÕES COMÉRCIO E SERVIÇOS",
        "value": 1157115.96,
        "start_date": date(2014, 3, 28),
        "end_date": date(2015, 3, 27),
        "excluded": False,
    }
    contract_obj = to_contract(item)
    assert contract_obj.external_code == expected_expense["external_code"]
    assert contract_obj.description == expected_expense["description"]
    assert contract_obj.details == expected_expense["details"]
    assert (
        contract_obj.company_or_person_document
        == expected_expense["company_or_person_document"]
    )
    assert contract_obj.company_or_person == expected_expense["company_or_person"]
    assert contract_obj.value == expected_expense["value"]
    assert contract_obj.start_date == expected_expense["start_date"]
    assert contract_obj.end_date == expected_expense["end_date"]
    assert contract_obj.excluded == expected_expense["excluded"]


def test_adapt_from_csv_data_to_bid():
    item = {
        "CODLIC": "42",
        "CODTIPOLIC": "7",
        "NUMLIC": "01/2014",
        "NUMTIPOLIC": "01/2014",
        "OBJETOLIC": "Aquisição de gêneros alimentícios em estabelecimentos",
        "DTLIC": "26/2/2014 09:00:00",
        "EXCLUIDO": "N",
    }
    expected_bid = {
        "external_code": "42",
        "modality": "pregao_presencial",
        "code": "01/2014",
        "code_type": "01/2014",
        "description": "Aquisição de gêneros alimentícios em estabelecimentos",
        "session_at": datetime(2014, 2, 26, 9, 0, 0),
        "excluded": False,
    }

    bid_obj = to_bid(item)

    assert bid_obj.external_code == expected_bid["external_code"]
    assert bid_obj.modality == expected_bid["modality"]
    assert bid_obj.code == expected_bid["code"]
    assert bid_obj.code_type == expected_bid["code_type"]
    assert bid_obj.description == expected_bid["description"]
    assert bid_obj.session_at == expected_bid["session_at"]
    assert bid_obj.excluded == expected_bid["excluded"]


def test_adapt_from_csv_data_to_revenue():
    item = {
        "CODLINHA": "27",
        "CODUNIDGESTORA": "101",
        "DTPUBLICACAO": "1/1/2014",
        "DTREGISTRO": "1/1/2014",
        "TIPOREC": "ORC",
        "MODALIDADE": "Repasse a Prefeitura indenização",
        "DSRECEITA": "TESTE DE RECEITA",
        "VALOR": "123131,00",
        "FONTE": "PREFEITURA",
        "DSNATUREZA": "CONTRATO",
        "DESTINACAO": "ORCAMENTO",
        "EXCLUIDO": "S",
    }

    expected_revenue = {
        "external_code": "27",
        "budget_unit": "101",
        "published_at": date(2014, 1, 1),
        "registered_at": date(2014, 1, 1),
        "revenue_type": "orcamentaria",
        "modality": "repasse a prefeitura indenização",
        "description": "TESTE DE RECEITA",
        "value": 123131.00,
        "resource": "prefeitura",
        "legal_status": "contrato",
        "destination": "orcamento",
        "excluded": True,
    }

    revenue_obj = to_revenue(item)

    assert revenue_obj.external_code == expected_revenue["external_code"]
    assert revenue_obj.budget_unit == expected_revenue["budget_unit"]
    assert revenue_obj.published_at == expected_revenue["published_at"]
    assert revenue_obj.registered_at == expected_revenue["registered_at"]
    assert revenue_obj.revenue_type == expected_revenue["revenue_type"]
    assert revenue_obj.modality == expected_revenue["modality"]
    assert revenue_obj.description == expected_revenue["description"]
    assert revenue_obj.value == expected_revenue["value"]
    assert revenue_obj.resource == expected_revenue["resource"]
    assert revenue_obj.legal_status == expected_revenue["legal_status"]
    assert revenue_obj.destination == expected_revenue["destination"]
    assert revenue_obj.excluded == expected_revenue["excluded"]
