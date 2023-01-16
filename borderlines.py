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

from pick_utils import EXIT_LABEL


def confirm_gradebook(objects: list[BorderlineObject], final_ass: FinalAssessment):
    data = {}
    data["Student No."] = [it.student_no for it in objects]
    data[full_coursework_name(final_ass.name)] = [
        str(it.final_exam_marks) for it in objects]

    print_in_table(data, "Ready to upload to CMS")

    return Confirm.ask("Proceed?", default=True)


def create_payload(objects: list[BorderlineObject]):

    marks = [it.final_exam_marks for it in objects]
    ids = [it.internal_std_no for it in objects]

    return {
        "x_StdModuleID[]": ids,
        f'x_{BorderlineObject.final_assessment.id}[]': marks
    }


def pick_and_act(objects: list[BorderlineObject]):
    cw = full_coursework_name(objects[0].final_assessment.name)
    _, index = pick([
        f"Increase {cw} with {objects[0].tipping_value()} marks for all students",
        f"Decrease {cw} with {objects[0].tipping_value()} marks for all students",
        "Address each student individually",
        EXIT_LABEL],
        f"Found {len(objects)} students with borderline issues",
        indicator="->")
    match index:
        case 0:
            for obj in objects:
                obj.increase()
        case 1:
            for obj in objects:
                obj.decrease()
        case 2:
            for i, it in enumerate(objects):
                cw = full_coursework_name(it.final_assessment.name)
                _, index = pick([
                    f"Increase {cw} with {it.tipping_value()} marks",
                    f"Decrease {cw} with {it.tipping_value()} marks",
                    "Skip"
                ],
                    f"{i+1}/{len(objects)}) {it.names}\n{cw}: {it.final_exam_marks}/{it.final_assessment.max_marks}\nTotal: {it.total}",
                    indicator='->')
                if index == 0:
                    it.increase()
                elif index == 1:
                    it.decrease()


def main(module: Module):
    while True:
        objects = browser.read_borderline_objects(module)
        if not objects:
            print(f"No borderline issues found in {module.name}")
            break
        else:
            pick_and_act(objects)
            confirmed = confirm_gradebook(
                objects, BorderlineObject.final_assessment)
            if confirmed:
                cw = CourseWork(id=BorderlineObject.final_assessment.id,
                                name=BorderlineObject.final_assessment.name)
                browser.upload_grades("1/1)", cw, create_payload(objects))
