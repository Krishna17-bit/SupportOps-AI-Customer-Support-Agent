APP_CSS = """
<style>
:root {
    --bg: #f8fafc;
    --panel: #ffffff;
    --panel-2: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
    --soft: #f1f5f9;

    --primary: #0f62fe;
    --primary-hover: #0043ce;
    --accent: #f97316;

    --danger-bg: #fee2e2;
    --danger-text: #991b1b;
    --warn-bg: #fef3c7;
    --warn-text: #92400e;
    --ok-bg: #d1fae5;
    --ok-text: #065f46;
}

/* Main app background overrides */
html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Streamlit top header */
[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.8) !important;
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
}

/* Main container padding */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px !important;
}

/* Sidebar styling overrides */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.02);
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

[data-testid="stSidebar"] .small-muted,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--muted) !important;
}

/* Custom Navigation Header in Sidebar */
.sidebar-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--primary) !important;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Headers & Markdown typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, li, label, [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
    line-height: 1.5;
}

.small-muted {
    color: var(--muted) !important;
    font-size: 0.85rem;
}

/* Custom premium card containers */
.panel {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
}

.panel:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

.panel-compact {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
}

/* Metric card stylings */
.metric-card {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 110px;
    transition: transform 0.15s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #cbd5e1;
}

.metric-label {
    color: var(--muted) !important;
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-value {
    color: var(--text) !important;
    font-size: 1.85rem;
    font-weight: 700;
    margin-top: 4px;
    letter-spacing: -0.03em;
}

.metric-note {
    color: var(--muted) !important;
    font-size: 0.8rem;
    margin-top: 6px;
}

/* Status and Risk badge pills */
.status-pill {
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--border);
    background: var(--soft);
    color: var(--text) !important;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 4px;
}

.pill-danger {
    background-color: var(--danger-bg) !important;
    color: var(--danger-text) !important;
    border-color: #fca5a5 !important;
}

.pill-warn {
    background-color: var(--warn-bg) !important;
    color: var(--warn-text) !important;
    border-color: #fde047 !important;
}

.pill-ok {
    background-color: var(--ok-bg) !important;
    color: var(--ok-text) !important;
    border-color: #86efac !important;
}

/* Outage or Incident warning banners */
.sla-warning-banner {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    color: #991b1b !important;
    font-weight: 500;
}

/* Evidence grounding block */
.evidence {
    border-left: 3px solid var(--primary);
    background: var(--soft);
    border-radius: 8px;
    padding: 12px 14px;
    margin: 8px 0;
    font-size: 0.9rem;
}

.evidence b {
    color: var(--text) !important;
    font-weight: 600;
}

.evidence span, .evidence p {
    color: var(--muted) !important;
}

/* Streamlit button customizations */
.stButton > button {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: 1px solid var(--primary) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    min-height: 40px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px 0 rgba(15, 98, 254, 0.1) !important;
}

.stButton > button:hover {
    background: var(--primary-hover) !important;
    border-color: var(--primary-hover) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
}

.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important;
}

/* Secondary Actions buttons */
div[data-testid="stFormSubmitButton"] button,
.stDownloadButton > button {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    min-height: 40px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}

div[data-testid="stFormSubmitButton"] button:hover,
.stDownloadButton > button:hover {
    background: var(--soft) !important;
    border-color: #cbd5e1 !important;
}

div[data-testid="stFormSubmitButton"] button p,
.stDownloadButton > button p,
div[data-testid="stFormSubmitButton"] button span,
.stDownloadButton > button span {
    color: var(--text) !important;
}

/* File Upload boxes */
[data-testid="stFileUploader"] section {
    background: #ffffff !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploader"] section * {
    color: var(--text) !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: 1px solid var(--primary) !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button span {
    color: #ffffff !important;
}

/* Input boxes & Text areas styling */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Tab menu */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 6px !important;
    border: none !important;
    color: var(--muted) !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab"] p {
    color: var(--muted) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--soft) !important;
    color: var(--primary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] p {
    color: var(--primary) !important;
    font-weight: 700 !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.streamlit-expanderHeader * {
    color: var(--text) !important;
}

/* Alert notifications overrides */
[data-testid="stAlert"] {
    background: #ffffff !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

[data-testid="stAlert"] * {
    color: var(--text) !important;
}

/* Hide streamlit default menu */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Custom Timeline / Activity Log */
.timeline-item {
    padding-left: 20px;
    border-left: 2px solid var(--border);
    position: relative;
    padding-bottom: 12px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 4px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--primary);
}

.timeline-time {
    font-size: 0.75rem;
    color: var(--muted);
    font-weight: 500;
}

.timeline-content {
    font-size: 0.875rem;
    margin-top: 2px;
}

/* Sticky top notification for Demo Mode */
.demo-banner {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af !important;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

</style>
"""