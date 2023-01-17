from openpyxl.worksheet.worksheet import Worksheet
from model import Module, Student
from rich import print
from sample_data import student_data
import openpyxl

from pick_utils import EXIT_LABEL


def get_classes(students: list[Student]):
    list = []
    for it in students:
        if it.class_name not in list:
            list.append(it.class_name)
    return list


def add_standard_data(sheet: Worksheet, module: Module):
    sheet["D2"] = "STUDENT MARK-SHEET"
    sheet.merge_cells("D2:J2")

    sheet['A9'] = "Lecture's Name"
    sheet['A10'] = "Thabo Lebese"
    sheet.merge_cells("A9:C9")
    sheet.merge_cells("A10:C10")


def crate_sheets(module: Module, classes: list[str]):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    for it in classes:
        sheet = workbook.create_sheet(it)
        add_standard_data(sheet, module)
    workbook.save("__module_name__.xlsx")
    print(workbook.path)


def main(module: Module):
    list = get_classes(student_data)
    crate_sheets(module, list)


if __name__ == '__main__':
    module = Module(
        id='101',
        code='PROG101',
        name='Principles of Programming Logic and Design',
    )
    main(module)
