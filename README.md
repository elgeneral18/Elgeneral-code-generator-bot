# 🤖 CodeGeneratorBot

CodeGeneratorBot is an AI-powered Telegram bot that turns simple ideas into complete, ready-to-download projects using Gemini AI.

The bot allows users to generate websites or Telegram bots, add images and assets, and download their generated projects as ZIP files.

---

## ✨ Features

- 🌐 Generate full website projects (HTML / CSS / JS)
- 🤖 Generate Telegram bots (Python + pyTelegramBotAPI)
- 🧠 AI-powered generation using Google Gemini
- 💡 Turn simple ideas into complete project files
- 📸 Upload images and assets
- 📦 Automatic ZIP project export
- 📂 Project history
- 📊 User statistics
- 👤 User and project management
- 🔔 Admin notifications
- ⚙️ Settings menu
- 💾 SQLite database

---

## 🛠️ Technologies

- 🐍 Python
- 🤖 Telegram Bot API
- 🧠 Google Gemini API
- 🗄️ SQLite
- 📦 ZIP / File Management

---

## 📂 Project Structure

```
CodeGeneratorBot/
├── main.py
├── generator.py
├── database.py
├── ai_client.py
├── ai_generator.py
├── project_writer.py
├── zip_builder.py
├── file_manager.py
├── config.py
├── requirements.txt
├── projects/
├── zips/
└── README.md
```

---

## 🚀 How It Works

```
User → Telegram Bot → Choose Project Type → Describe Idea
     → (Optional) Upload Images → Google Gemini
     → Generate Files → ZIP Export → Download
```

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CodeGeneratorBot.git
cd CodeGeneratorBot
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure `config.py`

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_ID = YOUR_TELEGRAM_USER_ID   # integer
CONTACT_USERNAME = "your_username"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"   # recommended
```

⚠️ Never upload real API keys or tokens to GitHub. Prefer environment variables or a `.env` file added to `.gitignore`.

4. Run the bot

```bash
python main.py
```

---

## 📌 Version

**v1.2.0** — Fixed & Improved

### Changes in v1.2
- Updated Gemini model to `gemini-3.8-flash`
- Robust AI response error handling (no more KeyError on empty candidates)
- Project name is now saved correctly after generation
- ZIP files go to a dedicated `zips/` folder
- Cleaner path-traversal protection
- Better JSON cleaning from AI responses
- Session helpers used consistently

---

## 🔮 Future Plans

- 🎨 More website templates
- 🤖 More AI-powered generation features
- ⚡ Faster project generation
- 🧩 More customization options
- 📁 Improved project management
- 🌍 Support for additional project types
- 🔧 More configuration options

---

## 👨‍💻 Author

Adam elgeneral

Building and learning through real-world projects. 🚀

---

## 📜 License

MIT License — Copyright (c) 2026 Adam elgeneral

See the [LICENSE](LICENSE) file for details.
