import requests
import re
from datetime import datetime

serial_regex = re.compile(r"Serial Number:\s[0-9]+")
title_regex = re.compile(r"(WARNING|ALERT|SUMMARY|WATCH):\s(.*)")

# valid_product_ids = [
#     'A20F',
#     'A30F',
#     'A50F',
#     'A99F'
# ]

def get_items():
    url = "https://services.swpc.noaa.gov/products/alerts.json"
    response = requests.get(url).json()
    items = []
    for alert in response:
        product_id = alert['product_id']
        # if product_id not in valid_product_ids:
        #     continue
        message = alert['message']
        if 'WATCH: Geomagnetic Storm Category' not in message:
            continue
        serial_number = serial_regex.search(message).group(0)
        title = title_regex.search(message).group(2)
        date = int(datetime.strptime(alert['issue_datetime'] + "Z", "%Y-%m-%d %H:%M:%S.%fZ").timestamp())
        # Don't keep alerts older than 1 week
        if date < int((datetime.now().timestamp()) - (7 * 24 * 3600)):
            continue
        items.append({
            "title": title,
            "link": "https://www.swpc.noaa.gov/",
            "guid": serial_number,
            "pub_date": date,
            "summary": message,
            "source": "SWPC",
            "type": product_id
        })
    
    return items