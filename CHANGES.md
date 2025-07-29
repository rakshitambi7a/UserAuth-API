##  Change 1: Updated to an Easier Setup Process for Convenience

###  Option 1: Automated Setup

```bash
# Clone/download this repository
# Navigate to the assignment directory
cd messy-migration

# For Unix/Linux/macOS:
./setup.sh

# For Windows:
setup.bat

# Or using Make (if available):
make setup

# Start the application
# On Unix/Linux/macOS:
source venv/bin/activate && python app.py

# On Windows:
venv\Scripts\activate && python app.py

# The API will be available at http://localhost:5000
```

###  Option 2: Manual Setup

```bash
# Clone/download this repository
# Navigate to the assignment directory
cd messy-migration

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Unix/Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

---

##  Change 2: Added a Migration Script for Password Hashing

Migrated legacy plaintext passwords to hashed ones using `werkzeug`.

### 🧪 Migration Script

```bash
# Migrate plaintext passwords to hashed passwords using werkzeug
python migrations/migrate_passwords.py
```

---

##  Change 3: Separation of Concerns

All logic was previously jammed into a single file (yikes). Now, the project structure is modular and clean:

```
Current File Hierarchy:
├── app.py                 # Main Flask application
├── config/               # Configuration management
├── core/                 # Dependency injection
├── db/                   # Database layer
├── models/               # Data models  
├── repositories/         # Repository pattern
├── services/             # Business logic
├── routes/               # API endpoints
├── utils/                # Utilities & validators
├── tests/                # Complete test suite (44 tests)
├── requirements.txt      # Dependencies
├── README.md             # Documentation
└── .env.example          # Environment template
```

---

##  Change 4: Added Validators

No validation existed earlier for `name`, `email`, and `password` fields. Now added custom validators placed in the `utils` directory.

---

##  Change 5: Major Security Concern – Leaking Passwords!

Fixed the `GET /users` endpoint that was irresponsibly returning user passwords in the response. Huge fix.

---

##  Change 6: SQL Injection Prevention

Implemented parameterized queries (`?` placeholders) to sanitize all user inputs, preventing SQL injection vulnerabilities.

---

##  Change 7: JWT Authentication Added

For better security, JWT-based authentication has been implemented for the login endpoint. Tokens are returned upon successful login and required for protected routes.

---

##  Change 8: Added Testing

A complete test suite has been added using `pytest`. Includes:

- Unit & integration tests  
- Security checks  
- Coverage for user creation, updates, deletion, and login  
- 44 tests in total  
- Isolated testing environment

---

##  Change 9: Rate Limiting

Implemented rate limiting to prevent brute-force attacks:

- Login endpoint: 5 requests/min  
- Entire app: 100 requests/hour

Helps ensure fair usage and protects against abuse.

---

##  Change 10: Input Sanitization

Sanitized all user inputs (email, name, password) to defend against XSS and other injection attacks. Validations added before data processing.

## Future Improvements
- If i had more time, I would have made the API more production ready by adding redis caching for distributed rate limiting and autocleanup
- Implemented a more robust logging system.
- Email verification and password reset functionality.
- More comprehensive error handling and logging.
- Additional security measures like CORS, CSRF protection, and more.
- Maybe better documentation 😅

## Ai usage:

For the most part, I used AI only for boilerplate generation—here’s what I mean:

Python isn’t my primary language. I had learned it a few years ago, but only at the syntax level. In the past, I’ve primarily worked with Node.js and PHP for backend development. This was actually my first time working with Flask. I had some familiarity with Django, but Flask still felt like unfamiliar territory. That said, Flask was surprisingly easy to pick up, and I can already see its advantages over something like Express.

While fixing security issues and separating the logic into clean modules, I intentionally avoided relying too much on AI. I treated that as a constraint—I only used it sparingly, mainly for syntax-level hiccups. But when I got to implementing JWT authentication, I hit a wall. That’s when I switched to Copilot Agent mode using Claude Sonnet 4.0. This was my first time using Sonnet within Copilot, and I was honestly impressed by what these systems are capable of.

Although I had a basic understanding of JWT, implementing it without the agent’s help would’ve been really tough. The one area where I *did* heavily rely on AI was generating docstrings and test cases—and I think this is where AI shines the most. The test cases it generated were well thought out and saved me hours of manual effort. Once they were in place, it was just a matter of iterating through and fixing the failed ones. Issues like over-logging in the debug file and incorrect use of the DB instance in return clauses were quickly highlighted by these tests and easy to fix, thanks to AI.

Going forward, I definitely plan to use these AI tools more often—not to cheat, but to delegate the mundane parts. I found Sonnet to be much better at handling context compared to GPT-4.0 or Gemini 2.5 Pro, which I used for regular tasks. Sonnet also helped a lot during debugging since it now has access to the terminal and can run scripts. Of course, it wasn’t perfect—it once introduced a circular import while suggesting fixes.

Still, I was curious to see how far Sonnet could go, so I deliberately tried to over-engineer parts of the project. And it didn’t fail. It even wrote the test cases keeping future scale in mind.

I ended up learning a lot about using AI effectively while working on this project.
