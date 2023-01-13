from dataclasses import dataclass


@dataclass
class Module:
    id: str
    code: str
    name: str

    def __str__(self):
        return f"{self.name} ({self.code})"


@dataclass
class CourseWork:
    id: str
    name: str

    def __str__(self):
        return self.fullname()

    def fullname(self):
        fullname = ''
        number = ''

        name = self.name

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
