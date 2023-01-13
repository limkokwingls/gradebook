
from pick import pick

EXIT_LABEL = '[[Back/Exit]]'


def multiple_pick(options: list, title="Select at least one item"):
    selected = []
    retry = True

    while retry:
        selected = pick(
            options,
            title,
            indicator='->',
            multiselect=True,
        )
        if selected:
            retry = False
        else:
            _, index = pick(
                ["Try Again", EXIT_LABEL],
                "You need to select at least one option by pressing space-bar",
                indicator='->',
            )
            if index == 1:
                return None
    return [it[0] for it in selected]  # type: ignore
