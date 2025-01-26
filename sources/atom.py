import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def load_feed(feed_url, additional_items=[]):
    # Load the RSS feed
    response = requests.get(feed_url)
    feed_content = response.content
    root = ET.fromstring(feed_content)

    namespace = root.tag.split("}")[0] + "}"

    items = []

    for item in root.findall(f"{namespace}entry"):
        title = item.find(f"{namespace}title").text
        link = item.find(f"{namespace}link").text
        guid = item.find(f"{namespace}id").text
        pub_date = item.find(f"{namespace}updated").text
        summary = item.find(f"{namespace}summary").text
        pub_date = int(datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
        notification = {
            "title": title,
            "link": link,
            "guid": guid,
            "pub_date": pub_date,
            "raw_summary": summary
        }
        for i in additional_items:
            found = item.find(f"{namespace}{i}")
            if found is not None:
                notification[i] = found.text
        items.append(notification)
    return items
