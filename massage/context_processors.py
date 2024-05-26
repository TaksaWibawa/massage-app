def nav_menus(request):
    MENU_ITEMS = [
        {
            "Dashboard": [
                {"name": "Home", "url": "landing_page"},
                {"name": "Chart", "url": "chart"},
                {"name": "Recap", "url": "recap"},
                {"name": "Report", "url": "report"},
                {"name": "New Assignment", "url": "new_assignment"}
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
    return {'MENU_ITEMS': MENU_ITEMS}


def chart_context(request):
    CHAIRS_GROUPED = [[1, 2], [3, 4]]
    TIME_SLOTS = ["18:00", "18:30", "19:00", "19:30",
                  "20:00", "20:30", "21:00", "21:30", "22:00"]
    CHAIRS = ["1", "2", "3", "4"]
    return {'CHAIRS_GROUPED': CHAIRS_GROUPED, 'TIME_SLOTS': TIME_SLOTS, 'CHAIRS': CHAIRS}
