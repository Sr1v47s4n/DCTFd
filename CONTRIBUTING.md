# Contributing to DCTFd

First off, thanks for taking the time to contribute! 🎉 

This document should help you get started with contributing to DCTFd. Don't worry too much about making mistakes - this project is about learning and improving together.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [What Can I Help With?](#what-can-i-help-with)
- [Your First Contribution](#your-first-contribution)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Questions?](#questions)

## Code of Conduct

Let's keep it simple: be nice to each other. Treat everyone with respect and kindness. Everyone involved cares about this project, and all have different backgrounds and skills.

## What Can I Help With?

There are lots of ways to contribute to DCTFd:

### 🐛 Bug Fixes
Found something that doesn't work right? Fixing bugs is super valuable! Check the [issues](https://github.com/Sr1v47s4n/DCTFd/issues) for reported bugs or report a new one.

### ✨ New Features 
Have an idea for a cool feature? Let's hear it! Open an issue first so we can discuss it.

### 📝 Documentation
Help improve the README, add comments to confusing code, or create guides for users and developers.

### 🎨 Design
From UI improvements to a new logo, design contributions are always welcome.

### 🔍 Testing
Write tests, try out new features before they're released, or help find edge cases.

### 💭 Ideas and Feedback
Sometimes the most valuable contribution is your perspective. Share your thoughts on how to make things better.

## Your First Contribution

Never contributed to open source before? No problem! Here's a quick guide:

1. Find an issue you want to work on, or create one if you've found a bug or have a feature idea
2. Comment on the issue to say you're working on it (so others don't duplicate work)
3. Fork the repository
4. Create a branch for your work
5. Make your changes
6. Test your changes
7. Submit a pull request

Not sure where to start? Look for issues tagged with `good first issue` or `help wanted`.

## Pull Requests

When submitting a pull request:

1. Update the README.md if necessary
2. Add tests if you're adding a feature
3. Make sure all tests pass
4. Keep your PR focused on a single topic
5. Be open to feedback and prepared to make changes

Don't worry about getting everything perfect on the first try. The review process is an opportunity for collaboration and improvement.

## Development Setup

To get the project running locally:

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file following the README guidelines
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Load sample data (optional):
   ```bash
   python manage.py devmode on
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Coding Standards

We try to keep things clean and consistent:

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused
- Write docstrings for classes and functions

But don't stress too much about this for your first contribution - code can always be refined during the review process.

## Questions?

Have questions that aren't answered here? Open an issue labeled `question` to get help.

---

Remember, the best contribution is one that happens. Don't let perfect be the enemy of good. Your help is appreciated!

Thanks for being part of making DCTFd better! 🚀
