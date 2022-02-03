from flask import Flask, render_template, request, redirect, url_for
from firebase import firebase
from datetime import datetime

app = Flask(__name__)
database_url = open("database.txt", "r")
firebase = firebase.FirebaseApplication(database_url.read(), None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/submit', methods=["GET", "POST"])
def submit():
    userinfo = firebase.get("/users", None)
    if (request.method == "POST" and "register" in request.referrer):
        username_exists = False
        userdata = dict(request.form)

        username = userdata['username'][0]
        password = userdata['password'][0]

        new_data = {
            "username":username,
            "password":password
        }

        for user in list(userinfo.values()):
            if username in user['username']:
                username_exists = True

        if (username_exists == False):
            firebase.post("/users", new_data)
            return "Account registered succesfully!"
        elif (username_exists == True):
            return "Username already exists. Please try again!"

    elif (request.method == "POST" and "register" not in request.referrer):
        logindata = dict(request.form)

        givenusername = logindata['username'][0]
        givenpassword = logindata['password'][0]

        givendata = {
            "password":givenpassword,
            "username":givenusername
        }

        if (givendata in userinfo.values()):
            return redirect(url_for('home', givenusername=givenusername))
        else:
            return "Login not successful. Try again!"
    else:
        return "Error!"

@app.route('/home/<givenusername>', methods=['GET', 'POST'])
def home(givenusername):
    if request.referrer:
        if "/update/" in request.referrer:
            task_id = request.referrer[-20:]
            updated_content = dict(request.form).get("content")[0]
            updated_data = {
                "content":updated_content,
                "date-added":firebase.get(f'/tasks/{givenusername}/{task_id}/date-added', None)
            }
            firebase.patch(f'/tasks/{givenusername}/{task_id}', updated_data)
        tasks = firebase.get(f'/tasks/{givenusername}', None) or {}
        tasks_values = list(tasks.values())
        tasks_ids = list(tasks.keys())
        return render_template('home.html', username=givenusername, tasks=tasks_values, task_ids=tasks_ids)
    else:
        return "You are not logged in!"

@app.route('/submit-task/<givenusername>', methods=['GET', 'POST'])
def submit_task(givenusername):
    if request.method == "POST":
            user_task = dict(request.form).get("task-content")[0]
            task_data = {
                "content":user_task,
                "date-added": datetime.utcnow().date()
            }
            firebase.post(f'/tasks/{givenusername}', task_data)
            return redirect(url_for('home', givenusername=givenusername))

@app.route('/delete/<givenusername>/<taskid>')
def delete(givenusername, taskid):
    firebase.delete(f'/tasks/{givenusername}/{taskid}', None)
    return redirect(url_for('home', givenusername=givenusername))

@app.route('/update/<givenusername>/<taskid>')
def update(givenusername, taskid):
    task_to_update = firebase.get(f'/tasks/{givenusername}/{taskid}', None)
    content_to_update = task_to_update.get("content")
    return render_template('update.html', givenusername=givenusername, content=content_to_update)

if (__name__ == "__main__"):
    app.run(debug=True)