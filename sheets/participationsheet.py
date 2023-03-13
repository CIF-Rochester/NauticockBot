from sheets.commandoutput import GivePointsOutput
import sheets.base26 as base26
from sheets.semester import Semester

sheets = None
SHEETID = None

"""
    Gets the column name of the column to the right of the column provided.
    If the last column ends with 'Z', returns AA, returns AB, ... 'AZ' 
"""


def next_column_name(col: str) -> str:
    return base26.str_from_b26(base26.tob26(col) + 1)


class Subsheet:
    EVENTSROW = 1
    TOTAL = 2
    MEAN = 3
    MEDIAN = 4
    QUARTILE1 = 5
    # Represents what row user data is stored at on the sheet. This is after Name, Total, Mean, Median, 1st Quartile
    USERDATASTART = 6
    # Where names show up
    NAME = "A"
    EVENTSSTART = "F"

    sheetname = ""

    def __init__(self, name: str):
        self.sheetname = name

    # Allow loading from JSON.
    def apply(self, jsonmap: dict):
        self.EVENTSROW = jsonmap["EVENTSROW"]
        self.TOTAL = jsonmap["TOTAL"]
        self.MEAN = jsonmap["MEAN"]
        self.MEDIAN = jsonmap["MEDIAN"]
        self.QUARTILE1 = jsonmap["QUARTILE1"]
        self.USERDATASTART = jsonmap["USERDATASTART"]
        self.NAME = jsonmap["NAME"]
        self.EVENTSSTART = jsonmap["EVENTSSTART"]

    """
        Gets the next empty column in the desired sheet. A column is empty if the first row does not contain values.
        Inputting a None or empty string will automatically check column 'A' first.
        Providing a column such as 'A' will check the next column ('B' in this case)
    """

    def next_open_column(self, col: str) -> str:
        col = next_column_name(col)
        result = sheets.sheet.values().get(spreadsheetId=SHEETID, range=self.named_range() + col + "1").execute()
        # Result will not contain a values key if the column is open.
        if "values" not in result:
            return col
        # If not open, check the next column.
        else:
            return self.next_open_column(col)

    """
        Creates a new event in the desired sheet in the next open column.
        Automatically Initializes the TOTAL, MEAN, MEDIAN, and 1ST QUARTILE rows with their math functions.
    """

    def create_new_event(self, name: str) -> str:
        col = self.next_open_column("")
        sheets.sheet.values().update(
            spreadsheetId=SHEETID,
            valueInputOption='USER_ENTERED',
            range=self.named_range() + c1range(col, 1, 5),
            body={
                "majorDimension": 'COLUMNS',
                "values": [[name,
                            # TOTAL
                            formulaic(self.sum_column(col)),
                            # MEAN
                            formulaic(
                                a1format(col, self.TOTAL) + "/" + counta(c1range(self.NAME, self.USERDATASTART, -1))),
                            # MEDIAN
                            formulaic(round_val(a1format(col, self.MEAN))),
                            # 1st Quartile
                            formulaic(round_val(a1format(col, self.MEAN) + "-0.25"))
                            ]]
            }
        ).execute()
        return col

    """
        Gives all names in the user list a point under the requested event. If the event doesn't exist it will be created.
    """

    def give_points_can_create(self, event: str, users: list) -> GivePointsOutput:
        events = self.get_events()
        if event in events:
            # Ensure the correct column is selected.
            return self.give_points(base26.str_from_b26(base26.tob26(self.EVENTSSTART) + events.index(event)), users)
        else:
            out = self.give_points(self.create_new_event(event), users)
            out.createdEvent = True
            return out

    """
        Gives all names in the users list a point under the requested column.
        TODO: Allow for additive point granting.
    """

    def give_points(self, col: str, users: list[str]) -> GivePointsOutput:
        names = self.get_names()
        # The data sent to the cloud.
        upload = self.get_points(col)
        # Failed to find users.
        failed = []
        # Successfully found.
        success = []
        # Convert to lowercase for user convenience
        for x in range(len(names)):
            names[x] = names[x].lower()
        for x in range(len(users)):
            users[x] = users[x].lower()
        # Find names matching the user query and grant them points.
        for u in users:
            options = []
            # Check if any names start with the name given.
            for name in names:
                if name.startswith(u):
                    options.append(name)
            # If only one person has been found, give them a point.
            if len(options) == 1:
                success.append(u + " = " + options[0])
                idx = names.index(options[0])
                if not upload[idx]:
                    upload[idx] = "1"
                else:
                    upload[idx] = str(int(upload[idx]) + 1)

            # Handle duplicates
            elif len(options) > 0:
                dupes = u + " has Duplicates: "
                for o in options:
                    dupes += o + ","
                failed.append(dupes)
            # Handle not found.
            else:
                failed.append(u + " Not Found.")
        sheets.sheet.values().update(
            spreadsheetId=SHEETID,
            valueInputOption='USER_ENTERED',
            range=self.named_range() + c1range(col, self.USERDATASTART, self.USERDATASTART + len(names)),
            body={
                "majorDimension": 'COLUMNS',
                "values": [upload]
            }
        ).execute()
        return GivePointsOutput(createdevent=False, success=success, failed=failed)

    def get_points(self, col: str):
        results = sheets.sheet.values().get(
            spreadsheetId=SHEETID,
            range=self.named_range() + c1range(col, self.USERDATASTART, -1),
            majorDimension="COLUMNS"
        ).execute()
        ret = [""] * len(self.get_names())
        if "values" in results:
            response = results["values"][0]
            for i in range(len(response)):
                if i >= len(ret):
                    break
                ret[i] = response[i]
        return ret

    # Specifies that the range is in a subsheet.
    def named_range(self):
        return self.sheetname + "!"

    """
        Gets the name of all events in the sheet.
    """

    def get_events(self) -> list:
        results = sheets.sheet.values().get(spreadsheetId=SHEETID, majorDimension="ROWS", range=self.named_range() + r1range(self.EVENTSROW, self.EVENTSSTART, "")).execute()
        return results["values"][0]

    """
        Gets all names in the participation sheet
    """

    def get_names(self) -> list[str]:
        results = sheets.sheet.values().get(spreadsheetId=SHEETID, majorDimension="COLUMNS", range=self.named_range() + c1range(self.NAME, self.USERDATASTART, -1)).execute()
        return results["values"][0]

    # For formulaic cells, adds all numbers in the range provided together.
    def sum_column(self, col: str) -> str:
        return "SUM(" + c1range(col, self.USERDATASTART, -1) + ")"


# For formulaic cells, rounds to the nearest integer.
def round_val(a1range: str) -> str:
    return "ROUND(" + a1range + ")"


# For formulaic cells, returns the number of non-empty cells in a range.
def counta(a1range: str) -> str:
    return "COUNTA(" + a1range + ")"


# Tells sheets to use a formulaic value for a cell.
def formulaic(formula: str) -> str:
    return "=" + formula


"""
    Returns in sheets A1 format. Returns CI if index >= 0 else returns C
    If col is empty, returns I.
"""


def a1format(col: str, index: int) -> str:
    if index < 0:
        return col
    if not col:
        return str(index)
    return col + str(index)


# Returns in format: CS:CE
def c1range(col: str, start: int, end: int) -> str:
    return a1format(col, start) + ":" + a1format(col, end)


# Returns in format: SR:ER
def r1range(row: int, start: str, end: str) -> str:
    return a1format(start, row) + ":" + a1format(end, row)


# Debug method, use if you're questioning if GSheets is working
def print_sheet():
    result = sheets.sheet.values().get(spreadsheetId=SHEETID, range="Masterlist!A1:AZ40").execute()
    print(result)


def get_sheet_semester() -> Semester:
    response = sheets.sheet.get(spreadsheetId=SHEETID, ranges=[], includeGridData=False).execute()
    title = str(response["properties"]["title"])
    splits = title.split()
    if splits[len(splits) - 2] == "Spring":
        return Semester(year=int(splits[len(splits) - 1]), season=0)
    else:
        return Semester(year=int(splits[len(splits) - 1]), season=1)
