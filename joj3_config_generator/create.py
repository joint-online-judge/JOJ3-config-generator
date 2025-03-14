from joj3_config_generator.models import answer, task


def create(answers: answer.Answers) -> task.Config:
    return task.Config(task=task.Task(name=answers.name, type_=answers.type_))
