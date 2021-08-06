import pandas as pd

def process():
    df = pd.read_excel('./data/b1.xlsx', header=0, sheet_name='Total', engine='openpyxl')
    #print(df)
    # print column headers
    #print(df.columns.ravel())
    # print column
    print(df['Work/\nMunkanem.1'].tolist())
    # print row
    #print(df.iloc[832])
    # lekérdezés sor
    #print(df.loc[(df["Quantity/\nmennyiség"] == 3.00) & (df["Materila unit price/\nanyag egység ár HUF"] == 0)])
    #df.to_excel("converted.xlsx")

    # https://xlsxwriter.readthedocs.io/worksheet.html#write_url









# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    process()
