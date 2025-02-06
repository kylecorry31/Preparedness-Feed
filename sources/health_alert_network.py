from . import html
from datetime import datetime

def get_items():
    items = html.load_feed("https://www.cdc.gov/han/index.html", '.bg-quaternary .card', 'a', 'a', None, 'p', ["%m/%d/%Y %I:%M %p", "%m/%d/%Y, %I:%M %p"])

    for item in items:
        item['source'] = "CDC Health Alert Network"
        item['type'] = "Alert"
        item['link'] = "https://www.cdc.gov" + item['link']
        # Convert from local time to UTC
        # TODO: Get eastern time
        item['pub_date'] = int(datetime.fromtimestamp(float(item['pub_date']), datetime.now().tzinfo).timestamp())
    return items
