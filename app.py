import base64
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import metrics as m

# Edit this text if the team words its objective differently.
OBJECTIVE = ("We wanted to find out where litter and sorting mistakes still happen on campus and how serious they look in each place. "
             "We counted them ourselves, and we set what students told us in a 2025 survey next to what we saw in a one-week audit in 2026.")
ASSETS = Path(__file__).parent / "assets"
FONT = "Public Sans, Source Sans, sans-serif"

st.set_page_config(page_title="Green Grizzly campus waste audit", layout="wide")
st.markdown("""<style>
[data-testid="stMainBlockContainer"]{max-width:1160px;padding:72px 24px 48px}
[data-testid="stMarkdownContainer"] .gg-credit{font-size:15px;margin:0 0 16px}
[data-testid="stMarkdownContainer"] .gg-h1{font-size:clamp(32px,5vw,52px);line-height:1.1;margin:0 0 24px;font-weight:700;padding:0}
[data-testid="stMarkdownContainer"] .gg-h2{font-size:26px;line-height:1.2;margin:48px 0 16px;font-weight:700;padding:0}
[data-testid="stMarkdownContainer"] .gg-fig{font-size:clamp(72px,12vw,112px);line-height:1;font-weight:700;font-variant-numeric:tabular-nums;color:#963B2C;margin:0}
[data-testid="stMarkdownContainer"] .gg-label{font-size:22px;font-weight:600;margin:8px 0 12px}
[data-testid="stMarkdownContainer"] .gg-note{font-size:17px;max-width:34rem;margin:0 0 8px}
[data-testid="stMarkdownContainer"] .gg-rem{background:#E8F2DE;padding:12px 16px;border-radius:4px;font-weight:600;max-width:34rem;margin:16px 0 0}
.gg-img{margin:0}.gg-img img{display:block;width:auto;height:auto;max-width:100%;max-height:560px;border-radius:4px}
[data-testid="stMarkdownContainer"] .gg-cap{font-size:15px;margin:8px 0 0;max-width:34rem}
[data-testid="stMarkdownContainer"] .gg-date{display:inline-block;font-weight:700;background:#173B2A;color:#FAF8F3;padding:4px 8px;border-radius:4px;font-size:15px}
[data-testid="stMarkdownContainer"] .gg-src{border-top:2px solid #2D6A43;padding-top:12px}
[data-testid="stMarkdownContainer"] .gg-stat{font-size:22px;line-height:1.3;font-weight:600;margin:8px 0 0;font-variant-numeric:tabular-nums}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>""", unsafe_allow_html=True)

@st.cache_data
def load():
    return m.load_audit(), m.load_survey(), m.load_methods()

@st.cache_data
def figure(file, alt, caption):
    try:
        p = ASSETS / file
        w, h = Image.open(p).size
        b64 = base64.b64encode(p.read_bytes()).decode()
    except OSError:
        return ""
    return (f'<figure class="gg-img"><img src="data:image/jpeg;base64,{b64}" alt="{alt}" width="{w}" height="{h}" style="aspect-ratio:{w}/{h}">'
            f'<figcaption class="gg-cap">{caption}</figcaption></figure>')

audit, survey, meth = load()
LOCS = ["Soccer field", "Cafeteria", "Basketball hub", "All audited locations"]
SESS = ["All sessions", "Snack", "Lunch"]
NAMES = list(m.ZONES.values())
ORDER = {"Snack": 0, "Lunch": 1}
BG = {"G": "#DCEEDB", "Y": "#FFF0C2", "R": "#FCE2DB"}
FG = {"G": "#205C3B", "Y": "#6F4D00", "R": "#963B2C"}

def reset():
    st.session_state["loc"], st.session_state["sess"] = LOCS[0], SESS[0]

def style(fig):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT, size=15, color="#173B2A"))
    fig.update_xaxes(gridcolor="#D5E3C8", automargin=True); fig.update_yaxes(gridcolor="#D5E3C8", automargin=True)
    return fig

def note(text):
    st.markdown(f'<div class="gg-cap" style="max-width:46rem">{text}</div>', unsafe_allow_html=True)

def fmt(s):
    return "no observations for this selection" if s is None else f"{s[0]} of {s[1]}"

lr = survey[survey["question_id"] == "location"].set_index("category")
SN = int(lr.loc["Soccer field", "denominator"]); sf_n = int(lr.loc["Soccer field", "count"])
sf_lit = m.audit_share(audit, "litter", "Soccer field"); sf_bin = m.audit_share(audit, "bin", "Soccer field")
PERIOD = "28 September–2 October 2026"

# 1. Opening finding
st.markdown('<p class="gg-credit">Green Grizzly, the student eco-club research team, Colegio Interamericano</p>', unsafe_allow_html=True)
a, b = st.columns([6, 5], gap="large")
with a:
    st.markdown(f'<h1 class="gg-h1">The soccer field is still a litter hotspot.</h1>'
                f'<p class="gg-fig">{fmt(sf_lit)}</p><p class="gg-label">Soccer-field litter checks rated Red.</p>'
                f'<p class="gg-note">Red means 16 or more visible pieces, or a concentrated litter pile.</p>'
                f'<p class="gg-note">Audit period: {PERIOD}.</p>'
                f'<p class="gg-rem">Take your rubbish with you. Check the bin label before you leave.</p>', unsafe_allow_html=True)
with b:
    st.markdown(figure("soccer-field-2025-11-06.jpg",
                       "Wet artificial-turf soccer field with a few scattered pieces of litter on the turf, mostly near the lower edge, with a painted wall and trees behind.",
                       '<span class="gg-date">Soccer field · 6 November 2025</span><br>Photo from 2025, not from the audit week.'), unsafe_allow_html=True)

# 2. Earlier concern, later observation
st.markdown('<h2 class="gg-h2">Students named the field in 2025. The audit found it again in 2026.</h2>', unsafe_allow_html=True)
s1, s2 = st.columns(2, gap="large")
s1.markdown(f'<div class="gg-src"><span class="gg-date">October 2025 survey</span><p class="gg-stat">{sf_n} of {SN} respondents selected the soccer field as a place they usually saw trash.</p></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="gg-src"><span class="gg-date">September–October 2026 audit</span><p class="gg-stat">{fmt(sf_lit)} soccer-field litter checks were rated Red.</p></div>', unsafe_allow_html=True)
st.markdown('<p class="gg-note" style="margin-top:12px;max-width:none">Different measures, collected about a year apart. Both identify the field as a continuing concern.</p>', unsafe_allow_html=True)

# 3. Sorting
st.markdown('<h2 class="gg-h2">Sorting also needs attention.</h2>', unsafe_allow_html=True)
p1, p2, p3 = st.columns([4, 4, 5], gap="large")
p1.markdown(figure("organic-bin-2026-09-30.jpg",
                   "Looking down into a bin lined with a dark green bag. At the bottom are snack wrappers, a crumpled white tissue, a white cup and clear plastic.",
                   '<b>Organic bin (green bag)</b><br>Soccer field, snack period, 30 September 2026<br>Visible: snack wrappers, a crumpled tissue, a white cup and clear plastic.'), unsafe_allow_html=True)
p2.markdown(figure("recycling-bin-2026-09-28.jpg",
                   "Looking down into a bin lined with a white bag. At the bottom are brown and yellow wrappers, a bottle with a blue label, crumpled white paper with food stains and an orange item in clear plastic.",
                   '<b>Recycling bin (white bag)</b><br>Basketball hub, 28 September 2026, as identified by the team<br>Visible: brown and yellow wrappers, a bottle with a blue label, crumpled paper with food stains and an orange item in clear plastic.'), unsafe_allow_html=True)
with p3:
    st.markdown(f'<p class="gg-stat" style="margin-top:0">{fmt(sf_bin)} recycling and organic-bin checks were rated Yellow or Red.</p>'
                f'<p class="gg-note" style="margin-top:12px">At the soccer field, {PERIOD}. Auditors graded the worst-looking bin cluster in each location, so this describes those bins, not an average bin.</p>'
                f'<p class="gg-note">The photos are single examples. They do not show how often sorting mistakes happen.</p>', unsafe_allow_html=True)

# 4. Comparison (fixed: full audit week, no filters)
st.markdown('<h2 class="gg-h2">Where were the problems most frequent?</h2>', unsafe_allow_html=True)
note(f"Among the three audited locations, full audit week ({PERIOD}). These are repeated checks, not different bins.")
def compare(col, kind, title, color):
    vals = {z: m.audit_share(audit, kind, z) for z in NAMES}
    fig = go.Figure(go.Bar(y=["Soccer field", "Cafeteria", "Basketball hub"], orientation="h",
                           x=[vals[z][2] for z in ["Soccer field", "Cafeteria", "Basketball hub"]],
                           marker_color=[color, "#8C7B75", "#8C7B75"], textposition="outside",
                           text=[f"\u00a0{vals[z][0]} of {vals[z][1]} ({m.pct(vals[z])})" for z in ["Soccer field", "Cafeteria", "Basketball hub"]]))
    fig.update_yaxes(autorange="reversed", ticklabelstandoff=8)
    fig.update_xaxes(range=[0, 125], tickvals=[0, 50, 100], title="% of checks")
    fig.update_layout(title=title, margin=dict(l=8, r=8, t=48, b=8), height=290)
    with col:
        st.plotly_chart(style(fig), theme=None, config={'displayModeBar': False})
        with st.expander(f"Table for this chart: {title}"):
            st.dataframe(pd.DataFrame([{"Location": z, "Checks rated": vals[z][0], "Checks audited": vals[z][1], "Share of checks": f"{m.pct(vals[z])}"} for z in NAMES]), hide_index=True)
c1, c2 = st.columns(2, gap="large")
compare(c1, "litter", "Litter checks rated Red", "#963B2C")
compare(c2, "bin", "Bin checks rated Yellow or Red", "#6F4D00")
bh = (m.audit_share(audit, "litter", "Basketball hub"), m.audit_share(audit, "bin", "Basketball hub"))
note(f"The basketball hub had {bh[0][0]} Red litter checks but {fmt(bh[1])} bin checks rated Yellow or Red. Bin checks cover the recycling (white) and organic (green) bins.")

# 5. Detailed evidence
st.markdown('<h2 class="gg-h2">View the audit evidence</h2>', unsafe_allow_html=True)
with st.expander("Filters, full audit matrix, definitions, sources and data downloads"):
    note("Filters here change only the audit figures in this section. The headline findings above and the 2025 survey stay fixed.")
    loc = st.segmented_control("Location", LOCS, default=LOCS[0], key="loc") or LOCS[0]
    sess = st.segmented_control("Audit session", SESS, default=SESS[0], key="sess") or SESS[0]
    st.button("Reset filters", on_click=reset)
    zone = None if loc.startswith("All") else loc
    session = None if sess.startswith("All") else sess
    st.markdown(f"**Selected:** {loc}, {sess.lower()}. Litter checks rated Red: {fmt(m.audit_share(audit, 'litter', zone, session))}. "
                f"Bin checks rated Yellow or Red: {fmt(m.audit_share(audit, 'bin', zone, session))}.")
    st.subheader("Audit matrix")
    view = audit if not zone else audit[audit["zone_name"] == zone]
    if session:
        view = view[view["session"] == session]
    view = view.assign(col=view["zone_name"] + " | " + view["metric"])
    order = [f"{z} | {t}" for z in ([zone] if zone else NAMES) for t in m.METRICS]
    grid = view.pivot(index=["date", "weekday", "session"], columns="col", values="grade")[order].reset_index()
    grid = grid.sort_values(["date", "session"], key=lambda c: c.map(ORDER) if c.name == "session" else c)
    grid = grid.rename(columns={"date": "Date", "weekday": "Day", "session": "Session"})
    st.dataframe(grid.style.map(lambda v: f"background-color:{BG[v]};color:{FG[v]};font-weight:600;text-align:center" if v in BG else "", subset=order), hide_index=True)
    note("Rows run from Monday snack to Friday lunch. Friday was a half day. Each cell shows the grade letter.")
    st.subheader("Scoring definitions")
    st.markdown("| Grade | Recycling and organic-bin checks | Litter checks |\n|---|---|---|\n"
                f"| G | {meth['bin_rubric']['G']} | {meth['litter_rubric']['G']} |\n| Y | {meth['bin_rubric']['Y']} | {meth['litter_rubric']['Y']} |\n"
                f"| R | {meth['bin_rubric']['R']} | {meth['litter_rubric']['R']} |")
    note("The organic bin is a bin type. Green (G) is a grade. A Green grade does not mean zero litter or perfect sorting.")
    st.subheader("What students reported")
    lo = lr.drop(["everywhere", "Everywhere", "no"]).reset_index().sort_values("count")
    fig = go.Figure(go.Bar(x=lo["count"] / SN * 100, y=lo["category"], orientation="h", marker_color="#2D6A43",
                           text=[f"{c} of {SN} ({c / SN * 100:.1f}%)" for c in lo["count"]], textposition="outside"))
    fig.update_xaxes(range=[0, 135], tickvals=[0, 25, 50, 75, 100], title=f"% of {SN} respondents")
    fig.update_layout(title="Where students usually saw trash, October 2025", margin=dict(l=8, r=8, t=48, b=8), height=340)
    st.plotly_chart(style(fig), theme=None, config={'displayModeBar': False})
    note("Multiple selections were allowed, so bars do not add to 100%. Other entries kept in the data file: everywhere (3 respondents) and no (1). The basketball hub was not a survey option.")
    if st.toggle("Show the table for the survey chart", key="t_survey"):
        st.dataframe(lo[["category", "count", "denominator"]].rename(columns={"category": "Location option", "count": "Respondents", "denominator": "Total respondents"}), hide_index=True)
    st.subheader("Context from the auditors")
    st.markdown("These are auditor notes, not proven causes. Lunch soccer tournaments and student-council cleanup on the field affected lunch conditions. "
                "The cafeteria was all Green on Wednesday lunch when students left for a tournament. Green organic-bin grades often meant the bin was empty. "
                "Auditors sometimes found white bags in the trash bin and black bags in the recycling bin.")
    st.subheader("Why we did this research")
    st.write(OBJECTIVE)
    st.subheader("Sources and limitations")
    st.markdown(f"**Audit:** {meth['audit_period']}. Source: Audit records.pdf, pages 1-2.  \n**Survey:** {meth['survey_period']} Source: Survey responses.pdf, pages {', '.join(str(p) for p in sorted(set(survey['source_page'])))}.")
    st.markdown("\n".join(f"- {x}" for x in meth["limitations"]))
    note(f"Data version {meth['version']}, updated {meth['updated']}. The data are sanitized aggregates and grades, free to download without an account.")
    st.download_button("Download audit data (CSV)", audit.to_csv(index=False), "audit.csv", "text/csv")
    st.download_button("Download survey counts (CSV)", survey.to_csv(index=False), "survey_aggregates.csv", "text/csv")
