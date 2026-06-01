APP_CSS = """
<style>
:root {
    --bg: #070707;
    --panel: #111111;
    --panel-2: #171717;
    --text: #f7f7f7;
    --muted: #b7b7b7;
    --border: #2a2a2a;
    --soft: #dedede;

    --orange: #ff8a1f;
    --orange-hover: #ffa64d;
    --blue: #2f80ed;
    --blue-hover: #4f9cff;

    --danger: #ffb4ab;
    --warn: #ffe2a8;
    --ok: #c9f7d2;
}

/* Main app background */
html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Streamlit top header */
[data-testid="stHeader"] {
    background: rgba(7, 7, 7, 0.92) !important;
}

/* Main container */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0c0c0c !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

[data-testid="stSidebar"] .small-muted,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--soft) !important;
}

/* General readable text, but do NOT force every div globally */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}

p, li, label {
    color: var(--text) !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong {
    color: var(--text) !important;
}

/* Muted helper text */
.small-muted {
    color: var(--muted) !important;
    font-size: 0.88rem;
}

/* Hero section */
.hero {
    border: 1px solid var(--border);
    background: linear-gradient(135deg, #151515 0%, #0b0b0b 58%, #171717 100%);
    border-radius: 24px;
    padding: 30px;
    margin-bottom: 22px;
    box-shadow: 0 18px 50px rgba(0,0,0,0.35);
}

.hero-title {
    color: #ffffff !important;
    font-size: 2.35rem;
    font-weight: 850;
    letter-spacing: -0.04em;
    margin-bottom: 10px;
}

.hero-subtitle {
    color: #c7c7c7 !important;
    font-size: 1.03rem;
    line-height: 1.65;
    max-width: 980px;
}

/* Cards and panels */
.panel {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.22);
}

.panel,
.panel * {
    color: var(--text) !important;
}

.panel-compact {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 16px;
    padding: 13px 14px;
    margin-bottom: 10px;
}

.panel-compact,
.panel-compact * {
    color: var(--text) !important;
}

/* Metric cards */
.metric-card {
    border: 1px solid var(--border);
    background: var(--panel-2);
    border-radius: 18px;
    padding: 16px;
    min-height: 112px;
}

.metric-card * {
    color: var(--text) !important;
}

.metric-label {
    color: var(--muted) !important;
    font-size: 0.85rem;
    margin-bottom: 8px;
}

.metric-value {
    color: #ffffff !important;
    font-size: 1.7rem;
    font-weight: 850;
    letter-spacing: -0.03em;
}

.metric-note {
    color: var(--muted) !important;
    font-size: 0.82rem;
    margin-top: 8px;
}

/* Status pills */
.status-pill {
    display: inline-block;
    border: 1px solid var(--border);
    background: #0d0d0d;
    color: var(--text) !important;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.82rem;
    margin: 2px 4px 2px 0;
}

.pill-danger {
    border-color: #6a2a2a;
    color: var(--danger) !important;
}

.pill-warn {
    border-color: #67501d;
    color: var(--warn) !important;
}

.pill-ok {
    border-color: #1d5e30;
    color: var(--ok) !important;
}

/* Evidence blocks */
.evidence {
    border-left: 3px solid var(--blue);
    background: #101010;
    border-radius: 12px;
    padding: 12px 14px;
    margin: 9px 0;
    color: var(--text) !important;
}

.evidence b {
    color: #ffffff !important;
}

.evidence span,
.evidence p {
    color: var(--soft) !important;
}

/* MAIN STREAMLIT BUTTONS - orange, readable */
.stButton > button {
    background: var(--orange) !important;
    color: #0b0b0b !important;
    border: 1px solid var(--orange) !important;
    border-radius: 13px !important;
    font-weight: 850 !important;
    min-height: 44px !important;
    box-shadow: 0 8px 22px rgba(255, 138, 31, 0.18) !important;
}

.stButton > button:hover {
    background: var(--orange-hover) !important;
    color: #000000 !important;
    border-color: var(--orange-hover) !important;
}

.stButton > button:disabled,
.stButton > button[disabled] {
    background: #242424 !important;
    color: #777777 !important;
    border-color: #333333 !important;
    box-shadow: none !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #0b0b0b !important;
    font-weight: 850 !important;
}

.stButton > button:disabled p,
.stButton > button:disabled span,
.stButton > button:disabled div {
    color: #777777 !important;
}

/* DOWNLOAD BUTTONS - blue */
.stDownloadButton > button {
    background: var(--blue) !important;
    color: #ffffff !important;
    border: 1px solid var(--blue) !important;
    border-radius: 13px !important;
    font-weight: 850 !important;
    min-height: 44px !important;
    box-shadow: 0 8px 22px rgba(47, 128, 237, 0.18) !important;
}

.stDownloadButton > button:hover {
    background: var(--blue-hover) !important;
    color: #ffffff !important;
    border-color: var(--blue-hover) !important;
}

.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button div {
    color: #ffffff !important;
    font-weight: 850 !important;
}

/* FILE UPLOADER - dark box, blue upload button, readable text */
[data-testid="stFileUploader"] {
    color: var(--text) !important;
}

[data-testid="stFileUploader"] section {
    background: #111111 !important;
    border: 1px dashed #3a3a3a !important;
    border-radius: 16px !important;
}

[data-testid="stFileUploader"] section * {
    color: #e9e9e9 !important;
}

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label * {
    color: #ffffff !important;
}

[data-testid="stFileUploader"] small {
    color: #bdbdbd !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: #111111 !important;
    border: 1px dashed #3a3a3a !important;
    border-radius: 16px !important;
}

[data-testid="stFileUploaderDropzone"] * {
    color: #e9e9e9 !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: var(--blue) !important;
    color: #ffffff !important;
    border: 1px solid var(--blue) !important;
    border-radius: 12px !important;
    font-weight: 850 !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: var(--blue-hover) !important;
    color: #ffffff !important;
    border-color: var(--blue-hover) !important;
}

[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploaderDropzone"] button div {
    color: #ffffff !important;
    font-weight: 850 !important;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #101010 !important;
    color: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #888888 !important;
}

.stTextInput label,
.stTextArea label,
.stNumberInput label,
.stSlider label,
.stCheckbox label {
    color: #ffffff !important;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: #101010 !important;
    color: #ffffff !important;
    border-color: var(--border) !important;
    border-radius: 12px !important;
}

.stSelectbox *,
.stMultiSelect * {
    color: #ffffff !important;
}

/* Checkbox */
.stCheckbox label span {
    color: #ffffff !important;
}

/* Slider */
.stSlider * {
    color: #ffffff !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
}

/* Tabs - dark normal, orange selected */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background: #111111 !important;
    border-radius: 999px !important;
    border: 1px solid var(--border) !important;
    color: #ffffff !important;
    padding: 9px 16px !important;
    font-weight: 750 !important;
}

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div {
    color: #ffffff !important;
    font-weight: 750 !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--orange) !important;
    border-color: var(--orange) !important;
    color: #111111 !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] p,
.stTabs [data-baseweb="tab"][aria-selected="true"] span,
.stTabs [data-baseweb="tab"][aria-selected="true"] div {
    color: #111111 !important;
    font-weight: 850 !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: #111111 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
}

.streamlit-expanderHeader * {
    color: #ffffff !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: #111111 !important;
    color: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

[data-testid="stAlert"] * {
    color: #ffffff !important;
}

/* Code blocks */
code,
pre {
    color: #f7f7f7 !important;
    background: #111111 !important;
}

/* Horizontal line */
hr {
    border-color: var(--border) !important;
}

/* Links */
a {
    color: var(--blue-hover) !important;
}

/* Make captions readable */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #bdbdbd !important;
}

/* Hide Streamlit default menu/footer less aggressively */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
</style>
"""