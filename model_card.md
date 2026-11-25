# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

MRS (MusicRecommendSim)



---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.) 
Genre, mood, energy and acousticness always count. Listener count, release year, song length, mood tags and the explicit flag count only when a user asks for them. 

- What user preferences are considered  
Favorite genre, mood, target energy and whether they like acoustic sound. Optionally also a target artist popularity, a preferred year, a preferred length, favorite mood tags, and “avoid explicit”.
- How does the model turn those into a score  
Genre +2.0, mood +1.0, energy up to +1.5, acoustic up to +0.5. The optional extras add more points, with the exact caps in the text.
Ther is also a penalty for repeated artist to have a benefit of diversifying a profile from one artist. Also a small genre penalty that very slight.
- What changes did you make from the starter logic 

 I wrote the loader, the scoring, the ranking and the explanations. I also replaced the fictional songs with 70 real ones, added six new columns and rules for them, and added the diversity penalty, the modes and the table output. There are now 19 tests.

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Imagine a game where songs get certian boost for different types of attributes of a song for someone to like it

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog 
There are currently 70 songs by 44 different artists

- What genres or moods are represented  
There are 19 different genres represented in this dataset lead by Hip-Hop, Rock, Jazz.
The different moods represented are playful, hopeful, sad, moody, mellow, emotional, intense.


- Did you add or remove data  

Originally started with fake songs by fake artist, but over time I just just replaced all of them with real artist
I added quite a few songs and added six different columns from the base.
(album, artist monthly listeners, release year, song length, mood tags, explicit flag)


- Are there parts of musical taste missing in the dataset 
I would say there would be some newer genres I would say that aren't in here like
 --Kpop, Blues, Punk/pop-punk, alternative, disco, lo-fi, EDM, Afrobeats
Some taste missing with energy ad feeling could be calmer songs, even happier/agressive could be considered
By decade there are only like 8 songs from before 1970 and this is a english dominated data set    

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
