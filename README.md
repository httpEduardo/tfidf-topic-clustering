# Tfidf Topic Clustering

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)

Tfidf Topic Clustering clusters documents into topics using TF-IDF vectors and a lightweight k-means implementation.

## Quick start

```bash
python -m tfidf_topic_clustering.server --port 5173
```

Open http://localhost:5173

## API

- POST `/api/cluster` `{ "k": 3 }`
- POST `/api/seed`

