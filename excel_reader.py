from pprint import pprint
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet


def is_number(s):
    if not s:
        return False
    try:
        float(s)
    except ValueError:
        return False
    return True


# Open the workbook
wb = openpyxl.load_workbook("C:/Users/Temp/Desktop/test.xlsx")


sheet: Worksheet = wb['INTY1S1']  # type: ignore

student_col = 'C'
marks_col = 'D'

student_numbers = list([it.value for it in sheet[student_col]])
marks = list([it.value for it in sheet[marks_col]])

grades_book = list(zip(student_numbers, marks))

result = []

for grade in grades_book:
    if is_number(grade[0]) or True:
        result.append([int(float(grade[0])), grade[1]])

pprint(result)
