"""Count the songs, artists, genres and moods in the catalog.

Run from the repo root:
    python3 catalog_stats.py
    python3 catalog_stats.py --top 5          # only show the 5 biggest in each list
    python3 catalog_stats.py --file data/songs.csv
"""
import argparse
from collections import Counter

from src.recommender import load_songs


def show(title, counter, top):
    print(f"\n{title}: {len(counter)}")
    for name, n in counter.most_common(top):
        print(f"  {n:3}  {name}")


def main():
    p = argparse.ArgumentParser(description="Count songs, artists, genres and moods")
    p.add_argument("--file", default="data/songs.csv")
    p.add_argument("--top", type=int, default=None, help="only list the biggest N in each group")
    args = p.parse_args()

    songs = load_songs(args.file)
    print(f"Songs: {len(songs)}")
    show("Artists", Counter(s["artist"] for s in songs), args.top)
    show("Genres", Counter(s["genre"] for s in songs), args.top)
    show("Moods", Counter(s["mood"] for s in songs), args.top)

    years = [s["release_year"] for s in songs]
    print(f"\nRelease years: {min(years)} to {max(years)}")
    print(f"Explicit songs: {sum(1 for s in songs if s['explicit'])}")


if __name__ == "__main__":
    main()