import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

def load_feed(feed_url):
    # Load the RSS feed
    response = requests.get(feed_url)
    feed_content = response.content
    root = ET.fromstring(feed_content)

    items = []

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        guid = item.find("guid").text
        pub_date = item.find("pubDate").text
        description = item.find("description")
        if description is not None:
            summary = description.text
        else:
            summary = None
        try:
            pub_date = int(datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").timestamp())
        except ValueError:
            # Get the timezone abbreviate from the end of the string (last word)
            tz_abbr = pub_date.split()[-1]
            # Get the timezone offset from pytz
            zone = pytz.timezone(tz_abbr if tz_abbr != 'EDT' else 'EST')
            parsed_utc = datetime.strptime(pub_date.replace(tz_abbr, '').strip(), "%a, %d %b %Y %H:%M:%S")
            localized = zone.localize(parsed_utc)
            pub_date = int(localized.timestamp())
        items.append({
            "title": title,
            "link": link,
            "guid": guid,
            "pub_date": pub_date,
            "raw_summary": summary
        })
    return items
