from rich.prompt import Prompt
from pick import pick
from browser import Browser
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt
from pathlib import Path
from excel_reader import get_grades, get_worksheet, open_file

console = Console()
error_console = Console(stderr=True, style="bold red")
browser = Browser()


def login():
    if Path('credentials').is_file():
        with open('credentials', 'r') as f:
            credentials = f.read().splitlines()
        username = credentials[0]
        password = credentials[1]
    else:
        username = Prompt.ask("Username")
        password = Prompt.ask("Password", password=True)

    browser.login(username, password)


def get_marks_for(grades: list[dict[str, str]], student_number: list[tuple[str]]):
    marks = ''
    for grade in grades:
        key, value = next(iter(grade.items()))
        if key == student_number[0]:
            marks = str(value)
    return marks

def main():
    while not browser.logged_in:
        try_function(login)

    module_list = browser.get_modules()
    module, _ = pick(module_list, "Pick Module", indicator='->') #type: ignore

    student_ids = browser.get_std_module_ids(module)

    workbook = open_file()
    sheet = get_worksheet(workbook)
    grades = get_grades(sheet)
    
    payload = []
    for id in student_ids:
        marks =  get_marks_for(grades, id)
        payload.append(
            (id[1], marks)
        )
    
    course_work = int(Prompt.ask("Course Work No", default=1))

    # proceed = Confirm.ask("Ready to rumble, proceed?", default=True)

    browser.upload_grades(course_work, payload)



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


if __name__ == '__main__':
    # with console.screen():
    main()
