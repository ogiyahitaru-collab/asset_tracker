def summarize_articles(articles):
    return [
        {"title": article["title"], "summary": article["content"][:20] + "..."}
        for article in articles
    ]
