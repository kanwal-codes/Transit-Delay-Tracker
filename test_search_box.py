"""
Test file: Multiple methods to create a purple box containing search bar + button
Run this with: streamlit run test_search_box.py
"""
import streamlit as st

st.title("🧪 Search Box Test - Different Methods")

method = st.selectbox("Select Method:", [
    "Method 1: st.columns inside st.container with wrapper div",
    "Method 2: st.columns with CSS targeting data-testid",
    "Method 3: HTML div wrapper around st.columns",
    "Method 4: CSS background on horizontal block",
    "Method 5: st.container with inline style",
    "Method 6: Pure CSS targeting parent container",
])

st.markdown("---")

if method == "Method 1: st.columns inside st.container with wrapper div":
    st.markdown('<div style="background:#eaddff;padding:2rem;border-radius:28px;max-width:42rem;margin:0 auto;">', unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
        with col2:
            st.button("🔍", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif method == "Method 2: st.columns with CSS targeting data-testid":
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        background: #eaddff !important;
        padding: 2rem !important;
        border-radius: 28px !important;
        max-width: 42rem !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        st.button("🔍", use_container_width=True)

elif method == "Method 3: HTML div wrapper around st.columns":
    st.markdown('<div class="purple-box" style="background:#eaddff;padding:2rem;border-radius:28px;max-width:42rem;margin:0 auto;">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        st.button("🔍", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif method == "Method 4: CSS background on horizontal block":
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        background: #eaddff !important;
        padding: 2rem !important;
        border-radius: 28px !important;
        max-width: 42rem !important;
        margin: 0 auto !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        st.button("🔍", use_container_width=True)

elif method == "Method 5: st.container with inline style":
    st.markdown("""
    <style>
    div[data-testid="stContainer"] {
        background: #eaddff !important;
        padding: 2rem !important;
        border-radius: 28px !important;
        max-width: 42rem !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
        with col2:
            st.button("🔍", use_container_width=True)

elif method == "Method 6: Pure CSS targeting parent container":
    st.markdown("""
    <style>
    /* Target all horizontal blocks on the page */
    .element-container:has(> div[data-testid="stHorizontalBlock"]) {
        background: #eaddff !important;
        padding: 2rem !important;
        border-radius: 28px !important;
        max-width: 42rem !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Search", placeholder="Type here...", label_visibility="collapsed")
    with col2:
        st.button("🔍", use_container_width=True)

st.markdown("---")
st.markdown("**Check if the purple box contains both the search bar and button!**")



