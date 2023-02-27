import click
from flask.cli import FlaskGroup, with_appcontext
from flask_migrate import Migrate
from lib.sqlalchemy_utils import init_db
from lib.bigquery import BigQuery
from flask_app.blueprints.user.models import User
from flask_app.blueprints.analysis.models import BookLocation

from flask_app.app import create_app, db

app = create_app()

migrate = Migrate(app, db)
cli = FlaskGroup(app)

#docker-compose exec web python manage.py create_db
@cli.command("create_db")
def create_db():
    init_db()
    u = User()
    u.email = 'email'
    u.password_hash = User.hash_password('sdadkjasdasekjs')
    u.role = 'ADMIN'
    u.slug = User.generate_slug(u.email)
    u.save()

@cli.command("backpop_books")
@click.command()
@with_appcontext
def backpop_books():
    return
    query_str_template = BigQuery.get_query_str(
        'backpop_locations')
    for year in range(1909, 1910):
        rows = BigQuery().query(
            query_str_template.format(year=year))

        for i, row in enumerate(rows):
            book_location = BookLocation()
            book_location.title = row['title']
            book_location.author = row['author']
            book_location.locations = row['location']
            print(i, year)
            book_location.save()



if __name__ == '__main__':
    cli()