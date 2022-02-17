import os
import random

from pymongo import MongoClient
from rich import print
from sentence_transformers import SentenceTransformer, util

from src.common.constants import CIK_COLLECTION, DB_CONNECTION_STRING

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
db = client["edgar"]
collection = db[CIK_COLLECTION]

industries = list(collection.distinct("industry"))
# print(industries)


query = "Electronic Computers"
docs = industries

# Load the model
model = SentenceTransformer("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

# Encode query and documents
query_emb = model.encode(query)
doc_emb = model.encode(docs)

# Compute dot score between query and all document embeddings
scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()


# Combine docs & scores
doc_score_pairs = list(zip(docs, scores))

# Sort by decreasing score
doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

# Output passages & scores
for doc, score in doc_score_pairs:
    print(score, doc)
