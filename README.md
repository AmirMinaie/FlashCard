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


---

## Spaced Repetition (SM-2 Review Algorithm)

FlashCard uses the **SM-2 (SuperMemo 2)** spaced repetition algorithm to schedule future reviews based on the user's performance. The goal is to maximize long-term retention while minimizing unnecessary reviews.

### Review Quality

Each review is rated on a **0–5** scale:

| Quality | Meaning |
|---------:|---------|
| 5 | Perfect recall |
| 4 | Correct answer with minor hesitation |
| 3 | Correct answer with noticeable difficulty |
| 2 | Incorrect answer, but familiar |
| 1 | Incorrect answer, remembered after seeing the answer |
| 0 | Complete blackout |

### Ease Factor

Every flashcard has an **Ease Factor** that determines how quickly its review interval grows.

Initial value:

```text
2.5
```

After each review it is updated using the original SM-2 formula:

```text
EF' = EF + (0.1 − (5 − q) × (0.08 + (5 − q) × 0.02))
```

where:

- **EF** = current ease factor
- **q** = review quality (0–5)

The ease factor is clamped to the range:

```text
1.3 ≤ EF ≤ 5.0
```

### Review Scheduling

If the review quality is **less than 3**:

- Repetitions are reset to **0**
- Next review interval becomes **1 day**

If the review quality is **3 or higher**:

- Repetitions increase by one
- Review interval is calculated as follows:

| Successful Review | Next Interval |
|------------------:|--------------|
| 1st | 1 day |
| 2nd | 6 days |
| 3rd and later | `round(Current Interval × Ease Factor)` |

### Next Review Date

The next review date is calculated by adding the new interval to the current date:

```python
next_review = datetime.now() + timedelta(days=interval)
```

### Card State

Each flashcard stores the following review data:

- **Ease Factor**
- **Review Interval (days)**
- **Successful Repetitions**
- **Next Review Date**

These values are updated automatically after every review, allowing the application to adapt the review schedule to each individual flashcard.