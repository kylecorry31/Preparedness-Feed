from . import rss

def get_items():
    feed_url = "https://www.whitehouse.gov/presidential-actions/feed/"
    items = rss.load_feed(feed_url)
    for item in items:
        item['source'] = "White House"
        item['type'] = "Executive Order"
    return items
