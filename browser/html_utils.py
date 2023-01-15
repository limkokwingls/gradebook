from bs4 import Tag


def read_table(table: Tag):
    data = []
    rows = table.select('tr:not(:first-child)')
    for row in rows:
        cols = row.find_all('td')
        cols = [it.get_text(strip=True) for it in cols]
        # remove empty strings
        data.append([it for it in cols if it])
    return data



def find_link_in_table(table: Tag, search_key: str, target_link_text: str):
    data = []
    rows = table.select('tr:not(:first-child)')
    for row in rows:
        cols = row.select('td')
        data.append([it for it in cols if it])
        str_col = ''.join(str(it) for it in cols)
        if search_key in str_col:
            for i in range(len(cols)):
                col = cols[i]
                text = col.get_text(strip=True)
                anchor = col.findChild("a")
                if isinstance(anchor, Tag):
                    if (text == target_link_text):
                        return anchor.attrs["href"]
