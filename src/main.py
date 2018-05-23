from functools import wraps
from datetime import timedelta
from dateutil.parser import parse as parse_date

from flask import Flask, session, jsonify, url_for, redirect, request, \
    render_template, flash
from authlib.flask.client import OAuth
from authlib.client.apps import google

from .config_parser import read_config
from .db import DB
from .football import FootballClient
from .utils import get_current_time, convert_submit_form_to_dict

config = read_config('./src/config/config.cfg')

app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.get('flask', 'secret_key'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=20),
    GOOGLE_CLIENT_ID=config.get('google_login', 'client_id'),
    GOOGLE_CLIENT_SECRET=config.get('google_login', 'client_secret'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI=config.get('db', 'sqlalchemy_db_url')
)

# Set up Football client
football = FootballClient(config.get('football', 'api_key'), 467)

# Set up DB
db = DB(app, football.get_all_teams())

# Set up Oauth
oauth = OAuth(
    app,
    fetch_token=(lambda name: db.get_user_token(session['sub'])),
    update_token=(
        lambda name, token: db.refresh_user_token(session['sub'], token)
    )
)
google.register_to(oauth)


def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('sub'):
            url = url_for('login', next=request.path)
            return redirect(url)
        return f(*args, **kwargs)
    return decorated


@app.template_filter('strftime')
def strftime(date_time):
    date_time_object = parse_date(date_time)
    return date_time_object.strftime('%a %d %B %Y - %H:%M UTC')


@app.template_filter('convert_to_datetime')
def convert_to_datetime(date_time):
    return parse_date(date_time)


@app.errorhandler(Exception)
def error(error):
    return jsonify(error=str(error)), 500


@app.route('/login')
def login():
    return google.authorize_redirect(url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    user_info = google.parse_openid(token)
    try:
        db.add_user(
            config.get('google_login', 'whitelisted_domains'), user_info, token
        )
    except Exception as e:
        print(e)
        return jsonify(error='Forbidden'), 403
    session.permanent = True
    session['sub'] = user_info['sub']
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    del session['sub']
    return redirect(url_for('index'))


@app.route('/')
def index():
    if session.get('sub'):
        return redirect(url_for('home'))
    return render_template(
        'index.html',
        google_login_url=url_for('login'),
        user_count=db.get_user_count()
    )


@app.route('/home')
@require_login
def home():
    return render_template(
        'home.html',
        user=db.get_user(session['sub']).to_json(),
        picture=google.profile()['picture'],
        fixtures=football.get_all_fixtures(),
        points=db.get_points_for_user(session['sub']),
        current_time=get_current_time()
    )


@app.route('/home/submit', methods=['POST'])
@require_login
def submit():
    user = db.get_user(session['sub'])
    predictions = convert_submit_form_to_dict(request.form)
    try:
        football.check_predictions_validity(predictions)
        db.add_predictions(user, predictions)
        flash('Your predictions were successfully saved!', 'info')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('home'))


@app.route('/user/<int:user_id>')
@require_login
def user(user_id):
    other_user = db.get_user_by_id(user_id)
    return render_template(
        'home.html',
        user=db.get_user(session['sub']).to_json(),
        picture=google.profile()['picture'],
        fixtures=football.get_all_fixtures(),
        points=db.get_points_for_user(other_user.sub),
        other_user=other_user.to_json(),
        current_time=get_current_time()
    )


@app.route('/sweepstakes')
@require_login
def sweepstakes():
    return render_template(
        'sweepstakes.html',
        user=db.get_user(session['sub']).to_json(),
        picture=google.profile()['picture'],
        allocations=db.get_team_allocations()
    )


@app.route('/predictions')
@require_login
def predictions():
    return render_template(
        'predictions.html',
        user=db.get_user(session['sub']).to_json(),
        picture=google.profile()['picture'],
        leaderboard=db.get_predictions_leaderboard()
    )


if __name__ == '__main__':
    app.run(port=8000, debug=True)
