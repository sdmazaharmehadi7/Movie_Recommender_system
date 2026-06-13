# Movie Recommender System

A content-based movie recommender built with Streamlit and TMDB API.

## Setup

1. Clone the repo
   git clone https://github.com/sdmazaharmehadi7/Movie_Recommender_system.git

2. Install dependencies
   pip install -r requirements.txt

3. Add your TMDB API key in a .env file
   TMDB_API_KEY=your_api_key_here

4. Generate the pickle files by running the notebook, then place
   movies.pkl and similarity.pkl in the project root

5. Run the app
   streamlit run app.py