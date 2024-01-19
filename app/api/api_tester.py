import requests
def common_check(response: requests.Response, expected_status: int = 200, precise_status_required: bool = False, requires_json: bool = True):
    """This function checks if the response is correct."""
    if (precise_status_required):
        assert (response.status_code == expected_status), \
            f"Unexpected status code: {response.status_code}. It was expected to get {expected_status}."

    else:
        assert ((response.status_code // 100) == (expected_status // 100)), \
            f"Unexpected status code: {response.status_code}. It was expected to get {expected_status // 100}XX."

    if (requires_json):
        content_type = response.headers["Content-Type"]
        content_types = content_type.split(";")
        assert ("application/json" in content_types), \
            f'The API is not responding with JSON, but with "{content_type}".'

s = requests.Session()
datas = [
    {'title_before': 'Bc.', 'first_name': 'Matyáš', 'middle_name': 'Ray', 'last_name': 'Kříž', 'title_after': 'Ph.D', 'picture_url': 'https://picsum.photos/200', 'location': 'Praha', 'claim': 'Bez dobré prezentace je i nejlepší myšlenka k ničemu.', 'bio': 'Vedení týmu vyžaduje empatii a strategii.', 'tags': [{'name': 'Marketing'}], 'price_per_hour': 380, 'contact': {'telephone_numbers': ['+420 122 901 729', '+420 356 496 608'], 'emails': ['d438e229-2a80-4fad-839f-b555022762d5@seznam.cz']}},
    {'title_before': '', 'first_name': 'Matyáš', 'middle_name': 'Ray', 'last_name': 'Kocich', 'title_after': 'Ph.D', 'picture_url': 'https://picsum.photos/200', 'location': 'Ostrava', 'claim': 'Efektivní řízení týmu zvyšuje produktivitu.', 'bio': 'Kreativní myšlení je cestou k úspěchu.', 'tags': [{'name': 'Kreativita'}, {'name': 'Marketing'}, {'name': 'Inovace'}], 'price_per_hour': 220, 'contact': {'telephone_numbers': ['+420 596 148 776', '+420 445 116 813'], 'emails': ['531bab04-d96d-4319-a94f-46cee53fbe22@gmail.com']}},
    {'title_before': 'Mgr.', 'first_name': 'Jakub', 'middle_name': '', 'last_name': 'Gindl', 'title_after': '', 'picture_url': 'https://picsum.photos/200', 'location': 'Ostrava', 'claim': 'Znalost trhu je základ úspěchu.', 'bio': 'Zkušenosti vedou k efektivitě.', 'tags': [{'name': 'Prezentace'}, {'name': 'Marketing'}], 'price_per_hour': 580, 'contact': {'telephone_numbers': ['+420 610 618 355', '+420 735 785 604'], 'emails': ['5bd05b5b-f372-4f26-82b6-970b8487bece@outlook.com']}},
    {'title_before': 'Ing.', 'first_name': 'Jakub', 'middle_name': 'Lynn', 'last_name': 'Novák', 'title_after': '', 'picture_url': 'https://picsum.photos/200', 'location': 'Ostrava', 'claim': 'Bez dobré prezentace je i nejlepší myšlenka k ničemu.', 'bio': 'Vedení týmu vyžaduje empatii a strategii.', 'tags': [{'name': 'Finance'}, {'name': 'Řízení'}], 'price_per_hour': 100, 'contact': {'telephone_numbers': ['+420 295 451 790'], 'emails': ['e1ddde7c-b9cf-4b66-a44e-318fca9a78af@yahoo.com']}},
    {'title_before': 'Ing.', 'first_name': 'Matyáš', 'middle_name': '', 'last_name': 'Novák', 'title_after': None, 'picture_url': 'https://picsum.photos/200', 'location': 'Brno', 'claim': 'Efektivní řízení týmu zvyšuje produktivitu.', 'bio': 'Zkušenosti vedou k efektivitě.', 'tags': [{'name': 'Kreativita'}], 'price_per_hour': 200, 'contact': {'telephone_numbers': ['+420 142 379 411'], 'emails': ['0db7555d-3b30-4baa-bc3e-facbc5f41c9b@yahoo.com']}}
]
for data in datas:
    response = s.post("http://192.168.101.108/api/lecturers", json=data)
    print(response)
