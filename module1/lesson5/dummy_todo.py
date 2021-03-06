from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://postgres:letmein@localhost:5432/tododb'

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, Description: {self.description}>'

db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
    description=request.form.get('description', '')
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())

if __name__ == '__main__':
    print('HELLOW')
    app.run()