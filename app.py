import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date
from config import Config
from models import db, User, Challenge, Goal, DailyProgress

app = Flask(__name__)

# Load environment variables first if .env exists
from dotenv import load_dotenv
load_dotenv()

# Configure app after env vars are loaded
app.config.from_object(Config)

# Ensure database directory exists BEFORE initializing db
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Initialize database after directory is created
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database with proper context
with app.app_context():
    db.create_all()

    # Create challenge if it doesn't exist
    challenge = Challenge.query.first()
    if not challenge:
        challenge = Challenge(start_date=date.today())
        db.session.add(challenge)
        db.session.commit()

# Authentication routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create default goals for new user
        default_goals = [
            'Two 45-minute workouts (one must be outdoors)',
            'Follow a diet plan (no cheat meals)',
            'Drink 1 gallon of water',
            'Read 10 pages of a non-fiction book',
            'Take a progress photo'
        ]
        
        for idx, goal_text in enumerate(default_goals, 1):
            goal = Goal(user_id=user.id, goal_text=goal_text, order=idx)
            db.session.add(goal)
        
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@app.route('/dashboard/<int:day>')
@login_required
def dashboard(day=None):
    challenge = Challenge.query.first()
    current_day = challenge.get_current_day()

    # If no day specified, default to current day
    if day is None:
        day = current_day

    # Ensure day is within valid range
    day = max(1, min(day, 75))

    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.order).all()

    # Get progress for the selected day
    day_progress = {}
    if day > 0:
        progress_records = DailyProgress.query.filter_by(
            user_id=current_user.id,
            day_number=day
        ).all()
        day_progress = {p.goal_id: p.completed for p in progress_records}

    # Calculate overall progress (up to current day, not selected day)
    total_possible = len(goals) * min(current_day, 75)
    completed_count = DailyProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).filter(DailyProgress.day_number <= current_day).count()

    progress_percentage = (completed_count / total_possible * 100) if total_possible > 0 else 0

    return render_template('dashboard.html',
                         challenge=challenge,
                         current_day=current_day,
                         selected_day=day,
                         goals=goals,
                         day_progress=day_progress,
                         progress_percentage=progress_percentage,
                         completed_count=completed_count,
                         total_possible=total_possible)

# Goal management
@app.route('/goals', methods=['GET', 'POST'])
@login_required
def manage_goals():
    if request.method == 'POST':
        # Get submitted data
        goal_ids = request.form.getlist('goal_id[]')
        goal_texts = request.form.getlist('goal_text[]')

        # Get current goals
        current_goals = Goal.query.filter_by(user_id=current_user.id).all()
        current_goal_ids = {g.id for g in current_goals}
        submitted_goal_ids = {int(gid) for gid in goal_ids if gid}

        # Delete goals that were removed
        goals_to_delete = current_goal_ids - submitted_goal_ids
        for goal_id in goals_to_delete:
            goal = Goal.query.get(goal_id)
            if goal and goal.user_id == current_user.id:
                db.session.delete(goal)

        # Update existing goals and add new ones
        for idx, (goal_id, goal_text) in enumerate(zip(goal_ids, goal_texts), 1):
            if goal_text.strip():  # Only process non-empty goals
                if goal_id:  # Existing goal
                    goal = Goal.query.get(int(goal_id))
                    if goal and goal.user_id == current_user.id:
                        goal.goal_text = goal_text
                        goal.order = idx
                else:  # New goal
                    new_goal = Goal(
                        user_id=current_user.id,
                        goal_text=goal_text,
                        order=idx
                    )
                    db.session.add(new_goal)

        db.session.commit()
        flash('Goals updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.order).all()
    return render_template('goals.html', goals=goals)

# Progress tracking
@app.route('/progress/toggle/<int:goal_id>', methods=['POST'])
@app.route('/progress/toggle/<int:goal_id>/<int:day>', methods=['POST'])
@login_required
def toggle_progress(goal_id, day=None):
    challenge = Challenge.query.first()
    current_day = challenge.get_current_day()

    # If no day specified, use current day
    if day is None:
        day = current_day

    # Validate day is in range
    if day < 1 or day > 75:
        return 'Invalid day', 400

    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        return 'Unauthorized', 403

    # Find or create progress record
    progress = DailyProgress.query.filter_by(
        user_id=current_user.id,
        goal_id=goal_id,
        day_number=day
    ).first()

    if not progress:
        progress = DailyProgress(
            user_id=current_user.id,
            goal_id=goal_id,
            day_number=day,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)
    else:
        progress.completed = not progress.completed
        progress.completed_at = datetime.utcnow() if progress.completed else None

    db.session.commit()
    
    # Return updated checkbox HTML
    checked = 'checked' if progress.completed else ''
    return f'''
    <input type="checkbox" 
           hx-post="/progress/toggle/{goal_id}"
           hx-target="this"
           hx-swap="outerHTML"
           {checked}>
    '''

# Scoreboard
@app.route('/scoreboard')
@login_required
def scoreboard():
    challenge = Challenge.query.first()
    current_day = challenge.get_current_day()
    
    users = User.query.all()
    scoreboard_data = []
    
    for user in users:
        goals = Goal.query.filter_by(user_id=user.id).all()
        goal_count = len(goals)
        
        total_possible = goal_count * min(current_day, 75)
        completed_count = DailyProgress.query.filter_by(
            user_id=user.id,
            completed=True
        ).filter(DailyProgress.day_number <= current_day).count()
        
        progress_percentage = (completed_count / total_possible * 100) if total_possible > 0 else 0
        
        # Calculate current streak
        streak = 0
        for day in range(current_day, 0, -1):
            day_progress = DailyProgress.query.filter_by(
                user_id=user.id,
                day_number=day,
                completed=True
            ).count()
            
            if day_progress == goal_count:
                streak += 1
            else:
                break
        
        scoreboard_data.append({
            'user': user,
            'goals': goals,
            'completed_count': completed_count,
            'total_possible': total_possible,
            'progress_percentage': progress_percentage,
            'streak': streak
        })
    
    # Sort by progress percentage
    scoreboard_data.sort(key=lambda x: x['progress_percentage'], reverse=True)
    
    return render_template('scoreboard.html',
                         challenge=challenge,
                         current_day=current_day,
                         scoreboard_data=scoreboard_data)

# Challenge settings (admin)
@app.route('/challenge/settings', methods=['GET', 'POST'])
@login_required
def challenge_settings():
    challenge = Challenge.query.first()
    
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        if start_date_str:
            challenge.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            db.session.commit()
            flash('Challenge start date updated!', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('challenge_settings.html', challenge=challenge)

if __name__ == '__main__':
    # Use debug mode only in development, not in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
