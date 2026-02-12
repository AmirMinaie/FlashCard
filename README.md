📚 FlashCard

FlashCard is a lightweight and extensible flashcard application built with Python to help users study, review, and memorize information efficiently.

The app is suitable for language learning, exam preparation, technical study, or daily knowledge review.

✨ Features

Simple and user-friendly graphical interface

Create, edit, and delete flashcards

Review cards easily

Organized and scalable project structure

Designed to be extendable for future features

Suitable for desktop and Android builds

🛠 Technologies Used

Python 3

Kivy / KivyMD for UI

Buildozer for Android APK generation

JSON/local storage for data management

🚀 Installation
Requirements

Make sure you have:

Python 3.10+

pip installed

virtual environment support (recommended)

Setup Steps

Clone the repository:

git clone https://github.com/AmirMinaie/FlashCard.git
cd FlashCard


Create and activate a virtual environment:

Windows

python -m venv venv
venv\Scripts\activate


Linux / macOS

python -m venv venv
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

▶️ Running the Application

Run the project using:

python main.py


Or use the provided run scripts if available.

📱 Building Android APK (Optional)

If you want to build an Android version:

buildozer android debug


Make sure Buildozer and Android dependencies are installed properly.

📂 Project Structure

Typical structure overview:

FlashCard/
├── app/                # Application source code
├── assets/             # Fonts, images, resources
├── config/             # Configuration files
├── main.py             # Application entry point
├── buildozer.spec      # Android build configuration
├── requirements.txt    # Python dependencies
└── README.md

🧩 Future Improvements (Ideas)

Possible future enhancements:

Card categories & decks

Spaced repetition algorithm

Import/export decks

Cloud sync

Progress tracking

Dark mode support

🤝 Contributing

Contributions are welcome!

Steps:

Fork the repository

Create a feature branch

Commit changes

Submit a Pull Request

📄 License

You can add your preferred open-source license here (MIT, GPL, etc.).

⭐ Support

If this project is helpful, consider giving the repository a star to support development.