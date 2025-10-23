from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Update the alembic version to the latest known revision
    db.session.execute(text("UPDATE alembic_version SET version_num = 'f793ad4e2228'"))
    db.session.commit()
    print("Updated alembic version to f793ad4e2228")