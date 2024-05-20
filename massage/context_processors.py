def nav_menus(request):
    MENU_ITEMS = [
        {
            "Dashboard": [
                {"name": "Landing Page", "url": "landing_page"},
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