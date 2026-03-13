import socket
import sqlite3
import json
import hashlib
import os
import urllib.parse
import urllib.request
import random
from datetime import datetime

# Load .env manually to avoid dependencies
def load_env():
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key.strip()] = value.strip().strip("'").strip('"')
    return env_vars

env = load_env()
PORT = int(env.get('PORT', 8000))
GROQ_API_KEY = env.get('GROQ_API_KEY', 'YOUR_FREE_GROQ_KEY_HERE')

# Unified path resolution
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(BASE_DIR, 'database.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email_or_mobile TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_login TIMESTAMP, is_active BOOLEAN DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS patient_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS doctor_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, specialization TEXT DEFAULT 'General', license_number TEXT UNIQUE, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, file_name TEXT NOT NULL, file_path TEXT NOT NULL, description TEXT, upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')
    conn.commit()
    conn.close()
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def handle_request(client_connection):
    header_data = b""
    while b"\r\n\r\n" not in header_data:
        chunk = client_connection.recv(4096)
        if not chunk: break
        header_data += chunk
    
    if not header_data: return
    
    parts = header_data.split(b"\r\n\r\n", 1)
    header_str = parts[0].decode('utf-8')
    initial_body = parts[1] if len(parts) > 1 else b""
    
    lines = header_str.split('\r\n')
    request_line = lines[0].split()
    if len(request_line) < 2: return
    
    method = request_line[0]
    path = request_line[1]
    
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    
    content_length = int(headers.get('content-length', 0))
    body = initial_body
    while len(body) < content_length:
        remaining = content_length - len(body)
        chunk = client_connection.recv(min(remaining, 4096))
        if not chunk: break
        body += chunk

    if method == "GET":
        if path.startswith('/api/schemes'):
            schemes = [
                {"name": "Ayushman Bharat (PM-JAY)", "desc": "World's largest health assurance scheme providing ₹5 lakh per family per year for secondary and tertiary care hospitalization."},
                {"name": "Pradhan Mantri Surakshit Matritva Abhiyan", "desc": "Providing fixed day assured, comprehensive and quality antenatal care universally to all pregnant women on the 9th of every month."},
                {"name": "Janani Shishu Suraksha Karyakram", "desc": "Entitles all pregnant women delivering in public health institutions to absolutely free and no expense delivery including C-section."},
                {"name": "National Health Mission (NHM)", "desc": "Attainment of universal access to equitable, affordable and quality health care services."},
                {"name": "Rashtriya Kishor Swasthya Karyakram", "desc": "Holistic development of adolescent population through community based interventions."}
            ]
            response_body = json.dumps({"schemes": schemes})
            header = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n"
            client_connection.sendall(header.encode() + response_body.encode())
        elif path.startswith('/uploads/'):
            # Path relative to BASE_DIR
            serve_file(client_connection, os.path.join(BASE_DIR, 'uploads', path.replace('/uploads/', '')))
        else:
            serve_static(client_connection, path)
    elif method == "POST":
        handle_post(client_connection, path, body)

def serve_static(conn, path):
    clean_path = path.split('?')[0]
    if clean_path == '/' or clean_path == '':
        clean_path = '/index.html'
    
    file_path = os.path.join(BASE_DIR, clean_path.lstrip('/'))
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
            
        header = "HTTP/1.1 200 OK\r\n"
        if file_path.endswith('.html'): header += "Content-Type: text/html\r\n"
        elif file_path.endswith('.css'): header += "Content-Type: text/css\r\n"
        elif file_path.endswith('.js'): header += "Content-Type: application/javascript\r\n"
        header += "Connection: close\r\n\r\n"
        conn.sendall(header.encode() + content)
    else:
        conn.sendall(b"HTTP/1.1 404 NOT FOUND\r\nConnection: close\r\n\r\nFile not found")

def serve_file(conn, file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        header = "HTTP/1.1 200 OK\r\n"
        if file_path.endswith('.pdf'): header += "Content-Type: application/pdf\r\n"
        elif file_path.endswith('.png'): header += "Content-Type: image/png\r\n"
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'): header += "Content-Type: image/jpeg\r\n"
        header += "Connection: close\r\n\r\n"
        conn.sendall(header.encode() + content)
    else:
        conn.sendall(b"HTTP/1.1 404 NOT FOUND\r\nConnection: close\r\n\r\nFile not found")

def handle_post(conn, path, body):
    try:
        if path == '/api/upload-record':
            user_id = 1 
            file_name = f"record_{int(datetime.now().timestamp())}.pdf"
            file_path = os.path.join(UPLOADS_DIR, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(body)
            
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            c.execute('INSERT INTO medical_records (user_id, file_name, file_path, description) VALUES (?, ?, ?, ?)', 
                      (user_id, file_name, file_path, "Uploaded Document"))
            db.commit()
            db.close()
            
            response_body = json.dumps({"message": "Uploaded", "fileName": file_name})
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            return

        data = {}
        if body:
            try:
                data = json.loads(body.decode('utf-8'))
            except: pass

        if path == '/api/analyze-prescription':
            medicines = [
                {"name": "Amoxicillin", "dosage": "500mg", "freq": "Three times a day", "type": "Antibiotic"},
                {"name": "Paracetamol", "dosage": "650mg", "freq": "Whenever fever > 100°F", "type": "Antipyretic"},
                {"name": "Cough Syrup", "dosage": "10ml", "freq": "Before sleep", "type": "Syrup"}
            ]
            response_body = json.dumps({"status": "Success", "medicines": medicines, "note": "AI Analysis complete (Free Tier simulated)."})
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            return

        if path == '/api/ai-chat':
            user_message = data.get('message', '')
            print(f"[{datetime.now()}] AI Chat Request: {user_message[:50]}...")
            
            # Use Groq for Free API
            if GROQ_API_KEY == 'YOUR_FREE_GROQ_KEY_HERE':
                mock_replies = [
                    "I suggest keeping track of your symptoms. If they persist, consult a doctor.",
                    "Rest and hydration are key. Please visit our 'Consult' section for expert advice.",
                    "That sounds serious. Please contact a healthcare professional immediately."
                ]
                ai_text = random.choice(mock_replies)
                response_body = json.dumps({"reply": ai_text})
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
                return

            # Real Groq API Call
            groq_url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful medical assistant for TeleHealth. Keep it short and professional."},
                    {"role": "user", "content": user_message}
                ]
            }
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            try:
                req = urllib.request.Request(groq_url, data=json.dumps(payload).encode(), headers=headers, method='POST')
                with urllib.request.urlopen(req) as resp:
                    res_data = json.loads(resp.read().decode())
                    ai_text = res_data['choices'][0]['message']['content']
                    response_body = json.dumps({"reply": ai_text})
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            except Exception as e:
                print(f"AI API Error: {e}")
                fallback = "I'm having trouble connecting to my brain right now. Please try again later."
                response_body = json.dumps({"reply": fallback})
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            return

        if path == '/api/nearby-pharmacies':
            pharmacies = [
                {"name": "Apollo Pharmacy", "dist": "0.8 km", "stock": "In Stock", "contact": "+91 98822 33441", "address": "Main St, 2nd Block"},
                {"name": "MedPlus Health", "dist": "1.2 km", "stock": "Limited", "contact": "+91 99332 11223", "address": "Central Mall Rd"},
            ]
            response_body = json.dumps({"pharmacies": pharmacies})
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            return

        if path == '/api/get-records':
            user_id = data.get('userId')
            role = data.get('role', 'patient')
            db = sqlite3.connect(DB_FILE)
            db.row_factory = sqlite3.Row
            c = db.cursor()
            if role == 'doctor':
                c.execute('SELECT medical_records.*, patient_profiles.first_name || " " || patient_profiles.last_name as patient_name FROM medical_records JOIN patient_profiles ON medical_records.user_id = patient_profiles.user_id ORDER BY upload_date DESC')
            else:
                c.execute('SELECT * FROM medical_records WHERE user_id = ? ORDER BY upload_date DESC', (user_id,))
            records = [dict(row) for row in c.fetchall()]
            db.close()
            response_body = json.dumps({"records": records})
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            
        elif path == '/api/register':
            fname = data.get('firstName')
            lname = data.get('lastName')
            contact = data.get('contact')
            role = data.get('role', 'patient')
            password = hash_password(data.get('password'))
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            try:
                c.execute('INSERT INTO users (email_or_mobile, password_hash, role) VALUES (?, ?, ?)', (contact, password, role))
                user_id = c.lastrowid
                if role == 'patient':
                    c.execute('INSERT INTO patient_profiles (user_id, first_name, last_name) VALUES (?, ?, ?)', (user_id, fname, lname))
                else:
                    c.execute('INSERT INTO doctor_profiles (user_id, first_name, last_name, specialization, license_number) VALUES (?, ?, ?, ?, ?)', (user_id, fname, lname, 'General', f"MED-{user_id}"))
                db.commit()
                response_body = '{"message": "OK", "redirect": "dashboard.html"}'
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            except sqlite3.IntegrityError:
                conn.sendall(b"HTTP/1.1 409 Conflict\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{\"error\": \"Exists\"}")
            finally:
                db.close()
                
        elif path == '/api/login':
            contact = data.get('contact')
            password = hash_password(data.get('password'))
            db = sqlite3.connect(DB_FILE)
            c = db.cursor()
            c.execute('SELECT id, role FROM users WHERE email_or_mobile = ? AND password_hash = ?', (contact, password))
            user = c.fetchone()
            if user:
                c.execute('SELECT first_name FROM patient_profiles WHERE user_id = ? UNION SELECT first_name FROM doctor_profiles WHERE user_id = ?', (user[0], user[0]))
                name_row = c.fetchone()
                name = name_row[0] if name_row else "User"
                response_body = f'{{"message": "OK", "redirect": "dashboard.html?name={name}&role={user[1]}&userId={user[0]}"}}'
                conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_body}".encode())
            else:
                conn.sendall(b"HTTP/1.1 401 Unauthorized\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{\"error\": \"Invalid\"}")
            db.close()
        
    except Exception as e:
        print(f"Error handling POST: {e}")
        conn.sendall(b"HTTP/1.1 500 SERVER ERROR\r\nConnection: close\r\n\r\n")

if __name__ == '__main__':
    init_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Listen on all interfaces for better connectivity
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(5)
    print(f"Backend listening on port {PORT} with .env support")
    
    try:
        while True:
            client_connection, client_address = server_socket.accept()
            try:
                handle_request(client_connection)
            except Exception as e:
                pass
            finally:
                client_connection.close()
    except KeyboardInterrupt:
        print("\nShutting down")
    finally:
        server_socket.close()
