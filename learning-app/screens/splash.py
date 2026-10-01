import base64
import time
from pathlib import Path

import streamlit as st

LOGO = Path(__file__).resolve().parent.parent / "assets" / "siq_logo.png"
LAVENDER = "#D6CCF2"
LAVENDER_DARK = "#B7A6E8"

encoded = base64.b64encode(LOGO.read_bytes()).decode()
st.markdown(
    f"""
    <style>
    .stApp {{ background: linear-gradient(160deg, {LAVENDER} 0%, #E9E2FA 100%); }}
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"], header[data-testid="stHeader"] {{ display: none; }}
    .block-container {{ padding-top: 0; animation: none !important; }}

    @keyframes logoIn  {{ from {{ opacity: 0; transform: scale(.85) translateY(10px); }}
                          to   {{ opacity: 1; transform: scale(1) translateY(0); }} }}
    @keyframes textIn  {{ from {{ opacity: 0; transform: translateY(14px); }}
                          to   {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes barFill {{ from {{ width: 0%; }} to {{ width: 100%; }} }}
    @keyframes floaty  {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}

    .siq-splash {{ display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; }}
    .siq-logo {{ width:min(280px,58vw); border-radius:28px; box-shadow:0 12px 32px rgba(60,40,120,.28);
                 animation: logoIn .9s cubic-bezier(.2,.8,.2,1) both, floaty 3s ease-in-out .9s infinite; }}
    .siq-name {{ margin-top:26px; font-family:Arial,'Helvetica Neue',Helvetica,sans-serif; font-size:4.4rem; color:#000000;
                 animation: textIn .8s ease-out .35s both; }}
    .siq-track {{ margin-top:34px; width:min(340px,70vw); height:10px; background:rgba(255,255,255,.75);
                  border-radius:999px; overflow:hidden; animation: textIn .8s ease-out .6s both; }}
    .siq-fill {{ height:100%; width:0%; border-radius:999px;
                 background:linear-gradient(90deg,#8FE3EF,#B7E4C7,#B7A6E8);
                 animation: barFill 3s linear .05s forwards; }}
    .siq-loading {{ margin-top:12px; font-family:Arial,'Helvetica Neue',Helvetica,sans-serif; font-size:1.6rem; color:#000000;
                    animation: textIn .8s ease-out .8s both; }}
    </style>
    <div class="siq-splash">
        <img class="siq-logo" src="data:image/png;base64,{encoded}" />
        <div class="siq-name">SophosIQ</div>
        <div class="siq-track"><div class="siq-fill"></div></div>
        <div class="siq-loading">Loading...</div>
    </div>
    """,
    unsafe_allow_html=True,
)

time.sleep(3.1)
st.session_state.stage = "login"
st.rerun()
