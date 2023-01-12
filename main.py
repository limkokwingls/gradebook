import os
from pprint import pprint
from openpyxl import Workbook
from rich.prompt import Prompt
from pick import pick
from browser import Browser
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt
from pathlib import Path
from console_utils import print_in_table
from credentials import read_credentials, write_credentials
from excel_reader import find_marks_column, find_student_column, open_file, read_numeric_column
from openpyxl.worksheet.worksheet import Worksheet
from model import CourseWork, Module
from rich import print

from pick_utils import EXIT_LABEL, multiple_pick
from utils import is_number

console = Console()
error_console = Console(stderr=True, style="bold red")
browser = Browser()


def input_username_and_password():
    username = Prompt.ask("Username")
    password = Prompt.ask("Password", password=True)
    display_name = browser.login(username, password)
    if not display_name:
        error_console.print("Invalid Credentials")
    else:
        write_credentials(username, password)
        print()
    return display_name


def login():
    username, password, display_name = None, None, None
    credentials = read_credentials()
    if credentials:
        username, password = credentials
        display_name = browser.login(username, password)
    else:
        print("Enter CMS credentials")
        display_name = input_username_and_password()

    while not display_name:
        display_name = input_username_and_password()

    if not Confirm.ask(f"{display_name} - Continue?", default=True):
        exit()


def get_marks_for(grades: list[dict[str, str]], student_number: list[tuple[str]]):
    marks = ''
    for grade in grades:
        key, value = next(iter(grade.items()))
        if key == student_number[0]:
            marks = str(value)
    return marks


# def repetitive_tasks(sheet, student_ids, course_works, module):
#     payload = []
#     course_work = []

#     proceed = False
#     while not proceed:
#         payload = []
#         course_work, _ = pick(course_works, "Pick an Assessment",
#                               indicator='->', )  # type: ignore
#         print("Course Work:", course_work)
#         grades = get_grades(sheet, course_work)
#         for id in student_ids:
#             marks = get_marks_for(grades, id)
#             payload.append(
#                 (id[1], marks)
#             )

#         proceed = Confirm.ask(
#             "I'm ready to rumble, should I proceed?", default=True)
#     return [course_work, payload]


def pick_module() -> Module | None:
    list = browser.get_modules()
    options = [str(it) for it in list]
    options.append('<- Exit')
    _, index = pick(options, "Pick a Module", indicator='->')
    if index <= (len(list) - 1):  # type: ignore
        return list[index]  # type: ignore
    return None


def pick_worksheet(workbook: Workbook) -> Worksheet | None:
    list = workbook.sheetnames
    sheet_name = None
    if len(list) > 1:
        options = [str(it) for it in list]
        options.append(EXIT_LABEL)
        _, index = pick(
            options, f"Pick a Sheet", indicator='->',
        )
        if index <= (len(list) - 1):  # type: ignore
            sheet_name = list[index]  # type: ignore
    else:
        sheet_name = workbook.sheetnames[0]
    if sheet_name:
        return workbook[sheet_name]


def pick_course_works(course_works: list) -> list[CourseWork] | None:
    return multiple_pick(course_works)


def get_workbook_std_numbers(sheet: Worksheet):
    col = find_student_column(sheet)
    while True:
        col = Prompt.ask(
            f"[{sheet.title}] Enter Student No Column", default=col)
        if col and col.isalpha():
            break
        error_console.print("Should be an alphabet")

    return read_numeric_column(sheet, col)


def get_workbook_marks(list: list[CourseWork], sheet: Worksheet):
    letters = []
    for i, cw in enumerate(list):
        while True:
            col = Prompt.ask(
                f"'{cw.get_fullname()}' Column Letter",
                default=find_marks_column(sheet, cw.get_fullname()),
            )
            if col and col.isalpha():
                break
            error_console.print("Should be an alphabet")
        letters.append(col)

    print(letters)


def main():
    workbook = open_file()
    sheet = pick_worksheet(workbook)
    module = pick_module()
    if module == None:
        exit()
    # console.print(module, style="green")
    print(str(module))
    student_ids, course_works = browser.get_std_module_ids_and_course_works(
        module)

    print(get_workbook_std_numbers(sheet))

    # selected_course_works = pick_course_works(course_works)
    # if selected_course_works:
    #     get_grades(selected_course_works, sheet)

    # while True:
    #     course_work, payload = repetitive_tasks(
    #         sheet, student_ids, course_works, module)
    #     browser.upload_grades(course_work, payload)  # type: ignore
    #     add_another = Confirm.ask(
    #         f"\nDo you want to add another assessment for {module}?", default=True)
    #     if add_another:
    #         clear_screen()
    #         console.print(module, style="green")
    #         print()
    #         continue
    #     else:
    #         break


def try_function(func, *args):
    retry = True
    results = None
    while retry:
        try:
            results = func(*args)
            retry = False
        except Exception as e:
            error_console.print("Error:", e)
            retry = Confirm.ask("Do you want to retry", default=True)
    return results


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    print("The Thing That Enters Marks into the CMS (0.0.1)\n")
    while not browser.logged_in:
        try_function(login)

    while True:
        main()
        input("Press any key to continue...")
        clear_screen()
