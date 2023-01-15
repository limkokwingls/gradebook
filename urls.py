from model import Module


_url = "https://cmslesotho.limkokwing.net/campus/lecturer"
login = f"{_url}/login.php"
faculty_programs = f"{_url}/f_programlist.php?showmaster=1&SchoolID=8"


def get_full_url(link: str):
    return _url + link


def modules():
    return f"{_url}/f_modulelecturerviewlist.php"


def student_numbers(module: Module):
    return f"{_url}/f_breakdownmarksviewlist_old.php?showmaster=1&RecPerPage=500&ModuleID={module.id}"


def grade_books(module: Module):
    return f"{_url}/f_breakdownmarksviewlist_new.php?showmaster=1&RecPerPage=500&ModuleID={module.id}"


def course_work_page(course_work: str):
    return f"{_url}/f_breakdownmarksviewlist_new.php?a=edit&w={course_work.lower()}"


def course_work_upload():
    return f"{_url}/f_breakdownmarksviewlist_new.php"
