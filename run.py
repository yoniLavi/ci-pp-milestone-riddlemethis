import os
import json
import operator
from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__)
app.secret_key = 'This shoudl be a secret!'
app.url_map.strict_slashes = False

def get_riddle(index):
    with open('data/riddles.json') as json_riddles:
        riddles = json.loads(json_riddles.read())
        return [riddle for riddle in riddles if riddle['index'] == index]
    
def init_game(username):
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
    return context
        
def add_to_leaderboard(username, final_score):
    leaders = get_leaders()
    print(leaders)
    with open('data/leaders.txt', 'a') as leaderboard:
        if not (username, final_score) in leaders:
            leaderboard.write('\n{}:{}'.format(str(username), str(final_score)))

def get_leaders():
    with open('data/leaders.txt') as leaders:
        leaders = [line for line in leaders.readlines()[1:]]
        sorted_leaders = []
        for leader in leaders:
            tupe = (leader.split(':')[0].strip(), int(leader.split(':')[1].strip()))
            sorted_leaders.append(tupe)
        return sorted(sorted_leaders, key=lambda x: x[1])[::-1][:10]

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
        
        ''' If we're on the first question, initialize the game with a default attempt, score, riddle index, etc.
        Otherwise, get the game info from the form that was submitted '''
        
        if form.get('first-question') == 'true':
            context = init_game(username)
            return render_template('riddle.html', context=context)
        else:
            # Get attempt number, riddle index, current score and the riddle from the riddle file to compare against
            attempt = int(request.form.get('attempt'))
            riddle_index = int(request.form.get('riddle_index'))
            score = int(request.form.get('current_score'))
            riddle = get_riddle(riddle_index)[0]
            
            # Check whether the answer is correct
            submitted_answer = request.form.get('submitted_answer').strip().lower()
            actual_answer = riddle['riddle_answer'].strip().lower()
            correct = submitted_answer == actual_answer
            
            ''' If we're on the first riddle, check whether or not it's correct.
            If it's correct, add 1 to score, reset attempt to 1 for the next riddle,
            and increment the riddle index. Then get the next riddle. 
            
            If it's wrong, check whether we're on attempt #2 and if so, increment the
            riddle index w/o adding to the score, then get the next riddle. If not, just
            return the same riddle again after incrementing the attempt. '''
            
            if riddle_index == 1:
                if correct:
                    riddle_index += 1
                    score += 1
                    attempt = 1
                    next_riddle = get_riddle(riddle_index)[0]
                    flash('Nice work! You nailed it!', 'success')
                else:
                    if attempt >= 2:
                        riddle_index += 1
                        attempt = 1
                        next_riddle = get_riddle(riddle_index)[0]
                        flash('That was your last attempt. How about a new riddle?', 'error')
                    else:
                        attempt += 1
                        next_riddle = get_riddle(riddle_index)[0]
                        flash('That\'s not right. You\'ve got one more try...', 'error')
            else:
                if correct:
                    riddle_index += 1
                    score += 1
                    attempt = 1
                    if riddle_index > 10:
                        final_score = score
                        add_to_leaderboard(username, final_score)
                        leaders = get_leaders()
                        return render_template('leaders.html', final_score=final_score, leaders=leaders)
                    else:
                        next_riddle = get_riddle(riddle_index)[0]
                        flash('Nice work! You nailed it!', 'success')
                else:
                    if riddle_index > 10:
                        final_score = score
                        add_to_leaderboard(username, final_score)
                        leaders = get_leaders()
                        return render_template('leaders.html', final_score=final_score, leaders=leaders)
                    else:
                        if attempt >= 2: 
                            riddle_index += 1
                            attempt = 1
                            next_riddle = get_riddle(riddle_index)[0]
                            flash('That was your last attempt. How about a new riddle?', 'error')
                        else:
                            attempt += 1
                            next_riddle = get_riddle(riddle_index)[0]
                            flash('That\'s not right. You\'ve got one more try...', 'error')
            
            # Now just populate a context dictionary to use in the template, and return the template
            context = {
                'riddle_index': next_riddle['index'], # We use the internal riddle index for clarity here
                'riddle': next_riddle['riddle_text'],
                'answer': next_riddle['riddle_answer'],
                'username': username,
                'current_score': score,
                'attempt': attempt
            }
            return render_template('riddle.html', context=context)
            
    # Redirect to the homepage with an error if using GET
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
    
@app.route('/leaders')
def leaders():
    leaders = get_leaders()
    return render_template("leaders.html")
    
app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)