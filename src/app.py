# from dateutil.parser import parse as parse_date

from flask import Flask
# session, jsonify, url_for, redirect, request, \
#     render_template, flash

from config import read_config
# from db import DB
# from football import FootballClient
# from utils import get_current_time, convert_submit_form_to_dict

config = read_config('./config/config.cfg')

app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.get('flask', 'secret_key'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
)

# Set up Football client
# football = FootballClient(
#     config.get('football', 'api_key'),
#     config.get('football', 'competition')
# )

# Set up DB
# db = DB(app, football.get_all_teams())


# @app.template_filter('strftime')
# def strftime(date_time):
#     date_time_object = parse_date(date_time)
#     return date_time_object.strftime('%a %d %B %Y - %H:%M UTC')


# @app.template_filter('convert_to_datetime')
# def convert_to_datetime(date_time):
#     return parse_date(date_time)


# @app.errorhandler(Exception)
# def error(error):
#     return jsonify(error=str(error)), 500


@app.route('/')
def index():
    return 'hello world'

# @app.route('/')
# def index():
#     if session.get('sub'):
#         return redirect(url_for('home'))
#     return render_template(
#         'index.html',
#         google_login_url=url_for('login'),
#         user_count=db.get_user_count()
#     )


# @app.route('/home')
# def home():
#     return render_template(
#         'home.html',
#         user=db.get_user(session['sub']).to_json(),
#         picture=google.profile()['picture'],
#         fixtures=football.get_all_fixtures(),
#         points=db.get_points_for_user(session['sub']),
#         current_time=get_current_time()
#     )


# @app.route('/home/submit', methods=['POST'])
# def submit():
#     user = db.get_user(session['sub'])
#     predictions = convert_submit_form_to_dict(request.form)
#     try:
#         football.check_predictions_validity(predictions)
#         db.add_predictions(user, predictions)
#         flash('Your predictions were successfully saved!', 'info')
#     except Exception as e:
#         flash(str(e), 'danger')
#     return redirect(url_for('home'))


# @app.route('/user/<int:user_id>')
# def user(user_id):
#     other_user = db.get_user_by_id(user_id)
#     return render_template(
#         'home.html',
#         user=db.get_user(session['sub']).to_json(),
#         picture=google.profile()['picture'],
#         fixtures=football.get_all_fixtures(),
#         points=db.get_points_for_user(other_user.sub),
#         other_user=other_user.to_json(),
#         current_time=get_current_time()
#     )


# @app.route('/sweepstakes')
# def sweepstakes():
#     return render_template(
#         'sweepstakes.html',
#         user=db.get_user(session['sub']).to_json(),
#         picture=google.profile()['picture'],
#         allocations=db.get_team_allocations()
#     )


# @app.route('/predictions')
# def predictions():
#     return render_template(
#         'predictions.html',
#         user=db.get_user(session['sub']).to_json(),
#         picture=google.profile()['picture'],
#         leaderboard=db.get_predictions_leaderboard()
#     )


if __name__ == '__main__':
    app.run(port=8000, debug=True)
