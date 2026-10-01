import streamlit as st

# Light palette: light greens, aqua blues, lavender. Base/bg = white. Text = black.
GREEN = "#B7E4C7"
GREEN_DARK = "#7FD8A8"
AQUA = "#8FE3EF"
AQUA_DARK = "#5FCFE0"
LAVENDER = "#D6CCF2"
LAVENDER_DARK = "#B7A6E8"
WHITE = "#FFFFFF"
BLACK = "#000000"

FONT_FACE = ""
FONT = "Arial, 'Helvetica Neue', Helvetica, sans-serif"

_TEXT_SELECTORS = (
    "html, body, .stApp, p, li, label, a, h1, h2, h3, h4, h5, h6, button, input, textarea, select, td, th, "
    "[data-testid='stMarkdownContainer'], [data-testid='stCaptionContainer'], "
    "[data-testid='stSidebarNav'] a span:not([data-testid='stIconMaterial']), "
    "[data-baseweb='tab'], [data-baseweb='select'] div, [data-testid='stMetricValue']"
)

LOADER_CSS = f"""
@keyframes siqSpin {{ to {{ transform: rotate(360deg); }} }}
@keyframes siqSpinIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
.stApp:has([data-testid="stStatusWidget"])::before {{
    content: ""; position: fixed; top: 84px; left: 50%; width: 38px; height: 38px; margin-left: -19px;
    border: 5px solid {LAVENDER}; border-top-color: {AQUA_DARK}; border-right-color: {GREEN_DARK};
    border-radius: 50%; z-index: 99999; pointer-events: none; background: transparent;
    box-shadow: 0 2px 10px rgba(0,0,0,.15);
    animation: siqSpin .8s linear infinite, siqSpinIn .25s ease .35s both;
}}
"""

MOTION_CSS = f"""
@keyframes siqFadeUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: translateY(0); }} }}
[data-testid="stMainBlockContainer"], .block-container {{ animation: siqFadeUp .55s ease-out both; }}
.stButton > button, .stLinkButton > a {{
    border: none; border-radius: 12px; padding: 0.5em 1.2em;
    transition: transform .18s ease, box-shadow .18s ease, background .25s ease, filter .2s ease;
}}
.stButton > button:hover, .stLinkButton > a:hover {{ transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,.18); }}
.stButton > button:active {{ transform: translateY(0) scale(.98); box-shadow: none; }}
.app-card {{ border-radius: 16px; padding: 1.2em; margin-bottom: 1em; transition: transform .2s ease, box-shadow .2s ease; }}
.app-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,0,0,.14); }}
[data-baseweb="input"], [data-baseweb="select"] > div {{ border-radius: 12px !important; transition: box-shadow .2s ease; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 10px 10px 0 0; transition: background-color .25s ease, transform .2s ease; }}
.stTabs [data-baseweb="tab"]:hover {{ transform: translateY(-2px); }}
[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 14px; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ transition: box-shadow .2s ease; }}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.10); }}
"""

LIGHT_CSS = f"""
html, body, [class*="css"] {{ color: {BLACK} !important; background-color: {WHITE}; }}
.stApp {{ background-color: {WHITE}; }}
h1, h2, h3, h4, h5, h6, p, span, label, li, div {{ color: {BLACK} !important; }}
.stButton > button, .stLinkButton > a {{ background: linear-gradient(90deg, {AQUA}, {GREEN}); color: {BLACK} !important; }}
.stButton > button:hover, .stLinkButton > a:hover {{ background: linear-gradient(90deg, {AQUA_DARK}, {GREEN_DARK}); color: {BLACK} !important; }}
section[data-testid="stSidebar"] {{ background-color: {LAVENDER}; }}
.app-card {{ background-color: {GREEN}; border: 1px solid {GREEN_DARK}; }}
.app-card.aqua {{ background-color: {AQUA}; border-color: {AQUA_DARK}; }}
.app-card.lavender {{ background-color: {LAVENDER}; border-color: {LAVENDER_DARK}; }}
input, textarea, select {{ background-color: {WHITE} !important; color: {BLACK} !important; }}
[data-baseweb="input"]:focus-within {{ box-shadow: 0 0 0 3px {LAVENDER}; }}
.stTabs [data-baseweb="tab"] {{ background-color: {LAVENDER}; color: {BLACK} !important; }}
.stTabs [aria-selected="true"] {{ background-color: {AQUA} !important; }}
"""

D_BG = "#15121F"
D_SURFACE = "#1E1A2E"
D_FIELD = "#262038"
D_LINE = "#4A3F73"
D_TEXT = "#F3EEFB"

DARK_CSS = f"""
html {{ color-scheme: dark; }}
.stApp span, .stApp div, .stApp p, .stApp li, .stApp label, .stApp a {{ color: {D_TEXT}; }}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background-color: {D_BG} !important; }}
[data-testid="stHeader"] {{ background: rgba(21,18,31,.85) !important; }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stWidgetLabel"], .stApp summary, .stApp [data-baseweb="tab"], .stApp small,
.stApp [data-testid="stMetricValue"], .stApp [data-testid="stMetricLabel"] {{ color: {D_TEXT} !important; }}
[data-testid="stSidebar"] {{ background-color: #1B1530 !important; }}
[data-testid="stSidebar"] * {{ color: {D_TEXT} !important; }}
.stButton > button, .stLinkButton > a {{ background: linear-gradient(90deg, #2A8397, #37946F); color: #FFFFFF !important; }}
.stButton > button *, .stLinkButton > a * {{ color: #FFFFFF !important; }}
.stButton > button:hover, .stLinkButton > a:hover {{ background: linear-gradient(90deg, #3396AB, #43A87F); color: #FFFFFF !important; }}
.stButton > button:disabled {{ background: #2D2745 !important; color: #8B83A8 !important; box-shadow: none; }}
.app-card {{ background-color: #24513F; border: 1px solid #3B7A60; }}
.app-card.aqua {{ background-color: #1D4B57; border-color: #2F7A8A; }}
.app-card.lavender {{ background-color: #3A2F63; border-color: #5B4B9A; }}
.app-card, .app-card * {{ color: {D_TEXT} !important; }}
input, textarea {{ background-color: {D_FIELD} !important; color: {D_TEXT} !important; }}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {{ background-color: {D_FIELD} !important; border-color: {D_LINE} !important; }}
[data-baseweb="select"] div, [data-baseweb="select"] span {{ color: {D_TEXT} !important; }}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {{ background-color: {D_FIELD} !important; }}
[data-baseweb="popover"] li, [data-baseweb="popover"] div, [role="listbox"] li {{ color: {D_TEXT} !important; }}
[data-baseweb="input"]:focus-within {{ box-shadow: 0 0 0 3px #5B4B9A; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {D_LINE} !important; }}
[data-testid="stExpander"] details {{ background-color: {D_SURFACE}; border-color: {D_LINE} !important; }}
[data-testid="stFileUploaderDropzone"] {{ background-color: {D_FIELD}; }}
[data-testid="stDialog"] div[role="dialog"] {{ background-color: {D_SURFACE} !important; }}
[data-testid="stDataFrame"] {{ filter: invert(.92) hue-rotate(180deg); }}
.stTabs [data-baseweb="tab"] {{ background-color: #2D2745; }}
.stTabs [aria-selected="true"] {{ background-color: #2A8397 !important; }}
.stTabs [aria-selected="true"], .stTabs [aria-selected="true"] * {{ color: #FFFFFF !important; }}
[data-testid="stAlert"] * {{ color: inherit !important; }}
.stApp [style*="background"], .stApp [style*="background"] * {{ color: #000000 !important; }}
"""


def inject_base_css():
    dark = st.session_state.get("theme", "light") == "dark"
    css = "\n".join([
        FONT_FACE,
        f"{_TEXT_SELECTORS} {{ font-family: {FONT} !important; }}",
        "h1, h2, h3, h4 { font-weight: 400 !important; letter-spacing: .01em; }",
        "h1 { font-size: 3rem !important; } h2 { font-size: 2.3rem !important; } h3 { font-size: 1.9rem !important; }",
        "p, li, label, [data-testid='stMarkdownContainer'] p { font-size: 1.15rem; }",
        MOTION_CSS,
        LOADER_CSS,
        DARK_CSS if dark else LIGHT_CSS,
    ])
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def card(title: str, body: str, tone: str = "green"):
    tone_class = {"green": "", "aqua": "aqua", "lavender": "lavender"}.get(tone, "")
    st.markdown(
        f"""
        <div class="app-card {tone_class}">
            <h4 style="margin-top:0;">{title}</h4>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
