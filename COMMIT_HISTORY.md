# Abubakar — Authentication Module Commit History
# Branch: feature-auth
# Target: 5+ commits following conventional commit format

================================================================================
COMMIT 1: feat(auth): initialize User model with Flask-Login integration
================================================================================

Message:
    feat(auth): initialize User model with Flask-Login integration

    - Create User SQLAlchemy model with id, username, email, password_hash
    - Integrate Flask-Login UserMixin for session handling
    - Add Werkzeug password hashing (set_password / check_password)
    - Define user_loader callback for session restoration
    - Establish one-to-many relationship with Task model (cascade delete)

Files changed:
    M models/__init__.py
    A models/user.py

================================================================================
COMMIT 2: feat(auth): add registration route with server-side validation
================================================================================

Message:
    feat(auth): add registration route with server-side validation

    - Implement /register GET/POST route in auth_routes.py
    - Add username validation (3-20 chars, alphanumeric + underscore)
    - Add email format validation with regex
    - Add strong password policy (8+ chars, upper, lower, digit)
    - Enforce password confirmation match
    - Check username/email uniqueness before creation
    - Flash appropriate messages for all validation errors
    - Redirect authenticated users away from register page

Files changed:
    A routes/auth_routes.py

================================================================================
COMMIT 3: feat(auth): implement login and logout with session management
================================================================================

Message:
    feat(auth): implement login and logout with session management

    - Add /login GET/POST route with credential verification
    - Integrate Flask-Login login_user() with optional "remember me"
    - Handle invalid username/password with specific flash messages
    - Implement /logout route with @login_required decorator
    - Add home (/) redirect logic for authenticated vs anonymous users
    - Support "next" URL parameter for post-login redirects
    - Clear session on logout and redirect to login page

Files changed:
    M routes/auth_routes.py

================================================================================
COMMIT 4: feat(ui): design responsive login page with Bootstrap 5
================================================================================

Message:
    feat(ui): design responsive login page with Bootstrap 5

    - Create login.html extending base.html layout
    - Add gradient header with icon and welcome message
    - Style username/password inputs with input-group icons
    - Include "Remember me" checkbox option
    - Add responsive layout (centered card, min-vh-100)
    - Link to registration page for new users
    - Preserve username on validation error

Files changed:
    A templates/login.html

================================================================================
COMMIT 5: feat(ui): design responsive registration page with validation hints
================================================================================

Message:
    feat(ui): design responsive registration page with validation hints

    - Create register.html extending base.html layout
    - Add gradient success header with icon
    - Include username, email, password, confirm_password fields
    - Add form-text hints for password requirements and username rules
    - Style inputs with Bootstrap icons (person, envelope, lock, shield)
    - Preserve username/email on validation error
    - Link back to login page for existing users

Files changed:
    A templates/register.html

================================================================================
COMMIT 6: refactor(auth): extract validation helpers and add code documentation
================================================================================

Message:
    refactor(auth): extract validation helpers and add code documentation

    - Extract validate_username(), validate_email(), validate_password()
      into standalone helper functions for reusability and testing
    - Add comprehensive module-level docstrings
    - Add function docstrings for all routes and helpers
    - Add __repr__ to User model for better debugging
    - Add database index on username and email columns
    - Clean up redundant code in auth_routes.py

Files changed:
    M models/user.py
    M routes/auth_routes.py

================================================================================
COMMIT 7: fix(auth): handle edge cases in login flow and improve UX
================================================================================

Message:
    fix(auth): handle edge cases in login flow and improve UX

    - Strip whitespace from username/email inputs to prevent accidental spaces
    - Normalize email to lowercase for consistent lookup
    - Prevent empty username/password submission with early validation
    - Add specific flash messages for "username not found" vs "wrong password"
    - Validate "next" parameter to prevent open redirect vulnerabilities
    - Ensure remember_me checkbox is properly parsed as boolean
    - Add autofocus to first input field on both login and register pages

Files changed:
    M routes/auth_routes.py
    M templates/login.html
    M templates/register.html

================================================================================
SUMMARY OF FEATURES DELIVERED
================================================================================

✅ User Registration
   - Form with username, email, password, confirm_password
   - Server-side validation for all fields
   - Uniqueness checks for username and email
   - Secure password hashing with Werkzeug
   - Flash messages for success/error feedback

✅ User Login
   - Credential verification against hashed passwords
   - Session creation via Flask-Login
   - "Remember me" persistent session option
   - Post-login redirect to originally requested page
   - Specific error messages for different failure modes

✅ Logout System
   - @login_required protected route
   - Session cleanup via logout_user()
   - Redirect to login with confirmation message

✅ Password Validation
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit
   - Password confirmation match check

✅ Session Management
   - Flask-Login integration with user_loader callback
   - Remember me cookie support
   - Automatic redirect for authenticated/anonymous users
   - Secure session handling

✅ User Model
   - SQLAlchemy ORM with UserMixin
   - Indexed username and email columns
   - One-to-many task relationship with cascade delete
   - Werkzeug password hashing methods

================================================================================
