# Debug Tools for Library Hold Agent

This directory contains debugging scripts to help diagnose login and hold placement issues.

## Available Debug Methods

### 1. Connect to Chrome Browser (Recommended for Manual Testing)

**File:** `debug_with_chrome.py`

This connects to a real Chrome browser with remote debugging, allowing you to:
- Manually interact with the browser while script runs
- Pause at key steps to inspect elements
- Use Chrome DevTools to debug
- Keep your Chrome extensions and profile

**Setup:**
```bash
# Step 1: Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug"

# Step 2: Install playwright in virtual environment (if not already)
source .venv/bin/activate
pip install playwright

# Step 3: Run the debug script
python debug_with_chrome.py
```

**Features:**
- Pauses at key steps for manual inspection
- Shows URL and page title after each action
- Allows manual login if automation fails
- Interactive prompts to continue/inspect

---

### 2. Playwright Inspector (GUI Debugger)

**File:** `debug_playwright_inspector.py`

Opens Playwright's built-in Inspector GUI for step-by-step debugging.

**Usage:**
```bash
source ./.venv/bin/activate

# Run with Inspector GUI
PWDEBUG=1 python debug_playwright_inspector.py
```

**Features:**
- Step through each action one at a time
- See screenshots and DOM at each step
- Record and generate test code
- Inspect element selectors in real-time

---

### 3. Visual Debug Mode (Existing)

**File:** `debug_hold_placement.py`

Simple visible browser with slow motion.

**Usage:**
```bash
source ./.venv/bin/activate
pip install playwright
playwright install chromium
python debug_hold_placement.py
```

---

## Common Issues & Solutions

### Issue: Login Fails

**Symptoms:**
- Script stays on login page after clicking submit
- Error: "Login failed - still on login page"

**Debug Steps:**

1. **Use Chrome hybrid mode** to manually try login:
   ```bash
   python debug_with_chrome.py
   ```
   
2. **Check credentials format:**
   - Card number: `21901028207102` (no spaces, dashes)
   - PIN: Try both `013175`
   
3. **Look for CAPTCHA:**
   - Some libraries detect automation and show CAPTCHA
   - Manual login in Chrome mode will reveal this
   
4. **Check for error messages:**
   - Red error text on page
   - Incorrect credentials message
   - Account locked/suspended message

### Issue: Hold Button Not Found

**Symptoms:**
- Script can't find "Place Hold" button
- Book page loads but no action taken

**Debug Steps:**

1. **Use Inspector mode** to see actual button text:
   ```bash
   PWDEBUG=1 python debug_playwright_inspector.py
   ```
   
2. **Check button selector:**
   - Button text might be "Add to Holds" not "Place Hold"
   - Button might be inside iframe
   - Button might be disabled (already on hold)

### Issue: Hold Placed but Not Visible on Website

**Symptoms:**
- Script returns success
- Hold saved in database
- Hold not visible when logging in manually

**Debug Steps:**

1. **Verify login actually succeeded:**
   - Use Chrome mode and manually check account dashboard
   - Look for username/account menu after login
   
2. **Check hold confirmation:**
   - Use slow motion to see if confirmation dialog appears
   - Check for success message in console logs

---

## Environment Setup

### Install Python Dependencies

```bash
# Activate virtual environment
cd /Users/joeli/PrjDev/public_library_agent/library_hold_agent
source .venv/bin/activate

# Install required packages
pip install playwright requests

# Install browser binaries
playwright install chromium
```

### Verify Installation

```bash
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed')"
```

---

## Credentials for Testing

Update these in the script files:
- Card Number: `21901028207102`
- PIN:  `013175`

**⚠️ Security Note:** Don't commit real credentials to GitHub!

---

## Tips for Successful Debugging

1. **Start with Chrome hybrid mode** - It's the easiest to see what's happening
2. **Check network tab** - Look for failed requests or 403/401 errors
3. **Inspect elements manually** - Right-click elements to verify selectors
4. **Compare manual vs automated** - Login manually first, then try automation
5. **Check timing** - Add longer waits if elements load slowly
6. **Look for JavaScript errors** - Open browser console (F12)

---

## Next Steps After Debugging

Once you identify the issue:

1. **Update selectors** in `services/library_service.py`
2. **Adjust timing** (add wait_for_timeout calls)
3. **Fix credentials format** if needed
4. **Add CAPTCHA handling** if detected
5. **Update error detection logic** to catch new error messages

---

## Example Debug Session

```bash
# Terminal 1: Start Chrome with debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug"

# Terminal 2: Run hybrid debug script
cd /Users/joeli/PrjDev/public_library_agent/library_hold_agent
source ../.venv/bin/activate
python debug_with_chrome.py
```

This will:
1. Connect to your Chrome browser
2. Navigate to login page and pause
3. Fill credentials and pause for inspection
4. Click login and show results
5. Navigate to book and try placing hold
6. Keep browser open for manual testing

You can take over at any point to manually complete the action!
