"""Compare the recommender's scoring modes side by side.

Usage (run from the repo root):
    python3 compare_modes.py                       # every built-in profile, top 5 per mode
    python3 compare_modes.py --profile "Late-Night Jazz"
    python3 compare_modes.py --genre pop --mood sad --energy 0.4 --acoustic
    python3 compare_modes.py --k 8 --no-diversity
"""
import argparse

from src.main import EDGE_CASES, PROFILES, STRETCH_PROFILES
from src.recommender import SCORING_MODES, load_songs, recommend_songs

ALL_PROFILES = {**PROFILES, **EDGE_CASES, **STRETCH_PROFILES}


def table(headers, rows):
    """Plain ASCII table (no extra libraries needed)."""
    widths = [max(len(str(r[i])) for r in [headers] + rows) for i in range(len(headers))]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    fmt = lambda r: "| " + " | ".join(str(c).ljust(w) for c, w in zip(r, widths)) + " |"
    return "\n".join([line, fmt(headers), line, *map(fmt, rows), line])

def label(song, width=34):
    """'Title - Artist', shortened so the table stays readable."""
    text = f"{song['title']} - {song['artist']}"
    return text if len(text) <= width else text[: width - 1] + "…"

def compare(name, prefs, songs, k, diversity):
    results = {m: recommend_songs(prefs, songs, k, diversity=diversity, mode=m) for m in SCORING_MODES}
    base = [s["id"] for s, _, _ in results["balanced"]]

    print("=" * 70)
    print(f"Profile: {name}")
    print(f"  genre={prefs['favorite_genre']}, mood={prefs['favorite_mood']}, "
          f"energy={prefs['target_energy']}, likes_acoustic={prefs['likes_acoustic']}")

    # 1) Top-k list for each mode, side by side (score in brackets).
    rows = []
    for i in range(k):
        row = [i + 1]
        for m in SCORING_MODES:
            song, score, _ = results[m][i]
            row.append(f"{label(song, 24)} [{score:.2f}]")
        rows.append(row)
    print(table(["#"] + list(SCORING_MODES), rows))

    # 2) How different is each mode from the default?
    summary = []
    for m in SCORING_MODES:
        ids = [s["id"] for s, _, _ in results[m]]
        shared = len(set(ids) & set(base))
        same_order = sum(1 for a, b in zip(ids, base) if a == b)
        genres = len({s["genre"] for s, _, _ in results[m]})
        summary.append([m, f"{shared}/{k}", f"{same_order}/{k}", genres, results[m][0][0]["title"][:28]])
    print(table(["mode", "same songs as balanced", "same rank as balanced", "genres in list", "#1 pick"], summary))

    # 3) Songs that only appear under some modes.
    seen = {}
    for m in SCORING_MODES:
        for s, _, _ in results[m]:
            seen.setdefault(s["id"], (s, set()))[1].add(m)
    unique = [(s, ms) for s, ms in seen.values() if len(ms) < len(SCORING_MODES)]
    if unique:
        print("Only in some modes:")
        for s, ms in sorted(unique, key=lambda x: x[0]["title"]):
            print(f"  {s['title']} by {s['artist']} ({s['genre']}/{s['mood']}): {', '.join(sorted(ms))}")
    print("Note: scores are not comparable across modes (each mode has a different maximum).\n")


def choose_profiles():
    """Show a numbered menu of profiles and return the ones the user picks."""
    names = list(ALL_PROFILES)
    print("\nPick a profile:")
    for i, n in enumerate(names, 1):
        print(f"  {i:2}. {n}")
    print("   a. all of them")
    print("   q. quit")
    while True:
        choice = input("\nType a number (or several, like 2,5,7), a, or q: ").strip().lower()
        if choice in ("q", "quit", ""):
            raise SystemExit
        if choice in ("a", "all"):
            return ALL_PROFILES
        try:
            picks = [names[int(x) - 1] for x in choice.replace(" ", "").split(",")]
            if all(int(x) >= 1 for x in choice.replace(" ", "").split(",")):
                return {n: ALL_PROFILES[n] for n in picks}
        except (ValueError, IndexError):
            pass
        print("That is not on the list. Try again.")


def main():
    p = argparse.ArgumentParser(description="Compare scoring modes side by side")
    p.add_argument("--list", action="store_true", help="print the profile names and exit")
    p.add_argument("--all", action="store_true", help="run every profile without the menu")
    p.add_argument("--profile", help="name (or part of a name) of a built-in profile")
    p.add_argument("--genre")
    p.add_argument("--mood")
    p.add_argument("--energy", type=float, default=0.5)
    p.add_argument("--acoustic", action="store_true", help="user likes acoustic sound")
    p.add_argument("--k", type=int, default=5, help="songs to show per mode (default 5)")
    p.add_argument("--no-diversity", action="store_true", help="turn the diversity penalty off")
    args = p.parse_args()

    if args.list:
        for i, n in enumerate(ALL_PROFILES, 1):
            print(f"{i:2}. {n}")
        return

    songs = load_songs("data/songs.csv")
    if args.genre and args.mood:
        profiles = {"Custom": {"favorite_genre": args.genre, "favorite_mood": args.mood,
                               "target_energy": args.energy, "likes_acoustic": args.acoustic}}
    elif args.profile:
        profiles = {n: v for n, v in ALL_PROFILES.items() if args.profile.lower() in n.lower()}
        if not profiles:
            raise SystemExit(f"No profile matches {args.profile!r}. Run with --list to see them.")
    elif args.all:
        profiles = ALL_PROFILES
    else:
        profiles = choose_profiles()

    for name, prefs in profiles.items():
        compare(name, prefs, songs, args.k, not args.no_diversity)


if __name__ == "__main__":
    main()