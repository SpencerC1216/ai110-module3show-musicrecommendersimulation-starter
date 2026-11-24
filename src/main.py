"""
Command line runner for the Music Recommender Simulation.

Run from the repo root:  python -m src.main
"""

import argparse

from src.recommender import DEFAULT_MODE, SCORING_MODES, load_songs, recommend_songs

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
    "Unknown genre (polka)": {
        "favorite_genre": "polka", "favorite_mood": "euphoric",
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


def _ascii_grid(headers: list, rows: list) -> str:
    """Tiny fallback table (used if `tabulate` is not installed). Cells may hold several lines."""
    cells = [[str(c).split("\n") for c in row] for row in rows]
    widths = [max(len(h), *(len(line) for row in cells for line in row[i])) for i, h in enumerate(headers)]
    rule = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt(parts: list) -> list:
        height = max(len(p) for p in parts)
        return [
            "| " + " | ".join((p[n] if n < len(p) else "").ljust(w) for p, w in zip(parts, widths)) + " |"
            for n in range(height)
        ]

    out = [rule, *fmt([[h] for h in headers]), rule]
    for row in cells:
        out += fmt(row) + [rule]
    return "\n".join(out)


def format_table(results: list) -> str:
    """Build a table of recommendations: rank, song, genre/mood, score and the reasons for the score."""
    headers = ["#", "Song", "Genre / Mood", "Score", "Why (reasons)"]
    rows = [
        [rank, f"{song['title']}\n{song['artist']}", f"{song['genre']} / {song['mood']}",
         f"{score:.2f}", explanation.replace("; ", "\n")]
        for rank, (song, score, explanation) in enumerate(results, 1)
    ]
    try:
        from tabulate import tabulate
        return tabulate(rows, headers=headers, tablefmt="grid", disable_numparse=True)
    except ImportError:
        return _ascii_grid(headers, rows)


def show(name: str, prefs: dict, songs: list, k: int = 5, mode: str = DEFAULT_MODE) -> None:
    """Print the top-k recommendations for one profile as a table (with the reasons for each score)."""
    print(f"Profile: {name}   [mode: {mode}]")
    print(
        f"  genre={prefs['favorite_genre']}, mood={prefs['favorite_mood']}, "
        f"energy={prefs['target_energy']}, likes_acoustic={prefs['likes_acoustic']}"
    )
    extras = {k: v for k, v in prefs.items() if k not in BASE_KEYS}
    if extras:
        print("  extra: " + ", ".join(f"{k}={v}" for k, v in extras.items()))
    print(format_table(recommend_songs(prefs, songs, k, mode=mode)))
    print()


def compare_modes(name: str, prefs: dict, songs: list, k: int = 3) -> None:
    """Show the top k for one profile under every scoring mode, side by side."""
    print(f"Profile: {name}  (top {k} per mode)")
    headers = ["#"] + list(SCORING_MODES)
    cols = {m: recommend_songs(prefs, songs, k, mode=m) for m in SCORING_MODES}
    rows = [[i + 1] + [f"{cols[m][i][0]['title']} ({cols[m][i][1]:.2f})" for m in SCORING_MODES] for i in range(k)]
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers=headers, tablefmt="grid", disable_numparse=True))
    except ImportError:
        print(_ascii_grid(headers, rows))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music recommender simulation")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=list(SCORING_MODES),
                        help="scoring strategy (default: %(default)s)")
    parser.add_argument("--compare", action="store_true", help="show the top 3 for every mode side by side")
    parser.add_argument("--list-modes", action="store_true", help="describe the available modes and exit")
    args = parser.parse_args()

    if args.list_modes:
        for mode in SCORING_MODES.values():
            print(f"{mode.name:15} genre={mode.genre} mood={mode.mood} energy={mode.energy} "
                  f"acoustic={mode.acoustic}  - {mode.description}")
        return

    songs = load_songs("data/songs.csv")
    print(f"\nLoaded songs: {len(songs)}\n")

    for name, prefs in {**PROFILES, **EDGE_CASES, **STRETCH_PROFILES}.items():
        if args.compare:
            compare_modes(name, prefs, songs)
        else:
            show(name, prefs, songs, mode=args.mode)


if __name__ == "__main__":
    main()
