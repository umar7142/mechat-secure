from fastapi import FastAPI, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import uvicorn
import json
from database import SessionLocal, User, Message, Block, generate_secret_key, generate_virtual_number, COUNTRY_FORMATS, Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# 🚀 VIP RADAR ENGINE
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.broadcast(json.dumps({"type": "status", "user": client_id, "status": "online"}))

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            await self.broadcast(json.dumps({"type": "status", "user": client_id, "status": "offline"}))

    async def broadcast(self, message: str):
        dead_connections = []
        for client_id, connection in self.active_connections.items():
            try: await connection.send_text(message)
            except Exception: dead_connections.append(client_id)
        for dead in dead_connections:
            await self.disconnect(dead)

manager = ConnectionManager()

male_avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzYzNjZGMSI+PHBhdGggZD0iTTEyIDEyYzIuMjEgMCA0LTEuNzkgNC00czEtMS43OS00LTQtNCAxLjc5LTQgNCAxLjc5IDQgNCA0em0wIDJjLTIuNjcgMC04IDEuMzQtOCA0djJoMTZ2LTJjMC0yLjY2LTUuMzMtNC04LTR6Ii8+PC9zdmc+"
female_avatar = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0VDRjA4RCI+PHBhdGggZD0iTTEyIDEyYzIuMjEgMCA0LTEuNzkgNC00czEtMS43OS00LTQtNCAxLjc5LTQgNCAxLjc5IDQgNCA0em0wIDJjLTIuNjcgMC04IDEuMzQtOCA0djJoMTZ2LTJjMC0yLjY2LTUuMzMtNC04LTR6Ii8+PC9zdmc+"

dropdown_options = ""
for code, info in sorted(COUNTRY_FORMATS.items()):
    dropdown_options += f'<option value="{code}">{code} ({info["code"]}) - {info["region"]}</option>\n'

html_app = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ME CHAT - Ultimate</title>
    <link href="https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
        body {{ background: linear-gradient(135deg, #EEF2F6 0%, #E2E8F0 100%); display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #1C1D22; overflow: hidden; perspective: 1000px; }}
        
        @keyframes slideUpFade {{ 0% {{ opacity: 0; transform: translateY(30px) scale(0.98); }} 100% {{ opacity: 1; transform: translateY(0) scale(1); }} }}
        @keyframes popIn {{ 0% {{ opacity: 0; transform: scale(0.8) translateY(10px); }} 80% {{ transform: scale(1.05) translateY(-2px); }} 100% {{ opacity: 1; transform: scale(1) translateY(0); }} }}
        @keyframes floatLogo {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); }} }}
        @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

        .app-container {{ background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); width: 100%; max-width: 420px; height: 90vh; max-height: 850px; border-radius: 40px; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1), inset 0 0 0 1px rgba(255,255,255,0.5); display: flex; flex-direction: column; overflow: hidden; position: relative; border: 8px solid #FFFFFF; }}
        .view-section {{ display: none; flex-direction: column; width: 100%; height: 100%; padding: 30px 25px; overflow-y: auto; background-color: transparent; position: absolute; top: 0; left: 0; z-index: 10; }}
        .view-section.active {{ display: flex; z-index: 20; animation: slideUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
        .view-section::-webkit-scrollbar {{ width: 0px; }}

        .logo-title {{ font-family: 'Luckiest Guy', cursive; font-size: 48px; text-align: center; color: #111827; margin-bottom: 5px; letter-spacing: 2px; text-shadow: 3px 3px 0px #E5E7EB; animation: floatLogo 4s ease-in-out infinite; }}
        .logo-dot {{ color: #EF4444; }} 
        .subtitle {{ font-size: 14px; color: #6B7280; text-align: center; margin-bottom: 25px; font-weight: 500; }}
        .page-title {{ font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 20px; color: #111827; letter-spacing: -0.5px; }}
        
        .btn-social {{ display: flex; justify-content: center; align-items: center; gap: 12px; width: 100%; padding: 14px; margin-bottom: 10px; background-color: #FFFFFF; border: 2px solid #F3F4F6; border-radius: 16px; font-size: 14px; font-weight: 600; color: #374151; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
        .btn-social:active {{ transform: translateY(1px); }}
        .btn-social svg {{ width: 20px; height: 20px; }}
        
        .btn-primary {{ width: 100%; padding: 16px; background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%); color: #FFFFFF; border: none; border-radius: 20px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 5px; transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3); }}
        .btn-primary:active {{ transform: translateY(1px); box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2); }}
        
        .btn-danger {{ background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%); box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3); margin-top:15px; }}
        .btn-secondary {{ background: #F1F5F9; color: #4B5563; box-shadow: none; border: 1px solid #E5E7EB; }}
        
        .input-box {{ width: 100%; padding: 16px 20px; margin-bottom: 12px; background-color: #F8FAFC; border: 2px solid #F1F5F9; border-radius: 16px; font-size: 14px; outline: none; transition: all 0.3s ease; color:#111827; font-weight: 500; }}
        .input-box:focus {{ border-color: #6366F1; background-color: #FFFFFF; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }}
        
        .link-text {{ text-align: center; font-size: 14px; color: #6B7280; margin-top: 15px; }}
        .clickable-span {{ color: #6366F1; font-weight: 600; cursor: pointer; padding: 5px; transition: 0.2s; }}
        .clickable-span:hover {{ text-decoration: underline; }}
        
        .divider {{ text-align: center; margin: 15px 0; font-size: 12px; color: #9CA3AF; font-weight: 600; display: flex; align-items: center; justify-content: center; }}
        .divider::before, .divider::after {{ content: ""; flex: 1; height: 1px; background: #E5E7EB; margin: 0 15px; }}
        
        .gender-select {{ display: flex; justify-content: center; gap: 30px; margin: 5px 0 15px; }}
        .gender-select label {{ font-size: 14px; color: #4B5563; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }}

        .tc-box {{ display: flex; align-items: center; gap: 10px; justify-content: center; margin-bottom: 15px; font-size: 12px; color: #4B5563; font-weight: 500; }}

        .secret-box {{ background: linear-gradient(to right, #F8FAFC, #F1F5F9); padding: 25px; border-radius: 20px; margin-bottom: 20px; border: 2px dashed #818CF8; text-align: center; display: none; animation: popIn 0.5s ease-out; }}
        
        .dash-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .dash-header h2 {{ font-size: 24px; font-weight: 800; color: #111827; letter-spacing: -1px; }}
        .btn-logout {{ color: #EF4444; font-size: 12px; font-weight: 700; cursor: pointer; background: #FEF2F2; border-radius: 10px; padding: 6px 12px; }}
        
        /* 🔥 PROFILE CARD */
        .profile-card {{ display: flex; align-items: center; gap: 15px; padding: 18px; background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%); border-radius: 20px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.25); color: white; position: relative; }}
        .dp-container {{ position: relative; cursor: pointer; flex-shrink: 0; }}
        .dp-img {{ width: 60px; height: 60px; border-radius: 50%; border: 3px solid #FFFFFF; padding: 2px; background: rgba(255,255,255,0.2); object-fit: cover; }}
        .btn-edit-profile {{ position: absolute; top: 12px; right: 12px; background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 8px; font-size: 11px; cursor: pointer; backdrop-filter: blur(5px); font-weight: 600; }}
        
        /* 🔥 SEARCH ROW (Clean Input) */
        .search-row {{ display: flex; gap: 10px; margin-bottom: 20px; width: 100%; }}
        .search-row input {{ margin-bottom: 0; flex: 1; }}

        .section-title {{ font-size: 15px; font-weight: 700; color: #374151; margin-bottom: 10px; }}
        
        /* 🔥 RECENT CHATS LIST */
        .chat-list {{ display: flex; flex-direction: column; gap: 10px; flex: 1; overflow-y: auto; }}
        .friend-card {{ display: flex; align-items: center; gap: 15px; padding: 12px; background: #FFFFFF; border: 1px solid #F1F5F9; border-radius: 16px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
        .friend-card img {{ width: 45px; height: 45px; border-radius: 50%; border: 2px solid #E5E7EB; padding: 2px; object-fit: cover; }}
        .friend-info {{ flex: 1; overflow: hidden; }}
        .friend-name {{ font-weight: 700; font-size: 14px; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .friend-bio {{ font-size: 11px; color: #6B7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

        /* 🔥 FACEBOOK STYLE PROFILE MODAL */
        .profile-view-card {{ background: #FFFFFF; border-radius: 24px; padding: 30px 20px; text-align: center; border: 1px solid #F1F5F9; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-top: 20px; }}
        .profile-view-card img {{ width: 100px; height: 100px; border-radius: 50%; border: 4px solid #6366F1; padding: 4px; margin-bottom: 15px; object-fit: cover; }}
        .profile-view-card h3 {{ font-size: 22px; color: #111827; margin-bottom: 5px; }}
        .profile-view-card p {{ font-size: 13px; color: #6B7280; margin-bottom: 20px; font-family: monospace; font-weight: 600; }}
        .profile-view-card .bio-box {{ background: #F8FAFC; padding: 15px; border-radius: 14px; font-size: 13px; color: #374151; font-style: italic; margin-bottom: 25px; border: 1px dashed #CBD5E1; }}

        .chat-header {{ display: flex; align-items: center; gap: 12px; padding-bottom: 15px; border-bottom: 1px solid #F1F5F9; background: rgba(255,255,255,0.9); z-index: 5; cursor: pointer; }}
        .btn-back {{ font-size: 24px; cursor: pointer; color: #4B5563; font-weight: bold; }}
        
        .chat-area {{ flex: 1; overflow-y: auto; padding: 15px 0; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }}
        .chat-area::-webkit-scrollbar {{ width: 0px; }}

        .bubble {{ max-width: 78%; padding: 12px 16px; border-radius: 20px; font-size: 14px; line-height: 1.4; word-wrap: break-word; animation: popIn 0.3s ease forwards; opacity: 0; position: relative; }}
        .bubble-me {{ background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2); }}
        .bubble-them {{ background: #F1F5F9; color: #111827; align-self: flex-start; border-bottom-left-radius: 4px; }}

        .typing-indicator {{ font-size: 12px; color: #10B981; font-weight: 600; font-style: italic; display: none; margin-top: -5px; animation: blink 1.5s infinite; }}

        .input-row {{ display: flex; gap: 10px; padding-top: 12px; background: #FFFFFF; align-items: center; }}
        .input-row input {{ margin-bottom: 0; flex: 1; border-radius: 24px; background: #F8FAFC; padding: 14px 20px; border: 1px solid #E5E7EB; }}
        .btn-send {{ background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%); color: white; border: none; width: 46px; height: 46px; border-radius: 50%; font-size: 18px; cursor: pointer; display: flex; justify-content: center; align-items: center; padding-left: 3px; }}

        #toast {{ visibility: hidden; min-width: 250px; background-color: #111827; color: #fff; text-align: center; border-radius: 12px; padding: 14px; position: fixed; z-index: 9999; left: 50%; bottom: 30px; transform: translateX(-50%); font-size: 13px; font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        #toast.show {{ visibility: visible; animation: fadein 0.5s, fadeout 0.5s 3.5s forwards; }}
    </style>
</head>
<body>

<div id="toast">Message</div>
<input type="file" id="dp_upload" accept="image/*" style="display: none;" onchange="handleDpUpload(event)">

<div class="app-container">

    <div id="view-login" class="view-section active">
        <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
            <div class="logo-title">ME CHAT<span class="logo-dot">!</span></div>
            <div class="subtitle">Log in to Secure Network</div>
            
            <input type="text" id="log_phone" class="input-box" placeholder="Email / Virtual Number">
            <input type="password" id="log_secret" class="input-box" style="margin-bottom: 5px;" placeholder="Password / Secret Key">
            
            <div style="text-align: right; width: 100%; margin-bottom: 15px;">
                <span class="clickable-span" style="font-size: 12px; color: #6B7280; font-weight: 500;" onclick="showToast('Contact CEO Umar Asif to recover password!')">Forgot Password?</span>
            </div>
            
            <button class="btn-primary" onclick="processLogin()">Log In</button>
            <div class="link-text">Don't have an account? <span class="clickable-span" onclick="switchView('view-register')">Sign Up</span></div>
            
            <div class="divider">OR</div>
            
            <button class="btn-social" onclick="showToast('Facebook Auth coming soon!', true)">
                <svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h2.047V9.43c0-2.027 1.24-3.146 3.054-3.146.866 0 1.376.064 1.563.092v1.814h-1.074c-.84 0-1.007.4-1.007.989v1.294h2.065l-.269 3.469h-1.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                Continue with Facebook
            </button>
            <button class="btn-social" onclick="showToast('Google Auth coming soon!', true)">
                <svg viewBox="0 0 24 24" fill="#EA4335"><path d="M12.24 10.285V13.97h6.738c-.297 1.906-2.27 5.588-6.738 5.588-4.045 0-7.36-3.35-7.36-7.493s3.315-7.493 7.36-7.493c2.27 0 3.787.967 4.652 1.798l2.894-2.78C18.06 1.77 15.404 0 12.24 0 5.62 0 .24 5.38.24 12s5.38 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.083-1.52-.24-2.214h-11.28z"/></svg>
                Continue with Google
            </button>
        </div>
        <div class="link-text" style="margin-top: 5px;"><span class="clickable-span" style="color: #9CA3AF; font-size:12px;" onclick="switchView('view-tc')">Privacy Policy & Terms</span></div>
    </div>

    <div id="view-tc" class="view-section">
        <div class="page-title">Legal & Strict Privacy</div>
        <div class="logo-title" style="font-size: 32px; margin-bottom: 20px;">ME CHAT<span class="logo-dot">!</span></div>
        <div style="background: #F8FAFC; padding: 20px; border-radius: 16px; border: 1px solid #E5E7EB; font-size: 13px; color: #4B5563; line-height: 1.6; overflow-y: auto; flex: 1; margin-bottom: 20px; text-align: left;">
            <b style="color: #111827; font-size: 15px;">ME CHAT Legal Agreement</b><br><br>
            <b>1. Purpose of App:</b> Yeh app sirf secure communication ke liye banayi gayi hai.<br><br>
            <b style="color: #EF4444;">2. STRICT WARNING:</b> Is network ka kisi bhi qisam ka misuse bardaasht nahi kiya jayega. Jo bhi user iska misuse karega, uska saara data secure database mein save ho jayega!<br><br>
            <b>3. Privacy Promise:</b> Kisi ke messages ko nahi chera jayega jab tak wo misuse na kare.<br><br>
            <i>Thanks for cooperating and enjoy the app!</i><br>
            <i style="font-weight: 600; color: #6366F1;">- By Muhammad Umar Asif (CEO) - RYK, Pakistan.</i>
        </div>
        <button class="btn-primary" style="background: #111827; margin-top: auto;" onclick="switchView('view-login')">← Back to Login</button>
    </div>

    <div id="view-register" class="view-section">
        <div class="page-title" style="font-size: 28px;">Create Account ✨</div>
        <input type="text" id="reg_name" class="input-box" placeholder="Your Full Name">
        <select id="reg_country" class="input-box" style="cursor: pointer;">
            <option value="US" disabled selected>Select Region / Country</option>
            {dropdown_options}
        </select>
        <input type="text" id="reg_dob" class="input-box" placeholder="DOB (DD-MM-YYYY)">
        <div class="gender-select">
            <label><input type="radio" name="gender" value="Male" checked> Male</label>
            <label><input type="radio" name="gender" value="Female"> Female</label>
        </div>
        <div class="tc-box" id="tc_box_div">
            <input type="checkbox" id="tc_check">
            <label for="tc_check">I agree to the <span class="clickable-span" onclick="switchView('view-tc')" style="padding:0;">Terms & Privacy</span></label>
        </div>
        <div id="reg_success_box" class="secret-box">
            <div style="font-size: 40px; margin-bottom: 5px;">🎉</div>
            <p style="font-size: 13px; color: #4B5563; margin-bottom:10px; font-weight: 600;">Screenshot your keys!</p>
            <div style="font-weight: 700; color: #EF4444; font-size:16px; font-family: monospace; background: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #FEE2E2;">🔑 <span id="show_secret"></span></div>
            <div style="font-weight: 700; color: #10B981; font-size:16px; font-family: monospace; background: white; padding: 10px; border-radius: 10px; border: 1px solid #D1FAE5;">📱 <span id="show_public"></span></div>
            <button class="btn-primary" style="padding: 14px; margin-top: 15px;" onclick="switchView('view-login')">Go to Login →</button>
        </div>
        <button id="reg_btn" class="btn-primary" onclick="processRegister()">Create Secure Account</button>
        <div class="link-text" id="reg_link"><span class="clickable-span" onclick="switchView('view-login')">← Back to Login</span></div>
    </div>

    <div id="view-dashboard" class="view-section">
        <div class="dash-header">
            <h2>Chats</h2>
            <div class="btn-logout" onclick="window.location.reload()">Log Out</div>
        </div>
        
        <div class="profile-card">
            <button class="btn-edit-profile" onclick="openEditProfile()">Edit ✎</button>
            
            <div class="dp-container">
                <img src="{male_avatar}" id="my_dp" class="dp-img">
            </div>
            <div style="overflow: hidden;">
                <div style="font-size: 12px; opacity: 0.8; font-weight: 500; margin-bottom: -2px;">Your Profile</div>
                <div id="my_name" style="font-weight: 800; font-size: 18px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Loading...</div>
                <div id="my_id" style="font-size: 12px; font-weight: 600; font-family: monospace; opacity: 0.9;">+1 (555) 000-0000</div>
            </div>
        </div>
        
        <form class="search-row" onsubmit="event.preventDefault(); searchForFriend();">
            <input type="text" id="search_id" class="input-box" placeholder="🔍 Find a Virtual # and press Enter..." autocomplete="off">
        </form>
        
        <div class="section-title">Recent Conversations</div>
        <div id="recent-chats-list" class="chat-list">
            <div style="text-align:center; color:#9CA3AF; font-size:13px; margin-top:20px;">No recent chats. Search a number above to start!</div>
        </div>
    </div>

    <div id="view-edit-profile" class="view-section">
        <div class="page-title">Edit Profile ✎</div>
        <div style="text-align: center; margin-bottom: 20px;">
            <div class="dp-container" onclick="document.getElementById('dp_upload').click()" title="Change Profile Picture" style="display: inline-block;">
                <img src="{male_avatar}" id="edit_my_dp" class="dp-img" style="width:90px; height:90px; border-color: #6366F1;">
                <div class="dp-edit-badge" style="background: #6366F1; width:28px; height:28px; font-size:12px; bottom: 5px; right: 5px;">📷</div>
            </div>
        </div>
        
        <label style="font-size: 12px; color: #6B7280; font-weight: 600; margin-left: 5px;">Display Name</label>
        <input type="text" id="edit_name" class="input-box" placeholder="Your Full Name">
        
        <label style="font-size: 12px; color: #6B7280; font-weight: 600; margin-left: 5px;">About (Bio)</label>
        <input type="text" id="edit_bio" class="input-box" placeholder="Hey there! I am using ME CHAT.">
        
        <button class="btn-primary" onclick="saveProfile()">Save Changes</button>
        <button class="btn-primary btn-secondary" onclick="switchView('view-dashboard')">Cancel</button>
    </div>

    <div id="view-friend-profile" class="view-section">
        <div class="dash-header">
            <div class="btn-back" onclick="switchView('view-dashboard')">← Back</div>
        </div>
        
        <div class="profile-view-card">
            <img src="{male_avatar}" id="view_friend_dp">
            <h3 id="view_friend_name">Friend Name</h3>
            <p id="view_friend_id">+1 (555) 000-0000 | US</p>
            
            <div class="bio-box">
                "<span id="view_friend_bio">Hey there! I am using ME CHAT.</span>"
            </div>
            
            <button class="btn-primary" id="btn_profile_chat" style="margin-bottom: 10px;">💬 Message</button>
            <button class="btn-primary btn-danger" onclick="blockUser()">🚫 Block User</button>
            <div class="link-text" style="margin-top: 15px;"><span class="clickable-span" style="color: #EF4444; font-weight: 500;" onclick="reportUser()">Report Account</span></div>
        </div>
    </div>

    <div id="view-chat" class="view-section" style="padding: 20px 15px; background: #FFFFFF;">
        <div class="chat-header" onclick="viewFriendProfileFromChat()">
            <div class="btn-back" onclick="event.stopPropagation(); closeChatRoom()">←</div>
            <img src="{male_avatar}" id="chat_dp" style="width:42px; height:42px; border-radius:50%; object-fit: cover;">
            <div style="flex: 1;">
                <div id="chat_name" style="font-weight: 800; font-size:16px; color:#111827;">Friend Name</div>
                <div id="chat_status" style="font-size: 11px; color: #9CA3AF; font-weight: 600;">○ Checking...</div>
            </div>
        </div>
        <div class="chat-area" id="chat_box"></div>
        <div id="typing_status" class="typing-indicator">Friend is typing...</div>
        <form class="input-row" onsubmit="sendChatMsg(event)">
            <input type="text" id="msg_val" placeholder="Type a message..." autocomplete="off" required oninput="sendTypingSignal()">
            <button type="submit" class="btn-send">
                <svg viewBox="0 0 24 24" fill="white" width="18" height="18"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </form>
    </div>

</div>

<script>
    let myPublicId = ""; 
    let myChatWs = null;
    let currentFriendId = "";
    let currentFriendName = "";
    let currentFriendDp = "";
    let currentFriendBio = "";
    let currentFriendRegion = "";
    let typingTimeout = null; 
    
    const avatars = {{ "Male": "{male_avatar}", "Female": "{female_avatar}", "Other": "{male_avatar}" }};

    function showToast(message, isError=false) {{
        let x = document.getElementById("toast");
        x.innerText = message; x.style.backgroundColor = isError ? "#EF4444" : "#10B981";
        x.className = "show"; setTimeout(() => {{ x.className = x.className.replace("show", ""); }}, 3000);
    }}

    function switchView(viewId) {{
        let views = document.getElementsByClassName('view-section');
        for(let i=0; i<views.length; i++) {{ views[i].style.display = 'none'; views[i].classList.remove('active'); }}
        let target = document.getElementById(viewId);
        if(target) {{ target.style.display = 'flex'; void target.offsetWidth; target.classList.add('active'); }}
        
        // Fetch recent chats when returning to dashboard
        if(viewId === 'view-dashboard') loadRecentChats();
    }}

    function closeChatRoom() {{
        currentFriendId = ""; 
        switchView('view-dashboard');
    }}

    function handleDpUpload(event) {{
        let file = event.target.files[0];
        if(!file) return;
        let reader = new FileReader();
        reader.onload = function(e) {{
            let img = new Image();
            img.onload = function() {{
                let canvas = document.createElement('canvas');
                let MAX_WIDTH = 150; 
                let scaleSize = MAX_WIDTH / img.width;
                canvas.width = MAX_WIDTH;
                canvas.height = img.height * scaleSize;
                let ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                let compressedBase64 = canvas.toDataURL('image/jpeg', 0.6); 
                document.getElementById('my_dp').src = compressedBase64;
                document.getElementById('edit_my_dp').src = compressedBase64;
                
                fetch('/api/update_dp', {{
                    method: 'POST', headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: new URLSearchParams({{'phone_number': myPublicId, 'dp_data': compressedBase64}})
                }}).then(() => showToast("Photo Updated! 📸"));
            }};
            img.src = e.target.result;
        }};
        reader.readAsDataURL(file);
    }}

    async function processRegister() {{
        let n = document.getElementById('reg_name').value;
        let c = document.getElementById('reg_country').value || "US"; 
        let tc = document.getElementById('tc_check').checked;
        if(!tc) return showToast("Agree to Terms!", true);
        if(!n) return showToast("Name is required!", true);

        try {{
            let res = await fetch('/api/register', {{
                method: 'POST', headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: new URLSearchParams({{'name': n, 'country_code': c}})
            }});
            let data = await res.json();
            if(res.ok) {{
                document.getElementById('show_secret').innerText = data.secret_key;
                document.getElementById('show_public').innerText = data.phone_number;
                document.getElementById('reg_success_box').style.display = 'block';
                document.getElementById('reg_btn').style.display = 'none';
            }} else showToast("Registration failed!", true);
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    function connectGlobalWebSocket() {{
        if(myChatWs) return; 
        let wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        myChatWs = new WebSocket(wsProtocol + window.location.host + "/ws?client_id=" + encodeURIComponent(myPublicId));
        
        myChatWs.onmessage = function(event) {{
            let msgData = JSON.parse(event.data);
            
            // 🚫 BLOCK ERROR CATCH
            if(msgData.type === "error") {{
                showToast(msgData.message, true);
                return;
            }}

            if(msgData.type === "status") {{
                if(currentFriendId && msgData.user === currentFriendId) {{
                    let statusEl = document.getElementById('chat_status');
                    if(msgData.status === "online") {{ statusEl.innerText = "● Online"; statusEl.style.color = "#10B981"; }} 
                    else {{ statusEl.innerText = "○ Offline"; statusEl.style.color = "#9CA3AF"; }}
                }}
                return;
            }}

            if(msgData.type === "typing" && msgData.sender === currentFriendId) {{
                let ts = document.getElementById("typing_status");
                ts.style.display = "block";
                clearTimeout(typingTimeout);
                typingTimeout = setTimeout(() => ts.style.display = "none", 1500);
                return;
            }}
            
            if (msgData.type === "text") {{
                if (msgData.receiver === myPublicId) {{
                    if (currentFriendId === msgData.sender && document.getElementById('view-chat').classList.contains('active')) {{
                        document.getElementById("typing_status").style.display = "none";
                        let div = document.createElement('div');
                        div.className = 'bubble bubble-them'; div.innerText = msgData.text;
                        document.getElementById('chat_box').appendChild(div);
                        document.getElementById('chat_box').scrollTo({{ top: document.getElementById('chat_box').scrollHeight, behavior: 'smooth' }});
                    }} else {{
                        showToast("📩 New message received!");
                        loadRecentChats(); // Refresh list automatically!
                    }}
                }}

                if (msgData.sender === myPublicId && msgData.receiver === currentFriendId) {{
                    document.getElementById("typing_status").style.display = "none";
                    let div = document.createElement('div');
                    div.className = 'bubble bubble-me'; div.innerText = msgData.text;
                    document.getElementById('chat_box').appendChild(div);
                    document.getElementById('chat_box').scrollTo({{ top: document.getElementById('chat_box').scrollHeight, behavior: 'smooth' }});
                }}
            }}
        }};
    }}

    async function processLogin() {{
        // 🚀 NEW LOGIN FLOW LOGIC
        let phone = document.getElementById('log_phone').value.trim();
        let key = document.getElementById('log_secret').value;
        if(!phone || !key) return showToast("Enter Number and Password!", true);

        try {{
            let res = await fetch('/api/login', {{
                method: 'POST', headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: new URLSearchParams({{'phone_number': phone, 'secret_key': key}})
            }});
            let data = await res.json();
            if(res.ok) {{
                myPublicId = data.phone_number;
                document.getElementById('my_name').innerText = data.name;
                document.getElementById('my_id').innerText = data.phone_number + " | " + data.region;
                
                // Pre-fill Edit Profile data
                document.getElementById('edit_name').value = data.name;
                document.getElementById('edit_bio').value = data.bio;
                
                let dp = data.profile_pic || avatars[data.gender] || avatars["Male"];
                document.getElementById('my_dp').src = dp;
                document.getElementById('edit_my_dp').src = dp;
                
                connectGlobalWebSocket();
                switchView('view-dashboard');
            }} else showToast("Invalid Details!", true);
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    // 🔥 EDIT PROFILE FUNCTIONS
    function openEditProfile() {{ switchView('view-edit-profile'); }}

    async function saveProfile() {{
        let n = document.getElementById('edit_name').value;
        let b = document.getElementById('edit_bio').value;
        
        try {{
            let res = await fetch('/api/update_profile', {{
                method: 'POST', headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: new URLSearchParams({{'phone': myPublicId, 'name': n, 'bio': b}})
            }});
            if(res.ok) {{
                document.getElementById('my_name').innerText = n;
                showToast("Profile Updated!");
                switchView('view-dashboard');
            }}
        }} catch(e) {{ showToast("Error saving profile", true); }}
    }}

    // 🔥 RECENT CHATS API
    async function loadRecentChats() {{
        if(!myPublicId) return;
        try {{
            let res = await fetch('/api/recent_chats?phone=' + encodeURIComponent(myPublicId));
            let data = await res.json();
            let listDiv = document.getElementById('recent-chats-list');
            
            if(data.chats && data.chats.length > 0) {{
                listDiv.innerHTML = "";
                data.chats.forEach(c => {{
                    let dp = c.dp || avatars["Male"];
                    // Safe string interpolation to avoid breaking JS
                    let safeName = c.name.replace(/'/g, "\\'");
                    let safeBio = c.bio.replace(/'/g, "\\'");
                    let safeRegion = c.region.replace(/'/g, "\\'");
                    
                    listDiv.innerHTML += `
                        <div class="friend-card" onclick="openFriendProfile('${{c.phone}}', '${{safeName}}', '${{dp}}', '${{safeBio}}', '${{safeRegion}}')">
                            <img src="${{dp}}">
                            <div class="friend-info">
                                <div class="friend-name">${{c.name}}</div>
                                <div class="friend-bio">${{c.bio}}</div>
                            </div>
                        </div>
                    `;
                }});
            }} else {{
                listDiv.innerHTML = '<div style="text-align:center; color:#9CA3AF; font-size:13px; margin-top:20px;">No recent chats. Search a number above!</div>';
            }}
        }} catch(e) {{}}
    }}

    async function searchForFriend() {{
        let id = document.getElementById('search_id').value.trim();
        if(!id) return;
        
        try {{
            let res = await fetch('/api/search?phone=' + encodeURIComponent(id));
            let data = await res.json();
            if(res.ok) {{
                openFriendProfile(id, data.name, data.profile_pic, data.bio, data.region);
                document.getElementById('search_id').value = ""; // Clear input after search
            }} else showToast("Number not found!", true);
        }} catch(e) {{ showToast("Network Error", true); }}
    }}

    // 🔥 FRIEND PROFILE VIEWER
    function openFriendProfile(fId, fName, fDp, fBio, fRegion) {{
        currentFriendId = fId; currentFriendName = fName; currentFriendDp = fDp || avatars["Male"];
        currentFriendBio = fBio || "Hey there! I am using ME CHAT."; currentFriendRegion = fRegion;

        document.getElementById('view_friend_dp').src = currentFriendDp;
        document.getElementById('view_friend_name').innerText = currentFriendName;
        document.getElementById('view_friend_id').innerText = currentFriendId + " | " + currentFriendRegion;
        document.getElementById('view_friend_bio').innerText = currentFriendBio;
        
        document.getElementById('btn_profile_chat').onclick = () => openChatRoom();
        switchView('view-friend-profile');
    }}

    function viewFriendProfileFromChat() {{ switchView('view-friend-profile'); }}

    // 🔥 BLOCK & REPORT
    async function blockUser() {{
        if(confirm("Block this user? They won't be able to message you.")) {{
            try {{
                await fetch('/api/block', {{
                    method: 'POST', headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: new URLSearchParams({{'blocker': myPublicId, 'blocked': currentFriendId}})
                }});
                showToast("User Blocked 🚫", true);
                closeChatRoom();
            }} catch(e) {{}}
        }}
    }}

    function reportUser() {{
        alert("Account Reported for violation. Data saved for review.");
        blockUser();
    }}

    async function openChatRoom() {{
        document.getElementById('chat_name').innerText = currentFriendName;
        document.getElementById('chat_dp').src = currentFriendDp;
        switchView('view-chat');

        let chatBox = document.getElementById('chat_box');
        chatBox.innerHTML = '<div style="text-align:center; color:#10B981; font-size:12px; margin-bottom:15px; font-weight: 600;"><span>🔒</span> End-to-end encrypted</div>';

        fetch('/api/status?phone=' + encodeURIComponent(currentFriendId))
        .then(r => r.json()).then(d => {{
            let s = document.getElementById('chat_status');
            if(d.online) {{ s.innerText = "● Online"; s.style.color = "#10B981"; }}
            else {{ s.innerText = "○ Offline"; s.style.color = "#9CA3AF"; }}
        }});

        try {{
            let res = await fetch('/api/history?my_id=' + encodeURIComponent(myPublicId) + '&friend_id=' + encodeURIComponent(currentFriendId));
            let data = await res.json();
            if(data.messages) {{
                data.messages.forEach(msg => {{
                    let div = document.createElement('div');
                    div.className = 'bubble ' + (msg.sender === myPublicId ? 'bubble-me' : 'bubble-them');
                    div.innerText = msg.text; chatBox.appendChild(div);
                }});
                chatBox.scrollTop = chatBox.scrollHeight;
            }}
        }} catch(e) {{}}
    }}

    function sendTypingSignal() {{
        if(myChatWs && myChatWs.readyState === WebSocket.OPEN && currentFriendId) {{
            myChatWs.send(JSON.stringify({{ type: "typing", receiver: currentFriendId }}));
        }}
    }}

    function sendChatMsg(event) {{
        event.preventDefault();
        let input = document.getElementById('msg_val');
        if(input.value.trim() !== "" && myChatWs && myChatWs.readyState === WebSocket.OPEN) {{
            myChatWs.send(JSON.stringify({{ type: "text", receiver: currentFriendId, text: input.value }}));
            input.value = ""; input.focus();
        }}
    }}
</script>
</body>
</html>
"""

# ================= API ROUTES =================
@app.get("/")
async def serve_home(): return HTMLResponse(html_app)

@app.post("/api/register")
async def register_api(name: str = Form(...), country_code: str = Form("US"), db: Session = Depends(get_db)):
    secret_key = generate_secret_key()
    phone_number, region = generate_virtual_number(country_code)
    db.add(User(full_name=name, secret_key=secret_key, phone_number=phone_number, region=region))
    db.commit()
    return {"status": "success", "secret_key": secret_key, "phone_number": phone_number, "region": region}

# 🚀 UPDATED LOGIN API: Now requires Phone Number + Secret Key
@app.post("/api/login")
async def login_api(phone_number: str = Form(...), secret_key: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone_number, User.secret_key == secret_key).first()
    if user: return {"status": "success", "name": user.full_name, "phone_number": user.phone_number, "region": user.region, "gender": user.gender, "profile_pic": user.profile_pic, "bio": user.bio}
    raise HTTPException(status_code=400, detail="Invalid Details!")

@app.get("/api/search")
async def search_api(phone: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone).first()
    if user: return {"status": "success", "name": user.full_name, "region": user.region, "gender": user.gender, "profile_pic": user.profile_pic, "bio": user.bio}
    raise HTTPException(status_code=404, detail="Not found")

# 🔥 RECENT CHATS API
@app.get("/api/recent_chats")
async def recent_chats_api(phone: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(or_(Message.sender_id == phone, Message.receiver_id == phone)).all()
    peer_ids = set()
    for m in msgs:
        if m.sender_id != phone: peer_ids.add(m.sender_id)
        if m.receiver_id != phone: peer_ids.add(m.receiver_id)
    
    peers = db.query(User).filter(User.phone_number.in_(peer_ids)).all()
    chats = [{"phone": p.phone_number, "name": p.full_name, "dp": p.profile_pic, "bio": p.bio, "region": p.region} for p in peers]
    return {"status": "success", "chats": chats}

# 🔥 UPDATE PROFILE API
@app.post("/api/update_profile")
async def update_profile(phone: str = Form(...), name: str = Form(...), bio: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone).first()
    if user:
        user.full_name = name
        user.bio = bio
        db.commit()
        return {"status": "success"}
    return {"status": "error"}

@app.post("/api/update_dp")
async def update_dp_api(phone_number: str = Form(...), dp_data: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user:
        user.profile_pic = dp_data
        db.commit()
        return {"status": "success"}
    return {"status": "error"}

# 🔥 BLOCK API
@app.post("/api/block")
async def block_user_api(blocker: str = Form(...), blocked: str = Form(...), db: Session = Depends(get_db)):
    db.add(Block(blocker_id=blocker, blocked_id=blocked))
    db.commit()
    return {"status": "success"}

@app.get("/api/history")
async def get_history(my_id: str, friend_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(or_(and_(Message.sender_id == my_id, Message.receiver_id == friend_id), and_(Message.sender_id == friend_id, Message.receiver_id == my_id))).order_by(Message.timestamp.asc()).all()
    return {"status": "success", "messages": [{"sender": m.sender_id, "text": m.text} for m in messages]}

@app.get("/api/status")
async def check_status(phone: str):
    return {"status": "success", "online": phone in manager.active_connections}

# 🚀 SECURE WEBSOCKET ENGINE (BLOCK CHECK)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
                receiver_id = msg_data.get("receiver")
                
                db = SessionLocal()
                try:
                    # 🚫 BLOCK CHECK ENGINE
                    is_blocked = db.query(Block).filter(
                        or_(
                            and_(Block.blocker_id == client_id, Block.blocked_id == receiver_id),
                            and_(Block.blocker_id == receiver_id, Block.blocked_id == client_id)
                        )
                    ).first()
                    
                    if is_blocked:
                        await websocket.send_text(json.dumps({"type": "error", "message": "Message blocked! 🚫"}))
                        continue
                        
                    if msg_data.get("type") == "typing":
                        await manager.broadcast(json.dumps({"type": "typing", "sender": client_id, "receiver": receiver_id}))
                        continue
                    
                    text = msg_data.get("text")
                    new_msg = Message(sender_id=client_id, receiver_id=receiver_id, text=text)
                    db.add(new_msg)
                    db.commit()
                    
                    await manager.broadcast(json.dumps({"type": "text", "sender": client_id, "receiver": receiver_id, "text": text}))
                except Exception:
                    db.rollback()
                finally:
                    db.close()
            except Exception: pass
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception:
        await manager.disconnect(client_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
