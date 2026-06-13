import os
import pickle
import streamlit as st
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# ---------------- TMDB API KEY ----------------
API_KEY = os.getenv("TMDB_API_KEY")

# ---------------- POSTER FUNCTION (cached) ----------------

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(3):
        try:
            response = requests.get(
                url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            return None

        except Exception as e:
            print(f"Poster Error for {movie_id}: {e}")
            time.sleep(0.3)

    return None


# ---------------- PARALLEL POSTER FETCHER ----------------

def fetch_posters_parallel(movie_ids):
    """Fetch all posters concurrently instead of sequentially."""
    posters = [None] * len(movie_ids)

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_index = {
            executor.submit(fetch_poster, mid): idx
            for idx, mid in enumerate(movie_ids)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                posters[idx] = future.result()
            except Exception as e:
                print(f"Thread error: {e}")

    return posters


# ---------------- RECOMMEND FUNCTION ----------------

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    movie_ids = []

    for i in movies_list:
        idx = i[0]
        recommended_movies.append(movies.iloc[idx]["title"])
        movie_ids.append(movies.iloc[idx]["movie_id"])

    # Fetch all posters in parallel
    recommended_posters = fetch_posters_parallel(movie_ids)

    return recommended_movies, recommended_posters


# ---------------- LOAD DATA (cached) ----------------

@st.cache_resource(show_spinner="Loading movie data...")
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity


# ---------------- STREAMLIT UI ----------------

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommender System")

movies, similarity = load_data()

selected_movie = st.selectbox(
    "Select a Movie",
    movies["title"].values
)

if st.button("Show Recommendations"):
    with st.spinner("Finding recommendations..."):
        names, posters = recommend(selected_movie)
    # Store in session state to prevent re-fetch on rerender
    st.session_state["names"] = names
    st.session_state["posters"] = posters

# Render results from session state
if "names" in st.session_state:
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.write(st.session_state["names"][i])
            poster = st.session_state["posters"][i]
            st.image(
                poster if poster else "https://placehold.co/300x450?text=Not+Available",
                use_container_width=True
            )