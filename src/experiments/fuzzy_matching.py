from pymongo import MongoClient
import os
from rich import print as print
# from polyleven import levenshtein

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar", authSource="admin"
)

db = client["edgar"]

company_names = db.ciks.distinct("title", filter={"title": {"$exists": True}})
company_names = [n for n in company_names if n]


def normalize(s: str):
    """
    Returns a normalized version of s
    """
    to_remove = [",", ".", " se", " ltd", " inc", " plc", " corp", " co"]
    s = s.lower()
    for item in to_remove:
        s = s.replace(item, "")
    return s.strip()


def get_top_matches_levenshtein(query: str, company_names: list, limit: int = 10):
    """
    Returns a list of tuples of the form (company_name, similarity_score)
    """
    matches = []
    query = normalize(query)
    for name in company_names:
        normalized_name = normalize(name)
        matches.append((name, levenshtein(query, normalized_name)))
    matches.sort(key=lambda x: x[1])
    return matches[:limit]


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

cv = CountVectorizer(analyzer="char_wb", ngram_range=(1, 4))
matrix = cv.fit_transform(company_names)


def get_top_matches_cv(query, matrix, cv, limit=10):  # best so far
    top_idxs = cosine_similarity(cv.transform([query]), matrix).argsort()[0][-limit:][
        ::-1
    ]
    return [company_names[idx] for idx in top_idxs]


# from pyinstrument import Profiler
print(get_top_matches_cv("micro", matrix, cv))

print("Done.")
