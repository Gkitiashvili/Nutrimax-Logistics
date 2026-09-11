import streamlit as st

# გვერდის კონფიგურაცია
st.set_page_config(page_title="Logistics Analytics", layout="wide")

# CSS სტილები და დარქ მოუდის კონფიგურაცია
st.markdown("""
<style>
    /* დარქ მოუდის და ლაით მოუდის ცვლადები */
    :root {
        --bg-body: #f3f4f6;
        --bg-sidebar: #ffffff;
        --bg-card: #ffffff;
        --text-main: #1f2937;
        --text-muted: #6b7280;
        --border-color: #e5e7eb;
        --tab-active-bg: #e0e7ff;
        --tab-active-text: #4f46e5;
        --btn-danger: #ef4444;
    }

    /* Streamlit-ის ძირითადი ფონის მორგება */
    .stApp {
        background-color: var(--bg-body);
        color: var(--text-main);
    }

    /* ერთიანად წაშლის ღილაკი */
    .clear-all-btn {
        background-color: transparent;
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 5px 10px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        transition: 0.2s;
    }
    .clear-all-btn:hover {
        background-color: #ef4444;
        color: white;
    }

    /* ფილტრების ტეგები */
    .filter-tag {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ef4444;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# საპილოტე ინტერფეისი Streamlit-ში
st.sidebar.markdown("### ⚙️ ფილტრი & ძებნა")

if st.sidebar.button("✖ ყველას წაშლა", key="clear_all"):
    st.success("ფილტრები წაიშალა!")

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="filter-tag">📍 საფრანგეთი → ფოთი</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="filter-tag">🏢 Caucasus Express</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="filter-tag">📦 თევზის საკვები</div>', unsafe_allow_html=True)

# მთავარი გვერდი
st.title("📊 ლოჯისტიკის ანალიტიკა")
st.info("სისტემა წარმატებით განახლდა და მუშაობს გამართულად!")
