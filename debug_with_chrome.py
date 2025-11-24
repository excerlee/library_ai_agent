#!/usr/bin/env python3
"""
Debug script that connects to Chrome with remote debugging enabled.
This allows you to manually interact with the browser while the script runs.

Usage:
1. Start Chrome with remote debugging:
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome-debug"

2. Run this script:
   python debug_with_chrome.py
"""

import asyncio
from playwright.async_api import async_playwright

CARD_NUMBER = "21901028207102"
PIN = "013175"

async def debug_login_with_chrome():
    """Connect to existing Chrome browser for debugging"""
    async with async_playwright() as p:
        # Connect to Chrome with remote debugging enabled
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        # Get the default context (uses your actual Chrome profile)
        context = browser.contexts[0]
        page = await context.new_page()
        
        print("🌐 Connected to Chrome browser")
        print("You can now manually interact with the browser while the script runs\n")
        
        # Step 1: Navigate to login page
        print("1. Navigating to login page...")
        await page.goto("https://ccclib.bibliocommons.com/user/login")
        await page.wait_for_load_state('networkidle')
        
        print("\n⏸️  PAUSED - Please check the browser window")
        print("   You can manually inspect elements, check network tab, etc.")
        input("   Press Enter to continue with automated login...\n")
        
        # Step 2: Find and fill credentials
        print("2. Detecting login form selectors...")
        
        # Try multiple possible selectors for username
        username_selectors = ['#name', '#username', 'input[name="name"]', 'input[type="text"]', '[placeholder*="card" i]', '[placeholder*="library" i]']
        username_field = None
        for selector in username_selectors:
            try:
                username_field = await page.query_selector(selector)
                if username_field:
                    print(f"   ✅ Found username field: {selector}")
                    break
            except:
                continue
        
        # Try multiple possible selectors for PIN
        pin_selectors = ['#user_pin', '#pin', '#password', 'input[name="user_pin"]', 'input[type="password"]', '[placeholder*="pin" i]']
        pin_field = None
        for selector in pin_selectors:
            try:
                pin_field = await page.query_selector(selector)
                if pin_field:
                    print(f"   ✅ Found PIN field: {selector}")
                    break
            except:
                continue
        
        if not username_field or not pin_field:
            print("\n❌ Could not find login form fields!")
            print("   Please manually fill the form and login")
            input("   Press Enter when you've logged in manually...\n")
        else:
            print("3. Filling in card number...")
            await username_field.type(CARD_NUMBER, delay=100)
            
            print("4. Filling in PIN...")
            await pin_field.type(PIN, delay=100)
        
            print("\n⏸️  PAUSED - Check if credentials are filled correctly")
            input("   Press Enter to click login button...\n")
            
            # Step 3: Click login
            print("5. Clicking login button...")
            login_button_selectors = ['input[type="submit"]', 'button[type="submit"]', 'button:has-text("Sign In")', 'button:has-text("Log In")']
            for selector in login_button_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    print(f"   ✅ Clicked login button: {selector}")
                    break
                except:
                    continue
            
            await page.wait_for_timeout(2000)
        
        print(f"\n6. After login:")
        print(f"   URL: {page.url}")
        print(f"   Title: {await page.title()}")
        
        # Check if login was successful
        if "login" in page.url.lower():
            print("\n❌ Login failed - still on login page")
            
            # Check for error messages
            try:
                error_elem = await page.query_selector('.alert-error, .error-message, [class*="error"]')
                if error_elem:
                    error_text = await error_elem.inner_text()
                    print(f"   Error message: {error_text}")
            except:
                pass
                
            print("\n⏸️  PAUSED - You can now manually try to login")
            input("   Press Enter when done to continue...\n")
        else:
            print("\n✅ Login successful!")
            
            print("\n⏸️  PAUSED - Check your account dashboard")
            input("   Press Enter to test hold placement...\n")
            
            # Step 4: Navigate to a book
            print("\n7. Navigating to test book (Creepy Pair of Underwear)...")
            await page.goto("https://ccclib.bibliocommons.com/v2/record/S154C1881879")
            await page.wait_for_load_state('networkidle')
            
            print("\n⏸️  PAUSED - Check the book page")
            print("   Can you see a 'Place Hold' button?")
            input("   Press Enter to continue...\n")
            
            # Step 5: Try to place hold
            print("8. Looking for hold button...")
            hold_button = await page.query_selector('button:has-text("Place Hold")')
            if hold_button:
                print("   ✅ Found 'Place Hold' button")
                
                print("\n⏸️  PAUSED - Ready to click hold button")
                input("   Press Enter to click...\n")
                
                await hold_button.click()
                await page.wait_for_timeout(2000)
                
                print("\n⏸️  PAUSED - Check if hold was placed")
                print("   Did you see a confirmation message?")
                input("   Press Enter to finish...\n")
            else:
                print("   ❌ 'Place Hold' button not found")
                print("   This might mean:")
                print("   - Book is already on hold")
                print("   - Book is not available for hold")
                print("   - Not logged in properly")
        
        print("\n✨ Debug session complete")
        print("Keeping browser open for manual inspection...")
        input("Press Enter to close...\n")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_login_with_chrome())
