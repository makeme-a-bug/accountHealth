from scraper.manager import Manager
from googlesheet.core import get_input_sheet_values

if __name__ == "__main__":
    inputs = get_input_sheet_values()
    m = Manager(inputs)
    m.gather_data()