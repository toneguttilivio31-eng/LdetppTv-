from flask import Flask, render_template_string, request, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = "supersecret_ldetpptv"

# --- Données utilisateur ---
users = {"Ldetpp":{"password":"ldetpp06","favorites":[],"history":[]}}

# --- Playlist française de base ---
channels = [
    {"name":"France 24","logo":"https://upload.wikimedia.org/wikipedia/commons/6/65/France_24_logo.svg","category":"Info","url":"https://static.france24.com/live/F24_FR_HI_HLS/live_web.m3u8"},
    {"name":"TV5MONDE","logo":"https://upload.wikimedia.org/wikipedia/commons/f/f3/TV5Monde_logo.svg","category":"Info","url":"https://pluzz.telerama.fr/live/tv5monde.m3u8"},
    {"name":"W9","logo":"https://upload.wikimedia.org/wikipedia/fr/6/63/W9_Logo_2016.png","category":"Divertissement","url":"https://example.com/w9.m3u8"},
    {"name":"TF1","logo":"https://upload.wikimedia.org/wikipedia/commons/0/0c/TF1_logo_2013.svg","category":"Divertissement","url":"https://example.com/tf1.m3u8"},
    {"name":"France 2","logo":"https://upload.wikimedia.org/wikipedia/commons/1/12/France_2_logo.svg","category":"Info","url":"https://example.com/france2.m3u8"}
]

# --- Routes ---
@app.route("/", methods=["GET","POST"])
def login():
    error=""
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if username in users and users[username]["password"]==password:
            session["user"]=username
            return redirect(url_for("home"))
        error="Identifiants incorrects"
    return render_template_string(login_html,error=error)

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("login"))

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    profile=session["user"]
    search=request.args.get("search","").lower()
    filtered=[c for c in channels if search in c["name"].lower()]
    categories={}
    for c in filtered:
        cat=c["category"]
        categories.setdefault(cat,[]).append(c)
    favs=users[profile]["favorites"]
    hist=users[profile]["history"]
    return render_template_string(home_html,categories=categories,profile=profile,favorites=favs,history=hist)

@app.route("/add_channel",methods=["POST"])
def add_channel():
    if "user" not in session:
        return redirect(url_for("login"))
    new={
        "name":request.form["name"],
        "logo":request.form["logo"],
        "category":request.form["category"],
        "url":request.form["url"]
    }
    channels.append(new)
    return redirect(url_for("home"))

@app.route("/toggle_favorite")
def toggle_favorite():
    if "user" not in session:
        return redirect(url_for("login"))
    name=request.args.get("name")
    profile=session["user"]
    favs=users[profile]["favorites"]
    if name in favs:
        favs.remove(name)
    else:
        favs.append(name)
    return ("",200)

@app.route("/add_history")
def add_history():
    if "user" not in session:
        return redirect(url_for("login"))
    name=request.args.get("name")
    profile=session["user"]
    hist=users[profile]["history"]
    if name not in hist:
        hist.append(name)
    return ("",200)

# --- HTML tout intégré ---
login_html="""
<!DOCTYPE html>
<html>
<head>
<title>LdetppTv — Connexion</title>
<style>
body{background:#111;color:white;font-family:Arial;text-align:center;padding:50px;}
input{padding:10px;margin:10px;width:200px;}
button{padding:10px;margin:10px;width:100px;background:#e50914;color:white;border:none;border-radius:5px;}
.error{color:red;}
</style>
</head>
<body>
<h1>LdetppTv</h1>
{% if error %}<p class="error">{{error}}</p>{% endif %}
<form method="post">
<input name="username" placeholder="Nom d’utilisateur" required><br>
<input type="password" name="password" placeholder="Mot de passe" required><br>
<button>Se connecter</button>
</form>
</body>
</html>
"""

home_html="""
<!DOCTYPE html>
<html>
<head>
<title>LdetppTv</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<style>
body{background:#111;color:white;font-family:Arial;margin:0;padding:0;}
header{display:flex;justify-content:space-between;padding:15px;background:#141414;}
header input{padding:5px;width:200px;}
.container{padding:20px;}
.category{margin-bottom:30px;}
.row{display:flex;overflow-x:auto;gap:15px;}
.card{background:#222;border-radius:8px;min-width:180px;padding:10px;position:relative;}
.card:hover{transform:scale(1.05);background:#e50914;}
.card img{width:100%;height:100px;object-fit:contain;border-radius:6px;}
.card p{margin:8px 0;font-size:14px;cursor:pointer;}
.fav{position:absolute;top:8px;right:10px;font-size:20px;cursor:pointer;}
#playerModal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);justify-content:center;align-items:center;}
video{width:85%;height:75%;}
.add-form{position:fixed;bottom:0;right:0;background:#222;padding:15px;border-top-left-radius:10px;}
.add-form input{display:block;margin:4px 0;width:200px;}
button{cursor:pointer;}
</style>
</head>
<body>
<header>
<h1>LdetppTv — {{profile}}</h1>
<input id="search" placeholder="Rechercher..." onkeyup="searchChannel()">
<a href="{{ url_for('logout') }}" style="color:white;">Déconnexion</a>
</header>
<div class="container">
{% for cat, items in categories.items() %}
<div class="category">
<h2>{{cat}}</h2>
<div class="row">
{% for c in items %}
<div class="card">
<img src="{{c.logo}}" onerror="this.src='https://via.placeholder.com/150'">
<p onclick="play('{{c.url}}','{{c.name}}')">{{c.name}}</p>
<span class="fav" onclick="toggleFav('{{c.name}}',event)">{% if c.name in favorites %}❤️{% else %}🤍{% endif %}</span>
</div>
{% endfor %}
</div>
</div>
{% endfor %}
</div>
<div id="playerModal">
<span class="close" onclick="closePlayer()" style="color:white;font-size:30px;position:absolute;top:10px;right:20px;cursor:pointer;">×</span>
<video id="player" controls autoplay></video>
</div>
<div class="add-form">
<form method="post" action="{{ url_for('add_channel') }}">
<input name="name" placeholder="Nom de la chaîne" required>
<input name="logo" placeholder="URL du logo">
<input name="category" placeholder="Catégorie">
<input name="url" placeholder="URL du flux m3u8" required>
<button>Ajouter</button>
</form>
</div>
<script>
function play(url,name){
    const modal=document.getElementById("playerModal")
    const video=document.getElementById("player")
    modal.style.display="flex"
    if(Hls.isSupported()){
        const hls=new Hls()
        hls.loadSource(url)
        hls.attachMedia(video)
    }else{video.src=url}
}
function closePlayer(){document.getElementById("playerModal").style.display="none"}
function toggleFav(name,event){event.stopPropagation();fetch('/toggle_favorite?name='+encodeURIComponent(name)).then(()=>location.reload())}
function searchChannel(){
    const input=document.getElementById("search").value.toLowerCase()
    document.querySelectorAll(".card p").forEach(p=>{
        p.parentElement.style.display = p.innerText.toLowerCase().includes(input)?"block":"none"
    })
}
</script>
</body>
</html>
"""

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
