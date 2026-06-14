import streamlit as st
import pandas as pd
import random
import os

st.write("Working dir:", os.getcwd())
st.write("Files here:", os.listdir("."))

# ---------- CONFIG ----------
CSV_PATH = "movie_recommender/mymoviedb_ipdated.csv"  # your CSV file

TITLE_COL = "Title"           # title column
GENRE_COL = "Genre"          # genres (comma-separated string)
POSTER_COL = "Poster_Url"     # full poster URL
DESCRIPTION_COL = "Overview"  # description / overview
PLATFORM_COL = "where_to_watch"  # where to watch column
POPULARITY_COL = "Vote_Count"    # integer popularity column


# ---------- DATA LOADING ----------

@st.cache_data
def load_movies():
    df = pd.read_csv(
        CSV_PATH,
        engine="python",
        encoding="utf-8",
        on_bad_lines="skip"
    )

    df = df[
        [TITLE_COL, GENRE_COL, POSTER_COL, DESCRIPTION_COL, PLATFORM_COL, POPULARITY_COL]
    ].dropna(subset=[TITLE_COL, POSTER_COL])

    def parse_genres(g):
        return [x.strip() for x in str(g).split(",") if x.strip()]

    df["genre_list"] = df[GENRE_COL].apply(parse_genres)
    df = df[df["genre_list"].map(len) > 0]

    # Normalize columns internally
    df = df.rename(
        columns={
            TITLE_COL: "title",
            GENRE_COL: "genres_raw",
            POSTER_COL: "poster_url",
            DESCRIPTION_COL: "description",
            PLATFORM_COL: "platform",
            POPULARITY_COL: "vote_count",
        }
    )

    # Ensure vote_count is numeric
    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)

    return df


movies_df = load_movies()


# ---------- SESSION STATE ----------

if "current_index" not in st.session_state:
    st.session_state.current_index = None

if "liked_genres" not in st.session_state:
    st.session_state.liked_genres = {}

if "disliked_genres" not in st.session_state:
    st.session_state.disliked_genres = {}

if "history_liked" not in st.session_state:
    st.session_state.history_liked = []

if "history_skipped" not in st.session_state:
    st.session_state.history_skipped = []

if "seen_indices" not in st.session_state:
    st.session_state.seen_indices = set()


# ---------- RECOMMENDATION LOGIC ----------

def score_movie(genres, vote_count):
    """
    Combine popularity (vote_count) with genre preferences:
    - vote_count gives popular movies a higher base score.
    - liked/disliked genres adjust around that.
    """
    base = float(vote_count) if vote_count is not None else 0.0
    pref = 0
    for g in genres:
        pref += st.session_state.liked_genres.get(g, 0)
        pref -= st.session_state.disliked_genres.get(g, 0)

    # Weight vote_count more, so popular movies show first when prefs are weak
    return base * 0.01 + pref  # 0.01 scales vote_count so numbers stay sane


def choose_next_movie():
    if len(movies_df) == 0:
        return None

    candidate_indices = list(
        set(random.sample(range(len(movies_df)), min(200, len(movies_df))))
    )

    best_idx = None    # index of best candidate
    best_score = -1e9

    for idx in candidate_indices:
        if idx in st.session_state.seen_indices:
            continue
        row = movies_df.iloc[idx]
        genres = row["genre_list"]
        vote_count = row["vote_count"]
        s = score_movie(genres, vote_count)
        s += random.uniform(-0.5, 0.5)  # tiny randomness
        if s > best_score:
            best_score = s
            best_idx = idx

    return best_idx


def update_genre_preferences(genres, liked: bool):
    if liked:
        for g in genres:
            st.session_state.liked_genres[g] = st.session_state.liked_genres.get(g, 0) + 1
    else:
        for g in genres:
            st.session_state.disliked_genres[g] = st.session_state.disliked_genres.get(g, 0) + 1


# ---------- UI ----------

st.title("🎬 Smart Movie Recommender By Yash Shah")
st.write(
    "Click **Generate movie** to start. "
    
)

# Generate button
if st.button("🎲 Generate movie"):
    next_idx = choose_next_movie()
    if next_idx is not None:
        st.session_state.current_index = next_idx
        st.session_state.seen_indices.add(next_idx)
    else:
        st.session_state.current_index = None

idx = st.session_state.current_index

if idx is not None:
    row = movies_df.iloc[idx]
    title = row["title"]
    genres = row["genre_list"]
    description = row["description"]
    poster_url = row["poster_url"]
    platform = row.get("platform", "")
    vote_count = int(row.get("vote_count", 0))

    st.subheader(title)
    st.caption(
        f"Genres: {', '.join(genres)} | Votes: {vote_count}"
    )

    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        if isinstance(poster_url, str) and poster_url.strip():
            st.image(poster_url, caption=title, width=250)
        else:
            st.write("_Poster not available._")

    if isinstance(description, str) and description.strip():
        st.write(description)
    else:
        st.write("_No description available._")

    if isinstance(platform, str) and platform.strip():
        st.write(f"**Where to watch:** {platform}")
    else:
        st.write("**Where to watch:** Not specified")

    col1, col2 = st.columns(2)
    like_clicked = col1.button("👍 Save (Right swipe)")
    skip_clicked = col2.button("👎 Skip (Left swipe)")

    if like_clicked or skip_clicked:
        update_genre_preferences(genres, liked=like_clicked)
        record = (title, ", ".join(genres))
        if like_clicked:
            st.session_state.history_liked.append(record)
        else:
            st.session_state.history_skipped.append(record)

        next_idx = choose_next_movie()
        if next_idx is not None:
            st.session_state.current_index = next_idx
            st.session_state.seen_indices.add(next_idx)
        else:
            st.session_state.current_index = None

else:
    st.info("Click **Generate movie** to start getting recommendations.")

st.markdown("---")
st.subheader("✅ Saved titles (Right swipes)")
if st.session_state.history_liked:
    liked_df = pd.DataFrame(st.session_state.history_liked, columns=["Title", "Genres"])
    st.table(liked_df)
else:
    st.write("No titles saved yet.")

st.subheader("❌ Skipped titles (Left swipes)")
if st.session_state.history_skipped:
    skipped_df = pd.DataFrame(st.session_state.history_skipped, columns=["Title", "Genres"])
    st.table(skipped_df)
else:
    st.write("No titles skipped yet.")
