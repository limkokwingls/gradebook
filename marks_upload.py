import os
from pathlib import Path

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pick import pick
from rich import print
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from browser import browser
from console_utils import print_in_table
from credentials import read_credentials, write_credentials
from excel_reader import (
    find_marks_column,
    find_student_column,
    open_file,
    read_numeric_column,
)
from model import CourseWork, Module
from pick_utils import EXIT_LABEL, multiple_pick
from utils import is_number

console = Console()
error_console = Console(stderr=True, style="bold red")


def get_marks_for(grades: list[dict[str, str]], student_number: list[tuple[str]]):
    marks = ""
    for grade in grades:
        key, value = next(iter(grade.items()))
        if key == student_number[0]:
            marks = str(value)
    return marks


def pick_worksheet(workbook: Workbook) -> Worksheet | None:
    list = workbook.sheetnames
    sheet_name = None
    # if len(list) > 1:
    options = [str(it) for it in list]
    options.append(EXIT_LABEL)
    _, index = pick(
        options,
        f"Pick a Sheet",
        indicator="->",
    )
    if index <= (len(list) - 1):  # type: ignore
        sheet_name = list[index]  # type: ignore
    # else:
    #     sheet_name = workbook.sheetnames[0]
    if sheet_name:
        return workbook[sheet_name]


def pick_course_works(course_works: list) -> list[CourseWork] | None:
    return multiple_pick(course_works)


def get_workbook_std_numbers(sheet: Worksheet):
    col = find_student_column(sheet)
    while True:
        col = Prompt.ask(f"- Student Numbers", default=col)
        if col and col.isalpha():
            break
        error_console.print("Should be an alphabet")

    return read_numeric_column(sheet, col)


def get_workbook_marks(course_works: list[CourseWork], sheet: Worksheet):
    result = {}
    for cw in course_works:
        while True:
            col = Prompt.ask(
                f"- {cw.fullname()} Marks",
                default=find_marks_column(sheet, cw.fullname()),
            )
            if col and col.isalpha():
                break
            error_console.print("Should be an alphabet")
        result[cw.id] = read_numeric_column(sheet, col)

    return result


def create_gradebook(student_numbers: list[str], marks: dict[str, list[str]]):
    """
    gradebook should look something like this:

    {
        'course_work_1': {
            'std_number': 'marks',
            'std_number': 'marks',
        }
        'course_work_2': {...}
    }
    """
    gradebook = {}
    for key in marks.keys():
        map = {}
        std_and_marks = list(zip(student_numbers, marks[key]))
        for grade in std_and_marks:
            if is_number(grade[0]) and is_number(grade[1]):
                map[grade[0]] = grade[1]
        gradebook[key] = map

    return gradebook


def get_course_work_fullname(cw_id: str, course_works: list[CourseWork]):
    for cw in course_works:
        if cw.id == cw_id:
            return cw.fullname()
    return cw_id


def confirm_gradebook(
    gradebook: dict[str, dict[str, str]], course_works: list[CourseWork]
):
    data = {}
    for i, key in enumerate(gradebook.keys()):
        cw = get_course_work_fullname(key, course_works)
        if i == 0:
            data["Student No."] = [str(it) for it in gradebook[key]]
        data[cw] = [str(it) for it in list(gradebook[key].values())]

    print_in_table(data, "Ready to upload to CMS")

    return Confirm.ask("Proceed?", default=True)


def create_payloads(
    course_work: CourseWork,
    gradebook: dict[str, dict[str, str]],
    cms_std_numbers: dict[str, str],
):
    course_work_res = gradebook[course_work.id]
    marks = []
    ids = []
    for std in cms_std_numbers:
        if std in course_work_res:
            ids.append(cms_std_numbers[std])
            marks.append(course_work_res[std])

    return {"x_StdModuleID[]": ids, f"x_{course_work.id}[]": marks}


def main(module: Module):
    while True:
        workbook = open_file()
        if not workbook:
            break
        sheet = pick_worksheet(workbook)
        if not sheet:
            continue
        cms_std_id, course_works = browser.read_cms_gradebook(module)
        if not course_works:
            error_console.print(
                f"{str(module)} does not have any assessments set, please set assessments first in the CMS"
            )
            break
        while True:
            course_works = pick_course_works(course_works)  # type: ignore
            if not course_works:
                continue
            print(
                f"\nReady to read from {sheet.title}, enter column letters for the following:"
            )
            student_numbers = get_workbook_std_numbers(sheet)
            marks = get_workbook_marks(course_works, sheet)
            gradebook = create_gradebook(student_numbers, marks)

            confirmed = confirm_gradebook(gradebook, course_works)
            if not confirmed:
                continue

            size = len(course_works)
            for i, cw in enumerate(course_works):
                payload = create_payloads(cw, gradebook, cms_std_id)
                browser.upload_grades(f"{i+1}/{size})", cw, payload)
            console.print("Done 😃", style="green")
            break
        break
