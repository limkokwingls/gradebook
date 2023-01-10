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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
