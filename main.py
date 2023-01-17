import os

from pick import pick
from credentials import read_credentials, write_credentials
from rich import print
from rich.table import Table
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt
from browser import browser
from model import Module
from pick_utils import EXIT_LABEL
import marks_upload
import borderlines

console = Console()
error_console = Console(stderr=True, style="bold red")


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


def pick_module() -> Module | None:
    list = browser.get_modules()
    options = [str(it) for it in list]
    options.append(EXIT_LABEL)
    _, index = pick(options, "Pick a Module", indicator='->')
    if index <= (len(list) - 1):  # type: ignore
        return list[index]  # type: ignore
    return None


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


def main():
    # while True:
    module = pick_module()
    if module == None:
        exit()
    print(f"[bold blue]{str(module)}")
    # _, index = pick([
    #     "Upload Marks to CMS",
    #     "Fix Border Lines",
    #     EXIT_LABEL
    # ], "Pick a Module", indicator='->')
    # if index == 0:
    # marks_upload.main(module)
    # elif index == 1:
    # borderlines.main(module)
    # else:
    # break


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    print("The thing that automates mundane CMS (gradebook) tasks (0.1.0_dev)\n")
    while not browser.logged_in:
        try_function(login)

    # while True:
        main()
        # input("\nPress any key to continue...")
        # clear_screen()
