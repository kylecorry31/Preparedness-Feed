from . import atom

def get_items():
    feed_url = "https://tools.cdc.gov/api/v2/resources/media/413690.rss"
    items = atom.load_feed(feed_url)
    for item in items:
        item['source'] = "CDC Health Alert Network"
        item['type'] = ""
    return items
