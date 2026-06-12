import random
import streamlit as st

# FIX: Refactored the game logic out of app.py into logic_utils.py using
# Claude Code agent mode. I described the bugs; the AI proposed splitting
# check_guess (decision) from hint_message (UI text) so the tests stay green.
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    hint_message,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX (Bug 1): start the counter at 0 (no attempts made yet), not 1.
# I reported "Attempts left didn't drop on the first guess"; the AI traced
# it to the wrong initial value plus the render-order issue handled below.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

# FIX (Bug 1): reserve a spot for the "Attempts left" message. The AI
# explained that Streamlit reran the script top-to-bottom and drew this
# message *before* the counter was incremented, so it always lagged a click
# behind. Using st.empty() lets us fill it *after* the guess is processed.
attempts_box = st.empty()

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX (Bug 2): a new game must reset ALL game state, including status,
    # score, and history. I reported "New Game does nothing"; the AI found
    # that status stayed "won"/"lost", so the game-over guard immediately
    # stopped the fresh game. Resetting every key fixes it.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

# Only process a guess while the game is still playable.
if submit and st.session_state.status == "playing":
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX (Bug 3, root cause): always compare against the real int secret.
        # I reported "hints are backwards"; the AI spotted that the old code
        # turned the secret into a string on even attempts, forcing a text
        # comparison ("9" > "50") that flipped the hints on alternating turns.
        outcome = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(hint_message(outcome))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

# FIX (Bug 1): fill the reserved box now, after the guess was counted, so
# the displayed count reflects this turn instead of the previous one.
attempts_left = max(0, attempt_limit - st.session_state.attempts)
attempts_box.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_left}"
)

# Show a standing message if the game is already over.
if st.session_state.status == "won":
    st.success("You already won. Start a new game to play again.")
elif st.session_state.status == "lost":
    st.error("Game over. Start a new game to try again.")

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
