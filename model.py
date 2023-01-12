from dataclasses import dataclass


@dataclass
class Module:
    id: str
    code: str
    name: str

    def __str__(self):
        return f"{self.name} ({self.code})"

    def __repr__(self):
        return f"{self.name} ({self.code})"


@dataclass
class CourseWork:
    id: str
    name: str

    def get_fullname(self):
        fullname = ''
        number = ''
        if self.name.isalnum():
            number = self.name[-1]
        if self.name.startswith("LabT"):
            fullname = "Lab Test"
        if self.name.startswith("CTst"):
            fullname = "Class Test"
        elif self.name.startswith("Ass"):
            fullname = "Assignment"
        elif self.name.startswith("MTT"):
            fullname = "MidTerm"
        elif self.name.startswith("GAss"):
            fullname = "Group Assignment"
        elif self.name.startswith("Excs"):
            fullname = "Exercises"
        elif self.name.startswith("FExm"):
            fullname = "Final Exam"
        else:
            fullname = self.name

        return fullname + number

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
