The TeleHealth platform is built using a modern, high-performance stack that prioritizes a premium "Vanilla" experience—meaning no heavy frameworks like React or Tailwind were used. This ensures maximum speed, smooth animations, and zero dependencies on the frontend.

🎨 Frontend (The "Apple-Style" UI)
Core: Vanilla HTML5, CSS3, and JavaScript (ES6+).
Architecture: Custom-built Single Page Application (SPA) routing for seamless tab transitions without page reloads.
Design System: Authentic Apple-inspired aesthetics including:
Glassmorphism: High-precision backdrop blurring (40px) and saturation (200%).
Typography: SF Pro Display system font stack.
Icons: Precise SVG-based iconography for a native feel.
Browser APIs:
Web Speech API: Powering the Simulated IVR voice prompts.
Web Audio API: Real-time DTMF tone generation for the interactive dialpad.
Geolocation API: Live tracking for finding nearby pharmacies.
⚙️ Backend (The "Master" Engine)
Language: Python 3.
Web Server: A highly custom server implementation using socket, sqlite3, and urllib.
Security: Dedicated .env configuration for safe management of API keys and environment variables.
Storage:
Database: SQLite3 (database.db) for persistent user and medical record storage.
Filesystem: Robust medical record upload handling in the /uploads directory.
🧠 AI Intelligence
Groq Cloud (Free Tier): The primary brain for the AI Symptom Checker and Prescription Analysis, utilizing ultra-fast Llama-3 models.
OpenAI API: Powering the Govt. Schemes module to dynamically fetch and summarize health welfare programs.
📂 Directory Structure
backend/: Centralized Python server and logic.
telehealth-auth/: The premium frontend dashboard.
database.db: The local persistent data layer.
.env: The secure configuration file.
This lightweight yet powerful stack allows the platform to feel like a native Apple application while running entirely in a standard web browser. 🚀🏥✨
