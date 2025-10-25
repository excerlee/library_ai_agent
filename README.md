# Library AI Agent

AI agents to interact with Libraries - A Python backend designed to automate the process of placing books on hold at local libraries and tracking the status of those holds.

## Features

1.  **Book Search:** Search for books by title, author, or ISBN.
2.  **Library Integration:**
    *   Login to Contra Costa County Library (CCCLib) and Alameda County Library (ACLib).
    *   Place a book on hold.
3.  **Hold Tracking (Database):**
    *   Store a list of books on hold.
    *   Track the estimated time of availability (ETA) and current status.
    *   User authentication (basic for now, using API keys or similar).

## Technology Stack

*   **Backend Framework:** FastAPI (for high performance and easy API definition)
*   **Database:** SQLite (for simplicity and development, easily upgradable to PostgreSQL/MySQL)
*   **ORM:** SQLAlchemy (for database interaction)
*   **Web Scraping:** Playwright (for dynamic content/login and browser automation)

## Next Steps

1.  Define the API endpoints and database schema.
2.  Implement the core FastAPI application.
3.  Develop the library-specific web scraping modules.
4.  Integrate the database models and tracking logic.
5.  Add user authentication and documentation.