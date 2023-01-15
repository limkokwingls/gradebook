from dataclasses import dataclass
import math
from turtle import width


@dataclass
class Module:
    id: str
    code: str
    name: str

    def __str__(self):
        return f"{self.name} ({self.code})"


@dataclass
class FinalAssessment:
    id: str
    name: str
    max_marks: float
    weight: float


@dataclass
class BorderlineObject:
    percent_covered = 0.0
    internal_std_no: str
    student_no: str
    names: str
    final_exam_marks: float
    total: float
    final_assessment = FinalAssessment(
        id='',
        name='',
        max_marks=0.0,
        weight=0.0,
    )

    def is_borderline(self):
        if self.total >= 44:
            s = str(self.total)
            if "." in s:
                s = s.split(".")[0]
            return s == '48' or s.endswith("9") or s.endswith("4")
        return False

    def increase(self):
        self.final_exam_marks += self.tipping_value()

    def decrease(self):
        self.final_exam_marks -= self.tipping_value()

    def tipping_value(self):
        """
        The value that can change overall weight by one point
        """
        value = self.final_assessment.max_marks / self.final_assessment.weight
        return math.ceil(value)


@dataclass
class CourseWork:
    id: str
    name: str

    def __str__(self):
        return self.fullname()

    def fullname(self):
        return full_coursework_name(self.name)


def full_coursework_name(name: str):
    fullname = ''
    number = ''
    try:
        name = name.split("(")[0].strip()
        if has_numbers(name):
            number = f" {name[-1]}"
    except:
        ...

    if name.startswith("LabT"):
        fullname = "Lab Test"
    elif name.startswith("CTst"):
        fullname = "Class Test"
    elif name.startswith("Ass"):
        fullname = "Assignment"
    elif name.startswith("MTT"):
        fullname = "MidTerm"
    elif name.startswith("GAss"):
        fullname = "Group Assignment"
    elif name.startswith("GPro"):
        fullname = "Group Project"
    elif name.startswith("Excs"):
        fullname = "Exercises"
    elif name.startswith("FExm"):
        fullname = "Final Exam"
    else:
        fullname = name

    return fullname + number


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)
