from loan import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()   # Deletes all tables
    db.create_all() # Creates tables according to current models
    print("Database reset successfully!")
