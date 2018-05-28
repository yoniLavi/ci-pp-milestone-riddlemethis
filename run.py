import os
from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.secret_key = 'This shoudl be a secret!'

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/ready/', methods=['GET', 'POST'])
def ready():
    if request.method == 'POST':
        form = request.form
        user = form['username']
        return render_template("riddle.html", username=user)
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
    
app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)