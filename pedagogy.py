from app import app, db
from app.models import Employee, Workshop

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Employee': Employee,
        'Workshop': Workshop
    }
