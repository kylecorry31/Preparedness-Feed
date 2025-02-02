from . import atom

def get_items():
    type_tag = "{urn:oasis:names:tc:emergency:cap:1.2}msgType"
    feed_url = "https://api.weather.gov/alerts/active.atom?area=RI"
    items = atom.load_feed(feed_url, [type_tag])
    for item in items:
        item['source'] = "National Weather Service"
        item['summary'] = item['raw_summary']
        item['type'] = item[type_tag] if type_tag in item else ''
    return items
