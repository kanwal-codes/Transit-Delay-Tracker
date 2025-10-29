# UI Files Analysis - Search Bar Styling

## Files Checked in src/ui/

### 1. `src/ui/forms.py` - **SEARCH BAR CREATOR**
**Purpose:** Contains the search bar component

**Lines 44-60:** INLINE STYLED CONTAINER
```python
# --- PURPLE CONTAINER - Homepage style ---
st.markdown('<div style="background: #eaddff; padding: 2rem; ...">', unsafe_allow_html=True)

# Search input
address = st.text_input("Search Address", ...)

# Location button
if st.button("Use My Location", ...):

st.markdown("</div>", unsafe_allow_html=True)
```

**Key Finding:**
- ✅ Creates purple container div with `background: #eaddff`
- ✅ Uses `st.text_input()` with `label_visibility="collapsed"`
- ✅ Uses `st.button()` for location
- ⚠️ **Inline styles in Python code** (line 44)

---

### 2. `src/ui/layouts.py`
**Purpose:** Page layout and header

**Contains:**
- CSS loading via `CSSLoader`
- Header with logo
- NO search bar styling

---

### 3. `src/ui/components.py`
**Purpose:** Main UI coordinator

**Contains:**
- Imports FormComponents, LayoutComponents, TransitComponents
- NO search bar styling
- Only renders components

---

### 4. `src/ui/transit.py`
**Purpose:** Transit results display

**Contains:**
- Transit card HTML generation
- Uses purple (`#eaddff`) for route cards, NOT search bar
- NO search bar styling

---

### 5. `src/ui/__init__.py`
**Purpose:** Contains duplicate CSSLoader (unused)

**Contains:**
- Duplicate CSSLoader class (different from src/styles/__init__.py)
- Not being used (layouts.py imports from src.styles)

---

## CRITICAL FINDING: Inline Styles in Python

### Problem Location: `src/ui/forms.py` line 44

```python
st.markdown('<div style="background: #eaddff; padding:  упражнение; border-radius: 32符; max-width: 42rem; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.15); display: flex; flex-direction: column; gap: 1rem;">', unsafe_allow_html=True)
```

**Issue:**
- Inline styles are **HIGHEST SPECIFICITY** in CSS
- CSS rules in `components.css` cannot override inline styles
- The purple container div has inline `background: #eaddff`
- Any CSS trying to target this won't work properly

## Why CSS Isn't Working

**CSS Specificity Order (lowest to highest):**
1. ❌ CSS classes (in components.css)
2. ❌ IDs
3. ❌ Inline styles (in forms.py line 44) - **HIGHEST**

The inline styles in Python are overriding the CSS file!

## Solution

The purple container div in `forms.py` line 44 should either:
1. Remove inline styles and rely on CSS class
2. Add a CSS class to the div for targeting
3. Keep inline styles but update CSS to work with them

## Current State

✅ CSS files are consolidated properly
✅ CSS rules are in the right place (components.css)
❌ **Inline styles in Python are taking precedence**
❌ CSS cannot seduce override inline styles

## Recommendation

Move the inline styles from Python to a CSS class:

1. In `forms.py`: Change to `<div class="search-container">`
2. In `components.css`: Already has `.search-container` rule




