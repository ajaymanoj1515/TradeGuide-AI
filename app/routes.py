from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import yfinance as yf
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from .models import User, Admin, Watchlist, History
from .analysis import TradeGuideEngine 
from .news import NewsEngine

bp = Blueprint('main', __name__)

# --- USER LOADER (Handles User & Admin IDs) ---
@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('admin_'):
        try:
            real_id = int(user_id.split('_')[1])
            return Admin.query.get(real_id)
        except:
            return None
    return User.query.get(int(user_id))

# --- HELPER FUNCTIONS ---
def format_ticker(symbol, market_type):
    if not symbol: return None
    symbol = symbol.upper().strip().replace(" ", "")
    if any(x in symbol for x in ['.', '=', '-']): return symbol
    if market_type == 'NSE': return f"{symbol}.NS"
    if market_type == 'BSE': return f"{symbol}.BO"
    if market_type == 'CRYPTO': return f"{symbol}-USD"
    if market_type == 'FOREX': return f"{symbol}=X"
    return symbol

# --- AUTH ROUTES ---

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for('main.admin_home'))
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for('main.admin_home'))
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. Try Admin Login
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('main.admin_home'))
            
        # 2. Try User Login
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
            
        flash('Invalid username or password')
    return render_template('login.html', mode='login')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username taken')
            return redirect(url_for('main.login'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('main.login'))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html', mode='register')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- USER FEATURES ---

@bp.route('/dashboard')
@login_required
def dashboard():
    if isinstance(current_user, Admin):
        return redirect(url_for('main.admin_home'))
    user_watchlist = Watchlist.query.filter_by(user_id=current_user.user_id).all()
    user_history = History.query.filter_by(user_id=current_user.user_id).order_by(History.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', user=current_user, watchlist=user_watchlist, history=user_history)

@bp.route('/prediction')
@login_required
def prediction():
    selected_ticker = request.args.get('ticker', '') 
    return render_template('prediction.html', user=current_user, selected_ticker=selected_ticker)

@bp.route('/portfolio')
@login_required
def portfolio():
    user_watchlist = Watchlist.query.filter_by(user_id=current_user.user_id).all()
    return render_template('watchlist.html', user=current_user, watchlist=user_watchlist)

@bp.route('/news')
@login_required
def news_page():
    category = request.args.get('cat', 'finance')
    engine = NewsEngine()
    engine.fetch_general_news(category)
    return render_template('news.html', news_list=engine.get_data(), category=category)

@bp.route('/watchlist/add', methods=['POST'])
@login_required
def add_watchlist():
    if isinstance(current_user, Admin): return redirect(url_for('main.admin_home'))
    raw_ticker = request.form.get('ticker')
    market_type = request.form.get('market_type')
    ticker = format_ticker(raw_ticker, market_type)
    if ticker and not Watchlist.query.filter_by(user_id=current_user.user_id, ticker=ticker).first():
        db.session.add(Watchlist(ticker=ticker, user_id=current_user.user_id))
        db.session.commit()
    referer = request.headers.get("Referer")
    if referer and "portfolio" in referer: return redirect(url_for('main.portfolio'))
    return redirect(url_for('main.dashboard'))

@bp.route('/watchlist/delete/<int:id>')
@login_required
def delete_watchlist(id):
    item = Watchlist.query.get(id)
    if item and item.user_id == current_user.user_id:
        db.session.delete(item)
        db.session.commit()
    referer = request.headers.get("Referer")
    if referer and "portfolio" in referer: return redirect(url_for('main.portfolio'))
    return redirect(url_for('main.dashboard'))

# --- SETTINGS ROUTES ---

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

@bp.route('/settings/update_profile', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    
    existing = User.query.filter_by(username=new_username).first()
    if existing and existing.user_id != current_user.user_id:
        flash('Username taken.')
        return redirect(url_for('main.settings'))
        
    current_user.username = new_username
    current_user.email = new_email
    db.session.commit()
    flash('Profile updated.')
    return redirect(url_for('main.settings'))

@bp.route('/settings/change_password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    if not current_user.check_password(current_pw):
        flash('Incorrect current password.')
        return redirect(url_for('main.settings'))

    if new_pw != confirm_pw:
        flash('Passwords do not match.')
        return redirect(url_for('main.settings'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Password changed successfully.')
    return redirect(url_for('main.settings'))

@bp.route('/settings/clear_data', methods=['POST'])
@login_required
def clear_data():
    Watchlist.query.filter_by(user_id=current_user.user_id).delete()
    History.query.filter_by(user_id=current_user.user_id).delete()
    db.session.commit()
    flash('All data cleared.')
    return redirect(url_for('main.settings'))

# --- ADMIN ROUTES ---

@bp.route('/admin')
@login_required
def admin_home():
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin): return redirect(url_for('main.dashboard'))
    return render_template('admin.html', 
                         page='dashboard', 
                         user_count=User.query.count(),
                         users=User.query.limit(5).all())

@bp.route('/admin/users')
@login_required
def admin_users():
    if not isinstance(current_user, Admin): return redirect(url_for('main.dashboard'))
    return render_template('admin.html', page='users', users=User.query.all())

@bp.route('/admin/database')
@login_required
def admin_database():
    if not isinstance(current_user, Admin): return redirect(url_for('main.dashboard'))
    stats = {
        'users_table_size': User.query.count(),
        'history_table_size': History.query.count(),
        'watchlist_table_size': Watchlist.query.count()
    }
    return render_template('admin.html', page='database', stats=stats)

@bp.route('/admin/alerts')
@login_required
def admin_alerts():
    if not isinstance(current_user, Admin): return redirect(url_for('main.dashboard'))
    return render_template('admin.html', page='alerts')

@bp.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not isinstance(current_user, Admin): return redirect(url_for('main.dashboard'))
    user = User.query.get(user_id)
    if user:
        # Clean up related data
        Watchlist.query.filter_by(user_id=user_id).delete()
        History.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
    # If referer was users page, go back there
    return redirect(url_for('main.admin_users'))

# --- API ROUTES ---

@bp.route('/api/market_status')
def market_status():
    tickers = { 'NIFTY': '^NSEI', 'SENSEX': '^BSESN', 'USD/INR': 'INR=X', 'BTC': 'BTC-USD' }
    data = {}
    for name, symbol in tickers.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2d")
            if len(hist) >= 1:
                close = hist['Close'].iloc[-1]
                change_pct = ((close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100 if len(hist) >= 2 else 0.0
                price_str = f"₹{close:.2f}" if name == 'USD/INR' else f"${close:,.0f}" if name == 'BTC' else f"{close:,.0f}"
                data[name] = {'price': price_str, 'change': f"{change_pct:+.2f}%", 'color': '#00e676' if change_pct >= 0 else '#ff5252'}
            else:
                data[name] = {'price': 'Loading..', 'change': '', 'color': '#aaa'}
        except:
            data[name] = {'price': 'Error', 'change': '', 'color': '#aaa'}
    return jsonify(data)

@bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    data = request.get_json()
    ticker = data.get('ticker')
    market = data.get('market', 'NSE')
    interval = data.get('interval', '1d')
    style = data.get('style', 'candle')
    
    if market != 'RAW': ticker = format_ticker(ticker, market)
    
    tech_engine = TradeGuideEngine(ticker)
    tech_success = tech_engine.fetch_data(interval=interval)
    news_engine = NewsEngine(ticker)
    news_success = news_engine.fetch_news()
    
    if tech_success:
        result_data = tech_engine.generate_signal(style=style)
        
        # --- SAVE HISTORY ---
        try:
            new_entry = History(
                user_id=current_user.user_id,
                ticker=result_data['ticker'],
                signal=result_data['signal'],
                price=float(result_data['current_price']),
                interval=interval
            )
            db.session.add(new_entry)
            db.session.commit()
        except Exception as e:
            print(f"DB Save Error: {e}")

        return jsonify({
            'success': True,
            'data': result_data,
            'news': news_engine.get_results() if news_success else {}
        })
    
    return jsonify({'success': False, 'error': f'Data not found for {ticker}'})