from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import AuthorForm, BookForm, GenreForm, BiographyForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ==================== MODELS ====================
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete-orphan")
    biography = db.relationship('Biography', backref='author', uselist=False, cascade="all, delete-orphan")

    def full_name(self):
        return f"{self.name} {self.surname}"

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    genres = db.relationship('Genre', secondary='book_genre', backref='books')

class Biography(db.Model):
    __tablename__ = 'biographies'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False, unique=True)

book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# ==================== ROUTES ====================
@app.route('/')
def home():
    role = session.get('role', 'user')
    books = Book.query.all()
    authors = Author.query.all()
    genres = Genre.query.all()
    
    # Example cookie usage
    last_visit = request.cookies.get('last_visit', 'Ніколи')
    resp = make_response(render_template('home.html', 
                                       books=books, 
                                       authors=authors, 
                                       genres=genres,
                                       role=role,
                                       last_visit=last_visit))
    resp.set_cookie('last_visit', 'Сьогодні', max_age=60*60*24*30)
    return resp

@app.route('/set-role/<role>')
def set_role(role):
    if role in ['admin', 'user']:
        session['role'] = role
        flash(f'Роль змінено на {role}', 'info')
    return redirect(url_for('home'))

# === GENRE CRUD ===
@app.route('/genres')
def genres_list():
    genres = Genre.query.all()
    return render_template('genres.html', genres=genres, role=session.get('role', 'user'))

@app.route('/add-genre', methods=['GET', 'POST'])
def add_genre():
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data)
        db.session.add(genre)
        db.session.commit()
        flash('Жанр успішно додано!', 'success')
        return redirect(url_for('genres_list'))
    return render_template('add_genre.html', form=form)

@app.route('/edit-genre/<int:genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    genre = Genre.query.get_or_404(genre_id)
    form = GenreForm(obj=genre)
    if form.validate_on_submit():
        genre.name = form.name.data
        db.session.commit()
        flash('Жанр оновлено!', 'success')
        return redirect(url_for('genres_list'))
    return render_template('edit_genre.html', form=form, genre=genre)

@app.route('/delete-genre/<int:genre_id>', methods=['POST'])
def delete_genre(genre_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash('Жанр видалено!', 'success')
    return redirect(url_for('genres_list'))

# === BIOGRAPHY CRUD ===
@app.route('/edit-biography/<int:author_id>', methods=['GET', 'POST'])
def edit_biography(author_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    author = Author.query.get_or_404(author_id)
    biography = author.biography
    if not biography:
        biography = Biography(author_id=author.id)
        db.session.add(biography)
    
    form = BiographyForm(obj=biography)
    if form.validate_on_submit():
        biography.text = form.text.data
        db.session.commit()
        flash('Біографію оновлено!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_biography.html', form=form, author=author)


# === CREATE ===
@app.route('/add-author', methods=['GET', 'POST'])
def add_author():
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    form = AuthorForm()
    if form.validate_on_submit():
        author = Author(name=form.name.data, surname=form.surname.data)
        db.session.add(author)
        db.session.commit()
        flash('Автора успішно додано!', 'success')
        return redirect(url_for('home'))
    return render_template('add_author.html', form=form)


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    form = BookForm()
    form.author_id.choices = [(a.id, a.full_name()) for a in Author.query.all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.all()]
    if form.validate_on_submit():
        book = Book(title=form.title.data, year=form.year.data, author_id=form.author_id.data)
        db.session.add(book)
        db.session.commit()
        # Add selected genres
        selected_genres = Genre.query.filter(Genre.id.in_(form.genre_ids.data)).all()
        book.genres.extend(selected_genres)
        db.session.commit()
        flash('Книгу успішно додано!', 'success')
        return redirect(url_for('home'))
    return render_template('add_book.html', form=form)


# === UPDATE, DELETE ===
@app.route('/edit-author/<int:author_id>', methods=['GET', 'POST'])
def edit_author(author_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    author = Author.query.get_or_404(author_id)
    form = AuthorForm(obj=author)
    if form.validate_on_submit():
        author.name = form.name.data
        author.surname = form.surname.data
        db.session.commit()
        flash('Автора оновлено!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_author.html', form=form, author=author)


@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    form.author_id.choices = [(a.id, a.full_name()) for a in Author.query.all()]
    form.genre_ids.choices = [(g.id, g.name) for g in Genre.query.all()]
    form.genre_ids.data = [g.id for g in book.genres]
    if form.validate_on_submit():
        book.title = form.title.data
        book.year = form.year.data
        book.author_id = form.author_id.data
        # Update genres
        book.genres = Genre.query.filter(Genre.id.in_(form.genre_ids.data)).all()
        db.session.commit()
        flash('Книгу оновлено!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_book.html', form=form, book=book)


@app.route('/delete-author/<int:author_id>', methods=['POST'])
def delete_author(author_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash('Автора видалено!', 'success')
    return redirect(url_for('home'))


@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if session.get('role') != 'admin':
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('home'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Книгу видалено!', 'success')
    return redirect(url_for('home'))

@app.route('/biography/<int:author_id>')
def view_biography(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('biography.html', author=author)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)