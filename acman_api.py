from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from flask_login import LoginManager, login_user, logout_user, current_user
from dbremote.db_session import create_session, global_init
from dbremote.user import User
from dbremote.storys import Story, Comment
import flask
import os

global_init("db/data.sqlite")

blueprint = flask.Blueprint('acman_api', __name__,
                            template_folder='templates')


class ChangeNickname(FlaskForm):
    change = StringField("change", validators=[DataRequired()])
    cub = SubmitField("sub")


class FollowForm(FlaskForm):
    subscribe = SubmitField("subscribe")


class DisFollowed(FlaskForm):
    author = StringField("author", validators=[DataRequired()])
    disfollow = SubmitField("disfollow")


@blueprint.route("/account_page",  methods=["GET", "POST"])
def cabinet():
    session = create_session()
    change_nick = ChangeNickname()
    disf = DisFollowed()
    if change_nick.validate_on_submit():
        user = session.query(User).filter(User.id == current_user.id)
        user.nickname = change_nick.change.data
        session.commit()
    if disf.validate_on_submit():
        user = session.query(User).filter(User.id == current_user.id)
        author = session.query(User).filter(User.id == disf.author.data)
        user.followed.remove(author)
        session.commit()
    user = session.query(User).filter(User.id == current_user.id)
    follows = user.followed
    return flask.render_template("account.html", follows=follows)


class DStory(FlaskForm):
    story = StringField("story", validators=[DataRequired()])
    destroy = SubmitField("del")


@blueprint.route("/dashboard", methods=["GET", "POST"])  # панель управления постами и авторской статистикой
def dashboard():
    session = create_session()
    change = ChangeNickname()
    dstory = DStory()
    if current_user.utype:
        session = create_session()
        dstory = DStory()
        if dstory.validate_on_submit():
            story = session.query(Story).filter(Story.id == dstory.story.data)
            session.delete(story)
            session.commit()
        change = ChangeNickname()
        if change.validate_on_submit():
            author = session.query(User).filter(User.id == current_user.id)
            author.nickname = change.change.data
            session.commit()
        author = session.query(User).filter(User.id == current_user.id)

        author.nickname = change.change.data
        session.commit()
    author = session.query(User).filter(User.id == current_user.id).first()
    print(author)
    stories = author.stories
    followers_count = author.followers
    return flask.render_template("dashboard.html", stories=stories, followers=followers_count, change=ChangeNickname)


@blueprint.route("/author/<int:aid>", methods=["GET", "POST"])  # "визитная карточка" автора
def card(aid):
    session = create_session()
    author = session.query(User).filter(User.id == aid)
    if current_user.is_authenticated:
        sub = FollowForm()
        if sub.validate_on_submit():
            user = session.query(User).filter(User.id == current_user.id)
            if author in user.followed:
                user.followed.remove(author)
                session.commit()
                author.followers -= 1
                session.commit()
            else:
                user.followed.append(author)
                session.commit()
                author.followers += 1
                session.commit()
    else:
        return flask.redirect("/")
    return flask.render_template("card.html", name=author.nickname, fc=author.followers)
