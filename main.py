from pprint import pprint
import json
import requests

for i in range(1, 2):
    payload = {}
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Host": "www.immoweb.be",
        "Sec-Fetch-Dest": "document",
    }
    response = requests.request(
        "GET",
        f"https://www.immoweb.be/en/search-results/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance",
        headers=headers,
        data=payload,
    )
    filtered = response.json().pop("results")
    with open(f"file{i}.json", "w", encoding="utf-8") as file:
        json.dump(filtered, file, ensure_ascii=False, indent=1)
    for i in range(len(filtered)):
        result = filtered[i]
        type = result["property"]["type"]
        postalcode = result["property"]["location"]["postalCode"]
        locality = result["property"]["location"]["locality"]
        id = result["id"]
        url = f"https://www.immoweb.be/en/classified/{type.lower()}/for-sale/{locality.replace(" ", "-")}/{postalcode}/{id}"
        print(url)
