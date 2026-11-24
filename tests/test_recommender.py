from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(id=1, title="Test Pop Track", artist="Test Artist", genre="pop", mood="happy",
             energy=0.8, tempo_bpm=120, valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist", genre="lofi", mood="chill",
             energy=0.4, tempo_bpm=80, valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    return Recommender(songs)

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    results = make_small_recommender().recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"

def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---- Stretch attribute tests ----
from src.recommender import load_songs, score_song, recommend_songs


def _base_prefs(**extra):
    prefs = {"favorite_genre": "x", "favorite_mood": "y", "target_energy": 0.5, "likes_acoustic": False}
    prefs.update(extra)
    return prefs


def _song(**over):
    s = {"genre": "a", "mood": "b", "energy": 0.5, "acousticness": 0.1, "artist_monthly_listeners": 1_000_000,
         "release_year": 2000, "duration_min": 3.5, "mood_tags": ["warm", "calm"], "explicit": 0}
    s.update(over)
    return s


NEW_COLS = {"album", "artist_monthly_listeners", "release_year",
            "duration_min", "mood_tags", "explicit"}


def test_csv_has_new_attribute_columns():
    song = load_songs("data/songs.csv")[0]
    for col in NEW_COLS:
        assert col in song
    assert isinstance(song["artist_monthly_listeners"], int)
    assert isinstance(song["release_year"], int)
    assert isinstance(song["duration_min"], float)
    assert isinstance(song["album"], str) and song["album"]
    assert isinstance(song["mood_tags"], list)


def test_same_artist_has_same_listener_count():
    by_artist = {}
    for s in load_songs("data/songs.csv"):
        by_artist.setdefault(s["artist"], set()).add(s["artist_monthly_listeners"])
    assert all(len(v) == 1 for v in by_artist.values())


def test_stretch_prefs_are_optional():
    song = _song()
    stripped = {k: v for k, v in song.items() if k not in NEW_COLS}
    assert score_song(_base_prefs(), song) == score_song(_base_prefs(), stripped)


def test_closer_listener_count_scores_higher():
    prefs = _base_prefs(target_monthly_listeners=20_000_000)
    near = score_song(prefs, _song(artist_monthly_listeners=18_000_000))[0]
    far = score_song(prefs, _song(artist_monthly_listeners=300_000))[0]
    assert near > far


def test_closer_release_year_scores_higher():
    prefs = _base_prefs(preferred_year=2000)
    exact = score_song(prefs, _song(release_year=2000))[0]
    near = score_song(prefs, _song(release_year=2005))[0]
    far = score_song(prefs, _song(release_year=1970))[0]
    assert exact > near > far


def test_tag_overlap_is_capped():
    prefs = _base_prefs(liked_tags=["a", "b", "c", "d", "e"])
    song = _song(mood_tags=["a", "b", "c", "d", "e"])
    score, reasons = score_song(prefs, song)
    assert any("mood tags" in r and "+1.20" in r for r in reasons)


def test_explicit_penalty_only_when_user_avoids_it():
    explicit = _song(explicit=1)
    clean = _song(explicit=0)
    assert score_song(_base_prefs(avoid_explicit=True), explicit)[0] < score_song(_base_prefs(avoid_explicit=True), clean)[0]
    assert score_song(_base_prefs(), explicit)[0] == score_song(_base_prefs(), clean)[0]


def test_closer_song_length_scores_higher():
    prefs = _base_prefs(target_duration_min=3.0)
    near = score_song(prefs, _song(duration_min=3.1))[0]
    far = score_song(prefs, _song(duration_min=6.7))[0]
    assert near > far


def test_release_years_are_plausible():
    for s in load_songs("data/songs.csv"):
        assert 1700 <= s["release_year"] <= 2026


def test_catalog_uses_only_real_artists_and_albums():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 70
    artists = {s["artist"] for s in songs}
    assert {"Kendrick Lamar", "Prince", "Michael Jackson", "Freddie Gibbs",
            "OutKast", "Coldplay", "Beyoncé", "Childish Gambino", "21 Savage",
            "Whirr", "Foo Fighters", "Pearl Jam", "Miles Davis",
            "Soundgarden", "Creed", "Staind", "Deftones", "Bad Bunny", "Justin Timberlake",
            "John Coltrane", "Ahmad Jamal Trio", "De La Soul", "Gorillaz", "Damian Marley", "Slowdive", "Nothing", "Dolly Parton", "Marvin Gaye", "The Temptations", "Local H", "Therapy?"} <= artists
    assert all(s["album"] for s in songs)


def test_duration_is_in_minutes_and_plausible():
    for s in load_songs("data/songs.csv"):
        assert 1.0 < s["duration_min"] < 35.0
