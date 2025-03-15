from joj3_config_generator.models import answer, task


# TODO: implement
def get_task_conf_from_answers(answers: answer.Answers) -> task.Config:
    return task.Config(task=task.Task(name=answers.name))
