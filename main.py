from scraper.manager import Manager
from googlesheet.core import get_input_sheet_values

if __name__ == "__main__":
    inputs = get_input_sheet_values()
    m = Manager([["https://docs.google.com/spreadsheets/d/1YwdL33MGS4NNk6UCIu8RDT8PcOmzKyKCXVBvrSrG9XM/edit#gid=0","Buyalot SC"]])
    m.gather_data()