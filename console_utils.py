from rich.console import Console
from rich.table import Table


def print_in_table(data, title=None):
    table = Table(title=title)

    values = []
    for index, (key, value) in enumerate(data.items()):
        if index == 0:
            table.add_column(key, style="cyan")
        else:
            table.add_column(key)
        values.append(value)

    values = list(zip(*values))
    for value in values:
        table.add_row(*value)

    console = Console()
    console.print(table)


if __name__ == '__main__':
    print_in_table({
        "No": ["1", "2", "3"],
        "Names": ["Thabo", "Lebese", "David"],
    })