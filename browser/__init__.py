import re
import subprocess

import requests
from bs4 import BeautifulSoup, Tag
from rich import print
from rich.console import Console

from browser.html_utils import find_link_in_table, read_table
from model import BorderlineObject, CourseWork, FinalAssessment, Module, Student
from utils import is_number

from . import urls

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
                token.attrs["name"]: token.attrs["value"],
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

    def upload_grades(
        self,
        progress: str,
        course_work: CourseWork,
        grade_payload: dict[str, list[str]],
    ):
        with console.status(
            f"{progress} Uploading marks for '{course_work.fullname()}'..."
        ):
            res = self.session.get(urls.course_work_page(course_work.id))
            page = BeautifulSoup(res.text, PARSER)
            form = page.select_one("#ff_breakdownmarksviewlist")
            if not form:
                raise Exception("form cannot be null")
            hidden_inputs = form.find_all("input", {"type": "hidden"})

            payload = {input["name"]: input["value"] for input in hidden_inputs}

            payload.update(grade_payload)
            payload["cw"] = course_work.id.lower()

            res = self.session.post(urls.course_work_upload(), payload)

            # print(payload)
            # subprocess.run("clip", text=True, input=res.text)

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
                id = link[link.find("ModuleID") :]
                if id:
                    id = id[id.find("=") + 1 :]
                module = Module(id=id, code=it[0], name=it[1])
                data.append(module)
            return data

    def read_cms_gradebook(self, module):
        with console.status(f"Reading CMS Gradebook..."):
            res = self.session.get(urls.student_numbers(module))
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one("#ewlistmain")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)
            course_works = get_course_works(table)
            id_dict = {}
            for it in table_data:
                try:
                    link = find_link_in_table(table, it[4], "Chg")
                    if not link:
                        raise Exception("link cannot be null")
                    id = link[link.find("StdModuleID") :]
                    if id:
                        id = id[id.find("=") + 1 :]
                    id_dict[it[4]] = id
                except:
                    error_console.print(
                        f"\nMarks will not be updated for {it[3]} ({it[4]}) in the CMS"
                    )
        return [id_dict, course_works]

    def read_borderline_objects(self, module: Module) -> list[BorderlineObject]:
        with console.status(f"Reading CMS Gradebook..."):
            res = self.session.get(urls.student_numbers(module))
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one("#ewlistmain")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)

            BorderlineObject.percent_covered = read_percent_covered(table)
            final_assessment = read_final_assessment(table)

            BorderlineObject.final_assessment = final_assessment
            result = []
            for it in table_data:
                try:
                    link = find_link_in_table(table, it[4], "Chg")
                    if not link:
                        raise Exception("link cannot be null")
                    id = link[link.find("StdModuleID") :]
                    if id:
                        id = id[id.find("=") + 1 :]
                    final_exam = it[-6:-5][0]
                    total = it[-4:-3][0]
                    if is_number(final_exam) and is_number(total):
                        obj = BorderlineObject(
                            internal_std_no=id,
                            student_no=it[4:5][0],
                            names=it[3:4][0],
                            final_exam_marks=float(final_exam),
                            total=float(total),
                        )
                        if obj.is_borderline():
                            result.append(obj)
                except:
                    error_console.print(
                        f"\nMarks will not be updated for {it[3]} ({it[4]}) in the CMS"
                    )
        return result

    def get_class_list(self) -> list[Student]:
        with console.status(f"Loading Modules..."):
            res = self.session.get(urls.modules())
            soup = BeautifulSoup(res.text, PARSER)
            table = soup.select_one(".ewReportTable")
            if not table:
                raise Exception("table cannot be null")
            table_data = read_table(table)
            module, class_name = "", ""
            data = []
            for it in table_data:
                if it and it[0] == "Module:":
                    module = it[1]
                elif it and it[0] == "Class:":
                    class_name = it[1]

                if it and it[0].isnumeric():
                    std = Student(
                        id=None,
                        std_no=it[0],
                        names=it[1],
                        class_name="-".join(class_name.split("-")[1:]),
                        module_code=module.split()[:1][0],
                        module_name=" ".join(module.split()[1:]),
                    )
                    data.append(std)
            return data


def read_percent_covered(table: Tag) -> float:
    value = 0.0
    raw = read_table_header(table)[0]
    for i, it in enumerate(raw):
        if i >= 7:
            if "Total" in it:
                try:
                    s = re.findall(r"\(([^)]+)\)", it)
                    s = s[0][0:-1]
                    return float(s)
                except:
                    ...
    return value


def read_final_assessment(table: Tag) -> FinalAssessment:
    raw = read_table_header(table)[0]
    marks = raw[-5:-4][0]
    weight = raw[-4:-3][0]

    link = find_link_in_table(table, marks, marks)
    if not link:
        raise Exception("link cannot be null")
    id = link[link.find("order") :]
    if id:
        id = id[id.find("=") + 1 :]

    marks_name = marks.split(" ")[0]
    marks = marks.split("(")[1].split(")")[0]
    weight = weight[0:-1]

    return FinalAssessment(
        id=id, name=marks_name, max_marks=float(marks), weight=float(weight)
    )


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
                cw = CourseWork(id=cw_id, name=it)
                items.append(cw)
    return items


def read_table_header(table: Tag):
    data = []
    row = table.select(".ewTableHeader")[0]
    cols = row.find_all("td")
    cols = [it.get_text(strip=True) for it in cols]
    # remove empty strings
    data.append([it for it in cols if it])
    return data


def find_course_work_id(table: Tag, course_work: str) -> str:
    id = ""
    data = []
    rows = table.select("tr")
    # subprocess.run("clip", text=True, input=str(rows))
    for row in rows:
        cols = row.select("td")
        data.append([it for it in cols if it])
        str_col = "".join(str(it) for it in cols)
        if course_work in str_col:
            for i in range(len(cols)):
                col = cols[i]
                text = col.get_text(strip=True)
                anchor = col.findChild("a")
                if isinstance(anchor, Tag):
                    if text == course_work:
                        link = anchor.attrs["href"]
                        id = link[link.find("order") :]
                        id = id[id.find("=") + 1 :]
    return id


browser = Browser()
