import requests



API_URL = "http://xyandex.pythonanywhere.com/"


def get_check(category, title, description, characteristics):
    url = f"{API_URL}/analyze_requirement"
    headers = {'Content-Type': 'application/json'}

    body = {
        "requirement": f'Категория требования: {category}. Название требования {title}. Описание требования: {description}'
    }

    response = requests.post(url, json=body, headers=headers)
    print(response.text)

    if response.status_code == 200:
        result = response.json()

        compliance = result.get("compliance", "").lower() == "соблюдается"
        summary = result.get("reglament_summary", "")
        recommendations = result.get("recommendations", [])
        comment = " ".join(recommendations)

        formatted_result = {
            'summary': summary,
            'is_done': compliance,
            'comment': comment
        }

        return formatted_result
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
            for result in result_batch:
                compliance = result.get("compliance", "").lower() == "соблюдается"
                summary = result.get("reglament_summary", "")
                recommendations = result.get("recommendations", [])
                comment = " ".join(recommendations)
                categories = ", ".join(result.get("certifiable_objects", []))

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
