import os
import time
from json import JSONEncoder

import httpagentparser  # for getting the user agent as json
from flask import Flask, render_template, session, request

from myapp.analytics.analytics_data import AnalyticsData
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine
from myapp.generation.rag import RAGGenerator
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default
# end lines ***for using method to_json in objects ***


# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = os.getenv("SECRET_KEY")
# open browser dev tool to see the cookies
app.session_cookie_name = os.getenv("SESSION_COOKIE_NAME")

# instantiate our search engine
search_engine = SearchEngine()
# instantiate our in memory persistence
analytics_data = AnalyticsData()
# instantiate RAG generator
rag_generator = RAGGenerator()

# load documents corpus into memory.
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
file_path = path + "/" + os.getenv("DATA_FILE_PATH")
corpus = load_corpus(file_path)

print("\nCorpus is loaded... \n First element:\n", list(corpus.values())[0])


# ---------------------------------------------------------
# Log every request automatically (Part 4 analytics)
# ---------------------------------------------------------
@app.before_request
def log_request():
    analytics_data.register_request(
        path=request.path,
        method=request.method,
        user_agent=request.headers.get("User-Agent", ""),
        ip=request.remote_addr,
        session_id=session.get("session_id"),
        ts=time.time()
    )


# Home URL "/"
@app.route('/')
def index():

    if "session_id" not in session:
        session["session_id"] = str(time.time()).replace(".", "")

    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    session['some_var'] = "Some value that is kept in session"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))
    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']

    # ---------------------------------------------------------
    # If user had clicked before, compute dwell time
    # ---------------------------------------------------------
    if "last_click_time" in session and "last_clicked_pid" in session:
        dwell = time.time() - session["last_click_time"]
        analytics_data.register_dwell(
            pid=session["last_clicked_pid"],
            search_id=session.get("last_search_id", -1),
            dwell_seconds=dwell
        )
        session.pop("last_click_time", None)
        session.pop("last_clicked_pid", None)
        session.pop("last_search_id", None)

    # store latest query in session
    session['last_search_query'] = search_query
    session['last_search_time'] = time.time()

    # generate search_id + automatically register query terms
    #search_id = analytics_data.save_query_terms(search_query)
    search_id = analytics_data.save_query_terms(
        terms=search_query,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent", ""),
        browser=request.user_agent.browser,
        session_id=session.get("session_id")
    )


    session["last_search_id"] = search_id

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------
    results = search_engine.search(search_query, search_id, corpus)

    # generate RAG response based on user query and retrieved results
    rag_response = rag_generator.generate_response(search_query, results)
    print("RAG response:", rag_response)

    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template(
        'results.html',
        results_list=results,
        page_title="Results",
        found_counter=found_count,
        rag_response=rag_response
    )


@app.route('/doc_details', methods=['GET'])
def doc_details():
    """
    Show document details page + register click analytics
    """
    print("doc details session: ")
    print(session)

    pid = request.args.get("pid")
    search_id = request.args.get("search_id")

    if pid is None:
        return render_template("doc_details.html", page_title="Document details", doc=None)

    doc_obj = corpus.get(pid)

    """
    # ---------------------------------------------------------
    # Register click analytics
    # ---------------------------------------------------------
    analytics_data.register_click(
        pid=pid,
        search_id=int(search_id) if search_id else -1,
        rank=None
    )
    """

    # ---------------------------------------------------------
    # Register click analytics + query + ranking
    # ---------------------------------------------------------
    analytics_data.register_click(
        pid=pid,
        search_id=int(search_id) if search_id else -1,
        rank=getattr(doc_obj, "ranking", None),
        query=session.get("last_search_query"),
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent", ""),
        session_id=session.get("session_id")
    )


    # store click time to compute dwell later
    session["last_click_time"] = time.time()
    session["last_clicked_pid"] = pid
    session["last_search_id"] = int(search_id) if search_id else -1

    return render_template(
        'doc_details.html',
        page_title="Document details",
        doc=doc_obj
    )


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show clicked docs ordered by number of clicks
    """
    docs = []
    for pid in analytics_data.fact_clicks:
        row: Document = corpus[pid]
        count = analytics_data.fact_clicks[pid]
        doc = StatsDocument(
            pid=row.pid,
            title=row.title,
            description=row.description,
            url=row.url,
            count=count
        )
        docs.append(doc)

    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', clicks_data=docs, page_title="Stats")


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Dashboard summary.
    Your dashboard.html can display stats['top_queries'], stats['avg_dwell'], etc.
    """
    stats = analytics_data.summary_stats()
    return render_template('dashboard.html', page_title="Dashboard", stats=stats)


# Altair plot for views per document (used in dashboard iframe)
@app.route('/plot_number_of_views', methods=['GET'])
def plot_number_of_views():
    return analytics_data.plot_number_of_views()


@app.route('/plot_top_queries', methods=['GET'])
def plot_top_queries():
    return analytics_data.plot_top_queries()

@app.route('/plot_top_terms', methods=['GET'])
def plot_top_terms():
    return analytics_data.plot_top_terms()


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=os.getenv("DEBUG"))
