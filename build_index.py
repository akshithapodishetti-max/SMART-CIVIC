from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

model=SentenceTransformer("all-MiniLM-L6-v2")

with open("knowledge/civic_rules.txt","r",encoding="utf-8") as f:
    docs=[d.strip() for d in f.read().split("\n\n") if d.strip()]

embeddings=model.encode(docs)

index=faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

faiss.write_index(index,"index.faiss")

with open("documents.pkl","wb") as f:
    pickle.dump(docs,f)

print("RAG Index Created")