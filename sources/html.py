import requests
import bs4
from datetime import datetime

def load_feed(feed_url, item_selector, title_selector, link_selector, summary_selector, date_selector, date_formats):
    # Load the RSS feed
    response = requests.get(feed_url)
    feed_content = response.content
    soup = bs4.BeautifulSoup(feed_content, 'html.parser')

    items = []

    for item in soup.select(item_selector):
        title_element = item.select(title_selector)
        if len(title_element) == 0:
            continue
        title = title_element[0].text
        link = item.select(link_selector)[0].get('href')
        if summary_selector is not None:
            summary = item.select(summary_selector)[0].text
        else:
            summary = None
        date_element = item.select(date_selector)
        if len(date_element) == 0:
            continue
        pub_date = date_element[0].text
        has_pub_date = False
        for date_format in date_formats:
            pub_date = date_element[0].text
            for i in range(len(pub_date)):
                try:
                    pub_date = int(datetime.strptime(pub_date, date_format).timestamp())
                    has_pub_date = True
                    break
                except:
                    pub_date = pub_date[1:]
                    pass
            if has_pub_date:
                break
        if not has_pub_date:
            print(f"Could not parse date for {title}")
            continue
        notification = {
            "guid": link,
            "title": title,
            "link": link,
            "pub_date": pub_date,
            "raw_summary": summary
        }
        items.append(notification)
    return items
