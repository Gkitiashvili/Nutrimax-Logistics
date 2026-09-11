# ==========================================
# Logistics Analytics Platform - Production Ready
# ==========================================
# საჭირო ბიბლიოთეკები:
#   pip install streamlit pandas folium streamlit-folium geopy openpyxl plotly
# გაშვება:
#   streamlit run app.py
# ==========================================

import io
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import streamlit as st

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Logistics Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Logistics Analytics Platform v2.0"
    }
)

# ==========================================
# SESSION STATE
# ==========================================
if "cached_df" not in st.session_state:
    st.session_state.cached_df = None

if "cached_filename" not in st.session_state:
    st.session_state.cached_filename = None

# ==========================================
# GPS COORDINATES DATABASE
# ==========================================
KNOWN_COORDS = {
    "საფრანგეთი": [46.2276, 2.2137],
    "ესპანეთი": [40.4637, -3.7492],
    "იტალია": [41.8719, 12.5674],
    "ბულგარეთი": [42.7339, 25.4858],
    "მოლდოვა": [47.0105, 28.8638],
    "რუმინეთი": [45.9432, 24.9668],
    "თურქეთი": [38.9637, 35.2433],
    "საქართველო": [42.3154, 43.3569],
    "აზერბაიჯანი": [40.1431, 47.5769],
    "ყაზახეთი": [48.0196, 66.9237],
    "უზბეკეთი": [41.3775, 64.5853],
    "ტურქმენეთი": [38.9697, 59.5563],
    "ტაჯიკეთი": [38.8610, 71.2761],
    "ყირგიზეთი": [41.2044, 74.7661],
    "ნიდერლანდები": [52.1326, 5.2913],
    "გერმანია": [51.1657, 10.4515],
    "პოლონეთი": [51.9194, 19.1451],
    "უკრაინა": [48.3794, 31.1656],
    "იორდანია": [30.5852, 36.2384],
    "სირია": [34.8021, 38.9968],
    "ფოთი": [42.1461, 41.6719],
    "თბილისი": [41.7151, 44.8271],
    "ბაქო": [40.4093, 49.8671],
    "აქტაუ": [43.6481, 51.1722],
    "ალმატი": [43.2220, 76.8512],
    "ტაშკენტი": [41.2995, 69.2401],
    "ხუჯანდი": [40.2826, 69.6222],
    "ბიშკეკი": [42.8746, 74.5698],
    "დუშანბე": [38.5598, 68.7870],
    "სამარყანდი": [39.6542, 66.9597],
    "ამანი": [31.9454, 35.9284],
}

# ==========================================
# UNIFIED COLOR PALETTE
# ==========================================
bg_primary = "#ffffff"
bg_secondary = "#f6f8fa"
bg_tertiary = "#eaeef2"
text_primary = "#24292f"
text_secondary = "#57606a"
border_color = "#d0d7de"
accent_primary = "#0969da"
accent_secondary = "#54aeff"
card_shadow = "0 3px 12px rgba(0, 0, 0, 0.06)"

# ==========================================
# GLOBAL CSS STYLES
# ==========================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    html, body, [class*="css"] {{
        background-color: {bg_primary};
        color: {text_primary};
    }}
    
    .main {{
        background-color: {bg_primary};
    }}
    
    /* ============ HEADER ============ */
    .header-wrap {{
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #3b82f6 100%);
        border-radius: 16px;
        padding: 2rem 2rem;
        margin-bottom: 2rem;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .header-wrap::before {{
        content: "";
        position: absolute;
        right: -80px;
        top: -80px;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
    }}
    
    .main-title {{
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }}
    
    .sub-title {{
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.85);
        font-weight: 400;
        max-width: 100%;
        line-height: 1.5;
        position: relative;
        z-index: 1;
    }}
    
    /* ============ KPI CARDS ============ */
    .metric-card {{
        background: {bg_secondary};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: {card_shadow};
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--accent-color, {accent_primary});
    }}
    
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        border-color: var(--accent-color, {accent_primary});
    }}
    
    .metric-icon {{
        font-size: 1.6rem;
        margin-bottom: 0.6rem;
        display: block;
    }}
    
    .metric-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {text_primary};
    }}
    
    .metric-change {{
        font-size: 0.8rem;
        margin-top: 0.3rem;
        color: {text_secondary};
    }}
    
    /* ============ OFFER CARDS ============ */
    .offer-card {{
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.9rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .offer-card:hover {{
        transform: translateX(3px);
    }}
    
    .offer-icon {{
        font-size: 1.6rem;
        flex-shrink: 0;
    }}
    
    .best-price-card {{
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
    }}
    
    .fastest-card {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
    }}
    
    .best-overall-card {{
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
    }}
    
    /* ============ SECTION TITLES ============ */
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {text_primary};
        margin: 1.2rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid {border_color};
    }}
    
    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        border-bottom: 2px solid {border_color};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        white-space: pre-wrap;
        background-color: {bg_secondary};
        border-radius: 10px 10px 0 0;
        color: {text_secondary};
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0px 20px;
        border: 1px solid {border_color};
        border-bottom: none;
        transition: all 0.2s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        color: {accent_primary};
        background-color: {bg_tertiary};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {accent_primary}, {accent_secondary}) !important;
        color: #ffffff !important;
        border-color: {accent_primary} !important;
    }}
    
    /* ============ SIDEBAR ============ */
    [data-testid="stSidebar"] {{
        background-color: {bg_secondary};
        border-right: 1px solid {border_color};
    }}
    
    [data-testid="stSidebar"] h3 {{
        color: {text_primary};
        font-weight: 700;
    }}
    
    /* ============ NATIVE BUTTON STYLING ============ */
    .stButton > button {{
        background: {bg_secondary};
        color: {text_primary};
        border: 1px solid {border_color};
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        border-color: {accent_primary};
        color: {accent_primary};
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(9, 105, 218, 0.1);
    }}
    
    /* აუქმებს ცისფერ ოთხკუთხედს დაჭერისას */
    .stButton > button:focus:not(:active) {{
        outline: none !important;
        box-shadow: none !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
    }}

    .stButton > button:active {{
        outline: none !important;
        box-shadow: none !important;
    }}
    
    /* ============ EMPTY STATE ============ */
    .empty-state {{
        text-align: center;
        padding: 3rem 1.5rem;
        color: {text_secondary};
        background: {bg_secondary};
        border-radius: 16px;
        border: 2px dashed {border_color};
        margin: 2rem 0;
    }}
    
    .empty-state-icon {{
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }}
    
    .empty-state-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {text_primary};
        margin: 0.5rem 0;
    }}
    
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GEOLOCATOR SETUP
# ==========================================
@st.cache_resource
def get_geolocator():
    geolocator = Nominatim(user_agent="logistics_v2_prod")
    return RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=2.0)

@st.cache_data(ttl=3600, show_spinner=False)
def get_coordinates(location_name):
    if not location_name or pd.isna(location_name):
        return None
    clean_name = str(location_name).strip().lower()
    if not clean_name:
        return None

    for key, coords in KNOWN_COORDS.items():
        if key.lower() in clean_name or clean_name in key.lower():
            return coords

    try:
        geocode = get_geolocator()
        location = geocode(location_name, timeout=6)
        if location:
            return [location.latitude, location.longitude]
    except Exception:
        pass
    return None

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def clean_numeric_series(series):
    return pd.to_numeric(
        series.astype(str).str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )

def find_col(columns, *keywords, exclude=None):
    exclude = exclude or []
    for col in columns:
        if any(kw in col for kw in keywords) and not any(ex in col for ex in exclude):
            return col
    return None

# ==========================================
# HEADER SECTION
# ==========================================
st.markdown("""
    <div class="header-wrap">
        <div class="main-title">🚚 ლოჯისტიკის ანალიტიკა</div>
        <div class="sub-title">Excel ფაილი → ანალიზი → გადაწყვეტილებები</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# FILE UPLOAD SECTION
# ==========================================
uploaded_file = st.file_uploader("📂 ატვირთეთ Excel ფაილი", type=["xlsx", "xls"], key="file_upload")

if uploaded_file is None:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-title">დაიწყეთ მონაცემების ანალიზი</div>
            <div style="margin-top: 1rem; line-height: 1.6; color: #8b949e;">
                ატვირთეთ Excel ფაილი სვეტებით:<br>
                <strong>სატრანსპორტო კომპანია</strong> • <strong>მარშრუტი</strong> • <strong>ღირებულება</strong> • <strong>ტრანზიტი</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ==========================================
# LOAD AND PROCESS FILE
# ==========================================
file_name = uploaded_file.name if uploaded_file else None

if st.session_state.cached_filename != file_name:
    try:
        raw_df = pd.read_excel(uploaded_file, header=None)
    except Exception as e:
        st.error(f"❌ ფაილის წაკითხვა ვერ მოხერხდა: {e}")
        st.stop()

    header_idx = None
    target_keywords = ["სატრანსპორტო კომპანია", "მარშრუტი", "სულ ღირებულება", "ტრანზიტი", "პროდუქტი"]

    for idx, row in raw_df.iterrows():
        row_str = " ".join(row.dropna().astype(str).values)
        matches = sum(1 for kw in target_keywords if kw in row_str)
        if matches >= 2:
            header_idx = idx
            break

    try:
        if header_idx is not None:
            df = pd.read_excel(uploaded_file, header=header_idx)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ ფორმატირება ვერ მოხერხდა: {e}")
        st.stop()

    df.columns = [str(col).strip() for col in df.columns]
    df = df.dropna(how="all").dropna(how="all", axis=1)

    if df.empty:
        st.error("❌ ფაილი ცარიელია ან მონაცემები ვერ მოიძებნა")
        st.stop()

    carrier_col = find_col(df.columns, "სატრანსპორტო კომპანია", "კომპანია", exclude=["ნუტრიმაქსი"])
    product_col = find_col(df.columns, "პროდუქტი")
    route_col = find_col(df.columns, "მარშრუტი")
    transit_countries_col = find_col(df.columns, "ტრანზიტული")
    price_col = find_col(df.columns, "სულ ღირებულება", "ღირებულება", "ფასი")
    transit_col = find_col(df.columns, "ტრანზიტი", "დღე")
    origin_col = find_col(df.columns, "საწყისი")
    dest_col = find_col(df.columns, "საბოლოო")

    df["clean_price"] = clean_numeric_series(df[price_col]) if price_col else None
    df["clean_transit"] = clean_numeric_series(df[transit_col]) if transit_col else None

    if carrier_col:
        df = df[df[carrier_col].notna() & ~df[carrier_col].astype(str).str.contains("სატრანსპორტო კომპანია", case=False)]

    if df.empty:
        st.error("❌ ფილტრაციის შემდეგ მონაცემები ვერ მოიძებნა")
        st.stop()

    st.session_state.cached_df = df
    st.session_state.cached_filename = file_name
else:
    df = st.session_state.cached_df
    carrier_col = find_col(df.columns, "სატრანსპორტო კომპანია", "კომპანია", exclude=["ნუტრიმაქსი"])
    product_col = find_col(df.columns, "პროდუქტი")
    route_col = find_col(df.columns, "მარშრუტი")
    transit_countries_col = find_col(df.columns, "ტრანზიტული")
    price_col = find_col(df.columns, "სულ ღირებულება", "ღირებულება", "ფასი")
    transit_col = find_col(df.columns, "ტრანზიტი", "დღე")
    origin_col = find_col(df.columns, "საწყისი")
    dest_col = find_col(df.columns, "საბოლოო")

# ==========================================
# SIDEBAR FILTERS
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ ფილტრი & ძებნა")
    
    filtered_df = df.copy()

    if route_col and not df[route_col].dropna().empty:
        routes = sorted(df[route_col].dropna().astype(str).unique().tolist())
        sel_routes = st.multiselect("📍 მარშრუტი", routes, default=[], key="route_filter")
        if sel_routes:
            filtered_df = filtered_df[filtered_df[route_col].astype(str).isin(sel_routes)]

    if carrier_col and not df[carrier_col].dropna().empty:
        carriers = sorted(df[carrier_col].dropna().astype(str).unique().tolist())
        sel_carriers = st.multiselect("🏢 კომპანია", carriers, default=[], key="carrier_filter")
        if sel_carriers:
            filtered_df = filtered_df[filtered_df[carrier_col].astype(str).isin(sel_carriers)]

    if product_col and not df[product_col].dropna().empty:
        products = sorted(df[product_col].dropna().astype(str).unique().tolist())
        sel_products = st.multiselect("📦 პროდუქტი", products, default=[], key="product_filter")
        if sel_products:
            filtered_df = filtered_df[filtered_df[product_col].astype(str).isin(sel_products)]

    st.divider()

    if price_col and df["clean_price"].notna().any():
        p_min, p_max = float(df["clean_price"].min()), float(df["clean_price"].max())
        if p_min < p_max:
            sel_price = st.slider("💰 ფასი ($)", p_min, p_max, (p_min, p_max), key="price_filter")
            filtered_df = filtered_df[
                filtered_df["clean_price"].between(sel_price[0], sel_price[1]) | filtered_df["clean_price"].isna()
            ]

    if transit_col and df["clean_transit"].notna().any():
        t_min, t_max = float(df["clean_transit"].min()), float(df["clean_transit"].max())
        if t_min < t_max:
            sel_transit = st.slider("⏱️ ტრანზიტი (დღე)", t_min, t_max, (t_min, t_max), key="transit_filter")
            filtered_df = filtered_df[
                filtered_df["clean_transit"].between(sel_transit[0], sel_transit[1]) | filtered_df["clean_transit"].isna()
            ]

    st.divider()

    search_term = st.text_input("🔎 ძებნა", placeholder="რომელიმე სვეტში...", key="global_search")
    if search_term:
        mask = filtered_df.apply(lambda r: search_term.lower() in " ".join(r.astype(str)).lower(), axis=1)
        filtered_df = filtered_df[mask]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 გასუფთავება", use_container_width=True):
            for key in ["route_filter", "carrier_filter", "product_filter", "global_search"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    with col2:
        st.metric("შედეგი", f"{len(filtered_df)}/{len(df)}")

if filtered_df.empty:
    st.warning("⚠️ არჩეული ფილტრებით შედეგი ვერ მოიძებნა")
    st.stop()

# ==========================================
# KPI METRICS
# ==========================================
min_p_val = filtered_df["clean_price"].min()
avg_p_val = filtered_df["clean_price"].mean()
max_p_val = filtered_df["clean_price"].max()
avg_t_val = filtered_df["clean_transit"].mean()
min_t_val = filtered_df["clean_transit"].min()

kpi_colors = ["#2563eb", "#7c3aed", "#059669", "#0891b2", "#ea580c"]

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
        <div class="metric-card" style="--accent-color: {kpi_colors[0]};">
            <span class="metric-icon">📦</span>
            <div class="metric-label">შეთავაზებები</div>
            <div class="metric-value">{len(filtered_df)}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    unique_carriers = filtered_df[carrier_col].nunique() if carrier_col else 0
    st.markdown(f"""
        <div class="metric-card" style="--accent-color: {kpi_colors[1]};">
            <span class="metric-icon">🏢</span>
            <div class="metric-label">კომპანიები</div>
            <div class="metric-value">{unique_carriers}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    p_text = f"${min_p_val:,.0f}" if pd.notna(min_p_val) else "—"
    st.markdown(f"""
        <div class="metric-card" style="--accent-color: {kpi_colors[2]};">
            <span class="metric-icon">💵</span>
            <div class="metric-label">მინ. ფასი</div>
            <div class="metric-value">{p_text}</div>
            <div class="metric-change">საშ. ${avg_p_val:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    avg_p_text = f"${avg_p_val:,.0f}" if pd.notna(avg_p_val) else "—"
    st.markdown(f"""
        <div class="metric-card" style="--accent-color: {kpi_colors[3]};">
            <span class="metric-icon">📊</span>
            <div class="metric-label">საშუალო ფასი</div>
            <div class="metric-value">{avg_p_text}</div>
            <div class="metric-change">მაქს. ${max_p_val:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi5:
    t_text = f"{avg_t_val:.1f}" if pd.notna(avg_t_val) else "—"
    st.markdown(f"""
        <div class="metric-card" style="--accent-color: {kpi_colors[4]};">
            <span class="metric-icon">⏱️</span>
            <div class="metric-label">საშუალო ტრანზიტი</div>
            <div class="metric-value">{t_text} დღე</div>
            <div class="metric-change">მინ. {min_t_val:.0f} დღე</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BEST OFFERS
# ==========================================
st.markdown('<div class="section-title">🏆 საუკეთესო შეთავაზებები</div>', unsafe_allow_html=True)

b1, b2, b3 = st.columns(3)

with b1:
    if not filtered_df["clean_price"].dropna().empty:
        best_price_row = filtered_df.loc[filtered_df["clean_price"].idxmin()]
        st.markdown(f"""
            <div class="offer-card best-price-card">
                <div class="offer-icon">🏆</div>
                <div>
                    <b>ყველაზე იაფი</b><br>
                    <strong>${best_price_row.get("clean_price", 0):,.0f}</strong> — {best_price_row.get(carrier_col, "N/A")}
                </div>
            </div>
        """, unsafe_allow_html=True)

with b2:
    if not filtered_df["clean_transit"].dropna().empty:
        fastest_row = filtered_df.loc[filtered_df["clean_transit"].idxmin()]
        st.markdown(f"""
            <div class="offer-card fastest-card">
                <div class="offer-icon">⚡</div>
                <div>
                    <b>ყველაზე სწრაფი</b><br>
                    <strong>{fastest_row.get("clean_transit", 0):.0f} დღე</strong> — {fastest_row.get(carrier_col, "N/A")}
                </div>
            </div>
        """, unsafe_allow_html=True)

with b3:
    if not filtered_df["clean_price"].dropna().empty and not filtered_df["clean_transit"].dropna().empty:
        norm_df = filtered_df.dropna(subset=["clean_price", "clean_transit"]).copy()
        if not norm_df.empty:
            p_range = norm_df["clean_price"].max() - norm_df["clean_price"].min()
            t_range = norm_df["clean_transit"].max() - norm_df["clean_transit"].min()
            norm_df["score"] = (
                (norm_df["clean_price"] - norm_df["clean_price"].min()) / p_range if p_range else 0
            ) + (
                (norm_df["clean_transit"] - norm_df["clean_transit"].min()) / t_range if t_range else 0
            )
            best_overall = norm_df.loc[norm_df["score"].idxmin()]
            st.markdown(f"""
                <div class="offer-card best-overall-card">
                    <div class="offer-icon">⭐</div>
                    <div>
                        <b>საუკეთესო ბალანსი</b><br>
                        <strong>${best_overall.get("clean_price", 0):,.0f}</strong>, {best_overall.get("clean_transit", 0):.0f}დღე
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📋 ცხრილი", "📊 გრაფიკი", "🗺️ რუკა"])

with tab1:
    st.markdown('<div class="section-title">📋 დეტალური შედარება</div>', unsafe_allow_html=True)

    sort_options = {"დახმარება": None}
    if price_col:
        sort_options["ფასი ↑"] = ("clean_price", True)
        sort_options["ფასი ↓"] = ("clean_price", False)
    if transit_col:
        sort_options["დრო ↑"] = ("clean_transit", True)
        sort_options["დრო ↓"] = ("clean_transit", False)

    sort_choice = st.selectbox("დახმარება", list(sort_options.keys()), label_visibility="collapsed")
    display_df = filtered_df.drop(columns=["clean_price", "clean_transit"], errors="ignore").copy()

    if sort_options[sort_choice]:
        sort_col, ascending = sort_options[sort_choice]
        display_df = display_df.loc[filtered_df.sort_values(sort_col, ascending=ascending, na_position="last").index]

    st.dataframe(display_df, use_container_width=True, height=420)

    export_buffer = io.BytesIO()
    with pd.ExcelWriter(export_buffer, engine="openpyxl") as writer:
        display_df.to_excel(writer, index=False, sheet_name="Logistics")
    st.download_button(
        label="⬇️ ჩამოტვირთვა",
        data=export_buffer.getvalue(),
        file_name="logistics_comparison.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False
    )

with tab2:
    st.markdown('<div class="section-title">📊 ვიზუალური ანალიტიკა</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)

    with c1:
        if carrier_col and not filtered_df["clean_price"].dropna().empty:
            st.markdown("**💰 ფასების შედარება**")
            chart_df = (
                filtered_df[[carrier_col, "clean_price"]]
                .dropna()
                .groupby(carrier_col, as_index=False)["clean_price"].mean()
                .sort_values("clean_price")
            )
            if PLOTLY_AVAILABLE:
                fig = px.bar(
                    chart_df, x="clean_price", y=carrier_col, orientation="h",
                    text=chart_df["clean_price"].map(lambda v: f"${v:,.0f}"),
                    color="clean_price", color_continuous_scale="Blues",
                )
                fig.update_layout(
                    showlegend=False, coloraxis_showscale=False,
                    xaxis_title="ფასი ($)", yaxis_title="",
                    template="plotly_white",
                    margin=dict(l=0, r=0, t=0, b=0), height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

    with c2:
        if carrier_col and not filtered_df["clean_transit"].dropna().empty:
            st.markdown("**⏱️ ტრანზიტის დრო**")
            chart_df_t = (
                filtered_df[[carrier_col, "clean_transit"]]
                .dropna()
                .groupby(carrier_col, as_index=False)["clean_transit"].mean()
                .sort_values("clean_transit")
            )
            if PLOTLY_AVAILABLE:
                fig2 = px.bar(
                    chart_df_t, x="clean_transit", y=carrier_col, orientation="h",
                    text=chart_df_t["clean_transit"].map(lambda v: f"{v:.0f} დღე"),
                    color="clean_transit", color_continuous_scale="Oranges",
                )
                fig2.update_layout(
                    showlegend=False, coloraxis_showscale=False,
                    xaxis_title="დღე", yaxis_title="",
                    template="plotly_white",
                    margin=dict(l=0, r=0, t=0, b=0), height=350,
                )
                st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">🗺️ ინტერაქტიული რუკა</div>', unsafe_allow_html=True)

    map_cols = st.columns([1, 1, 1])
    with map_cols[0]:
        tile_choice = st.radio("რუკა:", ["ქუჩა", "სატელიტი"], horizontal=True, label_visibility="collapsed")
    
    tile_map = {
        "ქუჩა": "OpenStreetMap",
        "სატელიტი": "Esri.WorldImagery"
    }

    m = folium.Map(location=[45.0, 35.0], zoom_start=4, tiles=tile_map[tile_choice])
    colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#ea580c", "#0891b2", "#4f46e5", "#db2777"]
    cluster = MarkerCluster(name="წერტილები").add_to(m)

    all_bounds = []
    carrier_color_map = {}
    drawn_routes = 0
    unmatched = set()

    for _, row in filtered_df.iterrows():
        route_points = []

        if route_col and pd.notna(row.get(route_col)):
            raw_route = str(row[route_col])
            raw_points = [p.strip() for p in raw_route.replace("/", "->").replace("➔", "->").split("->") if p.strip()]
            route_points.extend(raw_points)
        elif transit_countries_col and pd.notna(row.get(transit_countries_col)):
            if origin_col and pd.notna(row.get(origin_col)):
                route_points.append(str(row[origin_col]).strip())
            t_countries = [p.strip() for p in str(row[transit_countries_col]).replace("/", "->").split("->") if p.strip()]
            route_points.extend(t_countries)
            if dest_col and pd.notna(row.get(dest_col)):
                route_points.append(str(row[dest_col]).strip())

        path_coords = []
        for pt in route_points:
            coord = get_coordinates(pt)
            if coord:
                path_coords.append((pt, coord))
            else:
                unmatched.add(pt)

        if len(path_coords) >= 2:
            carrier = row.get(carrier_col, "N/A") if carrier_col else "N/A"
            if carrier not in carrier_color_map:
                carrier_color_map[carrier] = colors[len(carrier_color_map) % len(colors)]
            route_color = carrier_color_map[carrier]

            coords_only = [pt[1] for pt in path_coords]
            all_bounds.extend(coords_only)

            folium.PolyLine(
                coords_only, color=route_color, weight=3, opacity=0.8,
                tooltip=f"{carrier}",
            ).add_to(m)

            for idx, (pt_name, coord) in enumerate(path_coords):
                if idx == 0:
                    icon = folium.Icon(color="green", icon="play", prefix="fa")
                elif idx == len(path_coords) - 1:
                    icon = folium.Icon(color="red", icon="flag", prefix="fa")
                else:
                    icon = folium.Icon(color="orange", icon="circle", prefix="fa")
                folium.Marker(location=coord, icon=icon).add_to(cluster)

            drawn_routes += 1

    if all_bounds:
        m.fit_bounds([[min(b[0] for b in all_bounds), min(b[1] for b in all_bounds)],
                      [max(b[0] for b in all_bounds), max(b[1] for b in all_bounds)]])

    if carrier_color_map:
        legend_items = "".join(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            f'<span style="width:10px;height:10px;border-radius:50%;background:{c};"></span>'
            f'<span style="font-size:0.85rem;">{name}</span></div>'
            for name, c in carrier_color_map.items()
        )
        legend_html = f"""
            <div style="position: fixed; bottom: 50px; left: 70px; z-index:9999;
                background: {bg_secondary}; padding: 12px 14px; border-radius: 10px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2); border: 1px solid {border_color};
                font-family: Inter, sans-serif; font-size: 0.85rem;">
                <div style="font-weight:700; margin-bottom:6px; color:{text_primary};">კომპანიები</div>
                {legend_items}
            </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=500, use_container_width=True)

    i1, i2 = st.columns([2, 1])
    with i1:
        st.caption(f"📍 {drawn_routes} მარშრუტი {len(filtered_df)}-დან")
    with i2:
        if unmatched:
            with st.expander(f"⚠️ {len(unmatched)} ლოკაცია"):
                st.caption(", ".join(sorted(list(unmatched))[:10]))

st.divider()
st.caption("🚀 Logistics Analytics v2.1 Pro")
