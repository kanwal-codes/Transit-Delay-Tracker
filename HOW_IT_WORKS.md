# How the App Works Now

## 🚀 When You Run `./dev.sh` or `streamlit run src/app.py`:

### 1. **Homepage Loads First** (`src/pages/1_Homepage.py`)
   - Displays the beautiful homepage design
   - **Auto-detects your location** using browser geolocation
   - **Auto-populates the search bar** with your detected address
   - Shows featured transit route cards

### 2. **When You Click the Search Bar or Start Typing**
   - The search input field is detected
   - A **"🚀 Search Transit Routes"** button appears
   - When clicked, navigates to the Transit page

### 3. **Transit Page Loads** (`src/pages/2_Transit.py`)
   - The main transit functionality runs
   - Shows real-time TTC transit information
   - Displays live bus locations on map
   - Finds nearby stops within 700m radius

## 🔄 Navigation Flow

```
App Start → Homepage (auto-detect location) → User clicks search → Transit App
```

## 📁 File Structure

```
src/
├── app.py                    # Entry point (redirects to Homepage)
└── pages/
    ├── 1_Homepage.py        # Landing page with location detection
    └── 2_Transit.py         # Main transit functionality
```

## ✨ Features

- ✅ Homepage loads first (always)
- ✅ Location auto-detected and search bar populated
- ✅ Beautiful Material Design 3 styling
- ✅ Seamless navigation to transit app
- ✅ All existing transit functionality preserved



