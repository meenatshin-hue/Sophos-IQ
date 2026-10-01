import base64
from datetime import date
from pathlib import Path

import streamlit as st

LOGO = Path(__file__).resolve().parent.parent / "assets" / "siq_logo.png"

BROKEN_MESSAGE = "Oh no! You broke your streak, don't worry, you can still start a new one today!"

WELCOME_BACK = [
    "You're back! I knew you were a bright learner",
    "Welcome back super star",
    "Come on, we've got a good day ahead.",
]

# (emoji graphic, joke)
JOKES = [
    ("📘😢", "Why was the math book sad? It had too many problems."),
    ("💻🍫", "I told my computer I needed a break. Now it won't stop sending me KitKat ads."),
    ("🍰📚", "Why did the student eat his homework? The teacher said it was a piece of cake."),
    ("🐻🍬", "What do you call a bear with no teeth? A gummy bear."),
    ("⚛️🤥", "Why can't you trust atoms? They make up everything!"),
    ("0️⃣🥋", "What did zero say to eight? Nice belt!"),
    ("🌾🏆", "Why did the scarecrow win an award? He was outstanding in his field."),
    ("🦖💤", "What do you call a sleeping dinosaur? A dino-snore."),
    ("6️⃣😨", "Why is 6 afraid of 7? Because 7 8 9!"),
    ("🎵🪜", "Why did the music teacher need a ladder? To reach the high notes."),
    ("📖🚀", "I'm reading a book about anti-gravity. It's impossible to put down."),
    ("🏴‍☠️🎨", "What's a pirate's favorite subject? Arrrrt."),
    ("🌙✂️", "How does the moon cut his hair? Eclipse it."),
    ("🌊👋", "What did the ocean say to the beach? Nothing, it just waved."),
    ("📐🤯", "Why was the geometry class so tough? Too many angles to think about."),
    ("🍝🎭", "What do you call a fake noodle? An impasta."),
    ("📅🎉", "Why did the calendar go to the party? It had a lot of dates."),
    ("🖥️🍟", "What's a computer's favorite snack? Microchips."),
    ("🚲😴", "Why did the bicycle fall over? It was two-tired."),
    ("🐶🎩", "What do you call a dog magician? A labracadabrador."),
    ("👻🤥", "Why are ghosts bad liars? You can see right through them."),
    ("🌴🖐️", "What kind of tree fits in your hand? A palm tree."),
    ("☕🚔", "Why did the coffee file a police report? It got mugged."),
    ("⛄🧛", "What do you get when you cross a snowman with a vampire? Frostbite."),
    ("😎🌟", "Why did the teacher wear sunglasses? Her students were so bright."),
    ("🐊🕵️", "What do you call an alligator in a vest? An investigator."),
    ("🐸🚌", "Why did the frog take the bus? His car got toad."),
    ("📝✏️", "What did the paper say to the pencil? Write on!"),
    ("🧪😂", "I would tell you a chemistry joke, but I know I wouldn't get a reaction."),
    ("🔢🎈", "Why did the number 10 go to the party alone? Because 11 was a crowd."),
]

# (minimum streak, banner, number of stars)
MILESTONES = [
    (50, "STREAK OVERLOAD; YOU'RE TOO GOOD", 5),
    (21, "STAR IN THE MAKING", 3),
    (7, "YOU'RE ON FIRE", 2),
    (3, "SUPER LEARNER", 1),
]
MILESTONE_DAYS = (3, 7, 21, 50)


def joke_for(day: date | None = None) -> tuple[str, str]:
    day = day or date.today()
    return JOKES[day.toordinal() % len(JOKES)]


def welcome_for(day: date | None = None) -> str:
    day = day or date.today()
    return WELCOME_BACK[day.toordinal() % len(WELCOME_BACK)]


def milestone_for(count: int) -> tuple[str, int] | None:
    for minimum, banner, stars in MILESTONES:
        if count >= minimum:
            return banner, stars
    return None


def logo_data_uri() -> str:
    return "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()


def milestone_html(count: int) -> str:
    found = milestone_for(count)
    if not found:
        return ""
    banner, stars = found
    return (
        "<div style='text-align:center;margin:.6rem 0;padding:.9rem;border-radius:16px;"
        "background:linear-gradient(90deg,#8FE3EF,#B7E4C7,#D6CCF2);'>"
        f"<div style='font-size:2rem;letter-spacing:.2rem;'>{'⭐' * stars}</div>"
        f"<div style='font-size:1.25rem;color:#000;'>{banner}</div>"
        f"<div style='font-size:.9rem;color:#000;'>{count} day streak</div></div>"
    )


def joke_html(day: date | None = None) -> str:
    emoji, text = joke_for(day)
    return (
        "<div style='text-align:center;padding:1rem;border-radius:16px;background:#F6EEFF;"
        "border:1.5px solid #B7A6E8;'>"
        f"<div style='font-size:3.2rem;line-height:1.2;'>{emoji}</div>"
        "<div style='font-size:.85rem;margin:.2rem 0;color:#000;'>Joke of the day</div>"
        f"<div style='font-size:1.05rem;color:#000;'>{text}</div></div>"
    )


@st.dialog("Daily check-in")
def daily_dialog(info: dict) -> None:
    count, status = info["count"], info["status"]
    st.markdown(
        f"<div style='text-align:center;'><img src='{logo_data_uri()}' "
        "style='width:84px;border-radius:16px;'/></div>",
        unsafe_allow_html=True,
    )
    if status == "broken":
        st.markdown(
            f"<div style='text-align:center;font-size:1.15rem;margin:.6rem 0;'>{BROKEN_MESSAGE}</div>",
            unsafe_allow_html=True,
        )
    if status in ("broken", "new_user"):
        st.markdown(
            f"<div style='text-align:center;'><div style='font-size:3.4rem;'>😊</div>"
            f"<div style='font-size:1.1rem;'>{welcome_for()}</div></div>",
            unsafe_allow_html=True,
        )
    elif status == "continued":
        st.markdown(
            f"<div style='text-align:center;font-size:1.1rem;'>🔥 Day {count} of your streak. Keep it going!</div>",
            unsafe_allow_html=True,
        )
    if count in MILESTONE_DAYS or (status == "continued" and count >= 50):
        st.markdown(milestone_html(count), unsafe_allow_html=True)
    st.markdown(joke_html(), unsafe_allow_html=True)
    if st.button("Let's learn!", use_container_width=True):
        st.rerun()
