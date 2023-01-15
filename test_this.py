
from dataclasses import dataclass


@dataclass
class Person:
    race = "Black"
    name: str


Person.race = "Another One"
one = Person(name="One")
two = Person(name="Two")

print(one.race)
print(two.race)
