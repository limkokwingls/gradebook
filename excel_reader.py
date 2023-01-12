from pathlib import Path
from types import NoneType
from openpyxl import Workbook
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from rich.prompt import Prompt
from rich.console import Console

from console_utils import print_in_table
from model import CourseWork
from utils import is_number


error_console = Console(stderr=True, style="bold red")


def open_file() -> Workbook:
    workbook: Workbook | None = None
    while workbook == None:
        try:
            file_path = Prompt.ask(
                "RAW Mark-sheet", default="C:\\Users\\Temp\\Desktop\\test.xlsx")
            file_path = file_path.strip('\"')
            if Path(file_path).is_file():
                workbook = openpyxl.load_workbook(file_path)
        except Exception as e:
            error_console.print("Error:", e)
    return workbook


def read_numeric_column(sheet: Worksheet, col: str):
    result = []
    raw = list([it.value for it in sheet[col]])
    for it in raw:
        if is_number(it):
            result.append(it)
    return result

# TODO: Remember to delete this function


def old_read_grades(sheet: Worksheet, course_work: CourseWork) -> list[dict[str, str]]:
    result = []
    student_col = find_student_column(sheet)
    marks_col = find_marks_column(sheet, course_work.fullname())

    while True:
        student_col = Prompt.ask("Student No Column", default=student_col)
        marks_col = Prompt.ask(
            f"{course_work} Marks Column", default=marks_col)
        if (not student_col) or (not marks_col) or student_col.isalpha() or marks_col.isalpha():
            break
        error_console.print("Column should be an alphabet")

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
    }, ""
    )

    return result


def find_marks_column(sheet: Worksheet, course_work: str):
    for col in sheet.iter_cols():
        for cell in col:
            if type(cell.value) is str and cell.value.lower() == course_work.lower():
                return cell.column_letter


def find_student_column(sheet: Worksheet):
    for col in sheet.iter_cols():
        for cell in col:
            if type(cell.value) is str and cell.value.lower().startswith('student no'):
                return cell.column_letter
