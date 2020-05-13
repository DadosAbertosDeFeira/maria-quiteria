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
        "file_code": "253",
        "phase": "empenho",
        "file_line": "2",
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
        "modality": "ISENTO",
        "company_or_person": "VEREADORES",
        "document": "14.488.415/0001-60",
        "phase_code": "14000001",
        "number": "001/2014",
        "process_number": "",
        "value": 3790000.00,
    }
    assert to_expense(item) == expected_expense
