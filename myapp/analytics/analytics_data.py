# myapp/analytics/analytics_data.py
import json
import random
import time
from collections import Counter
from typing import Dict, List, Any, Optional, Tuple

import altair as alt
import pandas as pd


class AnalyticsData:
    """
    In-memory analytics storage for Part 4.
    Tables:
      - requests
      - queries
      - clicks
      - dwell_times
      - fact_clicks (quick counter)
    """

    def __init__(self):
        # quick stats counter (pid -> click count)
        self.fact_clicks: Dict[str, int] = {}

        # "tables"
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
        ip: str,
        user_agent: str,
        browser: Optional[str] = None,
        session_id: Optional[str] = None,
        ts: Optional[float] = None
    ):
        terms = query.split()
        self.queries.append({
            "ts": ts or time.time(),
            "search_id": search_id,
            "query": query,
            "n_terms": len(terms),
            "terms": terms,
            "ip": ip,
            "user_agent": user_agent,
            "browser": browser,
            "session_id": session_id
        })

    # keep backwards compatibility with teacher code
    def save_query_terms(
        self,
        terms: str,
        ip: str,
        user_agent: str,
        browser: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        search_id = random.randint(0, 100000)
        self.register_query(
            query=terms,
            search_id=search_id,
            ip=ip,
            user_agent=user_agent,
            browser=browser,
            session_id=session_id
        )
        return search_id

    # ---------- Clicks ----------
    def register_click(
        self,
        pid: str,
        search_id: int,
        rank: Optional[float] = None,
        query: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        ts: Optional[float] = None
    ):
        self.clicks.append({
            "ts": ts or time.time(),
            "pid": pid,
            "search_id": search_id,
            "rank": rank,
            "query": query,
            "ip": ip,
            "user_agent": user_agent,
            "session_id": session_id
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
    def top_queries(self, k: int = 10) -> List[Tuple[str, int]]:
        counts = Counter([q["query"] for q in self.queries])
        return counts.most_common(k)

    def top_terms(self, k: int = 15) -> List[Tuple[str, int]]:
        all_terms = []
        for q in self.queries:
            all_terms.extend(q["terms"])
        counts = Counter(all_terms)
        return counts.most_common(k)

    def avg_dwell_time(self) -> float:
        if not self.dwell_times:
            return 0.0
        return sum(d["dwell_seconds"] for d in self.dwell_times) / len(self.dwell_times)

    def summary_stats(self) -> Dict[str, Any]:
        total_searches = len(self.queries)
        total_clicks = len(self.clicks)
        ctr = round(total_clicks / total_searches, 3) if total_searches > 0 else 0

        unique_queries = len(set(q["query"] for q in self.queries))
        unique_terms = len(set(t for q in self.queries for t in q["terms"]))

        return {
            "total_searches": total_searches,
            "total_clicks": total_clicks,
            "ctr": ctr,
            "unique_queries": unique_queries,
            "unique_terms": unique_terms,
            "avg_dwell": round(self.avg_dwell_time(), 2),
            "top_queries": self.top_queries(10),
            "top_terms": self.top_terms(15)
        }

    # ---------- Plots for dashboard ----------
    def plot_number_of_views(self):
        data = [
            {"Document ID": doc_id, "Number of Views": count}
            for doc_id, count in self.fact_clicks.items()
        ]
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame([{"Document ID": "none", "Number of Views": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Document ID:N", sort="-y"),
            y="Number of Views:Q"
        ).properties(title="Number of Views per Document")

        return chart.to_html()

    def plot_top_queries(self):
        data = [{"Query": q, "Count": c} for q, c in self.top_queries(10)]
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame([{"Query": "none", "Count": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Query:N", sort="-y"),
            y="Count:Q"
        ).properties(title="Top Queries")

        return chart.to_html()

    def plot_top_terms(self):
        data = [{"Term": t, "Count": c} for t, c in self.top_terms(15)]
        df = pd.DataFrame(data)
        if df.empty:
            df = pd.DataFrame([{"Term": "none", "Count": 0}])

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Term:N", sort="-y"),
            y="Count:Q"
        ).properties(title="Top Query Terms")

        return chart.to_html()
    
    def funnel_metrics(self):
        """Compute search → click → dwell funnel."""
        total_searches = len(self.queries)
        total_clicks = len(self.clicks)
        total_dwell = sum(1 for d in self.dwell_times if d["dwell_seconds"] >= 5)

        return {
            "searches": total_searches,
            "clicks": total_clicks,
            "dwell_over_5s": total_dwell,
            "ctr": round(total_clicks / total_searches, 3) if total_searches else 0,
            "engagement_rate": round(total_dwell / total_searches, 3) if total_searches else 0
        }


    def session_paths(self):
        """Return the sequence of actions for each session."""
        paths = {}
        for r in self.requests:
            sid = r.get("session_id", "unknown")
            paths.setdefault(sid, [])
            paths[sid].append(r["path"])
        return paths
    

    def intent_clusters(self):
        """Group queries by shared terms."""
        cluster_map = {}
        for q in self.queries:
            key = " ".join(sorted(set(q["terms"])))  # normalize
            cluster_map.setdefault(key, 0)
            cluster_map[key] += 1
        return sorted(cluster_map.items(), key=lambda x: -x[1])
    

    def plot_searches_per_hour(self):
        df = pd.DataFrame(self.queries)
        if df.empty:
            df = pd.DataFrame([{"hour": 0, "count": 0}])
        else:
            df["hour"] = df["ts"].apply(lambda t: time.strftime("%H", time.localtime(t)))
            df = df.groupby("hour").size().reset_index(name="count")

        chart = alt.Chart(df).mark_line(point=True).encode(
            x="hour:N",
            y="count:Q"
        ).properties(title="Searches per Hour of Day")

        return chart.to_html()
    

    def plot_term_heatmap(self, k=20):
        from itertools import product

        terms = [t for q in self.queries for t in q["terms"]]
        top_terms = [t for t, _ in Counter(terms).most_common(k)]

        # build co-occurrence matrix
        pairs = Counter()
        for q in self.queries:
            unique = list(set(q["terms"]))
            for t1, t2 in product(unique, unique):
                pairs[(t1, t2)] += 1

        data = []
        for t1 in top_terms:
            for t2 in top_terms:
                data.append({"t1": t1, "t2": t2, "count": pairs[(t1, t2)]})

        df = pd.DataFrame(data)

        chart = alt.Chart(df).mark_rect().encode(
            x="t1:N",
            y="t2:N",
            color="count:Q"
        ).properties(title="Term Co-occurrence Heatmap")

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
