# Founder Connect

A platform connecting founders with technical co-founders. Founders can post their startup ideas, and developers can apply with their proposals, including equity and salary expectations.

## Features

- User registration for both founders and developers
- GitHub integration for developer profiles
- Idea posting with equity and salary details
- Application system with proposal submission
- WhatsApp contact sharing upon acceptance
- Modern, responsive UI

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Visit http://localhost:5000 in your browser

## Usage

### For Founders
1. Register as a founder
2. Post your startup idea with details
3. Review applications from developers
4. Accept promising applications

### For Developers
1. Register as a developer
2. Connect your GitHub profile
3. Browse available startup ideas
4. Apply with your proposal and terms

## Security
- Passwords are hashed before storage
- WhatsApp numbers are only shared upon mutual agreement
- Protected routes require authentication
