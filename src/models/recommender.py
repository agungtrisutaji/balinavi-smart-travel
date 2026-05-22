class DummyRecommender:
    def recommend(self, destinations: list[dict], top_k: int = 5) -> list[dict]:
        return destinations[:top_k]
