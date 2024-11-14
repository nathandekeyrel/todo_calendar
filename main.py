import json
from flask import Flask, request, render_template
from werkzeug.utils import redirect

from src.model.todo import Todo, db
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')

# with open("other/data/contacts.json", mode="r", encoding="utf-8") as read_file:
#     contact_data = json.load(read_file)

with db:
    db.create_tables([Todo])


@app.before_request
def _db_connect():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


@app.route('/')
def index():
    return redirect('/todos')


@app.get('/todos')
def all_todos():
    view = request.args.get('view', None)
    query = request.args.get('q', '')
    todos = Todo.all(view, query)

    if request.headers.get('HX-Request'):
        return render_template("main.html", todos=todos, view=view, search=query,
                               date_today=datetime.today().strftime('%Y-%m-%d'))

    return render_template("index.html", todos=todos, view=view, search=query,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.post('/todos')
def create_todo():
    view = request.form.get('view', None)
    priority = int(request.form.get('priority', 0))
    todo = Todo(text=request.form['todo'], complete=False, priority=priority, due_date=request.form['due_date'])
    todo.save()

    if request.headers.get('HX-Request'):
        todos = Todo.all(view)
        return render_template("main.html", todos=todos, view=view)

    return redirect('/todos' + add_view_filter(view))


@app.post('/todos/<id>/toggle')
def toggle_todo(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.toggle_completed()
    todo.save()
    todos = Todo.all(view)
    return render_template("main.html", todos=todos, view=view, editing=None,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.get('/todos/<id>/edit')
def edit_todo(id):
    view = request.args.get('view', None)
    todos = Todo.all(view)
    return render_template("index.html", todos=todos, editing=int(id), view=view,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.post('/todos/<id>')
def update_todo(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.text = request.form['todo']
    todo.due_date = request.form['due_date']
    todo.priority = int(request.form.get('priority', todo.priority))
    todo.save()
    return redirect('/todos' + add_view_filter(view))


@app.get('/todos/reorder')
def show_reorder_ui():
    view = request.args.get('view', None)
    todos = Todo.all(view)
    return render_template("reorder.html", todos=todos, date_today=datetime.today().strftime('%Y-%m-%d'))


@app.post('/todos/reorder')
def update_todo_order():
    view = request.args.get('view', None)
    id_list = request.form.getlist("ids")
    Todo.reorder(id_list)
    todos = Todo.all(view)
    return render_template("main.html", todos=todos, view=view, editing=None,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.get('/todos/calendar')
def calendar_view():
    view = request.args.get('view', None)
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Adjust the month/year for next/previous navigation
    current_date = datetime(year, month, 1)
    date_info = Todo.get_date(current_date)
    todos = Todo.get_current_month_of_todos(year,month)

    return render_template("calendar.html", view=view, **date_info, month=month, year=year, current_date=current_date, todos_map = todos)


def add_view_filter(view):
    return ("?view=" + view) if view is not None else ""


if __name__ == '__main__':
    app.run(port=5000, debug=True)
