from flask import Flask, render_template, request, jsonify, url_for
from login import login_bp
from signup import signup_bp

app = Flask(__name__)
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)

@app.route('/')
def index():
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Emergency Healthcare</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manuale:wght@700&display=swap');
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #d5ecfc;
                text-align: center;
            }}
            .navbar {{
                background-color: #002147;
                padding: 15px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                position: relative;
                z-index: 1002;
            }}
            .left-section {{
                display: flex;
                align-items: center;
            }}
            .logo {{
                width: 40px;
                height: 40px;
                background-color: yellow;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-left: 10px;
            }}
            .emergency-btn {{
                background-color: yellow;
                border: none;
                padding: 10px 20px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 20px;
                cursor: pointer;
                margin-left: 20px;
            }}
            .dots-icon {{
                width: 30px;
                height: 30px;
                cursor: pointer;
                color: white;
                margin-right: 10px;
                position: relative;
                z-index: 1002;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 80vh;
            }}
            .title {{
                font-size: 32px;
                font-weight: bold;
                font-family: 'Manuale', serif;
                margin-bottom: 20px;
            }}
            .input-box {{
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: white;
                padding: 10px;
                border-radius: 20px;
                width: 60%;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .input-box input {{
                border: none;
                outline: none;
                flex-grow: 1;
                padding: 10px;
                font-size: 16px;
                border-radius: 20px;
            }}
            .mic-icon {{
                width: 24px;
                height: 24px;
                cursor: pointer;
            }}
            .overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
            }}
            .emergency-menu {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
                text-align: left;
                width: 300px;
                z-index: 1001;
                animation: fadeIn 0.3s ease-in-out;
            }}
            .more-menu {{
                display: none;
                position: fixed;
                top: 0;
                right: 0;
                width: 500px;
                height: 100%;
                background: white;
                box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
                z-index: 1001;
                animation: slideIn 0.3s ease-in-out;
                padding-top: 80px;
            }}
            .more-menu button {{
                display: block;
                width: 100%;
                padding: 20px 25px;
                border: none;
                background: none;
                font-size: 18px;
                text-align: left;
                cursor: pointer;
                transition: background-color 0.3s;
                color: #002147;
            }}
            .more-menu button:hover {{
                background-color: #f0f0f0;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            @keyframes slideIn {{
                from {{ transform: translateX(100%); }}
                to {{ transform: translateX(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="left-section">
                <div class="logo">L</div>
                <button class="emergency-btn">Emergency</button>
            </div>
            <img src="{url_for('static', filename='more.png')}" class="dots-icon" alt="Menu">
        </div>
        <div class="container">
            <div class="title">Healthcare App</div>
            <div class="input-box">
                <input type="text" placeholder="Enter your symptoms" />
                <img src="https://cdn-icons-png.flaticon.com/512/709/709682.png" class="mic-icon" alt="Mic">
            </div>
        </div>
        
        <div class="overlay" id="overlay"></div>
        <div class="emergency-menu" id="emergencyMenu">
            <h2>Emergency Services</h2>
            <p><span>Press 1</span> for Ambulance 🚑🚑</p>
            <p><span>Press 2</span> for Fire Department 🚒🚒</p>
            <p><span>Press 3</span> for Police 🚓🚓</p>
        </div>
        
        <div class="more-menu" id="moreMenu">
            <button onclick="window.location.href='/'">Main Menu</button>
            <button onclick="window.location.href='/login'">Log In</button>
            <button onclick="window.location.href='/signup'">Sign Up</button>
        </div>

        <script>
            document.querySelector('.dots-icon').addEventListener('click', function() {{
                const moreMenu = document.getElementById('moreMenu');
                const overlay = document.getElementById('overlay');
                if (moreMenu.style.display === 'block') {{
                    moreMenu.style.display = 'none';
                    overlay.style.display = 'none';
                }} else {{
                    moreMenu.style.display = 'block';
                    overlay.style.display = 'block';
                }}
            }});

            document.getElementById('overlay').addEventListener('click', function() {{
                const moreMenu = document.getElementById('moreMenu');
                const emergencyMenu = document.getElementById('emergencyMenu');
                moreMenu.style.display = 'none';
                emergencyMenu.style.display = 'none';
                this.style.display = 'none';
            }});

            document.querySelector('.emergency-btn').addEventListener('click', function() {{
                const emergencyMenu = document.getElementById('emergencyMenu');
                const overlay = document.getElementById('overlay');
                emergencyMenu.style.display = 'block';
                overlay.style.display = 'block';
            }});

            document.addEventListener("keydown", function(event) {{
                const emergencyMenu = document.getElementById("emergencyMenu");
                const overlay = document.getElementById("overlay");
                const moreMenu = document.getElementById("moreMenu");
                
                if (event.key === "Escape") {{
                    if (emergencyMenu.style.display === "block") {{
                        emergencyMenu.style.display = "none";
                        overlay.style.display = "none";
                    }} else if (moreMenu.style.display === "block") {{
                        moreMenu.style.display = "none";
                        overlay.style.display = "none";
                    }} else {{
                        emergencyMenu.style.display = "block";
                        overlay.style.display = "block";
                    }}
                }} else if (emergencyMenu.style.display === "block") {{
                    if (event.key === "1") {{
                        alert("Calling Ambulance...🚑🚑");
                        window.location.href = "/emergency/ambulance";
                    }} else if (event.key === "2") {{
                        alert("Calling Fire Department...🚒🚒");
                        window.location.href = "/emergency/fire";
                    }} else if (event.key === "3") {{
                        alert("Calling Police...🚓🚓");
                        window.location.href = "/emergency/police";
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    '''

@app.route('/emergency/<service>')
def emergency_redirect(service):
    return f"<h1>Redirecting to {service.capitalize()}...</h1>"

if __name__ == '__main__':
    app.run(debug=True)