from typing import List,Union
import gspread
import pandas as pd

from .creds import get_creds


CREDS = get_creds()
G_CLIENT = gspread.authorize(CREDS)
MASTER_SHEET = "https://docs.google.com/spreadsheets/d/15-FXk8OWTN7Z1Mwqtv9YsvLCOI813xikUVDO3XlxfN8"
OUTPUT_SHEET = "https://docs.google.com/spreadsheets/d/1z7oWa711Fk1GUhOFP5hW4Sfrrsi6rsjN6zuhc_ZRdTw"



def get_input_sheet_values() -> List[List]:

    """
    Get all the reviews link sheets from master google spread sheet
    """

    try:

        spread_sheet = G_CLIENT.open_by_url(MASTER_SHEET)
        sheet = spread_sheet.worksheet("Sheet1")
        # Call the Sheets API
        table = pd.DataFrame(sheet.get_all_records())
        links = table['Sheet URLs']
        profiles = table['Account Name']

        result = list(zip(links,profiles))

        if not result:
            print('No data found.')
            return []

        result = list(filter(lambda x: len(x[1]) > 1 and  x[0].startswith("https"),result))

        return result 

    except Exception as e:
        print("couldn't work with master sheet")
        print(e)
        return []


def update_sheet(sheet_url,data):
    try:
        spread_sheet = G_CLIENT.open_by_url(sheet_url)
    except:
        print("main working sheet not found: ",OUTPUT_SHEET)
    
    try:
        sheet = spread_sheet.get_worksheet(0)
    except:
        print(f"sheet not found")
        return
        # sheet = spread_sheet.add_worksheet(title=sheet_name, rows=100, cols=20)

    sheet.clear()
    if len(data) > 0:
        sheet.update([data.columns.values.tolist()] + data.values.tolist())
    else:
        sheet.update([["Reason","Date","ASIN","Product Title","Action Taken","Status",]])


