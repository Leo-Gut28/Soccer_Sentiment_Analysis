from flask import Flask, render_template, request, redirect, url_for
from soccer_api import get_team_data
from reddit_api import get_reddit_data
import os

app = Flask(__name__, template_folder=os.path.abspath('templates'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve user input from the form
        first_team = request.form['first_team']
        second_team = request.form['second_team']
        competition = request.form['competition']

        # Call your existing functions with user input and perform sentiment analysis
        first_players, second_players = get_team_data(first_team, second_team)
        get_reddit_data(first_team, second_team, competition, 
                        first_players, second_players
        )

        # Redirect to the results route, passing relevant data as arguments
        return redirect(url_for('results', first_team=first_team, second_team=second_team))
    
    return render_template('index.html')

@app.route('/results')
def results():
    # Retrieve data from the URL parameters
    first_team = request.args.get('first_team')
    second_team = request.args.get('second_team')

    # Render the results template with the data
    return render_template('results.html', first_team=first_team, second_team=second_team)

if __name__ == '__main__':
    app.run(debug=True)
