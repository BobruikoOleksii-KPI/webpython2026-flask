from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Author, Book, Genre, Biography
from app.forms import AuthorForm, BookForm, GenreForm, BiographyForm

admin_bp = Blueprint('admin', __name__)

# ====================== ALL CRUD (protected by current_user) ======================

@admin_bp.route('/')
@login_required
def admin_panel():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено! Тільки для адміністратора.', 'danger')
        return redirect(url_for('main.home'))
    
    total_books = Book.query.count()
    total_authors = Author.query.count()
    total_genres = Genre.query.count()
    
    return render_template('admin/admin.html',
                           total_books=total_books,
                           total_authors=total_authors,
                           total_genres=total_genres)

@admin_bp.route('/genres')
@login_required
def genres_list():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено! Тільки для адміністратора.', 'danger')
        return redirect(url_for('main.home'))
    genres = Genre.query.all()
    return render_template('genres.html', genres=genres)


@admin_bp.route('/add-genre', methods=['GET', 'POST'])
@login_required
def add_genre():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data)
        db.session.add(genre)
        db.session.commit()
        flash('Жанр успішно додано!', 'success')
        return redirect(url_for('admin.genres_list'))
    return render_template('add_genre.html', form=form)


@admin_bp.route('/edit-genre/<int:genre_id>', methods=['GET', 'POST'])
@login_required
def edit_genre(genre_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    if form.validate_on_submit():
        genre.name = form.name.data
        db.session.commit()
        flash('Жанр оновлено!', 'success')
        return redirect(url_for('admin.genres_list'))
    return render_template('edit_genre.html', form=form, genre=genre)


@admin_bp.route('/delete-genre/<int:genre_id>', methods=['POST'])
@login_required
def delete_genre(genre_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash('Жанр видалено!', 'success')
    return redirect(url_for('admin.genres_list'))


# === AUTHOR, BOOK, BIOGRAPHY CRUD ===
@admin_bp.route('/add-author', methods=['GET', 'POST'])
@login_required
def add_author():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    form = AuthorForm()
    if form.validate_on_submit():
        author = Author(name=form.name.data, surname=form.surname.data)
        db.session.add(author)
        db.session.commit()
        flash('Автора успішно додано!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_author.html', form=form)


@admin_bp.route('/edit-author/<int:author_id>', methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    author = Author.query.get_or_404(author_id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        author.name = form.name.data
        author.surname = form.surname.data
        db.session.commit()
        flash('Автора оновлено!', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_author.html', form=form, author=author)


@admin_bp.route('/delete-author/<int:author_id>', methods=['POST'])
@login_required
def delete_author(author_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash('Автора видалено!', 'success')
    return redirect(url_for('main.home'))


@admin_bp.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    form = BookForm()
    form.author_id.choices = [(a.id, a.full_name()) for a in Author.query.all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.all()]
    if form.validate_on_submit():
        book = Book(title=form.title.data, year=form.year.data, author_id=form.author_id.data)
        db.session.add(book)
        db.session.commit()
        selected_genres = Genre.query.filter(Genre.id.in_(form.genre_ids.data)).all()
        book.genres.extend(selected_genres)
        db.session.commit()
        flash('Книгу успішно додано!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_book.html', form=form)


@admin_bp.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    form.author_id.choices = [(a.id, a.full_name()) for a in Author.query.all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.all()]
    form.genre_ids.data = [g.id for g in book.genres]
    if form.validate_on_submit():
        book.title = form.title.data
        book.year = form.year.data
        book.author_id = form.author_id.data
        book.genres = Genre.query.filter(Genre.id.in_(form.genre_ids.data)).all()
        db.session.commit()
        flash('Книгу оновлено!', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_book.html', form=form, book=book)


@admin_bp.route('/delete-book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Книгу видалено!', 'success')
    return redirect(url_for('main.home'))


@admin_bp.route('/edit-biography/<int:author_id>', methods=['GET', 'POST'])
@login_required
def edit_biography(author_id):
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    author = Author.query.get_or_404(author_id)
    biography = author.biography
    form = BiographyForm(obj=biography)
    if form.validate_on_submit():
        if biography is None:
            biography = Biography(author_id=author.id, text=form.text.data)
            db.session.add(biography)
        else:
            biography.text = form.text.data
        db.session.commit()
        flash('Біографію оновлено!', 'success')
        return redirect(url_for('main.home'))
    return render_template('edit_biography.html', form=form, author=author)


from app.utils import send_mail

@admin_bp.route('/send-test-email')
@login_required
def send_test_email():
    if not (current_user.is_authenticated and current_user.username == 'admin'):
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('main.home'))
    
    send_mail(
        subject="Тестове повідомлення від бібліотеки",
        recipient="alexey.bobruiko@gmail.com",
        html="<h1>Привіт!</h1><p>Це тестове повідомлення з вашого Flask Lab 7.</p>"
    )
    flash('Тестове повідомлення надіслано!', 'success')
    return redirect(url_for('admin.admin_panel'))