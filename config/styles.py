# config/styles.py

STYLES = """
<style>
/* ── Reset & global ── */
[data-testid="stAppViewContainer"] { background: #F7F8FC; }
[data-testid="stSidebar"]          { background: #0F0E1A !important; border-right: 1px solid #1a1929; }
[data-testid="stSidebar"] *        { color: #9090B0 !important; }
[data-testid="stSidebar"] .stButton > button { border-radius: 10px !important; font-size: 0.85rem !important; }
div[data-testid="stChatInput"] textarea { background: #fff !important; border-radius: 12px !important; }
[data-testid="stSidebar"] input { background: #1a1929 !important; color: #fff !important; border: 1px solid #2a2940 !important; border-radius: 8px !important; font-size: 0.82rem !important; }

/* ── Sidebar module buttons ── */
.mod-btn-active > button {
  background: #6C63FF !important; color: #fff !important;
  font-weight: 600 !important; border: none !important;
  text-align: left !important;
}
.mod-btn-inactive > button {
  background: transparent !important; color: #444 !important;
  border: none !important; text-align: left !important;
}
.mod-btn-inactive > button:hover { background: #1a1929 !important; color: #888 !important; }
.mod-btn-locked > button {
  background: transparent !important; color: #2a2940 !important;
  border: none !important; cursor: not-allowed !important;
}

/* ── Main content ── */
.block-container { padding: 2rem 3rem !important; max-width: 820px !important; margin: 0 auto; }

/* ── Step header ── */
.step-hdr { margin-bottom: 2rem; }
.step-hdr h1 { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; margin: 0 0 0.25rem; }
.step-hdr p  { color: #888; font-size: 0.88rem; margin: 0; }

/* ── Chat ── */
.chat-wrap { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1.5rem; }
.bubble-ai {
  background: #fff; border: 1px solid #EAEBF5; border-radius: 0 14px 14px 14px;
  padding: 0.75rem 1.1rem; max-width: 78%; font-size: 0.9rem; color: #1a1a2e;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04); line-height: 1.55;
}
.bubble-user {
  background: #6C63FF; border-radius: 14px 14px 0 14px;
  padding: 0.75rem 1.1rem; max-width: 78%; margin-left: auto;
  font-size: 0.9rem; color: #fff; line-height: 1.55;
}
.bubble-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em; margin-bottom: 4px; color: #aaa; }
.bubble-label.user { color: rgba(255,255,255,0.6); text-align: right; }

/* ── Summary table ── */
.sum-wrap { background: #fff; border: 1px solid #EAEBF5; border-radius: 14px; overflow: hidden; margin: 1.5rem 0; }
.sum-row  { display: flex; border-bottom: 1px solid #F0F0F8; }
.sum-row:last-child { border-bottom: none; }
.sum-key  { width: 38%; padding: 0.7rem 1.1rem; font-size: 0.75rem; font-weight: 700;
            color: #6C63FF; text-transform: uppercase; letter-spacing: 0.05em;
            background: #FAFAFE; border-right: 1px solid #F0F0F8; }
.sum-val  { flex: 1; padding: 0.7rem 1.1rem; font-size: 0.88rem; color: #1a1a2e; }

/* ── Ref ID ── */
.ref-wrap { background: #0F0E1A; border: 1px solid #6C63FF; border-radius: 12px;
            padding: 1rem 1.4rem; margin: 1.2rem 0; display: flex;
            justify-content: space-between; align-items: center; }
.ref-id   { font-family: monospace; font-size: 1.05rem; font-weight: 700; color: #a89fff; letter-spacing: 0.04em; }
.ref-meta { font-size: 0.72rem; color: #444; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Badges ── */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.73rem; font-weight: 700; }
.b-submitted { background: #EDE9FF; color: #4A42CC; }
.b-review    { background: #FFF3CD; color: #856404; }
.b-approved  { background: #D1F5EA; color: #0f6e56; }
.b-rejected  { background: #FDE8E8; color: #c0392b; }
.b-deferred  { background: #F0F0F0; color: #555; }

/* ── Coming soon ── */
.coming-wrap { text-align: center; padding: 5rem 2rem; color: #bbb; }
.coming-wrap h2 { font-size: 1.2rem; color: #ccc; margin: 0.5rem 0; }

/* ── M2 score bar ── */
.score-row { margin-bottom: 1rem; }
.score-row .s-label { display: flex; justify-content: space-between; font-size: 0.82rem; color: #444; margin-bottom: 4px; }
.score-bar-bg   { background: #F0F0F8; border-radius: 6px; height: 8px; }
.score-bar-fill { height: 8px; border-radius: 6px; transition: width 0.4s; }
</style>
"""
