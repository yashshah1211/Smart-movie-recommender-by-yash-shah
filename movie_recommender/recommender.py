import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ---------- Step 1: Load data ----------

# paths relative to this script
ratings_path = "ml-100k/u.data"
movies_path = "ml-100k/u.item"

# MovieLens 100K u.data has: user_id, item_id, rating, timestamp (tab-separated) [web:26]
ratings_cols = ["user_id", "movie_id", "rating", "timestamp"]
ratings = pd.read_csv(ratings_path, sep="\t", names=ratings_cols, encoding="latin-1")

# u.item has movie_id | title | other fields separated by '|'. [web:26]
movies_cols = [
    "movie_id", "title", "release_date", "video_release_date",
    "imdb_url", "unknown", "Action", "Adventure", "Animation",
    "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
    "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
    "Thriller", "War", "Western"
]
movies = pd.read_csv(movies_path, sep="|", names=movies_cols, encoding="latin-1")

# Merge ratings with movie titles
data = pd.merge(ratings, movies[["movie_id", "title"]], on="movie_id")

print("Sample of merged data:")
print(data.head())

# ---------- Step 2: Create user–item matrix ----------

# Rows: users, Columns: movies, Values: ratings (NaN if not rated)
user_item_matrix = data.pivot_table(
    index="user_id",
    columns="title",
    values="rating"
)

print("\nUser-Item matrix shape:", user_item_matrix.shape)

# ---------- Step 3: Compute user similarity ----------

# Fill NaNs with 0 for cosine similarity
user_item_matrix_filled = user_item_matrix.fillna(0)

# Cosine similarity between users [web:13]
user_similarity = cosine_similarity(user_item_matrix_filled)

# Convert to DataFrame for easier handling
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

print("\nUser similarity matrix shape:", user_similarity_df.shape)

# ---------- Step 4: Recommendation function ----------

def get_movie_recommendations_for_user(target_user_id, n_recommendations=10, min_common_movies=5):
    """
    Recommend movies for a target user based on similar users' ratings.
    """

    if target_user_id not in user_item_matrix.index:
        raise ValueError(f"User {target_user_id} not found in dataset.")

    # 1. Get similarity scores for the target user with every other user
    similarity_scores = user_similarity_df.loc[target_user_id]

    # 2. Sort users by similarity (descending), exclude the user themself
    similar_users = similarity_scores.drop(target_user_id).sort_values(ascending=False)

    # 3. Get the movies the target user has already rated
    target_user_ratings = user_item_matrix.loc[target_user_id]
    rated_movies = target_user_ratings[target_user_ratings.notna()].index

    # 4. Weighted average rating for each movie using similar users
    weighted_scores = {}
    similarity_sums = {}

    for other_user_id, sim_score in similar_users.items():
        if sim_score <= 0:
            continue  # ignore non-positive similarities

        other_user_ratings = user_item_matrix.loc[other_user_id]

        # Consider only movies the other user rated and target user did NOT rate
        for movie, rating in other_user_ratings.dropna().items():
            if movie in rated_movies:
                continue

            if movie not in weighted_scores:
                weighted_scores[movie] = 0.0
                similarity_sums[movie] = 0.0

            weighted_scores[movie] += sim_score * rating
            similarity_sums[movie] += sim_score

    if not weighted_scores:
        print("No recommendations possible (maybe this user rated too few movies).")
        return []

    # 5. Compute predicted rating (weighted average)
    predicted_ratings = []
    for movie, score_sum in weighted_scores.items():
        if similarity_sums[movie] == 0:
            continue
        predicted_rating = score_sum / similarity_sums[movie]
        predicted_ratings.append((movie, predicted_rating))

    # 6. Sort by predicted rating
    predicted_ratings.sort(key=lambda x: x[1], reverse=True)

    # 7. Return top N recommendations
    return predicted_ratings[:n_recommendations]


# ---------- Step 5: Test with a sample user ----------

if __name__ == "__main__":
    # Pick a user id that exists (MovieLens users are from 1 to 943) [web:23]
    sample_user_id = 1

    print(f"\nMovies already rated by user {sample_user_id}:")
    user_rated = user_item_matrix.loc[sample_user_id].dropna().sort_values(ascending=False)
    print(user_rated.head(10))

    print(f"\nTop recommendations for user {sample_user_id}:")
    recs = get_movie_recommendations_for_user(sample_user_id, n_recommendations=10)

    for movie, pred_rating in recs:
        print(f"{movie}  (predicted rating: {pred_rating:.2f})")