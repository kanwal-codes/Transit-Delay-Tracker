# CSS Loading Diagnostics

## Problem Analysis

CSS styling not applying to search bar - investigating loading mechanism.

## Current CSS Loading Mechanism

### Location: `src/styles/__init__.py`

```python
def load_all_styles(self):
    for css in ["main.css", "components.css", "themes.css", "transit.css"]:
        f = os.path.join(self.base, css)
        if os.path.exists(f):
            with open(fMarketing as fh:
                st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)
```

**Issue:** CSS is loaded via `st.markdown()` which injects `<style>` tags.

### CSS Load Order

1. `main.css` - Foundation styles
2. `components.css` - **SEARCH BAR STYLES**
3. `themes.css` - Variables
4. `transit.css` - Transit cards

## Where CSS is Applied

### Entry Point: `src/ui/layouts.py`

```python
def setup_page(self):
    st.set_page_config(...)
    self.css_loader.load_all_styles()  # Line 16
```

### Called From: `src/app.py`

```python
class MapleMoverApp:
    def run(self):
        self.ui.setup_page()  # This loads the CSS
        self.ui.render_header()
        address = self.ui.render_search_interface()
```

## Potential Issues

1. **CSS Specificity:** Streamlit's default CSS might have higher specificity
2. **Order of Injection:** CSS might be loaded before Streamlit's defaults
3. **Missing `!important`:** Some properties might not have enough weight
4. **Container Structure:** The search bar is wrapped in inline styled divs from `forms.py` line 44

## Search Bar Structure

### From `src/ui/forms.py` lines 44-60:

```html
<div style="background: #eaddff; padding: 2rem; ...">
  <st.text_input>  <!-- Search input -->
  <st.button>      <!-- Location button -->
</div>
```

The purple container is an inline div wrapping the search bar.

## CSS Rules in `components.css`

Line 51-59: Purple container styling
```css
.search-container,
div[style*="background: #eaddff"] {
    background: #eaddff !important;
    ...
}
```

Line 100-112: Input field styling
```css
.stTextInput > div > div > input {
    background: white !important;
    clip-path: polygon(...) !important;
    ...
}
```

Line 127-149: Button styling
```css
.stButton > button {
    background: #6750a4 !important;
    ...
}
```

## Diagnosis Steps

1. ✅ Verify CSS files exist
2. ✅ Check CSS syntax
3. ✅ Verify load order
4. ❓ Check browser DevTools - Is CSS loading?
5. ❓ Check CSS specificity - Are rules being overridden?
6. ❓ Check if `!important` is sufficient

## Recommendations

1. **Add `data-` attribute** to search container for more specific targeting
2. **Use `streamlit.components.v1.html()`** instead of `st.markdown()` for CSS injection
3. **Add debugging CSS** to verify CSS is loading
4. **Check Streamlit version** - CSS injection might have changed

## Next Steps

1. Run the app and inspect in DevTools
2. Verify which CSS rules are being applied
3. Check if Streamlit is overriding our CSS
4. Consider using a more forceful CSS injection method





