import csv
import math
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple

# --- Algorithm Recipe (change these to run weight experiments) ---
GENRE_WEIGHT = 2.0      # points for an exact genre match
MOOD_WEIGHT = 1.0       # points for an exact mood match
ENERGY_WEIGHT = 1.5     # max points for energy; scales with closeness to target
ACOUSTIC_WEIGHT = 0.5   # max points for matching the acoustic preference

# --- Stretch attributes: only used when the user profile asks for them ---
LISTENER_WEIGHT = 1.0       # max points for artist-popularity closeness (log scale)
LISTENER_SPAN = 3.0         # orders of magnitude (1,000x) apart = zero points
YEAR_WEIGHT = 0.75          # max points for release-year closeness
YEAR_SPAN = 20              # years apart at which year points reach zero
DURATION_WEIGHT = 0.5       # max points for song-length closeness
DURATION_SPAN = 3.0         # minutes apart at which length points reach zero
TAG_WEIGHT = 0.4            # points per overlapping mood tag
TAG_MAX = 1.2               # cap on total tag points
EXPLICIT_PENALTY = 1.0      # points removed for explicit songs when the user avoids them

# --- Diversity penalty (Challenge 3): applied while building the top-k list ---
ARTIST_FATIGUE = 0.6        # per earlier pick by the same artist; grows each time (0.6, 1.2, 1.8 ...)
GENRE_FATIGUE = 0.1         # per earlier pick in the same genre; deliberately tiny


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Stretch attributes (defaults keep older code and tests working)
    album: str = ""
    artist_monthly_listeners: int = 1_000_000
    release_year: int = 2020
    duration_min: float = 3.5
    mood_tags: List[str] = field(default_factory=list)
    explicit: int = 0


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Optional stretch preferences (None means "don't score this")
    target_monthly_listeners: Optional[int] = None
    preferred_year: Optional[int] = None
    target_duration_min: Optional[float] = None
    liked_tags: Optional[List[str]] = None
    avoid_explicit: Optional[bool] = None


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts, converting numeric fields and tag lists."""
    int_fields = {"id", "artist_monthly_listeners", "release_year", "explicit"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness", "duration_min"}
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                if key in row and row[key] != "":
                    row[key] = int(row[key])
            for key in float_fields:
                row[key] = float(row[key])
            if "mood_tags" in row:
                row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            songs.append(row)
    return songs


def _fmt_listeners(n: float) -> str:
    """Format a listener count with commas, like 89,563,979."""
    return f"{int(round(n)):,}"


def _fmt_duration(minutes: float) -> str:
    """Format minutes (for example 3.63) as m:ss (3:38)."""
    total = round(minutes * 60)
    return f"{total // 60}:{total % 60:02d}"


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user prefs and return (score, list of reasons)."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"].lower() == str(user_prefs.get("favorite_genre", "")).lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    if song["mood"].lower() == str(user_prefs.get("favorite_mood", "")).lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    if "target_energy" in user_prefs:
        gap = abs(song["energy"] - user_prefs["target_energy"])
        points = ENERGY_WEIGHT * (1.0 - gap)
        score += points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{points:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1.0 - song["acousticness"]
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    # ---- Stretch attributes (skipped when the song or profile lacks them) ----
    if user_prefs.get("target_monthly_listeners") is not None and "artist_monthly_listeners" in song:
        target = user_prefs["target_monthly_listeners"]
        gap = abs(math.log10(song["artist_monthly_listeners"]) - math.log10(target)) / LISTENER_SPAN
        points = LISTENER_WEIGHT * max(0.0, 1.0 - gap)
        score += points
        reasons.append(
            f"artist listeners {_fmt_listeners(song['artist_monthly_listeners'])} "
            f"vs target {_fmt_listeners(target)} (+{points:.2f})"
        )

    if user_prefs.get("preferred_year") is not None and "release_year" in song:
        diff = abs(song["release_year"] - user_prefs["preferred_year"])
        points = YEAR_WEIGHT * max(0.0, 1.0 - diff / YEAR_SPAN)
        if points > 0:
            score += points
            reasons.append(f"released {song['release_year']} vs preferred {user_prefs['preferred_year']} (+{points:.2f})")

    if user_prefs.get("target_duration_min") is not None and "duration_min" in song:
        diff = abs(song["duration_min"] - user_prefs["target_duration_min"])
        points = DURATION_WEIGHT * max(0.0, 1.0 - diff / DURATION_SPAN)
        if points > 0:
            score += points
            reasons.append(
                f"length {_fmt_duration(song['duration_min'])} vs target "
                f"{_fmt_duration(user_prefs['target_duration_min'])} (+{points:.2f})"
            )

    if user_prefs.get("liked_tags") and song.get("mood_tags"):
        song_tags = song["mood_tags"] if isinstance(song["mood_tags"], list) else song["mood_tags"].split("|")
        overlap = [t for t in user_prefs["liked_tags"] if t in song_tags]
        if overlap:
            points = min(TAG_WEIGHT * len(overlap), TAG_MAX)
            score += points
            reasons.append(f"mood tags: {', '.join(overlap)} (+{points:.2f})")

    if user_prefs.get("avoid_explicit") and song.get("explicit"):
        score -= EXPLICIT_PENALTY
        reasons.append(f"explicit content (-{EXPLICIT_PENALTY:.2f})")

    return round(score, 3), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, diversity: bool = True
) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation).

    With diversity=True the list is built one pick at a time. Before each pick, every remaining
    song loses points for each earlier pick by the same artist (ARTIST_FATIGUE x count, so the
    penalty grows: "voter fatigue") and a little for each earlier pick in the same genre
    (GENRE_FATIGUE x count). The best adjusted score wins the slot. diversity=False gives the
    plain score-sorted list.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    if not diversity:
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        return [(s, sc, "; ".join(r)) for s, sc, r in ranked]

    picked: List[Tuple[Dict, float, str]] = []
    artist_count: Dict[str, int] = {}
    genre_count: Dict[str, int] = {}
    remaining = list(scored)
    while remaining and len(picked) < k:
        best = None
        for song, base, reasons in remaining:
            n_artist = artist_count.get(song["artist"], 0)
            n_genre = genre_count.get(song["genre"], 0)
            adjusted = base - ARTIST_FATIGUE * n_artist - GENRE_FATIGUE * n_genre
            if best is None or adjusted > best[0]:
                best = (adjusted, song, reasons, n_artist, n_genre)
        adjusted, song, reasons, n_artist, n_genre = best
        reasons = list(reasons)
        if n_artist:
            reasons.append(f"artist already picked {n_artist}x (-{ARTIST_FATIGUE * n_artist:.2f})")
        if n_genre:
            reasons.append(f"genre already picked {n_genre}x (-{GENRE_FATIGUE * n_genre:.2f})")
        picked.append((song, round(adjusted, 3), "; ".join(reasons)))
        artist_count[song["artist"]] = n_artist + 1
        genre_count[song["genre"]] = n_genre + 1
        remaining = [r for r in remaining if r[0] is not song]
    return picked


class Recommender:
    """OOP wrapper around the functional recommender (used by tests)."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        return {k: v for k, v in asdict(user).items() if v is not None}

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for a user."""
        song_dicts = [asdict(s) for s in self.songs]
        ranked = recommend_songs(self._prefs(user), song_dicts, k)
        by_id = {s.id: s for s in self.songs}
        return [by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song scored the way it did."""
        _, reasons = score_song(self._prefs(user), asdict(song))
        return "; ".join(reasons)
