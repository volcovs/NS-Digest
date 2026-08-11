import feedparser

feed = feedparser.parse(
    "http://export.arxiv.org/rss/q-bio.NC"
)

print("bozo:", feed.bozo)
print("entries:", len(feed.entries))

for entry in feed.entries[:5]:
    print(entry.title)
    print(entry.link)
