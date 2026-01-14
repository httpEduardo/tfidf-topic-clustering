# TopicAtlas

TopicAtlas clusters documents into topics using TF-IDF vectors and a lightweight k-means implementation.

## Quick start

```bash
python -m app.server --port 5173
```

Open http://localhost:5173

## API

- POST `/api/cluster` `{ "k": 3 }`
- POST `/api/seed`

