from . import atom

def get_items():
    feed_url = "https://api.weather.gov/alerts/active.atom?area=RI"
    items = atom.load_feed(feed_url, ["cap:msgType"])
    for item in items:
        item['source'] = "National Weather Service"
        item['summary'] = item['raw_summary']
        item['type'] = item['cap:msgType'] if 'cap:msgType' in item else ''
    return items
