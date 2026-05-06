from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange

class AuthorForm(FlaskForm):
    name = StringField("Ім'я", validators=[DataRequired(), Length(max=100)])
    surname = StringField("Прізвище", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Зберегти автора")

class BookForm(FlaskForm):
    title = StringField("Назва книги", validators=[DataRequired(), Length(max=200)])
    year = IntegerField("Рік видання", validators=[DataRequired(), NumberRange(min=1000, max=2100)])
    author_id = SelectField("Автор", coerce=int, validators=[DataRequired()])
    genre_ids = SelectMultipleField("Жанри", coerce=int)
    submit = SubmitField("Зберегти книгу")

class GenreForm(FlaskForm):
    name = StringField("Назва жанру", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Зберегти жанр")

class BiographyForm(FlaskForm):
    text = TextAreaField("Біографія", validators=[DataRequired()])
    submit = SubmitField("Зберегти біографію")