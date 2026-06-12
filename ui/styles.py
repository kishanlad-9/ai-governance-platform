# ui/styles.py
# ─────────────────────────────────────────────────────────────────────────────
# Global CSS for the entire platform.
# Call inject_css() once at the top of app.py — do NOT call it per module.
# To restyle a component, search for its class name here.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

_CSS = """
<style>
/* ── Global layout ─────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] { background: #F4F5FB; }
[data-testid="stSidebar"]          { background: #12111F !important; }
[data-testid="stSidebar"] *        { color: #C8C8E0 !important; }
[data-testid="stSidebar"] .stButton > button { border-radius: 8px !important; }
[data-testid="stSidebar"] input    { background: #1e1d2e !important; color: #fff !important; border-color: #3a3a55 !important; }
div[data-testid="stChatInput"] textarea { background: #fff !important; }

/* ── Sidebar module nav buttons ─────────────────────────────────────────────── */
.mod-active > button {
  background: linear-gradient(135deg,#6C63FF,#4A42CC) !important;
  color: white !important; font-weight: 600 !important;
  border: none !important; border-radius: 10px !important;
}
.mod-inactive > button {
  background: #1c1b2e !important; color: #888 !important;
  border: 1px solid #2e2d45 !important; border-radius: 10px !important;
}
.mod-inactive > button:hover { background: #252438 !important; color: #ccc !important; }

/* ── Sub-navigation buttons ─────────────────────────────────────────────────── */
.subnav-active > button {
  background: #252438 !important; color: #a89fff !important;
  border-left: 3px solid #6C63FF !important;
  border-top: none !important; border-right: none !important; border-bottom: none !important;
  border-radius: 0 6px 6px 0 !important; font-weight: 600 !important;
}
.subnav-inactive > button {
  background: transparent !important; color: #555 !important;
  border: none !important; border-radius: 6px !important;
}
.subnav-inactive > button:hover { background: #1c1b2e !important; color: #999 !important; }

/* ── Progress bars ──────────────────────────────────────────────────────────── */
.prog-bg   { background:#2a2940; border-radius:8px; height:7px; margin:4px 0 10px; }
.prog-fill { height:7px; border-radius:8px; transition:width 0.5s; }

/* ── Field checklist dots (sidebar) ─────────────────────────────────────────── */
.fcheck    { display:flex; align-items:center; gap:8px; padding:4px 0; font-size:0.76rem; }
.fc-dot    { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.fc-on     { background:#1D9E75; }
.fc-off    { background:#2e2d45; border:1px solid #444; }
.fc-lbl-on  { color:#7effc8 !important; }
.fc-lbl-off { color:#484860 !important; }

/* ── Section card ───────────────────────────────────────────────────────────── */
.scard {
  background:#fff; border:1px solid #E4E5F0; border-radius:14px;
  padding:1.4rem 1.6rem; margin-bottom:1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ── Page header banner ─────────────────────────────────────────────────────── */
.page-hdr {
  background: linear-gradient(135deg,#6C63FF 0%,#3d35b0 100%);
  border-radius:14px; padding:1.3rem 1.8rem; margin-bottom:1.4rem; color:white;
}
.page-hdr h2 { color:white; margin:0; font-size:1.35rem; }
.page-hdr p  { color:rgba(255,255,255,0.8); margin:0.2rem 0 0; font-size:0.85rem; }

/* ── Chat bubbles ───────────────────────────────────────────────────────────── */
.chat-u {
  background:#EDEEFF; border-radius:14px 14px 4px 14px;
  padding:0.7rem 1rem; margin:0.5rem 0; margin-left:18%;
}
.chat-a {
  background:#fff; border:1px solid #EAEBF5; border-radius:14px 14px 14px 4px;
  padding:0.7rem 1rem; margin:0.5rem 0; margin-right:18%;
  box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.chat-lbl { font-size:0.65rem; font-weight:800; letter-spacing:0.07em;
            color:#6C63FF; margin-bottom:0.25rem; }

/* ── Field extraction cards ─────────────────────────────────────────────────── */
.fcard {
  background:#fff; border:1px solid #e8e8f5;
  border-left:3px solid #6C63FF; border-radius:8px;
  padding:0.6rem 0.9rem; margin-bottom:0.45rem;
}
.fcard.done      { border-left-color:#1D9E75; background:#f4fdf8; }
.fcard-lbl       { font-size:0.65rem; font-weight:800; color:#6C63FF;
                   text-transform:uppercase; letter-spacing:0.07em; }
.fcard-lbl.done  { color:#1D9E75; }
.fcard-val       { font-size:0.88rem; color:#1a1a2e; margin-top:3px; line-height:1.45; }
.fcard-val.pending { color:#ccc; font-style:italic; }

/* ── Summary table ──────────────────────────────────────────────────────────── */
.sum-table { width:100%; border-collapse:collapse; font-size:0.88rem; }
.sum-table th {
  background:#6C63FF; color:white; padding:9px 14px;
  text-align:left; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em;
}
.sum-table td { padding:9px 14px; border-bottom:1px solid #f0f0f8; color:#1a1a2e; vertical-align:top; }
.sum-table tr:last-child td  { border-bottom:none; }
.sum-table tr:nth-child(even) td { background:#f9f9fd; }
.sum-table .lbl-col { color:#6C63FF; font-weight:600; width:35%; }

/* ── Status badges ──────────────────────────────────────────────────────────── */
.badge       { display:inline-block; padding:3px 11px; border-radius:20px; font-size:0.75rem; font-weight:700; }
.b-draft     { background:#FFF3CD; color:#856404; }
.b-ready     { background:#D1F5EA; color:#0f6e56; }
.b-submitted { background:#E8E0FF; color:#4A42CC; }
.b-review    { background:#FFF3CD; color:#856404; }
.b-approved  { background:#D1F5EA; color:#0f6e56; }
.b-rejected  { background:#FDE8E8; color:#c0392b; }
.b-deferred  { background:#F0F0F0; color:#555; }

/* ── Coming-soon placeholder ────────────────────────────────────────────────── */
.coming-soon {
  text-align:center; padding:4rem 2rem; color:#aaa;
  border:2px dashed #E4E5F0; border-radius:14px; background:#fff;
}
.coming-soon h3 { color:#bbb; margin-bottom:0.5rem; font-size:1.2rem; }

/* ── Reference ID box ───────────────────────────────────────────────────────── */
.ref-box {
  background:#1a1a2e; border:1px solid #6C63FF; border-radius:10px;
  padding:1rem 1.4rem; margin:1rem 0; font-family:monospace;
  display:flex; justify-content:space-between; align-items:center;
}
.ref-id  { color:#a89fff; font-size:1.1rem; font-weight:700; letter-spacing:0.05em; }
.ref-lbl { color:#555; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; }

/* ── Sidebar section label ──────────────────────────────────────────────────── */
.sbar-lbl {
  font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
  color:#3a3a55 !important; text-transform:uppercase;
  padding:0 4px; margin:10px 0 4px;
}
</style>
"""


def inject_css():
    """Inject the global CSS into the Streamlit page. Call once in app.py."""
    st.markdown(_CSS, unsafe_allow_html=True)
