
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from pick_utils import multiple_pick


def find_marks_column(sheet: Worksheet, course_work: str):
    for col in sheet.iter_cols():
        for cell in col:
            if type(cell.value) is str and cell.value.lower() == course_work.lower():
                return cell.column_letter


workbook = openpyxl.open("C:\\Users\\Temp\\Desktop\\test.xlsx")
worksheet = workbook["Two"]

print(find_marks_column(worksheet, "Assignment 1"))
