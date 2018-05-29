import os
import json
from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)
app.secret_key = 'This should be a secret!'
app.url_map.strict_slashes = False # make URLs trailing-slash-agnostic 

# Get the info for the next riddle
def get_riddle(index):
    with open('data/riddles.json') as json_riddles:
        riddles = json.loads(json_riddles.read())
        return riddles[index] if index < 10 else None # Return None to avoid IndexError on the last riddle

# Inialize the game with some default values
def init_game(username):
    score = 0
    attempt = 1
    riddle = get_riddle(0)
    context = {
        'riddle_index': 0,
        'riddle': riddle['riddle_text'],
        'answer': riddle['riddle_answer'],
        'username': username,
        'current_score': score,
        'attempt': attempt
    }
    return context

# Function to add a player to the leaderboard after the game has been completed.
def add_to_leaderboard(username, final_score):
    leaders = get_leaders()
    with open('data/leaders.txt', 'a') as leaderboard:
        if not (username, final_score) in leaders:
            leaderboard.write('\n{}:{}'.format(str(username), str(final_score)))

# Function to get current top 10 leaders
def get_leaders():
    with open('data/leaders.txt') as leaders:
        leaders = [line for line in leaders.readlines()[1:]]
        sorted_leaders = []
        for leader in leaders:
            tupe = (leader.split(':')[0].strip(), int(leader.split(':')[1].strip()))
            sorted_leaders.append(tupe)
            
        # Sort leaders on the 2nd elem of the tuple, reverse the sort, then return the top 10
        return sorted(sorted_leaders, key=lambda x: x[1])[::-1][:10]

@app.route('/')
def index():
    return render_template("index.html")
    
# Provide instructions to the user.
@app.route('/ready/', methods=['GET', 'POST'])
def ready():
    if request.method == 'POST':
        form = request.form
        user = form['username']
        return render_template("ready.html", username=user)
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')

# Route to loop through to show riddles
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
            riddle = get_riddle(riddle_index)
            
            # Check whether the answer is correct
            submitted_answer = request.form.get('submitted_answer').strip().lower()
            actual_answer = riddle['riddle_answer'].strip().lower()
            correct = submitted_answer == actual_answer
            
            # Scoring/game logic
            while riddle_index < 10:
                if correct:
                    riddle_index += 1
                    score += 1
                    attempt = 1
                    next_riddle = get_riddle(riddle_index)
                    flash('Nice work! You nailed it!', 'success')
                else:
                    if attempt >= 2: 
                        riddle_index += 1
                        attempt = 1
                        next_riddle = get_riddle(riddle_index)
                        flash('"{}" was your last attempt. The answer was "{}". How about a new riddle?'.format(submitted_answer, actual_answer), 'error')
                    else:
                        attempt += 1
                        next_riddle = get_riddle(riddle_index)
                        flash('"{}" wasn\'t right. You\'ve got one more try...'.format(submitted_answer), 'error')
                
                # Now just populate a context dictionary to use in the template, and return the template.
                # next_riddle will be none if we're on the final question. If so we clear flashed messages
                # and return the leaderboard instead
                if next_riddle is not None:
                    context = {
                        'riddle_index': riddle_index, # We use the internal riddle index for clarity here
                        'riddle': next_riddle['riddle_text'],
                        'answer': next_riddle['riddle_answer'],
                        'username': username,
                        'current_score': score,
                        'attempt': attempt
                    }
                    return render_template('riddle.html', context=context)
                else:
                    session.pop('_flashes', None) # Clear flashed messages if we're on the final question
            
            # Return final score and add the player to the leaderboard
            add_to_leaderboard(username, score)
            return render_template('leaders.html', final_score=score, leaders=get_leaders())
            
    # Redirect to the homepage with an error if using GET
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')

# Dislay only for the leaderboard
@app.route('/leaders')
def leaders():
    leaders = get_leaders()
    return render_template("leaders.html", leaders=leaders)

# Dead route to redirect curious tinkerers
@app.route('/riddleme')
def riddle_redirect():
    # Redirect to the homepage with an error
    flash('You can\'t access that page directly. Enter your username below:')
    return redirect('/')
    
app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)