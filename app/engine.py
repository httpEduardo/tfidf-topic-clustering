import math
import random
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def build_vectors(docs):
    doc_tokens = [tokenize(doc["body"]) for doc in docs]
    doc_freq = Counter()
    for tokens in doc_tokens:
        doc_freq.update(set(tokens))
    total_docs = len(docs)
    idf = {term: math.log((1 + total_docs) / (1 + freq)) + 1 for term, freq in doc_freq.items()}

    vectors = []
    for tokens in doc_tokens:
        tf = Counter(tokens)
        vec = {term: (tf[term] / len(tokens)) * idf.get(term, 0.0) for term in tf}
        vectors.append(vec)
    return vectors


def cosine(vec_a, vec_b):
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for term, value in vec_a.items():
        dot += value * vec_b.get(term, 0.0)
        norm_a += value * value
    for value in vec_b.values():
        norm_b += value * value
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def kmeans(vectors, k, iterations=8):
    random.seed(42)
    centroids = [vectors[i].copy() for i in random.sample(range(len(vectors)), k)]

    for _ in range(iterations):
        clusters = [[] for _ in range(k)]
        for idx, vec in enumerate(vectors):
            sims = [cosine(vec, centroid) for centroid in centroids]
            best = sims.index(max(sims))
            clusters[best].append(idx)
        new_centroids = []
        for cluster in clusters:
            if not cluster:
                new_centroids.append(random.choice(vectors).copy())
                continue
            aggregate = Counter()
            for idx in cluster:
                aggregate.update(vectors[idx])
            centroid = {term: value / len(cluster) for term, value in aggregate.items()}
            new_centroids.append(centroid)
        centroids = new_centroids

    assignments = {}
    for idx, vec in enumerate(vectors):
        sims = [cosine(vec, centroid) for centroid in centroids]
        assignments[idx] = sims.index(max(sims))
    return assignments, centroids


def top_terms(centroid, limit=5):
    return [term for term, _ in sorted(centroid.items(), key=lambda item: item[1], reverse=True)[:limit]]
