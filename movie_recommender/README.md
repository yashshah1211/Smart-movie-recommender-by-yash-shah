**Smart Movie Recommender By Yash Shah**

**An interactive Streamlit web app that recommends movies using a simple swipe interface.**

**You see one movie at a time (poster, overview, where to watch) and swipe:**



**👍 Save if you like it**



**👎 Skip if you don’t**



**The app learns your taste from your swipes and uses genres + vote count to prioritize what to show next, starting with more popular movies.**



**Features**

**One‑card‑at‑a‑time Tinder-style movie browsing.**



**Movie details:**



**Title and genres**



**Poster image**



**Overview / description**



**Where to watch (Netflix / Prime / Hotstar / etc.).**



**Adaptive recommendations:**



**Uses your liked/disliked genres.**



**Also uses vote\_count to prefer movies with more ratings (more popular).**



**History:**



**Table of all movies you saved.**



**Table of all movies you skipped.**



**Tech Stack**

**Python**



**Streamlit for the web UI**



**pandas for data loading and preprocessing**



**CSV dataset (titles, genres, vote\_count, poster\_url, where\_to\_watch)**



**Dataset**

**This app uses a pre‑processed CSV stored in data/movies\_with\_posters\_and\_platforms.csv (rename if different), which contains:**



**title – movie title**



**genres – comma‑separated genre list**



**poster\_url – direct image URL for the movie poster**



**overview – short description of the movie**



**where\_to\_watch – platform information (e.g. Netflix, Prime Video, Hotstar)**



**vote\_count – number of votes (used as a popularity signal)**



**You can swap in any similar CSV as long as you update the column names at the top of app.py.**



**How Recommendations Work**

**For each candidate movie, the app computes a score:**



**Base score from vote\_count → more popular movies get a higher base score.**



**Preference score from your swipes:**



**Each liked genre increases its weight.**



**Each skipped genre decreases its weight.**



**The final score is a weighted combination:**



**Popular movies from your preferred genres float to the top.**



**At the beginning (before many swipes), popularity matters more.**



**As you swipe more, your genre profile dominates.**



**Running the App Locally**

**Clone this repo and move into the project folder:**



**bash**

**git clone <your-repo-url>**

**cd <your-repo-folder>**

**Create a virtual environment (optional but recommended).**



**Install dependencies:**



**bash**

**pip install -r requirements.txt**

**Run the Streamlit app:**



**bash**

**streamlit run app.py**

**Open the URL shown in the terminal (usually http://localhost:8501).**



**Usage**

**Click “Generate movie” to start.**



**Look at the poster, genres, overview, and “Where to watch”.**



**Click:**



**👍 Save (Right swipe) if you like the suggestion.**



**👎 Skip (Left swipe) if you’re not interested.**



**A new movie card appears instantly after each swipe.**



**Scroll down to see:**



**All saved titles.**



**All skipped titles.**



**Possible Improvements**

**Add a “show only favourite genres” filter.**



**Allow exporting saved movies to a watchlist CSV.**



**Add a search bar to jump to a specific title.**



**Integrate a live API later (TMDB / JustWatch) for real‑time platform data.**

