import requests

API_URL = "http://xyandex.pythonanywhere.com/"


def get_check(category, title, description, characteristics):
    req = f'''Категория требования: {category}. Название требования {title}. Описание требования: {description}'''
    print(req)
    url = "http://xyandex.pythonanywhere.com/analyze_requirement"

    headers = {'Content-Type': 'application/json'}

    body = {
        "requirement": req
        #"requirement": f'''The vehicle is power on, and the driver is sitting in the driver's seat. The driver can activate the wipers in one of the following ways, using the front buttons on the steering wheel or on the SWP Android system: 1. There are 5 wiper states: - Off - wipers and washer are off - Auto - works based on sensor data - 1 - low speed of wipers. The wipers operate until the user turns them off. - 2 - average speed of wipers. The wipers operate until the user turns them off. - 3 - fast speed of wipers. The wipers operate until the user turns them off. 2. Front buttons on the steering wheel control: - **Single press (second gear contact)**: - If the wipers are turned off, press once (second gear contact) to turn on speed 1. - If the wipers are already on at any speed (1-2), the next speed is activated. - If the third speed is active, after pressing the button, the wipers turn off. - If Auto mode was active, it is temporarily disabled. After X seconds, Auto mode is reactivated. - **Quick half press (first gear contact)**: - One sweep of the wipers. - After a single wipe, the wipers return to their previous state. - **Half press and hold the button (first gear contact)**: - While the button is held, washer + wiper works (min 3 swipes, timeout 15 sec). - If the wipers are active and a speed level is applied, cleaning occurs using the current speed mode. - If the wipers are inactive, the default speed is set to level 2. - After releasing the button, a single swipe will clear the glass. - **Press repeatedly (3 or more times - second gear contact)**: - Causes Rush mode (speed 3). - Exit the mode with a single press (second gear contact). - If Auto mode was active, it is temporarily disabled and reactivates after X seconds. - **Long press (second gear contact)**: - Opens the wiper menu on the SWP Android system. 3. SWP Android control: - Wiper operating modes (1-3 speed). - Turn off the wipers. - Activate front washer (water flow from front washer nozzles). - Toggle Auto mode (on/off). - Activate service mode (wipers move vertically upward to replace rubber bands/brushes). - Rear washer control. **Postconditions:** - The driver has set their preferred mode for the wipers, including speed and Auto mode. - The driver profile stores information about Auto mode: - If Auto mode is turned on, the next time the car is powered on, Auto mode will be active. - If Auto mode is turned off, the next time the car is powered on, wipers and washer settings will be inactive.'''
    }

    response = requests.post(url, json=body)
    print(response.text)

    if response.status_code == 200:
        result = response.json()
        formatted_results = []

        for inner_array in result:
            for result in inner_array:
                compliance = result.get("compliance", "").lower() == "соблюдается"
                summary = result.get("reglament_summary", "")
                recommendations = result.get("recommendations", [])
                comment = " ".join(recommendations)  # Соединяем все рекомендации в одну строку
                categories = ", ".join(result.get("certifiable_objects", []))  # Соединяем категории через запятую

                formatted_result = {
                    'summary': summary,
                    'is_done': compliance,
                    'comment': comment,
                    'categories': categories
                }

                formatted_results.append(formatted_result)
        return formatted_results
    else:
        raise Exception(f"Ошибка при обработке запроса: {response.status_code} - {response.text}")


import os


def process_large_query(pdf_files, batch_size=5):
    url = f"{API_URL}/generate_from_file"

    processed_results = []

    for i in range(0, len(pdf_files), batch_size):
        batch_files = pdf_files[i:i + batch_size]
        files = [('files', (os.path.basename(file), open(file, 'rb'))) for file in batch_files]

        response = requests.post(url, files=files)

        if response.status_code == 200:
            result_batch = response.json()

            for inner_list in result_batch:
                for result in inner_list:
                    compliance = result.get("compliance", "").lower() == "соблюдается"
                    summary = result.get("reglament_summary", "")
                    recommendations = result.get("recommendations", [])
                    comment = " ".join(recommendations)  # Соединяем рекомендации в одну строку
                    categories = ", ".join(result.get("certifiable_objects", []))  # Соединяем категории через запятую

                    formatted_result = {
                        'summary': summary,
                        'is_done': compliance,
                        'comment': comment,
                        'categories': categories
                    }

                    processed_results.append(formatted_result)
        else:
            raise Exception(f"Ошибка при обработке батча: {response.status_code} - {response.text}")

    return processed_results