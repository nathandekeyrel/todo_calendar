from flask import Flask, request, render_template
from werkzeug.utils import redirect

from src.model.todo import Todo, db
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')

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
    sort_type = request.args.get('sort_option', '')
    todos = Todo.all(view, query, sort_type)

    if request.headers.get('HX-Request'):
        return render_template("main.html", todos=todos, view=view, search=query,
                               date_today=datetime.today().strftime('%Y-%m-%d'))

    return render_template("index.html", todos=todos, view=view, search=query,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.post('/todos')
def create_todo():
    view = request.form.get('view', None)
    priority = int(request.form.get('priority', 0))
    recurring = request.form.get('recurring', None)
    todo = Todo(text=request.form['todo'], complete=False, priority=priority,
                due_date=request.form['due_date'], recurring=recurring)
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


@app.post('/todos/<id>/toggle_on_cal')
def toggle_todo_on_cal(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.toggle_completed()
    todo.save()
    todos = Todo.all(view)
    return render_template("calendar_todo.html", todo=todo, view=view, editing=None,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.get('/todos/<id>/edit')
def edit_todo(id):
    view = request.args.get('view', None)
    todos = Todo.all(view)

    if request.headers.get('HX-Request'):
        return render_template("main.html", todos=todos, editing=int(id), view=view,
                               date_today=datetime.today().strftime('%Y-%m-%d'))

    return render_template("index.html", todos=todos, editing=int(id), view=view,
                           date_today=datetime.today().strftime('%Y-%m-%d'))


@app.post('/todos/<id>')
def update_todo(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.text = request.form['todo']
    todo.due_date = request.form['due_date']
    todo.priority = int(request.form.get('priority', todo.priority))
    todo.recurring = request.form.get('recurring', None)
    todo.save()

    if request.headers.get('HX-Request'):
        return redirect('/todos' + add_view_filter(view))

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


@app.post('/todos/<id>/delete')
def delete_todo(id):
    todo = Todo.find(int(id))
    todo.delete_instance()
    todos = Todo.all(request.form.get('view', None))
    return render_template("main.html", todos=todos, view=request.form.get('view', None))


@app.get('/todos/calendar')
def calendar_view():
    view = request.args.get('view', None)
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Adjust the month/year for next/previous navigation
    current_date = datetime(year, month, 1)
    date_info = Todo.get_date(current_date)

    return render_template("calendar.html", view=view, Todo=Todo, **date_info,
                           month=month, year=year, current_date=current_date)


def add_view_filter(view):
    return ("?view=" + view) if view is not None else ""


if __name__ == '__main__':
    app.run(port=5000, debug=True)
