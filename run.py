import os
from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.secret_key = 'This shoudl be a secret!'
app.url_map.strict_slashes = False

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route('/ready/', methods=['GET', 'POST'])
def ready():
    if request.method == 'POST':
        form = request.form
        user = form['username']
        return render_template("ready.html", username=user)
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
    
@app.route('/riddleme/<username>', methods=['GET', 'POST'])
def riddleme(username):
    if request.method == 'POST':
        riddle_index = int(request.form.get('riddle_index', 0))
        while riddle_index < 10:
            riddle_index += 1
            context = {
                'username': username,
                'riddle_index': riddle_index
            }
            return render_template('riddle.html', context=context)
        return redirect('/')
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
        
        
    
app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)