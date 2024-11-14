from collections import defaultdict

from peewee import *
import logging
import datetime

db = SqliteDatabase('todos.db')

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Todo(Model):
    text = CharField()
    complete = BooleanField()
    order = IntegerField(null=True)
    due_date = DateField()
    priority = IntegerField(default=0)

    @classmethod
    def all(cls, view, search=None):
        select = Todo.select()
        if view == "active":
            select = select.where(Todo.complete == False)
        if view == "complete":
            select = select.where(Todo.complete == True)
        if search:
            select = select.where(Todo.text.contains(search))

        return select.order_by(Todo.priority.desc(), Todo.order)

    @classmethod
    def sort_by_date(cls, view, search=None):
        select = Todo.select()
        if view == "active":
            select = select.where(Todo.complete == False)
        if view == "complete":
            select = select.where(Todo.complete == True)
        if search:
            select = select.where(Todo.text.contains(search))

        return select.order_by(Todo.due_date.asc(), Todo.order)

    @classmethod
    def get_current_month_of_todos(cls,year,month):
        select = Todo.select()
        select = select.where(Todo.complete == False)
        print("TESTING:",month,year)
        sorted_todos = select.order_by(Todo.due_date.day).where(Todo.due_date.month == month or Todo.due_date.year == year)
        print([x.text for x in sorted_todos])
        sorted_todos_map = {x:[] for x in range(0,31)}
        for todo in sorted_todos:
            sorted_todos_map[todo.due_date.day].append(todo)

        print(sorted_todos_map)
        todo_day_map = []
        # for i in range(0,31):
        #

        # for x in select.where(Todo.due_date.month == month and Todo.due_date.year == year ):
        #     print("hi:",x)
        return sorted_todos_map

    @classmethod
    def find(cls, todo_id):
        return Todo.get(Todo.id == todo_id)

    def toggle_completed(self):
        self.complete = not self.complete

    def return_formatted_date(self):
        day = self.due_date.day
        month = self.due_date.month
        year = self.due_date.year
        date= f'{month}/{day}/{year}'
        return date

    @classmethod
    def reorder(cls, id_list):
        i = 0
        for tid in id_list:
            todo = Todo.find(int(tid))
            todo.order = i
            i = i + 1
            todo.save()

    @classmethod
    def get_date(cls, date):
        first_of_month = datetime.datetime(date.year, date.month, 1)
        start_day = (first_of_month.weekday() + 1) % 7
        next_month = first_of_month.replace(day=28) + datetime.timedelta(days=4)
        days_in_current_month = (next_month - datetime.timedelta(days=next_month.day)).day
        last_day_of_prev_month = first_of_month - datetime.timedelta(days=1)
        days_in_prev_month = last_day_of_prev_month.day

        return {
            "start_day": start_day,
            "days_in_current_month": days_in_current_month,
            "days_in_prev_month": days_in_prev_month
        }
    @classmethod
    def reorder_date(cls, id_list):
        i = 0

        temp_list= []
        for id in id_list:
            temp_list.append(Todo.find(int(id)))
        temp_list.sort(key=lambda todo_date: datetime.strptime(str(todo_date.due_date), "%Y-%m-%d"))

        for todo in temp_list:
            todo.order = i
            i = i + 1
            todo.save()

    def priority_marker(self):
        return f'[ { '!'* self.priority } ] -- '

    class Meta:
        database = db
