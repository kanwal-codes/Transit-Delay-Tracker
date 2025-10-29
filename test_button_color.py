"""
Test file: Multiple methods to change button color
Run this with: streamlit run test_button_color.py
"""
import streamlit as st

st.title("🎨 Button Color Test - Different Methods")

method = st.selectbox("Select Method:", [
    "Method 1: .stButton > button (basic)",
    "Method 2: button element selector",
    "Method 3: data-testid selector",
    "Method 4: attribute selector with !important",
    "Method 5: Multiple selectors",
    "Method 6: Direct element style",
    "Method 7: CSS in components.html",
    "Method 8: CSS with key inline style",
])

st.markdown("---")

if method == "Method 1: .stButton > button (basic)":
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("Test Button"):
        st.success("✅ Method 1 worked!")

elif method == "Method 2: button element selector":
    st.markdown("""
    <style>
    button {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("Test Button", key="btn2"):
        st.success("✅ Method 2 worked!")

elif method == "Method 3: data-testid selector":
    st.markdown("""
    <style>
    button[data-testid="baseButton-secondary"],
    div[data-testid="stButton"] > button {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("Test Button")

elif method == "Method 4: attribute selector with !important":
    st.markdown("""
    <style>
    button[kind="secondary"] {
        background-color: #6750a4 !important;
        color: white !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("Test Button", type="secondary")

elif method == "Method 5: Multiple selectors":
    st.markdown("""
    <style>
    .stButton > button,
    button.stButton-secondary,
    div[data-testid="stButton"] button {
        background-color: #6750a4 !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.5rem 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("Test Button")

elif method == "Method 6: Direct element style":
    st.markdown("""
    <style>
    * button {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("Test Button")

elif method == "Method 7: CSS in components.html":
    import streamlit.components.v1 as components
    components.html("""
    <style>
    button {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, height=0)
    st.button("Test Button")

elif method == "Method 8: CSS with key inline style":
    st.markdown("""
    <style>
    #test-btn {
        background-color: #6750a4 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.button("Test Button", key="test-btn")

st.markdown("---")
st.markdown("**Purple color should be #6750a4**")
st.markdown("**Expected: Button should be purple with white text**")

