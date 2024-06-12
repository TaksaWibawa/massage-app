from .utils import get_global_setting

def nav_menus(request):
    if request.user.is_superuser:
        MENU_ITEMS = [
            {
                "Dashboard": [
                    {"name": "Home", "url": "landing_page"},
                    {"name": "Chart", "url": "chart"},
                    {"name": "New Assignment", "url": "new_assignment"},
                    {"name": "Recap", "url": "recap"},
                    {"name": "Recap History", "url": "recap_history"},
                    {"name": "Report", "url": "report"},
                ]
            },
            {
                "Employee": [
                    {"name": "New Employee", "url": "employee_new"},
                    {"name": "Employee List", "url": "employee_list"}
                ]
            },
            {
                "Service": [
                    {"name": "New Service", "url": "service_new"},
                    {"name": "Service List", "url": "service_list"}
                ]
            }
        ]
    elif request.user.groups.filter(name__iexact='supervisor').exists():
        MENU_ITEMS = [
            {
                "Priority": [
                    {"name": "Chart", "url": "chart"},
                    {"name": "New Assignment", "url": "new_assignment"},
                ],
            },
            {
                "Employee": [
                    {"name": "New Employee", "url": "employee_new"},
                    {"name": "Employee List", "url": "employee_list"}
                ]
            },
            {
                "Service": [
                    {"name": "New Service", "url": "service_new"},
                    {"name": "Service List", "url": "service_list"}
                ]
            }
        ]
    elif request.user.groups.filter(name__iexact='accountant').exists():
        MENU_ITEMS = [
            {
                "Priority": [
                    {"name": "Recap", "url": "recap"},
                    {"name": "Recap History", "url": "recap_history"},
                    {"name": "Report", "url": "report"}
                ]
            }
        ]
    elif request.user.groups.filter(name__iexact='employee').exists():
        MENU_ITEMS = [
            {
                "Priority": [
                    {"name": "Recap", "url": "recap"},
                    {"name": "Recap History", "url": "recap_history"},
                ]
            }
        ]
    else:
        MENU_ITEMS = []

    return {'MENU_ITEMS': MENU_ITEMS}


def chart_context(request):
    max_chairs = get_global_setting('max chairs')
    CHAIRS = list(range(1, max_chairs + 1))
    CHAIRS_GROUPED = [CHAIRS[i:i + 2] for i in range(0, len(CHAIRS), 2)]
    TIME_SLOTS = ["18:00", "18:30", "19:00", "19:30",
                  "20:00", "20:30", "21:00", "21:30", "22:00"]
    return {'CHAIRS_GROUPED': CHAIRS_GROUPED, 'TIME_SLOTS': TIME_SLOTS, 'CHAIRS': CHAIRS}

def assignment_context(request):
    select_fields = ['employee', 'service', 'chair']
    return {'SELECT_FIELDS': select_fields}