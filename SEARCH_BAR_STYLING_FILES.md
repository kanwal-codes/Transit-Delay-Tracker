# Files That Style the Search Bar

## Primary CSS Files (loaded automatically)

1. **MapleMover/src/styles/main.css**
   - Lines 87-97: Input field styling
   - `.stTextInput > div > div > input` - border, border-radius, etc.
   - `.stTextInput > div > div > input:focus` - focus state
   - `.stButton > button` - button styling (lines 76-85)

2. **MapleMover/src/styles/components.css**
   - Lines 51-59: Purple container styling
   - Lines 86-96: Input field styling  
   - Lines 102-106: Focus state styling
   - Lines 109-112: Non-focused state styling
   - Lines 115-131: Button styling
   - Lines 133-137: Button hover state
   - Lines 140-150: GPS/location button styling

3. **MapleMover/src/styles/themes.css**
   - Does NOT style search bar

4. **MapleMover/src/styles/transit.css**
   - Does NOT style search bar (only suggestion buttons)

## Python Files with Inline Styles

5. **MapleMover/src/ui/forms.py**
   - Line 44: Purple container div with inline styles
   - Line 56: Spacing div
   - Lines 32-39: Page title with inline styles
   - Lines 64-70: Location label with inline styles

6. **MapleMover/src/ui/layouts.py**
   - Loads all CSS files via CSSLoader
   - Does NOT add extra search bar styling

## Summary

**Total files affecting search bar:**
- **2 CSS files**: `main.css`, `components.css`
- **1 Python file**: `forms.py` (inline styles for container)

**Load order:**
1. `main.css` 
2. `components.css` 
3. `themes.css`
4. `transit.css`
5. Inline styles in `forms.py`


