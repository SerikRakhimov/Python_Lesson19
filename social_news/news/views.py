from flask import render_template,url_for,flash, redirect,request,Blueprint
from flask_login import current_user,login_required
from social_news import db
from social_news.models import NewsItem
from social_news.news.forms import NewsItemForm

news = Blueprint('news', __name__)

@news.route('/create', methods=['GET', 'POST'])
@login_required
def create_news_item():
    form = NewsItemForm( )

    if form.validate_on_submit():

        news_item = NewsItem(title=form.title.data,
                             text=form.text.data,
                             user_id=current_user.id
                             )
        db.session.add(news_item)
        db.session.commit()
        flash("NEws Created")
        return redirect(url_for('core.index'))

    return render_template('create_news.html',form=form)


# instead of a string so we can look it up later.
@news.route('/<int:news_item_id>')
def news_item(news_item_id):
    news_item = NewsItem.query.get_or_404(news_item_id)
    return render_template('news_item.html', title=news_item.title,
                           date=news_item.date, news_item=news_item
                           )

@news.route("/<int:news_item_id>/update", methods=['GET', 'POST'])
@login_required
def update(news_item_id):
    news_item = NewsItem.query.get_or_404(news_item_id)
    if news_item.author != current_user:
        # Forbidden, No Access
        abort(403)

    form = NewsItemForm( )
    if form.validate_on_submit():
        news_item.title = form.title.data
        news_item.text = form.text.data
        db.session.commit()
        flash('news Updated')
        return redirect(url_for('news.news_item', news_item_id=news_item.id))
    # the old text and title.
    elif request.method == 'GET':
        form.title.data = news_item.title
        form.text.data = news_item.text
    return render_template('create_news.html', title='Update',
                           form=form)


@news.route("/<int:news_item_id>/delete", methods=['POST'])
@login_required
def delete_news_item(news_item_id):
    news_item = NewsItem.query.get_or_404(news_item_id)
    if news_item.author != current_user:
        abort(403)
    db.session.delete(news_item)
    db.session.commit()
    flash('News has been deleted')
    return redirect(url_for('core.index'))
