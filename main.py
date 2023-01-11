import os
from pprint import pprint
from rich.prompt import Prompt
from pick import pick
from browser import Browser
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt
from pathlib import Path
from console_utils import print_in_table
from credentials import read_credentials, write_credentials
from excel_reader import get_grades, get_worksheet, open_file
from model import CourseWork

console = Console()
error_console = Console(stderr=True, style="bold red")
browser = Browser()


def login():
    credentials = read_credentials()
    if credentials:
        username, password = credentials
    else:
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)
        write_credentials(username, password)

    browser.login(username, password)


def get_marks_for(grades: list[dict[str, str]], student_number: list[tuple[str]]):
    marks = ''
    for grade in grades:
        key, value = next(iter(grade.items()))
        if key == student_number[0]:
            marks = str(value)
    return marks

def repetitive_tasks(sheet, student_ids, course_works, module):
    payload = []
    course_work = []

    proceed = False
    while not proceed:
        payload = []
        course_work, _ = pick(course_works, "Pick an Assessment",
                                indicator='->', )  # type: ignore
        print("Course Work:", course_work)
        grades = get_grades(sheet, course_work)
        for id in student_ids:
            marks = get_marks_for(grades, id)
            payload.append(
                (id[1], marks)
            )

        proceed = Confirm.ask(
            "I'm ready to rumble, should I proceed?", default=True)
    return [course_work, payload]

def main():

    module_list = browser.get_modules()
    module, _ = pick(module_list, "Pick a Module",  # type: ignore
                     indicator='->')
    console.print(module, style="green")

    student_ids, course_works = browser.get_std_module_ids_and_course_works(
        module)

    workbook = open_file()
    sheet = get_worksheet(workbook)

    while True:
        course_work, payload = repetitive_tasks(sheet, student_ids, course_works, module)
        browser.upload_grades(course_work, payload)  # type: ignore
        add_another = Confirm.ask(f"\nDo you want to add another assessment for {module}?", default=True)
        if add_another:
            clear_screen()
            console.print(module, style="green")
            print()
            continue
        else:
            break


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
    os.system('cls' if os.name=='nt' else 'clear')

if __name__ == '__main__':
    while not browser.logged_in:
        try_function(login)

    while True:
        main()
        input("Press any key to continue...")
        clear_screen()
