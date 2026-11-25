# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Major music apps like Spotify and Apple Music have algorithms that find certains attributes of songs that are similar to others. Some of the main features of these apps. I have set my turning with genre and energy that are strong signs that will be recommended to the user. There is also the monthly listeners that is barely there in the tuning.

-- Main Song Features: -- title, artist, album, genre, mood, energy, tempo_bpm,
valence, danceability, acousticness, artist_monthly_listeners, release_year,
duration_min, mood_tags, explicit

--Website--:
Shows list of songs that can be tuned to your liking
Can go by certain genre and mood that includes a target energy and many more options
Weight's adjustment meter for genre, mood, energy and acoustic


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot/COPY**

Profile: Middle-of-the-road (no genre fit)
  genre=classical, mood=angry, energy=0.5, likes_acoustic=True
+---+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| # | balanced                        | genre_first                     | mood_first                      | energy_focused                  |
+---+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| 1 | Piano Concerto No. 21 i… [3.83] | Piano Concerto No. 21 i… [4.38] | Bound for the Floor - L… [3.98] | Piano Concerto No. 21 i… [4.17] |
| 2 | Flight of the Bumblebee… [3.27] | Flight of the Bumblebee… [3.98] | Smells Like Teen Spirit… [3.90] | Jolene - Dolly Parton [3.35]    |
| 3 | Bound for the Floor - L… [1.98] | Bound for the Floor - L… [1.66] | Master of Puppets - Met… [3.87] | Blue Train - John Coltr… [3.27] |
| 4 | Smells Like Teen Spirit… [1.90] | Smells Like Teen Spirit… [1.60] | Piano Concerto No. 21 i… [2.83] | Trouble - Coldplay [3.20]       |
| 5 | Master of Puppets - Met… [1.87] | Master of Puppets - Met… [1.58] | Flight of the Bumblebee… [2.27] | What's Going On - Marvi… [3.20] |
+---+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
+----------------+------------------------+-----------------------+----------------+------------------------------+
| mode           | same songs as balanced | same rank as balanced | genres in list | #1 pick                      |
+----------------+------------------------+-----------------------+----------------+------------------------------+
| balanced       | 5/5                    | 5/5                   | 4              | Piano Concerto No. 21 in C M |
| genre_first    | 5/5                    | 5/5                   | 4              | Piano Concerto No. 21 in C M |
| mood_first     | 5/5                    | 0/5                   | 4              | Bound for the Floor          |
| energy_focused | 1/5                    | 1/5                   | 5              | Piano Concerto No. 21 in C M |
+----------------+------------------------+-----------------------+----------------+------------------------------+
Only in some modes:
  Blue Train by John Coltrane (jazz/soulful): energy_focused
  Bound for the Floor by Local H (grunge/angry): balanced, genre_first, mood_first
  Flight of the Bumblebee by Nikolai Rimsky-Korsakov (classical/restless): balanced, genre_first, mood_first
  Jolene by Dolly Parton (country/sad): energy_focused
  Master of Puppets by Metallica (metal/angry): balanced, genre_first, mood_first
  Smells Like Teen Spirit by Nirvana (rock/angry): balanced, genre_first, mood_first
  Trouble by Coldplay (rock/sad): energy_focused
  What's Going On by Marvin Gaye (soul/reflective): energy_focused

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5

Things looked alot different when you change the weight on genre since you get alot more varity of genres atleast

- What happened when you added tempo or valence to the score


---

## Limitations and Risks

Summarize some limitations of your recommender.
I think there might be too much rap that really migth override it. The monthly listeners might be a net negative with having it in the calculations.
You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:



The biggest lesson was how much the data shapes the results, and how bias can sneak in without anyone meaning it. Hip-hop had 13 songs in my catalog and some genres had one, so a hip-hop fan got a great list while a shoegaze or k-pop fan got one good song and a weak tail. It's also hard for these type of recommenders would be using fake data like i think even though it is a bare bones music recommender I still think a regular person could use it and not be dissapointed. I will say I think this has helped me try to really look out of bias since that can truly make or break this project. I will say claude sisnt help with me developing the penalties and also adjusting my algorithm. 

