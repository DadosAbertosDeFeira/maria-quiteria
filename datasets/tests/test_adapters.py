from datetime import date

from datasets.adapters import to_expense


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
