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


def main():
    # while not browser.logged_in:
    #     try_function(login)

    # module_list = browser.get_modules()
    # module, _ = pick(module_list, "Pick Module", indicator='->')

    # print(module)

    workbook = open_file()
    sheet = get_worksheet(workbook)
    grades = get_grades(sheet)
    print(grades)



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
