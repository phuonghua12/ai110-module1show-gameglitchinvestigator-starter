# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### Describe the game's purpose
A simple Streamlit number-guessing game. The app picks a secret number within
a range that depends on the chosen difficulty (Easy 1–20, Normal 1–100, Hard
1–50). The player types guesses, gets "Higher/Lower" hints, and has a limited
number of attempts to find the secret. A running score rewards faster wins, and
a "Developer Debug Info" panel reveals the secret for testing.

### Detail which bugs you found
1. **"Attempts left" didn't decrease on the first guess.** The counter started
   at 1 instead of 0, and — more importantly — the "Attempts left" message was
   drawn *before* the counter was incremented. Because Streamlit reruns the
   script top-to-bottom on every click, the displayed number always lagged one
   click behind.
2. **"New Game" button didn't restart the game.** It reset the secret and
   attempts but left `status` as `"won"`/`"lost"`, so the game-over guard
   immediately stopped the "new" game. Score and history weren't cleared either.
3. **Hints were backwards.** Two causes: the hint text was swapped ("Too High"
   told the player to go HIGHER), and on even-numbered attempts the secret was
   cast to a string, forcing a lexicographic comparison (`"9" > "50"`) that
   flipped the hints on alternating turns.

### Explain what fixes you applied
1. Initialized `attempts` at 0 and moved the "Attempts left" display into an
   `st.empty()` placeholder that is filled *after* the guess is processed, so
   the count is always current.
2. Made "New Game" reset **all** state: `secret`, `attempts`, `score`,
   `status`, and `history`.
3. Corrected the hint text and removed the `str()` cast so the guess is always
   compared against the real integer secret.
4. **Refactor & Test:** moved `get_range_for_difficulty`, `parse_guess`,
   `check_guess`, and `update_score` into `logic_utils.py`, and split the UI
   text into a new `hint_message` helper. `check_guess` now returns just the
   outcome string so the existing tests pass.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User enters a guess of 40
2. Game returns "Too Low"
3. User enters a guess of 70 → "Too High"
4. Score updates correctly after each guess
5. Game ends after the correct guess

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ python -m pytest tests/
platform darwin -- Python 3.13.0, pytest-9.0.3, pluggy-1.6.0
collected 3 items

tests/test_game_logic.py ...                                             [100%]

============================== 3 passed in 0.01s ===============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
