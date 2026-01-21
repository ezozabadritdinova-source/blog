import hashlib

from flask import (
    Flask, 
    render_template , 
    request, 
    session,
    make_response,
    redirect
)
from articles import Article

app = Flask(__name__)
app.secret_key = "your_secret_key"

articles = Article.all()

users = {
    "admin": "7b4434313f4ace2ee5ce6b4374551073c6c3310faee6062dddc1bb16404c414a"
}

@app.route("/")
def home():
    return render_template("home.html", articles=articles)

@app.route("/admin")
def admin():
    if "user_id" in session:
        return "You are logged in!"
    return render_template("login.html")

@app.get("/logout")
def logout():
    session.pop("user_id", None)
    return "You have been logged out."

@app.post("/admin")
def admin_login():
    username = request.form["username"]
    password = request.form["password"]

    if username not in users:
        return render_template("login.html", error="Invalid username or password.")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if users[username] != hashed_password:
        return render_template("login.html", error="Invalid username or password.")
    
    session["user_id"] = username
    return "You are logged in!"

@app.route("/set-session")
def set_session():
    session["user_id"] = "admin"
    return "Session set!"

@app.route("/get-session")
def get_session():
    user_id = session.get("user_id", None)
    return f"User ID in session is: {user_id}"

@app.route("/first-time")
def first_time():
    if "seen" not in request.cookies:
        response = make_response('you are visiting for the first time!')
        response.set_cookie("seen", "1")
        return response
    
    seen = int (request.cookies.get("seen"))
    response = make_response(f'I have seen you {seen+1} times before!')
    response.set_cookie("seen", str(seen+1))
    return response

@app.route("/blog/<slug>")
def article(slug: str):
    if slug not in articles:
        return "Article not found", 404
    
    article = articles[slug]
    return render_template("article.html",article=article)

@app.route("/publish")
def publish():
    if "user_id" not in session:
        return redirect("/admin")
    return render_template("publish.html")

@app.post("/publish")
def publish_post():
    if "user_id" not in session:
        return redirect("/admin")
    
    title = request.form["title"]
    content = request.form["content"]

    with open(f"articles/{title}", "w") as file:
        file.write(content)
    global articles
    articles = Article.all()
    
    return redirect(f"/blog/{Article(title).slug}")

if __name__ == "__main__":
    app.run(port=1488, debug=True)