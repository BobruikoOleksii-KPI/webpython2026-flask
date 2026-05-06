from flask import Blueprint, render_template, request, make_response, session, redirect, url_for, flash
from app.models import Book, Author, Genre
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    books = Book.query.all()
    authors = Author.query.all()
    genres = Genre.query.all()
    
    last_visit = request.cookies.get('last_visit', 'Ніколи')
    resp = make_response(render_template('home.html', 
                                       books=books, 
                                       authors=authors, 
                                       genres=genres,
                                       role='admin' if (current_user.is_authenticated and current_user.username == 'admin') else 'user',
                                       last_visit=last_visit))
    resp.set_cookie('last_visit', 'Сьогодні', max_age=60*60*24*30)
    return resp

@main_bp.route('/set-role/<role>')
def set_role(role):
    flash('Ця функція більше не потрібна — використовуйте логін', 'info')
    return redirect(url_for('main.home'))

@main_bp.route('/genres')
def genres_list():
    genres = Genre.query.all()
    return render_template('genres.html', genres=genres, role=session.get('role', 'user'))

@main_bp.route('/biography/<int:author_id>')
def view_biography(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('biography.html', author=author)