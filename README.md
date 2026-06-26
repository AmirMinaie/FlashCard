# FlashCard

A desktop flashcard application built with Python, Kivy, and KivyMD.

FlashCard helps learners create, organize, review, and manage flashcards in a focused desktop environment. It is designed primarily for language learning, exam preparation, technical study, and any workflow that benefits from repeated review.

> The project uses a layered architecture to keep the user interface, business logic, and data-access code separate and maintainable.

---

## Features

- Create, edit, and delete flashcards
- Browse and manage flashcard lists
- Review cards in a dedicated review screen
- Store flashcard data locally
- Manage flashcard-related files
- Configurable application settings
- Local backup support
- Custom Kivy/KivyMD widgets and reusable UI components
- Splash screen support
- Windows executable packaging with PyInstaller

---

## Tech Stack

- **Python**
- **Kivy** — application framework
- **KivyMD** — Material Design components
- **SQLAlchemy** — database ORM
- **pyodbc** — database connectivity
- **PyInstaller** — Windows executable packaging

---

## Project Structure

```text
FlashCard/
├── app/
│   ├── BL/                 # Business logic layer
│   ├── DA/                 # Data-access layer and database models
│   ├── Kv/                 # Kivy language UI layouts
│   ├── Screens/            # Application screens
│   ├── assets/             # Fonts, images, and other resources
│   ├── cmn/                # Shared helpers and utilities
│   ├── theme/              # Colors and UI theme configuration
│   ├── widgets/            # Reusable custom widgets
│   └── Main.py             # Application entry point
├── output/                 # Generated build output (if created)
├── requirements.txt        # Python dependencies
├── buildozer.spec.backup   # Android build configuration backup
└── README.md