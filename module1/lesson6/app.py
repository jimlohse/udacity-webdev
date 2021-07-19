import sys
from flask import Flask, json, render_template, request, redirect, url_for, jsonify, abort
from flask_debugtoolbar import DebugToolbarExtension

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://postgres:letmein@localhost:5432/tododb'
app.config['SECRET_KEY'] = '42'

db = SQLAlchemy(app)

toolbar = DebugToolbarExtension(app)

migrate = Migrate(app, db)

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    alldone = db.Column(db.Boolean, nullable=True, default=False)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, Description: {self.description}>'

# load lists
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', lists=TodoList.query.all(),
        active_list=TodoList.query.get(list_id),
        todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

# create a list
@app.route('/lists/create', methods=['POST'])
def create_list():

    error = False
    body = {}

    try: 
        print("request name is " + str(request.get_json()['name']))
        name = request.get_json()['name']
        todo_list = TodoList(name=name)
        db.session.add(todo_list)
        db.session.commit()
        body['name'] = todo_list.name
        body['id'] = todo_list.id
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if not error:
        return jsonify(body)
    else:
        print("Hit the else statement, error is True")
        abort(500)


# set entire list completed
@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False
    try:
        # print("request is not set yet")
        its_complete = request.get_json()['completed']
        # print("Complete is: " + str(its_complete))
        list = TodoList.query.get(list_id)
        list.alldone = its_complete
        
        for todo in list.todos:
            todo.completed = its_complete

        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    
    if not error:
        return redirect(url_for('index'))
    else:
        abort(500)

# delete a list (alert for confirmation)
@app.route('/lists/<list_id>/delete-list', methods=['DELETE'])
def delete_list(list_id):
    
    error = False
    
    try:
        list = TodoList.query.get(list_id)
        for todo in list.todos:
            db.session.delete(todo)
        db.session.delete(list)
        db.session.commit()     
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        return jsonify({'success': True})
    else:
        abort(500)

# create a todo
@app.route('/todos/create', methods=['POST'])
def create_todo():

    error = False
    body = {}

    try:
        description=request.get_json()['description']
        todo = Todo(description=description, completed=False)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        return jsonify(body)
    else:
        abort(400)
    # return redirect(url_for('index'))

#delete a todo item
@app.route('/todos/<todo_id>/delete-todo', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()

    except:
        db.session.rollback()
    finally:
        db.session.close()
    # return redirect(url_for('index'))
    # return redirect('http://127.0.0.1:5000')
    return jsonify({ 'success': True })

# set todo item completed
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

if __name__ == '__main__':
    app.run()