from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import aiosqlite
import uvicorn

app = FastAPI()
app.mount("/web_app/assets", StaticFiles(directory="web_app/assets"),name="assets")
templates = Jinja2Templates(directory="web_app")

class WordDifficultyAnalyzer:
    def __init__(self):
        self.common_prefixes = ('un', 'in', 'dis', 'en', 'non', 'pre', 'post', 'over', 'under', 're', 'semi', 'anti', 'mid', 'mis')
        self.common_suffixes = ('ing', 'ly', 'ed', 'ion', 'er', 'ment', 'ness', 'ship', 's', 'es')
        self.rare_words = set(['ubiquitous', 'quintessential', 'ephemeral', 'serendipity'])  # Misol uchun

    def count_syllables(self, word):
        word = word.lower()
        vowel_count = sum(1 for char in word if char in "aeiouy")
        for i in range(1, len(word)):
            if word[i] in "aeiouy" and word[i-1] in "aeiouy":
                vowel_count -= 1
        return max(1, vowel_count)

    def has_affixes(self, word):
        return any(word.startswith(prefix) for prefix in self.common_prefixes) or any(word.endswith(suffix) for suffix in self.common_suffixes)

    def is_rare_word(self, word):
        return word.lower() in self.rare_words

    def evaluate_word_difficulty(self, word):
        syllables = self.count_syllables(word)
        affix = self.has_affixes(word)
        rare = self.is_rare_word(word)
        difficulty_score = 5  # Eng oson so'zlar uchun boshlang'ich ball

        if syllables >= 3 or affix or rare:
            difficulty_score = 1.5
        elif syllables == 2:
            difficulty_score = 3
        elif syllables == 1:
            difficulty_score = 4

        return difficulty_score

class Word(BaseModel):
    english: str
    uzbek: str
    ielts_level: str
    difficulty: float

async def get_db():
    async with aiosqlite.connect("words.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                english TEXT NOT NULL,
                uzbek TEXT NOT NULL,
                ielts_level TEXT NOT NULL,
                difficulty REAL NOT NULL
            )
        """)
        await db.commit()
        yield db

@app.post("/add_word/")
async def add_word(english: str = Form(...), uzbek: str = Form(...), ielts_level: str = Form(...), db: aiosqlite.Connection = Depends(get_db)):
    print(english)
    analyzer = WordDifficultyAnalyzer()
    difficulty = analyzer.evaluate_word_difficulty(english)
    query = "INSERT INTO words (english, uzbek, ielts_level, difficulty) VALUES (?, ?, ?, ?)"
    await db.execute(query, (english, uzbek, ielts_level, difficulty))
    await db.commit()
    return {"message": "Word added successfully"}

@app.get("/word_list", response_class=HTMLResponse)
async def get_words(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM words")
    words = await cursor.fetchall()
    return templates.TemplateResponse("word_list.html", {"request": request, "words": words})

@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/add_words", response_class=HTMLResponse)
async def read_add_word(request: Request):
    return templates.TemplateResponse("add_words.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
