from TodoApp.models import ToDos



class TestGet:

    predefined_todo = ToDos(
        title="Test",
        description="Test",
        priority=5,
        complete=False,
        owner_id=1
    )
