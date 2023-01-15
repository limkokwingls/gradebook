from rich.prompt import Prompt
from pick import pick
from browser import browser
from pathlib import Path
from console_utils import print_in_table
from credentials import read_credentials, write_credentials
from excel_reader import find_marks_column, find_student_column, open_file, read_numeric_column
from openpyxl.worksheet.worksheet import Worksheet
from model import CourseWork, Module
from rich import print
from rich.table import Table
from rich.prompt import Confirm
from rich.console import Console
from rich.prompt import Prompt


def main(module: Module):
    while True:
        pass
    print("Borderline")
