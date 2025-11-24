#!/usr/bin/env python3
"""
Test script for placing a hold on "Snow Thief" at Contra Costa Library.
This script demonstrates the complete flow of using the Library Hold Tracker API.

Usage:
    python test_snow_thief_hold.py <card_number> <pin>
    
Example:
    python test_snow_thief_hold.py "1234567890123" "1234"
"""

import asyncio
import sys
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
BOOK_LIST = [
    # "The Wonderful Things You Will Be",
    # "Dragons Love Tacos",
    # "The Day the Crayons Quit",
    # "Creepy Pair of Underwear!",
    # "The Bad Seed Presents: The Good, the Bad, and the Spooky",
    # "How to Catch a Turkey",
    # "The Leaf Thief",
    # "Creepy Crayon!",
    "The Smart Cookie",
    "Time For School, Little Blue Truck",
    "THE HUMBLE PIE",
    "HOW TO CATCH A TURKEY",
    "BLUEY'S NIGHT BEFORE CHRISTMAS",
    "THE LITTLEST YAK",
    "BALLOONS OVER BROADWAY",
    "CHRISTMAS AT HOGWARTS",
    "DON'T LET THE PIGEON DRIVE THE SLEIGH!",
    "HOW TO CATCH AN ELF",
    "HOW TO CATCH A REINDEER",
]

LIBRARY_NAME = "Contra Costa"

def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Make HTTP request to the API"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # HTTP errors (404, 500, etc.) - don't exit, let caller handle
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        raise  # Re-raise so search_for_book can catch it
    except requests.exceptions.RequestException as e:
        # Network errors - these are more serious
        print(f"❌ Network error: {e}")
        sys.exit(1)

def test_api_connection():
    """Test if the API is running"""
    print("🔍 Testing API connection...")
    result = make_request("GET", "/")
    print(f"✅ API is running: {result['message']}")
    return True

def create_test_user() -> Dict[str, Any]:
    """Create a test user for the hold"""
    print("👤 Creating test user...")
    user_data = {
        "username": "test_user_snow_thief"
    }
    
    try:
        user = make_request("POST", "/users/", user_data)
        print(f"✅ Created user: ID={user['id']}, Username={user['username']}")
        return user
    except:
        # User might already exist, try to get existing users
        print("⚠️  User creation failed, this might be expected if user already exists")
        # For demo purposes, we'll assume user ID 1 exists
        return {"id": 1, "username": "test_user_snow_thief"}


def search_for_book(title: str) -> Dict[str, Any]:
    """Search for a book in the Contra Costa Library catalog by title"""
    print(f"📚 Searching for '{title}' at {LIBRARY_NAME} Library...")
    search_data = {
        "query": title,
        "search_type": "title",
        "library": LIBRARY_NAME
    }

    try:
        results = make_request("POST", "/books/search", search_data)
        if not results or len(results) == 0:
            print(f"❌ No search results found for '{title}'")
            return None
        book = results[0]  # Take the first result (should be physical book)
        print(f"✅ Found book:")
        print(f"   Title: {book['title']}")
        print(f"   Author: {book['author']}")
        print(f"   Library Item ID: {book['library_item_id']}")
        print(f"   Availability: {book['availability']}")
        return book
    except (requests.exceptions.HTTPError, Exception) as e:
        # HTTP error (404, 500) or other error - continue with next book
        print(f"⚠️  Skipping '{title}' - book not found or search failed")
        return None

def place_hold(user_id: int, book: Dict[str, Any], card_number: str, pin: str) -> Dict[str, Any]:
    """Place a hold on the book"""
    print(f"📌 Placing hold on '{book['title']}' for user {user_id}...")
    
    hold_request = {
        "user_id": user_id,
        "title": book["title"],
        "author": book["author"],
        "isbn": book.get("isbn"),
        "library_name": book["library_name"],
        "library_item_id": book["library_item_id"],
        "library_card_number": card_number,
        "library_pin": pin
    }
    
    try:
        hold = make_request("POST", "/holds/place", hold_request)
        print(f"✅ Hold placed successfully:")
        print(f"   Hold ID: {hold['id']}")
        print(f"   Status: {hold['status']}")
        print(f"   Queue Position: {hold.get('queue_position', 'N/A')}")
        print(f"   Estimated Wait: {hold.get('estimated_wait_days', 'N/A')} days")
        print(f"   Last Checked: {hold['last_checked']}")
        return hold
    except Exception as e:
        print(f"❌ Failed to place hold: {e}")
        sys.exit(1)

def get_user_holds(user_id: int):
    """Retrieve all holds for the user"""
    print(f"📋 Retrieving all holds for user {user_id}...")
    
    holds = make_request("GET", f"/holds/{user_id}")
    
    if not holds:
        print("📝 No holds found for this user")
        return
        
    print(f"✅ Found {len(holds)} hold(s):")
    for i, hold in enumerate(holds, 1):
        print(f"   {i}. {hold['title']} ({hold['library_name']})")
        print(f"      Status: {hold['status']}")
        print(f"      Queue Position: {hold.get('queue_position', 'N/A')}")


def main():
    """Main test function for multiple books"""
    if len(sys.argv) != 3:
        print("❌ Usage: python test_snow_thief_hold.py <card_number> <pin>")
        print("Example: python test_snow_thief_hold.py '1234567890123' '1234'")
        sys.exit(1)
    card_number = sys.argv[1]
    pin = sys.argv[2]
    print("🚀 Starting Library Hold Test for Book List")
    print("=" * 50)
    # Step 1: Test API connection
    test_api_connection()
    print()
    # Step 2: Create test user
    user = create_test_user()
    print()
    # Step 3: Iterate through book list
    for title in BOOK_LIST:
        print("-" * 40)
        book = search_for_book(title)
        if not book:
            print(f"❌ Skipping '{title}' (not found)")
            continue
        hold = place_hold(user["id"], book, card_number, pin)
        print()
    # Step 4: Verify holds
    print("=" * 50)
    get_user_holds(user["id"])
    print()
    print("🎉 Test completed for all books!")
    print("\nNext steps you can try:")
    print(f"1. Visit the API docs: {BASE_URL}/docs")
    print(f"2. Check hold status: GET {BASE_URL}/holds/{user['id']}")
    print("3. Run the status update endpoint to simulate hold progress")

if __name__ == "__main__":
    main()