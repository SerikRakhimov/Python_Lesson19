from flask import render_template,request,Blueprint
from social_news.models import NewsItem

core = Blueprint('core',__name__)

@core.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    news = NewsItem.query.order_by(NewsItem.date.asc()).paginate(page=page, per_page=3)
    return render_template('index.html',news=news)

@core.route('/info')
def info():
    return render_template('info.html')
