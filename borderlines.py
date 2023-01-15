from rich.prompt import Prompt
from pick import pick
from browser import browser
from pathlib import Path
from console_utils import print_in_table
from credentials import read_credentials, write_credentials
from excel_reader import find_marks_column, find_student_column, open_file, read_numeric_column
from openpyxl.worksheet.worksheet import Worksheet
from model import BorderlineObject, CourseWork, FinalAssessment, Module, full_coursework_name
from rich import print
from rich.table import Table
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt


def confirm_gradebook(objects: list[BorderlineObject], final_ass: FinalAssessment):
    data = {}
    data["Student No."] = [it.student_no for it in objects]
    data[full_coursework_name(final_ass.name)] = [
        str(it.total) for it in objects]

    print_in_table(data, "Ready to upload to CMS")

    return Confirm.ask("Proceed?", default=True)


def main(module: Module):
    # while True:

    list = browser.read_borderline_objects(module)
    for it in list:
        cw = full_coursework_name(it.final_assessment.name)
        _, index = pick([
            f"Add {it.tipping_value()} to {cw}",
            f"Deduct {it.tipping_value()} from {cw}",
            "Do Nothing"
        ], f"Address borderline marks for '{it.names}'\n{cw}: {it.final_exam_marks}/{it.final_assessment.max_marks}\nTotal: {it.total}",
            indicator='->')
        if index == 0:
            it.increase()
        elif index == 1:
            it.decrease()
    confirm_gradebook(list, BorderlineObject.final_assessment)
