import os
import json
from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.secret_key = 'This shoudl be a secret!'
app.url_map.strict_slashes = False

def get_riddle(index):
    with open('data/riddles.json') as json_riddles:
        riddles = json.loads(json_riddles.read())
        return [riddle for riddle in riddles if riddle['index'] == index]
        
        

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
        form = request.form
        if form.get('first-question') == 'true':
            score = 0
            attempt = 1
            riddle = get_riddle(1)[0]
            context = {
                'riddle_index': 1,
                'riddle': riddle['riddle_text'],
                'answer': riddle['riddle_answer'],
                'username': username,
                'current_score': score,
                'attempt': attempt
            }
            return render_template('riddle.html', context=context)
        else:
            attempt = int(request.form.get('attempt'))
            riddle_index = int(request.form.get('riddle_index'))
            score = int(request.form.get('current_score'))
            riddle = get_riddle(riddle_index)[0]
            submitted_answer = request.form.get('submitted_answer').strip().lower()
            actual_answer = riddle['riddle_answer'].strip().lower()
            correct = submitted_answer == actual_answer
            
            print('Riddle Index: {}'.format(riddle_index))
            print('Riddle Object: {}'.format(riddle))
            print('Answers: \n\tSubmitted: {} --> Actual: {}'.format(submitted_answer, actual_answer))
            print('Correct: {}'.format(correct))
            
            if riddle_index == 1:
                if correct:
                    riddle_index += 1
                    score += 1
                    attempt = 1
                    next_riddle = get_riddle(riddle_index)[0]
                else:
                    if attempt >= 2: 
                        riddle_index += 1
                        attempt = 1
                        next_riddle = get_riddle(riddle_index)[0]
                    else:
                        attempt += 1
                        next_riddle = get_riddle(riddle_index)[0]
                    
            else:
                if correct:
                    riddle_index += 1
                    score += 1
                    attempt = 1
                    if riddle_index > 10:
                        return redirect('/')
                    else:
                        next_riddle = get_riddle(riddle_index)[0]
                else:
                    if riddle_index > 10:
                        return redirect('/')
                    else:
                        if attempt >= 2: 
                            riddle_index += 1
                            attempt = 1
                            next_riddle = get_riddle(riddle_index)[0]
                        else:
                            attempt += 1
                            next_riddle = get_riddle(riddle_index)[0]
                
            context = {
                'riddle_index': next_riddle['index'],
                'riddle': next_riddle['riddle_text'],
                'answer': next_riddle['riddle_answer'],
                'username': username,
                'current_score': score,
                'attempt': attempt
            }
            return render_template('riddle.html', context=context)
                
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
        
        
    
app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)