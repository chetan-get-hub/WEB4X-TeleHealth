<title>WEB4X-TeleHealth</title>

The TeleHealth platform is built using a modern, high-performance stack that prioritizes a premium "Vanilla" experience—meaning no heavy frameworks like React or Tailwind were used. This ensures maximum speed, smooth animations, and zero dependencies on the frontend.

<h2>🎨 Frontend (The "Apple-Style" UI)</h2>
<h3>Core:</h3> Vanilla HTML5, CSS3, and JavaScript (ES6+).
<h3>Architecture:</h3> Custom-built Single Page Application (SPA) routing for seamless tab transitions without page reloads.
<h3>Design System:</h3> Authentic Apple-inspired aesthetics including:
<h3>Glassmorphism:</h3> High-precision backdrop blurring (40px) and saturation (200%).
<h3>Typography:</h3> SF Pro Display system font stack.
<h3>Icons:</h3> Precise SVG-based iconography for a native feel.

<h2>Browser APIs:</h2>
Web Speech API: Powering the Simulated IVR voice prompts.
Web Audio API: Real-time DTMF tone generation for the interactive dialpad.
Geolocation API: Live tracking for finding nearby pharmacies.

<h2>⚙️ Backend (The "Master" Engine)</h2>
<h3>Language:</h3> Python 3.
<h3>Web Server:</h3> A highly custom server implementation using socket, sqlite3, and urllib.
<h3>Security:</h3> Dedicated .env configuration for safe management of API keys and environment variables.
<h3>Storage:</h3>
Database: SQLite3 (database.db) for persistent user and medical record storage.
Filesystem: Robust medical record upload handling in the /uploads directory.

<h2>🧠 AI Intelligence</h2>
<h3>Groq Cloud (Free Tier):</h3> The primary brain for the AI Symptom Checker and Prescription Analysis, utilizing ultra-fast Llama-3 models.
<h3>OpenAI API:</h3> Powering the Govt. Schemes module to dynamically fetch and summarize health welfare programs.

<h2>📂 Directory Structure</h2>
<h3>backend/:</h3> Centralized Python server and logic.
<h3>telehealth-auth/:</h3> The premium frontend dashboard.
<h3>database.db:</h3> The local persistent data layer.
<h3>.env:</h3> The secure configuration file.

<h3>This lightweight yet powerful stack allows the platform to feel like a native Apple application while running entirely in a standard web browser. 🚀🏥✨</h3>
