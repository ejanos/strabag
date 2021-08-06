import xlsxwriter

workbook = xlsxwriter.Workbook('./data/b1.xlsx')

for worksheet in workbook.worksheets():
    print(worksheet)

#worksheet.write('J7', '55')