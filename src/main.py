"""
Command line runner for the Music Recommender Simulation.

Run from the repo root:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# Normal profiles: clear, consistent tastes.
PROFILES = {
    "Smooth Pop (Michael Jackson fan)": {
        "favorite_genre": "pop", "favorite_mood": "moody",
        "target_energy": 0.65, "likes_acoustic": False,
    },
    "Hip-Hop Confidence": {
        "favorite_genre": "hip-hop", "favorite_mood": "confident",
        "target_energy": 0.62, "likes_acoustic": False,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock", "favorite_mood": "intense",
        "target_energy": 0.88, "likes_acoustic": False,
    },
    "Sad Acoustic Ballads": {
        "favorite_genre": "country", "favorite_mood": "sad",
        "target_energy": 0.30, "likes_acoustic": True,
    },
    "Stadium Singalong (Coldplay fan)": {
        "favorite_genre": "rock", "favorite_mood": "hopeful",
        "target_energy": 0.66, "likes_acoustic": False,
    },
    "R&B Confidence": {
        "favorite_genre": "r&b", "favorite_mood": "confident",
        "target_energy": 0.62, "likes_acoustic": False,
    },
    "Late-Night Jazz": {
        "favorite_genre": "jazz", "favorite_mood": "mellow",
        "target_energy": 0.2, "likes_acoustic": True,
    },
}

# Adversarial profiles: built to expose weaknesses in the scoring logic.
EDGE_CASES = {
    "Conflicting (sad but 0.9 energy)": {
        "favorite_genre": "soul", "favorite_mood": "sad",
        "target_energy": 0.9, "likes_acoustic": False,
    },
    "Unknown genre (k-pop)": {
        "favorite_genre": "k-pop", "favorite_mood": "euphoric",
        "target_energy": 0.8, "likes_acoustic": False,
    },
    "Middle-of-the-road (no genre fit)": {
        "favorite_genre": "classical", "favorite_mood": "angry",
        "target_energy": 0.5, "likes_acoustic": True,
    },
}

# Stretch profiles: these use the extra attributes (artist monthly listeners,
# release year, song length in minutes, mood tags, explicit flag).
STRETCH_PROFILES = {
    "Clean Mainstream Rap (avoids explicit)": {
        "favorite_genre": "hip-hop", "favorite_mood": "confident",
        "target_energy": 0.62, "likes_acoustic": False,
        "target_monthly_listeners": 70_000_000, "liked_tags": ["powerful", "swagger"],
        "avoid_explicit": True,
    },
    "Deep-Cut Hunter (smaller artists)": {
        "favorite_genre": "hip-hop", "favorite_mood": "gritty",
        "target_energy": 0.60, "likes_acoustic": False,
        "target_monthly_listeners": 4_000_000, "liked_tags": ["gritty", "laid-back"],
        "preferred_year": 2015,
    },
    "Retro Soul and Country": {
        "favorite_genre": "soul", "favorite_mood": "sad",
        "target_energy": 0.30, "likes_acoustic": True,
        "preferred_year": 1975, "liked_tags": ["heartfelt", "soulful", "stripped"],
        "target_monthly_listeners": 15_000_000, "target_duration_min": 3.0,
    },
    "Epic Long-Form Rock": {
        "favorite_genre": "rock", "favorite_mood": "emotional",
        "target_energy": 0.60, "likes_acoustic": False,
        "preferred_year": 1985, "liked_tags": ["epic", "emotional"],
        "target_duration_min": 8.5,
    },
}

BASE_KEYS = {"favorite_genre", "favorite_mood", "target_energy", "likes_acoustic"}


def show(name: str, prefs: dict, songs: list, k: int = 5) -> None:
    """Print the top-k recommendations for one profile."""
    print("=" * 64)
    print(f"Profile: {name}")
    print(
        f"  genre={prefs['favorite_genre']}, mood={prefs['favorite_mood']}, "
        f"energy={prefs['target_energy']}, likes_acoustic={prefs['likes_acoustic']}"
    )
    extras = {k: v for k, v in prefs.items() if k not in BASE_KEYS}
    if extras:
        print("  extra: " + ", ".join(f"{k}={v}" for k, v in extras.items()))
    print("-" * 64)
    for rank, (song, score, explanation) in enumerate(recommend_songs(prefs, songs, k), 1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']}/{song['mood']}]")
        if song.get("album"):
            print(f"   Album: {song['album']} ({song['release_year']})")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded songs: {len(songs)}\n")

    for name, prefs in {**PROFILES, **EDGE_CASES, **STRETCH_PROFILES}.items():
        show(name, prefs, songs)


if __name__ == "__main__":
    main()