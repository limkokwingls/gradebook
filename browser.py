from pprint import pprint
from bs4 import BeautifulSoup
import requests
from model import CourseWork, Module
import urls
from rich.console import Console
from bs4 import Tag
from html_utils import find_link_in_table, read_table
import subprocess


console = Console()
error_console = Console(stderr=True, style="red")

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
            res = self.session.post(urls.login, payload)
            page = BeautifulSoup(res.text, PARSER)
            tags = page.select(".phpmaker")

            if len(tags) > 2:
                display_name = tags[-2]
                display_name = display_name.get_text(strip=True)
                if "Welcome" in display_name:
                    self.logged_in = True
                    return display_name

    def upload_grades(self, course_work: CourseWork, grade_payload: list):
        with console.status("Uploading marks..."):
            res = self.session.get(urls.course_work_page(course_work.id))
            page = BeautifulSoup(res.text, PARSER)
            form = page.select_one("#ff_breakdownmarksviewlist")
            if not form:
                raise Exception("form cannot be null")
            hidden_inputs = form.find_all('input', {'type': 'hidden'})

            payload = {input['name']: input['value']
                       for input in hidden_inputs}
            student_ids = []
            marks = []
            for it in grade_payload:
                student_ids.append(it[0])
                marks.append(it[1])
            payload['x_StdModuleID[]'] = student_ids
            payload[f'x_{course_work.id}[]'] = marks
            payload['cw'] = course_work.id.lower()

            # res = self.session.post(urls.course_work_upload(), payload)
            # print(payload)
            # subprocess.run("clip", text=True, input=res.text)
            console.print("Done 😃", style="green")

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
                module = Module(id=id, code=it[0], name=it[1])
                data.append(module)
            return data

    def get_std_module_ids_and_course_works(self, module):
        with console.status(f"Loading Students..."):
            res = self.session.get(urls.student_numbers(module))
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one("#ewlistmain")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)
            course_works = get_course_works(table)
            data = []
            for it in table_data:
                try:
                    link = find_link_in_table(table, it[4], "Chg")
                    if not link:
                        raise Exception("link cannot be null")
                    id = link[link.find("StdModuleID"):]
                    if id:
                        id = id[id.find("=")+1:]
                    data.append(
                        (it[4], id)
                    )
                except:
                    error_console.print(
                        f"\nMarks will not be uploaded for {it[3]} ({it[4]})")
        return [data, course_works]


def get_course_works(table: Tag):
    raw = read_table_header(table)[0]
    items = []
    cw_id = 1
    for i, it in enumerate(raw):
        if i >= 7:
            if "Total" in it:
                break
            if i == 7 or i % 2 != 0:
                cw_id = find_course_work_id(table, it)
                cw = CourseWork(
                    id=cw_id,
                    name=it
                )
                items.append(cw)
    return items


def read_table_header(table: Tag):
    data = []
    row = table.select('.ewTableHeader')[0]
    cols = row.find_all('td')
    cols = [it.get_text(strip=True) for it in cols]
    # remove empty strings
    data.append([it for it in cols if it])
    return data


def find_course_work_id(table: Tag, course_work: str) -> str:
    id = ""
    data = []
    rows = table.select('tr')
    # subprocess.run("clip", text=True, input=str(rows))
    for row in rows:
        cols = row.select('td')
        data.append([it for it in cols if it])
        str_col = ''.join(str(it) for it in cols)
        if course_work in str_col:
            for i in range(len(cols)):
                col = cols[i]
                text = col.get_text(strip=True)
                anchor = col.findChild("a")
                if isinstance(anchor, Tag):
                    if (text == course_work):
                        link = anchor.attrs["href"]
                        id = link[link.find("order"):]
                        id = id[id.find("=")+1:]
    return id
