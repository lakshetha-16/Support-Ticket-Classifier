"""Small, explainable TF-IDF + Logistic Regression models."""
from collections import Counter
from threading import RLock
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from app.data import build_dataset

LOCK = RLock()
CATEGORIES = ["Account Access", "Billing", "Feature Request", "Security", "Service Outage", "Technical Issue"]
PRIORITIES = ["low", "medium", "high"]

class TicketModels:
    def __init__(self):
        self.category_model = None
        self.priority_model = None
        self.examples = []
        self.metrics = {}

    def train(self, feedback_rows=None):
        rows = build_dataset()
        if feedback_rows:
            rows.extend([
                {"text": r["text"], "category": r["category"], "priority": r["priority"]}
                for r in feedback_rows
                if r.get("text") and r.get("category") in CATEGORIES and r.get("priority") in PRIORITIES
            ])
        texts = [r["text"] for r in rows]
        cats = [r["category"] for r in rows]
        priorities = [r["priority"] for r in rows]

        # Holdout evaluation uses the generated base data for reproducible metrics.
        base = build_dataset()
        train_text, test_text, train_cat, test_cat = train_test_split(
            [r["text"] for r in base], [r["category"] for r in base],
            test_size=0.2, random_state=42, stratify=[r["category"] for r in base]
        )
        eval_model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=800, class_weight="balanced"))
        ])
        eval_model.fit(train_text, train_cat)
        cat_acc = accuracy_score(test_cat, eval_model.predict(test_text))
        self.category_model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=800, class_weight="balanced"))
        ])
        self.priority_model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=800, class_weight="balanced"))
        ])
        self.category_model.fit(texts, cats)
        self.priority_model.fit(texts, priorities)
        self.examples = rows
        # Metrics are illustrative model evaluation on synthetic data only.
        train_p, test_p, train_pr, test_pr = train_test_split(
            [r["text"] for r in base], [r["priority"] for r in base],
            test_size=0.2, random_state=42, stratify=[r["priority"] for r in base]
        )
        p_eval = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=800, class_weight="balanced"))
        ])
        p_eval.fit(train_p, train_pr)
        pred_p = p_eval.predict(test_p)
        self.metrics = {
            "category_accuracy": round(float(cat_acc), 3),
            "priority_accuracy": round(float(accuracy_score(test_pr, pred_p)), 3),
            "priority_macro_f1": round(float(f1_score(test_pr, pred_p, average="macro")), 3),
            "training_examples": len(rows),
            "data_note": "Evaluation uses synthetic examples; real-world performance may be lower."
        }

    def predict(self, text: str) -> Dict:
        if not self.category_model or not self.priority_model:
            self.train()
        with LOCK:
            cat_probs = self.category_model.predict_proba([text])[0]
            cat_classes = self.category_model.classes_
            cat_idx = int(cat_probs.argmax())
            pri_probs = self.priority_model.predict_proba([text])[0]
            pri_classes = self.priority_model.classes_
            pri_idx = int(pri_probs.argmax())
            # Lightweight explanation: strongest matching TF-IDF terms from the ticket.
            vectorizer = self.category_model.named_steps["tfidf"]
            vector = vectorizer.transform([text])
            names = vectorizer.get_feature_names_out()
            pairs = [(names[i], float(vector[0, i])) for i in vector[0].indices]
            keywords = [term for term, weight in sorted(pairs, key=lambda x: x[1], reverse=True)[:5]]
            cat_conf = float(cat_probs[cat_idx])
            pri_conf = float(pri_probs[pri_idx])
            threshold = 0.42
            return {
                "category": str(cat_classes[cat_idx]),
                "category_confidence": round(cat_conf, 3),
                "priority": str(pri_classes[pri_idx]),
                "priority_confidence": round(pri_conf, 3),
                "needs_review": cat_conf < threshold or pri_conf < threshold,
                "review_reason": "Low confidence: please review the prediction." if cat_conf < threshold or pri_conf < threshold else None,
                "keywords": keywords,
                "threshold": threshold
            }

MODELS = TicketModels()
