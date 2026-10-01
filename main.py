import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Переменная окружения DATABASE_URL не найдена в файле .env")
engine = create_engine(DATABASE_URL)
status_names = {
    0: "waiting",
    1: "in progress",
    2: "done",
}
class Base(DeclarativeBase):
    pass
class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_of_task: Mapped[str] = mapped_column(String(60))
    details_of_task: Mapped[str] = mapped_column(String(360))
    task_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
Base.metadata.create_all(engine)
def check_input(prompt: str, max_len: int) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print("Can't be empty")
        elif len(value) > max_len:
            print(f"Length can't be over {max_len} symbols (yours: {len(value)})")
        else:
            return value
def choosing_task(a: int) -> int:
    while True:
        n = input(f"Enter number (1-{a}): ").strip()
        if not n.isdigit():
            print("It must be a number, try again")
        elif int(n) < 1 or int(n) > a:
            print(f"It must be from 1 to {a}")
        else:
            return int(n)
def ask_status() -> int:
    print("1 - waiting")
    print("2 - in progress")
    print("3 - done")
    return choosing_task(3) - 1
def add_task():
    name = check_input("Enter task name: ", 60)
    details = check_input("Enter details of task: ", 360)
    status = ask_status()

    with Session(engine) as session:
        new_task = Task(
            name_of_task=name,
            details_of_task=details,
            task_status=status,
        )
        session.add(new_task)
        session.commit()
        print(f"Task #{new_task.id} added")


def show_tasks() -> int:
    with Session(engine) as session:
        tasks = session.scalars(select(Task)).all()

        if not tasks:
            print("You don't have any tasks yet")
            return 0

        print("\n--- Your tasks ---")
        for t in tasks:
            status_label = status_names.get(t.task_status, "unknown")
            print(f"[{t.id}] {t.name_of_task} | {t.details_of_task} | {status_label}")
        print("------------------\n")
        return len(tasks)


def get_task_by_number(number: int) -> Task | None:
    with Session(engine) as session:
        tasks = session.scalars(select(Task).order_by(Task.id)).all()
        if number < 1 or number > len(tasks):
            return None
        return tasks[number - 1]


def update_task():
    total = show_tasks()
    if total == 0:
        return

    print("Choose which task you want to update:")
    n1 = choosing_task(total)
    selected = get_task_by_number(n1)
    if selected is None:
        print("Task not found")
        return

    print("\n1 - Change task name")
    print("2 - Change task details")
    print("3 - Change task status")
    choice = choosing_task(3)

    with Session(engine) as session:
        t = session.get(Task, selected.id)
        if t is None:
            print("Task not found")
            return

        if choice == 1:
            t.name_of_task = check_input("Enter new task name: ", 60)
        elif choice == 2:
            t.details_of_task = check_input("Enter new task details: ", 360)
        else:
            t.task_status = ask_status()

        session.commit()
        print(f"Task #{t.id} updated")


def delete_task():
    total = show_tasks()
    if total == 0:
        return

    print("Choose which task you want to delete:")
    n = choosing_task(total)
    selected = get_task_by_number(n)
    if selected is None:
        print("Task not found")
        return

    confirm = input(f"Delete task #{selected.id} '{selected.name_of_task}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled")
        return

    with Session(engine) as session:
        t = session.get(Task, selected.id)
        if t is None:
            print("Task not found")
            return
        session.delete(t)
        session.commit()
        print(f"Task #{selected.id} deleted")


def main():
    print("Hello! I'm a task manager.")
    while True:
        print("\nWhat do you want to do?")
        print("1 - Add task")
        print("2 - Update task")
        print("3 - Show tasks")
        print("4 - Delete task")
        print("0 - Exit")

        choice = input("> ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            update_task()
        elif choice == "3":
            show_tasks()
        elif choice == "4":
            delete_task()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
