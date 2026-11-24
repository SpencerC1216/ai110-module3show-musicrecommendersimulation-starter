"""Streamlit front end for the Music Recommender Simulation (flat, Jon Bois-style look).

Run from the repo root:  streamlit run app.py
"""

import html
import re

import altair as alt
import pandas as pd
import streamlit as st

import src.recommender as rec
from src.recommender import load_songs, recommend_songs

st.set_page_config(page_title="Music Recommender", page_icon="🟨", layout="wide")

INK, PAPER, GRAY = "#111111", "#ffffff", "#e9e7df"
YELLOW, BLUE, RED, GREEN = "#ffd400", "#1f5bff", "#e5322d", "#19a974"
RANK_COLORS = [(YELLOW, INK), (BLUE, "#fff"), (RED, "#fff"), (GREEN, "#fff"), (INK, "#fff")]

st.markdown(
    f"""
<style>
html, body, [class*="css"], .stApp {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }}
.stApp {{ background: {PAPER}; color: {INK}; }}
section[data-testid="stSidebar"] {{ background: {GRAY}; border-right: 4px solid {INK}; }}
.block-container {{ max-width: 1100px; padding-top: 2.5rem; }}
h1.big {{ font-size: 3.4rem; font-weight: 900; letter-spacing: -1.5px; line-height: 1; margin: 0 0 .4rem 0; }}
p.deck {{ font-size: 1.15rem; max-width: 46rem; margin: 0 0 1.5rem 0; }}
h3.lbl {{ font-size: 1.1rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1px;
         border-bottom: 4px solid {INK}; padding-bottom: .3rem; margin: 2rem 0 1rem 0; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
.card {{ border: 4px solid {INK}; padding: 14px 16px 16px 16px; min-height: 330px; }}
.card .rank {{ font-size: 5.5rem; font-weight: 900; line-height: .9; letter-spacing: -3px; }}
.card .title {{ font-size: 2.2rem; font-weight: 900; line-height: 1.1; margin-top: .4rem; }}
.card .meta {{ font-size: 1.3rem; margin-top: .3rem; }}
.card .why1 {{ font-size: 1.15rem; margin-top: .6rem; font-style: italic; }}
.card .score {{ font-size: 1.4rem; font-weight: 900; margin-top: .9rem; border-top: 3px solid currentColor; padding-top: .4rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, 56px); gap: 6px; }}
.sq {{ width: 56px; height: 56px; border: 3px solid {INK}; display: flex; align-items: center;
       justify-content: center; font-weight: 900; font-size: .95rem; background: {GRAY}; color: #8a877c; }}
.why {{ border-left: 8px solid {INK}; padding: .2rem 0 .2rem .9rem; margin: .7rem 0; font-size: 1.3rem; }}
.eyebrow {{ font-weight: 900; letter-spacing: 3px; font-size: .85rem; color: {RED}; text-transform: uppercase; margin-bottom: .4rem; }}
mark.y {{ background: {YELLOW}; color: {INK}; padding: 0 .25em; font-weight: 900; }}
mark.b {{ background: {BLUE}; color: #fff; padding: 0 .25em; font-weight: 900; }}
mark.r {{ background: {RED}; color: #fff; padding: 0 .25em; font-weight: 900; }}
.part {{ font-weight: 900; font-size: .85rem; letter-spacing: 3px; text-transform: uppercase; color: {BLUE}; margin: 2.2rem 0 .1rem 0; }}
.story {{ font-size: 1.2rem; line-height: 1.55; max-width: 44rem; margin: .4rem 0 1rem 0; }}
.huge {{ font-size: 7rem; font-weight: 900; letter-spacing: -5px; line-height: .95; margin: .6rem 0 0 0; }}
.aside {{ border: 3px dashed {INK}; padding: .7rem 1rem; margin: 1.2rem 0; max-width: 44rem; font-size: 1rem; background: #fffbe0; }}
.foot {{ font-size: .85rem; color: #555; max-width: 44rem; border-top: 2px solid {INK}; margin-top: 2.5rem; padding-top: .6rem; }}
button[data-baseweb="tab"] {{ font-weight: 900; text-transform: uppercase; letter-spacing: .5px; }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")


songs = get_songs()
genres = sorted({s["genre"] for s in songs})
moods = sorted({s["mood"] for s in songs})

# ---------------------------------------------------------------- sidebar
st.sidebar.header("What do you like?")
genre = st.sidebar.selectbox("Favorite genre", genres, index=genres.index("hip-hop"))
mood = st.sidebar.selectbox("Favorite mood", moods, index=moods.index("confident"))
energy = st.sidebar.slider("Target energy", 0.0, 1.0, 0.62, 0.01)
acoustic = st.sidebar.checkbox("I like acoustic sound", value=False)
k = st.sidebar.slider("How many songs", 3, 10, 3)

prefs = {
    "favorite_genre": genre,
    "favorite_mood": mood,
    "target_energy": energy,
    "likes_acoustic": acoustic,
}

with st.sidebar.expander("Optional extras"):
    if st.checkbox("Target artist popularity"):
        prefs["target_monthly_listeners"] = st.select_slider(
            "Monthly listeners",
            options=[100_000, 500_000, 1_000_000, 5_000_000, 20_000_000, 50_000_000, 90_000_000],
            value=20_000_000,
            format_func=lambda n: f"{n:,}",
        )
    if st.checkbox("Preferred release year"):
        prefs["preferred_year"] = st.slider("Year", 1955, 2025, 2000)
    if st.checkbox("Target song length"):
        prefs["target_duration_min"] = st.slider("Minutes", 1.0, 12.0, 4.0, 0.25)
    if st.checkbox("Avoid explicit songs"):
        prefs["avoid_explicit"] = True

with st.sidebar.expander("Weight experiment"):
    rec.GENRE_WEIGHT = st.slider("Genre weight", 0.0, 4.0, 2.0, 0.1)
    rec.MOOD_WEIGHT = st.slider("Mood weight", 0.0, 4.0, 1.0, 0.1)
    rec.ENERGY_WEIGHT = st.slider("Energy weight", 0.0, 4.0, 1.5, 0.1)
    rec.ACOUSTIC_WEIGHT = st.slider("Acoustic weight", 0.0, 2.0, 0.5, 0.1)

# ---------------------------------------------------------------- helpers
LABELS = [
    ("genre match", "Genre"), ("mood match", "Mood"), ("energy", "Energy"),
    ("acoustic fit", "Acoustic"), ("non-acoustic fit", "Acoustic"),
    ("artist listeners", "Listeners"), ("released", "Year"), ("length", "Length"),
    ("mood tags", "Tags"), ("explicit", "Explicit"),
]
RULE_COLORS = {
    "Genre": YELLOW, "Mood": BLUE, "Energy": RED, "Acoustic": GREEN, "Listeners": "#ff8a00",
    "Year": "#8a4fff", "Length": "#00b3c7", "Tags": "#ff5fa2", "Explicit": INK,
}


def breakdown(explanation: str) -> dict:
    """Turn the reason strings into {rule: points}."""
    parts = {}
    for reason in explanation.split("; "):
        match = re.search(r"\(([+-]\d+(?:\.\d+)?)\)\s*$", reason)
        if not match:
            continue
        for prefix, label in LABELS:
            if reason.startswith(prefix):
                parts[label] = parts.get(label, 0.0) + float(match.group(1))
                break
    return parts


def esc(x) -> str:
    return html.escape(str(x))


def pie_chart(rank: int, song: dict, score: float, explanation: str):
    """Donut chart of how one song's points were split between the rules."""
    parts = {r: p for r, p in breakdown(explanation).items() if p > 0}
    if not parts:
        return None
    df = pd.DataFrame({"Rule": list(parts), "Points": list(parts.values())})
    df["Share"] = (df["Points"] / df["Points"].sum() * 100).round(0).astype(int).astype(str) + "%"
    df["Label"] = df["Rule"] + " " + df["Points"].map(lambda p: f"{p:g}")
    base = alt.Chart(df).encode(
        theta=alt.Theta("Points:Q", stack=True),
        color=alt.Color(
            "Rule:N",
            scale=alt.Scale(domain=list(RULE_COLORS), range=list(RULE_COLORS.values())),
            legend=None,
        ),
        order=alt.Order("Points:Q", sort="descending"),
        tooltip=["Rule", "Points", "Share"],
    )
    arcs = base.mark_arc(innerRadius=48, outerRadius=105, stroke=INK, strokeWidth=3)
    labels = base.mark_text(radius=128, fontSize=14, fontWeight="bold", color=INK).encode(text="Points:Q")
    center = (
        alt.Chart(pd.DataFrame({"t": [f"{score:.2f}"]}))
        .mark_text(fontSize=26, fontWeight="bold", color=INK)
        .encode(text="t:N")
    )
    return (
        (arcs + labels + center)
        .properties(width=260, height=290)
        .configure_view(strokeWidth=0)
    )


def show_pies() -> None:
    cols = st.columns(min(3, len(results)))
    for idx, (s, score, ex) in enumerate(results[:3]):
        chart = pie_chart(idx + 1, s, score, ex)
        with cols[idx]:
            st.markdown(f"<div style='font-size:1.4rem;font-weight:900'>{idx + 1}. {esc(s['title'])}</div>", unsafe_allow_html=True)
            if chart is not None:
                st.altair_chart(chart)


results = recommend_songs(prefs, songs, k)
everything = recommend_songs(prefs, songs, len(songs))
max_pts = rec.GENRE_WEIGHT + rec.MOOD_WEIGHT + rec.ENERGY_WEIGHT + rec.ACOUSTIC_WEIGHT
n_words = {3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def top_rule(explanation: str) -> str:
    parts = breakdown(explanation)
    return max(parts, key=parts.get) if parts else "nothing in particular"


def pts(x: float) -> str:
    return f"{x:.2f}"


# ---------------------------------------------------------------- page
st.markdown('<div class="eyebrow">A music recommender, explained slowly</div>', unsafe_allow_html=True)
st.markdown('<h1 class="big">Music Recommender Simulation</h1>', unsafe_allow_html=True)
st.markdown(
    f'<p class="deck">You told us you like <mark class="y">{esc(genre)}</mark> songs that feel '
    f'<mark class="b">{esc(mood)}</mark>, at an energy level of <mark class="r">{energy:.2f}</mark>. '
    f"We have {len(songs)} songs. We scored every one of them. What follows is what happened.</p>",
    unsafe_allow_html=True,
)

tab_picks, tab_catalog, tab_details = st.tabs(["The winners", f"All {len(songs)} songs, ranked", "Show your work"])

with tab_picks:
    win, win_score = results[0][0], results[0][1]
    st.markdown('<div class="part">Part 1: The winner</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="huge">{pts(win_score)}</div>', unsafe_allow_html=True)
    if win_score >= max_pts - 0.005:
        verdict = (f"That is the highest score the basic rules allow. <b>{esc(win['title'])}</b> by "
                   f"{esc(win['artist'])} got every point available. This is rare, and we are not sure how to feel about it.")
    else:
        verdict = (f"That is how many points <b>{esc(win['title'])}</b> by {esc(win['artist'])} earned. "
                   f"The most the basic rules allow is {pts(max_pts)}, so it missed perfect by {pts(max_pts - win_score)} points.")
    st.markdown(f'<p class="story">{verdict}</p>', unsafe_allow_html=True)

    st.markdown(f'<div class="part">Part 2: The top {n_words.get(len(results), len(results))}</div>', unsafe_allow_html=True)
    cards = ""
    for i, (s, score, ex) in enumerate(results, 1):
        bg, fg = RANK_COLORS[min(i, len(RANK_COLORS)) - 1]
        cards += (
            f'<div class="card" style="background:{bg};color:{fg}">'
            f'<div class="rank">{i}</div>'
            f'<div class="title">{esc(s["title"])}</div>'
            f'<div class="meta">{esc(s["artist"])}<br>{esc(s["album"])}, {esc(s["release_year"])}</div>'
            f'<div class="why1">Mostly here because of: {esc(top_rule(ex).lower())}.</div>'
            f'<div class="score">{pts(score)} points</div></div>'
        )
    st.markdown(f'<div class="cards">{cards}</div>', unsafe_allow_html=True)

    if len(results) > 1:
        gap = results[0][1] - results[1][1]
        if gap < 0.005:
            gap_line = "The top two songs tied. We had to pick one anyway, so we picked the one that was listed first."
        else:
            gap_line = (f"First place beat second place by {pts(gap)} points. "
                        f"That is {gap / max_pts * 100:.1f}% of the maximum score. Make of that what you will.")
        st.markdown(f'<div class="aside">{gap_line}</div>', unsafe_allow_html=True)

    st.markdown('<div class="part">Part 3: Where the points came from</div>', unsafe_allow_html=True)
    st.markdown(
        "<p class='story'>Every point comes from one of a few rules. A song gets points for matching your genre, "
        "matching your mood, having energy close to your target, and sounding the way you like it to sound. "
        "Here is how the top three split it up. A bigger slice means that rule did more of the work.</p>",
        unsafe_allow_html=True,
    )
    chips = "".join(
        f'<span style="display:inline-block;margin:0 14px 6px 0;font-weight:700">'
        f'<span style="display:inline-block;width:16px;height:16px;border:3px solid {INK};background:{c};'
        f'vertical-align:-3px;margin-right:6px"></span>{r}</span>'
        for r, c in RULE_COLORS.items()
    )
    st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)
    show_pies()

with tab_catalog:
    st.markdown('<div class="part">Part 4: Everybody else</div>', unsafe_allow_html=True)
    last_s, last_score, _ = everything[-1]
    st.markdown(
        f"<p class='story'>Here are all {len(songs)} songs, from best fit to worst fit. The colored bars are your picks. "
        f"The gray bars are everything that did not make it. In last place, with {pts(last_score)} points, "
        f"is <b>{esc(last_s['title'])}</b> by {esc(last_s['artist'])}. It is a fine song. It is just not what you asked for.</p>",
        unsafe_allow_html=True,
    )
    picked = {s["id"]: i for i, (s, _, _) in enumerate(results, 1)}
    df_all = pd.DataFrame(
        [
            {
                "Song": f"{s['title']} - {s['artist']}",
                "Score": sc,
                "Color": RANK_COLORS[min(picked[s["id"]], len(RANK_COLORS)) - 1][0] if s["id"] in picked else "#c9c6ba",
            }
            for s, sc, _ in everything
        ]
    )
    bars = (
        alt.Chart(df_all)
        .mark_bar(stroke=INK, strokeWidth=2)
        .encode(
            y=alt.Y("Song:N", sort=list(df_all["Song"]), title=None, axis=alt.Axis(labelFontSize=16, labelLimit=420)),
            x=alt.X("Score:Q", title="Points", scale=alt.Scale(domain=[0, max(max_pts, df_all["Score"].max())])),
            color=alt.Color("Color:N", scale=None),
            tooltip=["Song", alt.Tooltip("Score:Q", format=".2f")],
        )
    )
    nums = bars.mark_text(align="left", dx=5, fontSize=15, fontWeight="bold", color=INK).encode(
        text=alt.Text("Score:Q", format=".2f"), color=alt.value(INK)
    )
    st.altair_chart(
        (bars + nums)
        .properties(height=30 * len(df_all))
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor=INK, titleColor=INK, domainColor=INK, gridColor="#dddbd2")
    )

with tab_details:
    st.markdown('<div class="part">Part 5: The receipts</div>', unsafe_allow_html=True)
    st.markdown("<p class='story'>If you do not trust the colored boxes, here are the numbers.</p>", unsafe_allow_html=True)
    table = pd.DataFrame(
        [
            {
                "Rank": i, "Song": s["title"], "Artist": s["artist"], "Genre": s["genre"],
                "Mood": s["mood"], "Year": s["release_year"], "Score": round(score, 2),
            }
            for i, (s, score, _) in enumerate(results, 1)
        ]
    )
    st.dataframe(table, hide_index=True)

    st.markdown('<div class="part">Part 6: In plain words</div>', unsafe_allow_html=True)
    for i, (s, score, ex) in enumerate(results, 1):
        lines = "<br>".join(esc(r) for r in ex.split("; "))
        st.markdown(
            f'<div class="why"><b>{i}. {esc(s["title"])}</b> by {esc(s["artist"])}, {pts(score)} points<br>{lines}</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    "<div class='foot'>1. Scores are rounded to two decimal places. The computer is less rounded than we are.<br>"
    "2. A song cannot get points for a rule it does not know about. The rules are a short list.<br>"
    "3. A pie chart cannot show negative points, so a penalty will not appear as a slice. It shows up in Part 6.</div>",
    unsafe_allow_html=True,
)