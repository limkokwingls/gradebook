import imp
from pathlib import Path
from pprint import pprint
from types import NoneType
from openpyxl import Workbook
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from rich.prompt import Prompt
from rich.console import Console
from rich.prompt import Confirm
from pick import pick

from console_utils import print_in_table



error_console = Console(stderr=True, style="bold red")


def is_number(s):
    if not s or type(s) == NoneType:
        return False
    try:
        float(s)
    except ValueError:
        return False
    return True

def open_file() -> Workbook: 
    workbook: Workbook | None = None
    while workbook == None:
        try:
            file_path = Prompt.ask("Workbook file path", default="C:/Users/Ntholi Nkhatho/Desktop/test.xlsx")
            if Path(file_path).is_file():
                workbook = openpyxl.load_workbook(file_path)
        except Exception as e:
            error_console.print("Error:", e)
    return workbook

def get_worksheet(workbook: Workbook) -> Worksheet:
    sheet_names = workbook.sheetnames
    if len(sheet_names) > 1:
        sheet_name, _ = pick(workbook.sheetnames, "Select a sheet", indicator='->') #type: ignore    
    else:
        sheet_name = workbook.sheetnames[0]
    return workbook[sheet_name]


def get_grades(sheet: Worksheet) -> list[dict[str, str]]:

    retry = True
    result = []

    while retry:
        student_col = Prompt.ask("Enter Column Student No", default='C')
        marks_col = Prompt.ask("Enter Column Marks", default='D')

        student_numbers = list([it.value for it in sheet[student_col]])
        marks = list([it.value for it in sheet[marks_col]])

        grades_book = list(zip(student_numbers, marks))


        for grade in grades_book:
            if is_number(grade[0]) and is_number(grade[1]):
                result.append({str(int(float(grade[0]))): int(float(grade[1]))})

        sample_std, sample_marks = next(iter(result[0].items()))
        print_in_table({
            "Student No": [str(sample_std)],
            "Marks": [str(sample_marks)],
            },
            "First Record"
        )
        retry = not Confirm.ask(
            f"Proceed?", default=True)

    return result
