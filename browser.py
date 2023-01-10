from bs4 import BeautifulSoup
import requests
from model import Module
import urls
from rich.console import Console
from html_utils import find_link_in_table, read_table

console = Console()

PARSER = "html5lib"


class Browser:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False

    def login(self, username: str, password: str):
        with console.status("Logging in..."):
            form = self.session.get(urls.login)
            page = BeautifulSoup(form.text, PARSER)
            token = page.select("form table tr:last-child input")[0]
            payload = {
                "submit": "Login",
                "username": username,
                "password": password,
                token.attrs['name']: token.attrs["value"]
            }
            self.session.post(urls.login, payload)
            console.print("Login Successful", style="green")
            self.logged_in = True

    def get_modules(self) -> list[Module]:
        with console.status(f"Loading Modules..."):
            res = self.session.get(urls.modules())
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one("#ewlistmain")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)
            data = []
            for it in table_data:
                link = find_link_in_table(table, it[0], "GradeBook")
                if not link:
                    raise Exception("link cannot be null")
                id = link[link.find("ModuleID"):]
                if id:
                    id = id[id.find("=")+1:]
                module = Module(id=id, name=it[1])
                data.append(module)
            return data


    def get_std_module_ids(self, module):
        with console.status(f"Loading Students..."):
            res = self.session.get(urls.student_numbers(module))
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one("#ewlistmain")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)
            data = []
            for it in table_data:
                link = find_link_in_table(table, it[0], "Chg")
                if not link:
                    raise Exception("link cannot be null")
                id = link[link.find("ModuleID"):]
                if id:
                    id = id[id.find("=")+1:]
                data.append(
                    (it[4], id)
                )
        return data