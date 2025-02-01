from sources import summarizer
from sources import executive_orders, health_alert_network, national_weather_service, usgs, swpc
import sqlite3
from datetime import datetime


# Create a table to store the notifications
conn = sqlite3.connect("notifications.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        title TEXT,
        link TEXT,
        guid TEXT,
        published_date INTEGER,
        summary TEXT,
        type TEXT,
        original_summary TEXT
    )
''')

while True:
    action = input("Enter 'u' to update items, 'r' to read all items, or 'q' to quit: ")
    if action == 'u':
        items = executive_orders.get_items()
        items += health_alert_network.get_items()
        items += national_weather_service.get_items()
        items += usgs.get_items()
        items += swpc.get_items()

        # Process new items
        new_count = 0
        for item in items:
            # Insert data into the database
            existing = cursor.execute(
                "SELECT published_date FROM notifications WHERE guid = ? AND source = ?", (item['guid'], item['source'])).fetchone()
            exists = existing is not None and existing[0] == item['pub_date']
            if not exists:
                new_count += 1
                summary = summarizer.summarize_url(
                    item['link']) if 'summary' not in item else summarizer.summarize_text(item['summary'])
                cursor.execute('DELETE FROM notifications WHERE guid = ? AND source = ?', (item['guid'],item['source']))
                cursor.execute('''
                    INSERT INTO notifications (source, title, link, guid, published_date, summary, type, original_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (item['source'], item['title'], item['link'], item['guid'], item['pub_date'], summary, item['type'], item['summary'] if 'summary' in item else None))
                conn.commit()

        if new_count > 0:
            print(f"Processed {new_count} new items.")
        else:
            print("No new items.")
    elif action == 'r':
        # Read the notifications table
        hours_to_show = 24 * 3
        min_time = int(datetime.now().timestamp()) - (hours_to_show * 3600)
        cursor.execute("SELECT * FROM notifications WHERE published_date > ? ORDER BY published_date DESC", (min_time,))
        rows = cursor.fetchall()

        # Print the notifications
        for row in rows:
            id = row[0]
            source = row[1]
            title = row[2]
            link = row[3]
            guid = row[4]
            pub_date = row[5]
            summary = row[6]
            type = row[7]

            print(f"{source} - {type}".upper())
            print(title.title().replace("'S", "'s").replace("’S", "'s"))
            local_pub_date = datetime.fromtimestamp(pub_date).astimezone()
            print(f"{local_pub_date} at {link}")
            print()
            print(f"{summary}")
            print()
            print("-" * 40)
            print()
    elif action == 'q':
        break

# Close the database connection
conn.close()
