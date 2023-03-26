import json

GSHEETS = dict()


def sheets_main(ps, sheets):
    with open("keys/sheets.json", "r") as file:
        jsonmap = json.load(file)
        ps.SHEETID = jsonmap["id"]
        ps.sheets = sheets
        subs = jsonmap["subsheets"]
        for k, v in subs.items():
            GSHEETS[k] = ps.Subsheet(k)
            GSHEETS[k].apply(v)


def get_sub_sheet(n: str):
    return GSHEETS[n]


def get_sheets():
    return GSHEETS.values()
