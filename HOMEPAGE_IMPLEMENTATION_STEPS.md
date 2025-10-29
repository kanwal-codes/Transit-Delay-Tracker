# Homepage Design Implementation - Step by Step Plan

## Current State
- Working Streamlit app with Material 3 transit cards
- Search functionality with geolocation
- Real-time bus locations on map
- Transit route cards displaying correctly

## Homepage Design to Implement
From `/Homepage` folder, the design shows:
1. **Header** - Sticky header with logo, title, tagline
2. **Hero Section** - Large search box with "Find Your Route" heading
3. **Featured Routes** - Grid of 3 sample route cards
4. **Footer** - Simple copyright text

---

## Implementation Steps

### **Step 1: Create Homepage Header Component** ✅ SAFE
**What to do:**
- Add new method `render_header()` to `src/ui/components.py`
- Create header with: Logo icon, "Maple Mover" title, "Canadian Transit" tagline
- Make it sticky at top

**Risk Level:** LOW - Just adding to UI, won't affect existing functionality

**Files to modify:**
- `src/ui/components.py` - Add header rendering method

**Test:** Check header appears at top

---

### **Step 2: Update Hero Search Section** ✅ SAFE
**What to do:**
- Modify existing search bar to match Homepage design
- Add large "Find Your Route" heading
- Add subtitle "Real-time transit information across Canada"
- Keep existing search functionality intact

**Risk Level:** LOW - Only cosmetic changes to UI

**Files to modify:**
- `src/ui/forms.py` - Update `render_search_interface()` method
- `src/ui/components.py` - Add hero section wrapper

**Test:** Search should work exactly as before with new styling

---

### **Step 3: Add Footer Component** ✅ SAFE
**What to do:**
- Create simple footer component
- Add at bottom of app
- Show copyright text

**Risk Level:** VERY LOW - Just adding at bottom

**Files to modify:**
- `src/ui/components.py` - Add footer rendering method
- `src/app.py` - Call footer at end of `run()` method

**Test:** Check footer appears at bottom

---

### **Step 4: Create Landing Page with Featured Routes** ⚠️ MODERATE
**What to do:**
- Detect when no location/search is active
- Show landing page with 3 sample route cards
- Use hardcoded sample data matching Homepage design
- When user searches, hide landing page and show results

**Risk Level:** MODERATE - Changes app flow logic

**Files to modify:**
- `src/app.py` - Add landing page logic in `run()` method
- `src/ui/transit.py` - Add method to render featured routes

**Test:** 
- App starts with landing page showing 3 cards
- Search functionality still works
- Clicking route doesn't break anything

---

### **Step 5: Add Back Navigation** ✅ SAFE (OPTIONAL)
**What to do:**
- Add "Back to Home" button when showing search results
- Allow user to return to landing page

**Risk Level:** LOW - Adds convenience feature

**Files to modify:**
- `src/ui/components.py` - Add back button component

**Test:** Can navigate back and forth

---

## Recommended Order of Implementation

### **Phase 1: Visual Components (No Logic Changes)**
1. ✅ Step 1 - Create Header
2. ✅ Step 2 - Update Hero Search Section  
3. ✅ Step 3 - Add Footer

**Goal:** App looks like Homepage design but functions exactly as before

---

### **Phase 2: Landing Page Logic**
4. ⚠️ Step 4 - Add Landing Page with Featured Routes
5. ✅ Step 5 - Add Back Navigation (Optional)

**Goal:** App shows landing page by default, search shows results

---

## What NOT to Touch (Keep Working)
- `src/api/` - All API logic
- `src/geocoding/` - Geolocation services
- Map rendering - Already working
- Transit card rendering - Already matching design
- Real-time bus location - Keep as is

---

## Testing Strategy
After each step:
1. Run the app
2. Search for an address
3. Verify routes appear
4. Check map displays
5. Verify cards look correct
6. If anything breaks, revert that step

---

## Rollback Plan
- Git commit after each successful step
- If Step 4 breaks, we can keep Steps 1-3 (which are safe)
- Can revert any step independently



