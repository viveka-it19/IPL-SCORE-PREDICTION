from datetime import datetime
from score import db, login_manager,admin
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    isAdmin=db.Column(db.Boolean,nullable=False,default=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class AddMatch(db.Model):
    match_id=db.Column(db.Integer, primary_key=True)
    team1=db.Column(db.String(50),nullable=False)
    team2=db.Column(db.String(50),nullable=False)
    place=db.Column(db.String(50),nullable=False)
    imageUrl=db.Column(db.String(1000),nullable=False)
    date=db.Column(db.Date,nullable=False)
    time=db.Column(db.Time,nullable=False)



class TeamList(db.Model):
    team_id=db.Column(db.Integer,primary_key=True)
    teamName=db.Column(db.String(50),nullable=False)
    teamImage=db.Column(db.String(1000),nullable=False)
    teamSize=db.Column(db.Integer,nullable=False)


class TournamentList(db.Model):
    tour_match_id=db.Column(db.Integer, primary_key=True)
    tour_team1=db.Column(db.String(50),nullable=False)
    tour_team2=db.Column(db.String(50),nullable=False)
    tour_place=db.Column(db.String(50),nullable=False)
    tour_imageUrl=db.Column(db.String(1000),nullable=False)
    tour_date=db.Column(db.Date,nullable=False)
    tour_time=db.Column(db.Time,nullable=False)


class LiveScore(db.Model):
    score_id=db.Column(db.Integer, primary_key=True)
    score_team1=db.Column(db.String(50),nullable=False)
    score_team2=db.Column(db.String(50),nullable=False)
    score_live=db.Column(db.Integer,nullable=False)
    score_wicket=db.Column(db.Integer,nullable=False)
    score_over=db.Column(db.Integer,nullable=False)
    score_batting_team=db.Column(db.String(50),nullable=False)
    score_bowling_team=db.Column(db.String(50),nullable=False)


admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(AddMatch,db.session)) 
admin.add_view(ModelView(TeamList,db.session))
admin.add_view(ModelView(TournamentList,db.session))
admin.add_view(ModelView(LiveScore,db.session))
