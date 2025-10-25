# Usage Guide for Library Hold Tracker API

This guide explains how to set up, run, and interact with the **Library Hold Tracker API**.

## 1. Setup and Installation

### Prerequisites
*   Python 3.8+
*   `pip` (Python package installer)

### Installation Steps

1.  **Navigate to the project directory:**
    \`\`\`bash
    cd library_hold_tracker
    \`\`\`

2.  **Install dependencies:**
    The project uses `fastapi`, `sqlalchemy`, and `playwright` for web automation.
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

3.  **Install Playwright browser drivers:**
    Playwright requires browser binaries to run the web automation logic.
    \`\`\`bash
    playwright install
    \`\`\`

## 2. Running the API Server

The API server can be started using the provided `run.sh` script.

\`\`\`bash
./run.sh
\`\`\`

The server will start at `http://0.0.0.0:8000`. You can access the interactive documentation (Swagger UI) at `http://0.0.0.0:8000/docs`.

## 3. API Endpoints and Examples

The following examples use `curl` to demonstrate how to interact with the key endpoints.

### A. Create a User

A user must be created before placing a hold to associate the hold with an account.

*   **Endpoint:** `POST /users/`
*   **Purpose:** Registers a new user.

\`\`\`bash
curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" -d '{
  "username": "john_doe"
}'
# Example Response:
# {
#   "username": "john_doe",
#   "id": 1
# }
\`\`\`

### B. Search for a Book

This endpoint uses Playwright to perform a live search on the library's catalog.

*   **Endpoint:** `POST /books/search`
*   **Purpose:** Searches the specified library catalog.

\`\`\`bash
curl -X POST "http://localhost:8000/books/search" -H "Content-Type: application/json" -d '{
  "query": "Project Hail Mary",
  "search_type": "title",
  "library": "Alameda"
}'
# Example Response (Simulated):
# [
#   {
#     "title": "Search Result for Project Hail Mary",
#     "author": "Placeholder Author",
#     "isbn": "9780000000001",
#     "library_item_id": "aclib_simulated_id_987654",
#     "library_name": "Alameda",
#     "availability": "Available at Main Branch"
#   }
# ]
\`\`\`

### C. Place a Hold

This is the core feature. It attempts to log in and place the hold on the library website, then records the hold in the database.

*   **Endpoint:** `POST /holds/place`
*   **Purpose:** Places a hold on a book and tracks it. **NOTE: The library card number and PIN are placeholders and should be treated as sensitive information.**

\`\`\`bash
curl -X POST "http://localhost:8000/holds/place" -H "Content-Type: application/json" -d '{
  "user_id": 1,
  "title": "Project Hail Mary",
  "author": "Andy Weir",
  "isbn": "9780593134909",
  "library_name": "Alameda",
  "library_item_id": "aclib_simulated_id_987654",
  "library_card_number": "YOUR_CARD_NUMBER",
  "library_pin": "YOUR_PIN"
}'
# Example Response (Simulated):
# {
#   "title": "Project Hail Mary",
#   "author": "Andy Weir",
#   "isbn": "9780593134909",
#   "library_name": "Alameda",
#   "library_item_id": "aclib_simulated_id_987654",
#   "id": 1,
#   "user_id": 1,
#   "status": "Pending",
#   "queue_position": 15,
#   "estimated_wait_days": 45,
#   "last_checked": "2025-10-25T00:00:00.000000"
# }
\`\`\`

### D. Get All Holds for a User

*   **Endpoint:** `GET /holds/{user_id}`
*   **Purpose:** Retrieves all tracked holds for a given user.

\`\`\`bash
curl -X GET "http://localhost:8000/holds/1"
# Example Response: (A list of Hold objects)
# [
#   {
#     "title": "Project Hail Mary",
#     "author": "Andy Weir",
#     "isbn": "9780593134909",
#     "library_name": "Alameda",
#     "library_item_id": "aclib_simulated_id_987654",
#     "id": 1,
#     "user_id": 1,
#     "status": "Pending",
#     "queue_position": 15,
#     "estimated_wait_days": 45,
#     "last_checked": "2025-10-25T00:00:00.000000"
#   }
# ]
\`\`\`

### E. Manually Update All Hold Statuses

This endpoint simulates the background task that checks the status of all tracked holds.

*   **Endpoint:** `POST /holds/update_all_status`
*   **Purpose:** Logs into the respective libraries for all tracked holds, checks their current status (queue position, ETA), and updates the database.

\`\`\`bash
curl -X POST "http://localhost:8000/holds/update_all_status"
# Example Response (Simulated):
# {
#   "message": "Successfully checked and updated status for 1 holds."
# }
\`\`\`

## 4. Customization and Next Steps

### Library Web Scraping Logic
The core logic for interacting with the library websites is in `services/library_service.py`. The selectors used for login, search, and hold placement are currently **placeholders**.

**To make this functional, you must:**
1.  Manually inspect the Contra Costa and Alameda library websites.
2.  Find the correct CSS selectors for the login fields (card number, PIN) and the "Log In" button.
3.  Update the `_login_to_library` function in `services/library_service.py` with the correct selectors.
4.  Implement the search result parsing and hold placement logic in `_search_and_find_item` and `_place_hold_on_item` based on the library's HTML structure.

### Security Note
In a production environment, the `library_card_number` and `library_pin` should **never** be stored in plain text. They should be encrypted and stored in a secure vault, and only decrypted when needed for the web automation process. For this example, we have not implemented this security layer.
