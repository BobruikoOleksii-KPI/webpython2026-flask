from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

# ==================== NEW: Login Form ====================
class LoginForm(FlaskForm):
    username = StringField('Ім’я користувача', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')


# ==================== EXISTING FORMS ====================
class AuthorForm(FlaskForm):
    name = StringField('Ім’я', validators=[DataRequired(), Length(max=100)])
    surname = StringField('Прізвище', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Зберегти автора')


class GenreForm(FlaskForm):
    name = StringField('Назва жанру', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Зберегти жанр')


class BiographyForm(FlaskForm):
    text = TextAreaField('Текст біографії', validators=[DataRequired()])
    submit = SubmitField('Зберегти біографію')


class BookForm(FlaskForm):
    title = StringField('Назва книги', validators=[DataRequired(), Length(max=200)])
    year = IntegerField('Рік видання', validators=[DataRequired(), NumberRange(min=1500, max=2030)])
    author_id = SelectField('Автор', coerce=int, validators=[DataRequired()])
    genre_ids = SelectMultipleField('Жанри', coerce=int)
    submit = SubmitField('Зберегти книгу')