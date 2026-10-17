import sys
import pandas as pd

path = 'data/PHC5-2022_Main_Indicators.xlsx'
xls = pd.ExcelFile(path)

if len(sys.argv) == 1:
    # no argument: list every sheet name with its number
    for i, name in enumerate(xls.sheet_names):
        print(i, name)
else:
    # with a sheet name: show its first 45 rows
    df = pd.read_excel(xls, sheet_name=sys.argv[1], header=None)
    print(df.head(45).to_string())
    