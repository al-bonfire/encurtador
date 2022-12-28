from flask import Blueprint, render_template, request, url_for, redirect
from src.models import URL, engine
from sqlalchemy.orm import Session
from secrets import token_urlsafe
from src.config import settings as s

bp = Blueprint('router', __name__)

@bp.route("/", methods=['GET', 'POST'])
def home():
    token = None
    if request.method == 'POST':
        
        with Session(engine) as db:
            
            url = request.form.get('url')
            
            if (not url.startswith('http') and
                not url.startswith('https')):
                url = f'http://{url}'
            
            data = db.query(URL).filter_by(url=url).first()
            
            if data:
                token = data.token
                
            else:
                
                loop = True
                while loop:  
                    token = token_urlsafe(6)
                    data = db.query(URL).filter_by(token=token).first()
                    if not data:
                        loop = False
                        
                data = URL(url=url, token=token)
                db.add(data)
                db.commit()
    
    return render_template('home.html', token=token, host=s.HOST)

@bp.route('/<string:token>/')
def redir(token):
    with Session(engine) as db:
        data = db.query(URL).filter_by(token=token).first()
        
    if data:
        return redirect(data.url)
    else:
        return redirect(url_for('router.home'))