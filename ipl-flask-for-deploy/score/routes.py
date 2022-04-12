from flask import render_template, url_for, flash, redirect, request
from score import app, db, bcrypt
from score.forms import RegistrationForm, LoginForm
from score.models import User,AddMatch,TeamList,TournamentList,LiveScore
from flask_login import login_user, current_user, logout_user, login_required
from pickle import load
import numpy as np

score_pred="score/lib/model/score_prediction_model.pkl"
win_pred="score/lib/model/winner_prediction_model.pkl"

with open(score_pred,'rb') as f:
    score_model=load(f)

with open(win_pred,'rb') as f:
    win_model=load(f)





@app.route("/")
# @app.route("/home")
def home():
    return render_template('index.html')


@app.route('/addmatch')
@login_required
def addmatchFN():
    addmatchList=AddMatch.query.all()
    return render_template("addmatch.html",matchList=addmatchList)

@app.route('/teamlist')
@login_required
def teamlistFN():
    teamlist=TeamList.query.all()
    return render_template("teamlist.html",teamLists=teamlist)

@app.route('/tournamentlist')
@login_required
def tournamentlistFN():
    tournamentlist=TournamentList.query.all()
    return render_template("tournamentlist.html",tournamentlists=tournamentlist)

@app.route('/livescore')
@login_required
def livescoreFN():
    livescore=LiveScore.query.all()
    return render_template("livescore.html",livescores=livescore)



@app.route("/playerlist")
@login_required
def playerList():
    return render_template('playerList.html')



@app.route("/index/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route("/index/login", methods=['GET', 'POST'])
def login():
    admin_email="admin@gmail.com"
    admin_password="admin123"
    if current_user.is_authenticated:
        print("THE CURRENT USER ADMIN CHECK........",current_user.isAdmin)
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
            print("THE CURRENT USER ADMIN CHECK........",current_user.isAdmin)
        elif(admin_email==form.email.data and admin_password==form.password.data):
            return redirect(url_for('adminHome'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin')
@login_required
def adminHome():
    return render_template("adminHome.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))







@app.route("/score-prediction")
@login_required
def scorePre():
    return render_template("score.html")


@app.route("/scoreResult",methods=['POST'])
def scorePredict():
    temp_array=list()
    if request.method == 'POST':
        batting_team = request.form['batting-team']
        if batting_team == 'Chennai Super Kings':
            temp_array = temp_array + [1,0,0,0,0,0,0,0]
        elif batting_team == 'Delhi Daredevils':
            temp_array = temp_array + [0,1,0,0,0,0,0,0]
        elif batting_team == 'Kings XI Punjab':
            temp_array = temp_array + [0,0,1,0,0,0,0,0]
        elif batting_team == 'Kolkata Knight Riders':
            temp_array = temp_array + [0,0,0,1,0,0,0,0]
        elif batting_team == 'Mumbai Indians':
            temp_array = temp_array + [0,0,0,0,1,0,0,0]
        elif batting_team == 'Rajasthan Royals':
            temp_array = temp_array + [0,0,0,0,0,1,0,0]
        elif batting_team == 'Royal Challengers Bangalore':
            temp_array = temp_array + [0,0,0,0,0,0,1,0]
        elif batting_team == 'Sunrisers Hyderabad':
            temp_array = temp_array + [0,0,0,0,0,0,0,1]
        
        bowling_team = request.form['bowling-team']
        if batting_team == 'Chennai Super Kings':
            temp_array = temp_array + [1,0,0,0,0,0,0,0]
        elif batting_team == 'Delhi Daredevils':
            temp_array = temp_array + [0,1,0,0,0,0,0,0]
        elif batting_team == 'Kings XI Punjab':
            temp_array = temp_array + [0,0,1,0,0,0,0,0]
        elif batting_team == 'Kolkata Knight Riders':
            temp_array = temp_array + [0,0,0,1,0,0,0,0]
        elif batting_team == 'Mumbai Indians':
            temp_array = temp_array + [0,0,0,0,1,0,0,0]
        elif batting_team == 'Rajasthan Royals':
            temp_array = temp_array + [0,0,0,0,0,1,0,0]
        elif batting_team == 'Royal Challengers Bangalore':
            temp_array = temp_array + [0,0,0,0,0,0,1,0]
        elif batting_team == 'Sunrisers Hyderabad':
            temp_array = temp_array + [0,0,0,0,0,0,0,1]
        
        

        overs=float(request.form["overs"])
        runs=int(request.form['runs'])
        wickets=int(request.form["wickets"])
        runs_in_prev_5=int(request.form["runs_in_prev_5"])
        wickets_in_prev_5=int(request.form["wickets_in_prev_5"])

        temp_array=temp_array+[overs,runs,wickets,runs_in_prev_5,wickets_in_prev_5]
        data=np.array([temp_array])
        my_prediction=int(score_model.predict(data)[0])

    return render_template('scoreResults.html', lower_limit = my_prediction-10, upper_limit = my_prediction+15)


@app.route('/winner-prediction')
@login_required
def winnerPre():
    return render_template("winner.html")


@app.route('/winnerResult',methods=['POST'])
def winnerPrediction():
    temp_array =list()
    # To get V                                #   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if request.method=="POST":
        venue=request.form["venue"]
        if venue=='Barabati Stadium':
            temp_array = temp_array + [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Brabourne Stadium":
            temp_array = temp_array + [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Buffalo Park':
            temp_array = temp_array + [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="De Beers Diamond Oval":
            temp_array = temp_array + [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Dr DY Patil Sports Academy':
            temp_array = temp_array + [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Dubai International Cricket Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Eden Gardens":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Feroz Shah Kotla':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Himachal Pradesh Cricket Association Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Holkar Cricket Stadium": #------------------
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="JSCA International Stadium Complex":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Kingsmead':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="M Chinnaswamy Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='M.Chinnaswamy Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="MA Chidambaram Stadium, Chepauk":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Maharashtra Cricket Association Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="New Wanderers Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Newlands':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="OUTsurance Oval":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        elif venue=='Punjab Cricket Association IS Bindra Stadium, Mohali':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Punjab Cricket Association Stadium, Mohali":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Rajiv Gandhi International Stadium, Uppal':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif venue=="Sardar Patel Stadium, Motera":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        elif venue=='Sawai Mansingh Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        elif venue=="Shaheed Veer Narayan Singh International Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        elif venue=='Sharjah Cricket Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
        elif venue=="Sheikh Zayed Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        elif venue=='Subrata Roy Sahara Stadium':
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
        elif venue=="SuperSport Park":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
        elif venue=="Wankhede Stadium":
            temp_array = temp_array + [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]


        team1 = request.form['team1']
        if team1 == 'Chennai Super Kings':
            team_no=0
            temp_array = temp_array + [1,0,0,0,0,0,0,0]
            sample_test1 =temp_array
        elif team1 == 'Delhi Daredevils':
            team_no=1
            temp_array = temp_array + [0,1,0,0,0,0,0,0]
            sample_test1 =temp_array
        elif team1 == 'Kings XI Punjab':
            team_no=2
            temp_array = temp_array + [0,0,1,0,0,0,0,0]
            sample_test1 =temp_array
        elif team1 == 'Kolkata Knight Riders':
            team_no=3
            temp_array = temp_array + [0,0,0,1,0,0,0,0]
            sample_test1 =temp_array
        elif team1 == 'Mumbai Indians':
            team_no=4
            temp_array = temp_array + [0,0,0,0,1,0,0,0]
            sample_test1 =temp_array
        elif team1 == 'Rajasthan Royals':
            team_no=5
            temp_array = temp_array + [0,0,0,0,0,1,0,0]
            sample_test1 =temp_array
        elif team1 == 'Royal Challengers Bangalore':
            team_no=6
            temp_array = temp_array + [0,0,0,0,0,0,1,0]
            sample_test1 =temp_array
        elif team1 == 'Sunrisers Hyderabad':
            team_no=7
            temp_array = temp_array + [0,0,0,0,0,0,0,1]
            sample_test1 =temp_array
        
        team2 = request.form['team2']
        if team2 == 'Chennai Super Kings':
            team_no=0
            temp_array = temp_array + [1,0,0,0,0,0,0,0]
            sample_test2 =temp_array
        elif team2 == 'Delhi Daredevils':
            team_no=1
            temp_array = temp_array + [0,1,0,0,0,0,0,0]
            sample_test2 =temp_array
        elif team2 == 'Kings XI Punjab':
            team_no=2
            temp_array = temp_array + [0,0,1,0,0,0,0,0]
            sample_test2 =temp_array
        elif team2 == 'Kolkata Knight Riders':
            team_no=3
            temp_array = temp_array + [0,0,0,1,0,0,0,0]
            sample_test2 =temp_array
        elif team2 == 'Mumbai Indians':
            team_no=4
            temp_array = temp_array + [0,0,0,0,1,0,0,0]
            sample_test2 =temp_array
        elif team2 == 'Rajasthan Royals':
            team_no=5
            temp_array = temp_array + [0,0,0,0,0,1,0,0]
            sample_test2 =temp_array
        elif team2 == 'Royal Challengers Bangalore':
            team_no=6
            temp_array = temp_array + [0,0,0,0,0,0,1,0]
            sample_test2 =temp_array
        elif team2 == 'Sunrisers Hyderabad':
            team_no=7
            temp_array = temp_array + [0,0,0,0,0,0,0,1]
            sample_test2 =temp_array

    # To get Toss winner
        toss=request.form['toss_winner']
        if(toss=='team1'):
            temp_array = temp_array + [0]
        else:
            temp_array = temp_array + [1]
        
        toss_det=request.form['toss_decision']
        if(toss_det=="batt"):
            temp_array=temp_array+[0]
        else:
            temp_array=temp_array+[1]
        

        team_list=[
            'Chennai Super Kings','Delhi Daredevils','Kings XI Punjab','Kolkata Knight Riders',
            'Mumbai Indians','Rajasthan Royals','Royal Challengers Bangalore','Sunrisers Hyderabad'        
        ]

        data=np.array([temp_array])
        winner_prediction=win_model.predict(data)
        if(winner_prediction==0):
            win_team_name=team_list[team_no]
            print("**********************************TEAM1",team_list[team_no])
        elif(winner_prediction==1):
            win_team_name=team_list[team_no]
            print("**********************************TEAM2",team_list[team_no])

    return render_template('winnerResult.html', name_of_team_win=win_team_name)
