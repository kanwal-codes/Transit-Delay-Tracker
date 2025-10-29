# How to Use MapleMover

## Current Setup (Default)
```bash
./dev.sh
# or
streamlit run src/app.py
```
Runs the main app with full transit functionality.

## To Run Homepage Reference
```bash
streamlit run homepage_streamlit.py
```
Shows the static homepage design with location detection in search bar.

## To Make Homepage the Landing Page

### Option 1: Multi-Page Setup
1. Create pages directory:
   ```bash
   mkdir src/pages
   ```

2. Rename files:
   ```bash
   mv homepage_streamlit.py src/pages/1_🏠_Homepage.py
   mv src/app.py src/pages/2_🚌_Transit_Info.py
   ```

3. Create a minimal main app:
   ```python
   # Create new src/app.py
   import streamlit as st
   st.switch_page("pages/1_🏠_Homepage.py")
   ```

4. Run:
   ```bash
   streamlit run src/app.py
   ```

### Option 2: Replace Main App
Just rename:
```bash
mv homepage_streamlit.py src/app.py
mv src/app.py src/app_backup.py
```


