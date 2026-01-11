import os
import warnings
import faiss
import numpy as np
from typing import Tuple, Dict
from dotenv import load_dotenv
import openai

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    warnings.warn("OPENAI_API_KEY missing in environment; intent embeddings won't work until provided.")
else:
    openai.api_key = OPENAI_API_KEY

# Intents catalog (suggestive, not rule-based)
INTENTS = {
    "view_own_timesheet": [
        "show my timesheet",
        "my timesheet",
        "hours I worked",
        "log of my work",
        "timesheet for me",
        "how many hours did I log",
    ],
    "view_teammate_timesheet": [
        "show teammate timesheet",
        "timesheet of my colleague",
        "see bob's timesheet",
        "view alice hours",
    ],
    "view_team_timesheet": [
        "show team timesheets",
        "timesheet of my team",
        "team hours",
        "timesheet for all team members",
    ],
    "view_team_members": [
        "who is under me",
        "list my team members",
        "which project are my reports on",
        "people reporting to me",
    ],
    "view_own_details": [
        "my details",
        "show my profile",
        "what is my employee info",
    ],
    "view_own_projects": [
        "projects I am working on",
        "my projects",
        "what am I assigned to",
    ],
    "view_holidays": [
        "holidays",
        "upcoming holidays",
        "next holiday",
        "company holidays",
    ],
    "out_of_scope": [
        "random question",
        "not related",
        "other topic",
    ],
}

# Build FAISS index from intent exemplars
class IntentIndex:
    def __init__(self):
        self.labels = []
        self.emb_matrix = None
        self.index = None
        self._built = False

    def _embed(self, texts):
        # Use a modern embedding model for better intent separation
        resp = openai.Embedding.create(model="text-embedding-3-large", input=texts)
        vecs = [np.array(d["embedding"], dtype=np.float32) for d in resp["data"]]
        return np.vstack(vecs)

    def _build(self):
        exemplars = []
        for label, phrases in INTENTS.items():
            for p in phrases:
                exemplars.append(p)
                self.labels.append(label)

        emb = self._embed(exemplars)
        dim = emb.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # cosine via normalized vectors
        # Normalize for cosine similarity
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        emb_norm = emb / np.clip(norms, 1e-12, None)
        self.emb_matrix = emb_norm
        self.index.add(emb_norm)
        self._built = True

    def build(self):
        if not self._built:
            self._build()

    def detect(self, text: str) -> Tuple[str, float]:
        # Ensure index built lazily (avoids network calls at import time)
        if not self._built:
            self.build()

        q = self._embed([text])
        q = q / np.clip(np.linalg.norm(q, axis=1, keepdims=True), 1e-12, None)
        D, I = self.index.search(q, k=3)
        best_idx = I[0][0]
        best_score = float(D[0][0])
        label = self.labels[best_idx]
        return label, best_score


# Singleton index
INTENT_INDEX = IntentIndex()


def detect_intent(user_text: str) -> Dict[str, float]:
    label, score = INTENT_INDEX.detect(user_text)
    
    return {"label": label, "score": score}