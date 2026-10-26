import re
from typing import List, Tuple
from app.database import get_db_connection

def tokenize(text: str) -> set:
    text = text.lower()
    # Support both Malayalam and English word tokens
    words = re.findall(r'[\w\u0D00-\u0D7F]+', text)
    return set(words)

def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return (intersection / union) * 100.0

class ScriptDeduplicator:
    @staticmethod
    def check_topic_uniqueness(new_title: str, new_title_mal: str) -> Tuple[bool, float, str]:
        """
        Compares new topic title against all existing topics in the database.
        Returns: (is_unique, highest_similarity_pct, duplicate_title)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, mal_title FROM topics")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return True, 0.0, ""

        new_tokens = tokenize(new_title).union(tokenize(new_title_mal))
        max_sim = 0.0
        most_similar_title = ""

        for r in rows:
            existing_tokens = tokenize(r["title"]).union(tokenize(r["mal_title"]))
            sim = jaccard_similarity(new_tokens, existing_tokens)
            if sim > max_sim:
                max_sim = sim
                most_similar_title = r["title"]

        # Threshold: > 65% similarity is treated as duplicate / repetitive
        is_unique = max_sim < 65.0
        return is_unique, round(max_sim, 2), most_similar_title
