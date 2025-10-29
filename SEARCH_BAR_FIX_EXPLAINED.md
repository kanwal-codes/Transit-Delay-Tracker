# Search Bar Issue - Root Cause & Solution

## The Problem

The search bar styling works perfectly in `homepage_streamlit.py` but not in `src/app.py`.

## Root Cause

**Streamlit wraps every component in multiple `<div>` elements**, breaking the container structure:

### How `homepage_streamlit.py` Works (✅ Perfect)
```python
components.html(html_content, height=2000)  # Embeds entire HTML
```
- Pure HTML/CSS inside an iframe
- No Streamlit wrapper divs
- CSS applies directly

### How `src/app.py` Works (❌ Broken)
```python
st.markdown('<div class="search-container">')
address = st.text_input(...)  # Wrapped in divs
st.button(...)                  # Wrapped in divs
st.markdown('</div>')
```

**Problem:** Each Streamlit component creates its own container:
```html
<div class="search-container">      ← Opens
  <div>                              ← Streamlit wrapper
    <stElementContainer>             ← Another wrapper
      <!-- Input here -->
    </stElementContainer>
  </div>
  <div>                              ← Streamlit wrapper
    <stButton>                       ← Another wrapper
      <!-- Button here -->
    </stButton>
  </div>
</div>                               ← Closes
```

The components are INSIDE the container, but wrapped in layers of divs that:
1. Add borders/padding/margin
2. Break flexbox layout
3. Interfere with styling

## Solution Applied

### 1. Fixed HTML Structure (`src/ui/forms.py`)
```python
# Wrap everything in a complete container
st.markdown("""
<div class="search-container">
<div style="width: 100%;">
""", unsafe_allow_html=True)

# Now the elements are wrapped together
address = st.text_input(...)
st.button(...)

st.markdown("</div></div>")
```

### 2. Enhanced CSS Specificity (`src/styles/components.css`)
Added aggressive targeting of all possible wrappers:
```css
/* Remove borders from everything inside */
.search-container div {
    border: none !important;
    box-shadow: none !important;
}

/* Target Streamlit-specific containers */
.stApp div.stElementContainer:has(.search-container),
.block-container:has(.search-container) {
    border: none !important;
    background: none !important;
}
```

## Why This Works

1. **Proper nesting:** Elements are inside the container div
2. **Universal selectors:** CSS targets all nested divs
3. **!important flags:** Override Streamlit's defaults
4. **Has selectors:** Target parents of search-container

## Test It

Visit: **http://localhost:8501**

You should now see:
- ✅ Purple container (#eaddff) with padding
- ✅ Rounded search input (16px border-radius)
- ✅ Gradient button
- ✅ NO purple borders
- ✅ Perfect vertical stacking

The same styling as `homepage_streamlit.py` but with **full Streamlit functionality**!




