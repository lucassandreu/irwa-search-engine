import json
import random
import time
from collections import Counter
from typing import Dict, List, Any, Optional

import altair as alt
import pandas as pd


class AnalyticsData:
    """
    In-memory analytics storage.
    Keeps small "tables" as lists/dicts.
    """

    def __init__(self):
        # Existing table (doc_id -> click count)
        self.fact_clicks: Dict[str, int] = {}

        # ---- New "tables" for Part 4 ----
        self.requests: List[Dict[str, Any]] = []
        self.queries: List[Dict[str, Any]] = []
        self.clicks: List[Dict[str, Any]] = []
        self.dwell_times: List[Dict[str, Any]] = []

    # ---------- Requests ----------
    def register_request(
        self,
        path: str,
        method: str,
        user_agent: str,
        ip: str,
        session_id: Optional[str] = None,
        ts: Optional[float] = None
    ):
        self.requests.append({
            "ts": ts or time.time(),
            "path": path,
            "method": method,
            "user_agent": user_agent,
            "ip": ip,
            "session_id": session_id
        })

    # ---------- Queries ----------
    def register_query(
        self,
        query: str,
        search_id: int,
        ts: Optional[float] = None
    ):
        terms = query.split()
        self.queries.append({
            "ts": ts or time.time(),
            "search_id": search_id,
            "query": query,
            "n_terms": len(terms),
            "terms": terms
        })

    # keep backwards compatibility with teacher code
    def save_query_terms(self, terms: str) -> int:
        search_id = random.randint(0, 100000)
        self.register_query(terms, search_id)
        return search_id

    # ---------- Clicks ----------
    def register_click(
        self,
        pid: str,
        search_id: int,
        rank: Optional[int] = None,
        ts: Optional[float] = None
    ):
        self.clicks.append({
            "ts": ts or time.time(),
            "pid": pid,
            "search_id": search_id,
            "rank": rank
        })

        # update quick stats counter
        self.fact_clicks[pid] = self.fact_clicks.get(pid, 0) + 1

    # ---------- Dwell time ----------
    def register_dwell(
        self,
        pid: str,
        search_id: int,
        dwell_seconds: float,
        ts: Optional[float] = None
    ):
        self.dwell_times.append({
            "ts": ts or time.time(),
            "pid": pid,
            "search_id": search_id,
            "dwell_seconds": dwell_seconds
        })

    # ---------- Dashboard helpers ----------
    def top_queries(self, k: int = 10):
        counts = Counter([q["query"] for q in self.queries])
        return counts.most_common(k)

    def avg_dwell_time(self) -> float:
        if not self.dwell_times:
            return 0.0
        return sum(d["dwell_seconds"] for d in self.dwell_times) / len(self.dwell_times)

    def summary_stats(self):
        return {
            "n_requests": len(self.requests),
            "n_queries": len(self.queries),
            "n_clicks": len(self.clicks),
            "avg_dwell": round(self.avg_dwell_time(), 2),
            "top_queries": self.top_queries(10)
        }

    # ---------- Existing plot ----------
    def plot_number_of_views(self):
        data = [
            {"Document ID": doc_id, "Number of Views": count}
            for doc_id, count in self.fact_clicks.items()
        ]
        df = pd.DataFrame(data)

        if df.empty:
            df = pd.DataFrame([{"Document ID": "none", "Number of Views": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x="Document ID",
            y="Number of Views"
        ).properties(title="Number of Views per Document")

        return chart.to_html()
    
    def plot_top_queries(self, k: int = 10):
        counts = Counter([q["query"] for q in self.queries])
        top = counts.most_common(k)
        df = pd.DataFrame(top, columns=["Query", "Count"])

        if df.empty:
            df = pd.DataFrame([{"Query": "none", "Count": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Query:N", sort="-y"),
            y="Count:Q"
        ).properties(title="Top Queries")

        return chart.to_html()

    def plot_top_terms(self, k: int = 15):
        all_terms = []
        for q in self.queries:
            all_terms.extend(q.get("terms", []))

        counts = Counter(all_terms)
        top = counts.most_common(k)
        df = pd.DataFrame(top, columns=["Term", "Count"])

        if df.empty:
            df = pd.DataFrame([{"Term": "none", "Count": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Term:N", sort="-y"),
            y="Count:Q"
        ).properties(title="Top Query Terms")

        return chart.to_html()



class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.__dict__)
