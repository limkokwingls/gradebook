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
from model import CourseWork


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
            file_path = Prompt.ask("RAW Mark-sheet")
            file_path = file_path.strip('\"')
            if Path(file_path).is_file():
                workbook = openpyxl.load_workbook(file_path)
        except Exception as e:
            error_console.print("Error:", e)
    return workbook


def get_worksheet(workbook: Workbook) -> Worksheet:
    sheet_names = workbook.sheetnames
    if len(sheet_names) > 1:
        sheet_name, _ = pick(workbook.sheetnames,
                             "Select a sheet", indicator='->')  # type: ignore
        print("Sheet Name:", sheet_name)
    else:
        sheet_name = workbook.sheetnames[0]
    return workbook[sheet_name]


def get_grades(sheet: Worksheet, course_work) -> list[dict[str, str]]:

    result = []
    student_col = None
    marks_col = None

    while True:
        student_col = Prompt.ask("Student No Column", default='C')
        marks_col = Prompt.ask(f"{course_work} Marks Column")
        if (not student_col) or (not marks_col) or student_col.isalpha() or marks_col.isalpha():
            break
        error_console.print("Column should be an alphabet")

    student_numbers = list([it.value for it in sheet[student_col]])
    marks = list([it.value for it in sheet[marks_col]])

    grades_book = list(zip(student_numbers, marks))

    for grade in grades_book:
        if is_number(grade[0]) and is_number(grade[1]):
            result.append(
                {str(int(float(grade[0]))): int(float(grade[1]))})

    keys = [str(list(it.keys())[0]) for it in result]
    values = [str(list(it.values())[0]) for it in result]

    print_in_table({
        "Student No": keys,
        "Marks": values,
    },""
    )

    return result
