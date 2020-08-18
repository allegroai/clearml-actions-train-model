import json
import os

from github3 import login

from trains import Task


def clone_and_queue(template_task: str, queue: str) -> Task:
    github_payload = os.getenv('GITHUB_EVENT_PATH')
    with open(github_payload, 'r') as f:
        payload = json.load(f)

    task = Task.get_task(task_id=template_task)
    # Clone the task to pipe to. This creates a task with status Draft whose parameters can be modified.
    cloned_task = Task.clone(
        source_task=task,
        name=f"{template_task} cloned task from Github"
    )
    script_commit = payload.get("comment", {}).get("body", "").partition(" ")[2]
    selected_type, _, selected_value = script_commit.partition(" ")
    if selected_type and selected_value:
        data_script = cloned_task.data.script
        if selected_type == "branch":
            data_script.branch = selected_value
            data_script.tag = ""
            data_script.version_num = ""
        elif selected_type == "tag":
            data_script.branch = ""
            data_script.tag = selected_value
            data_script.version_num = ""
        elif selected_type == "commit":
            data_script.branch = ""
            data_script.tag = ""
            data_script.version_num = selected_value
        else:
            raise Exception(f"You must supply branch, tag or commit as type, not {selected_type}")

        print(f"Change train script head to {selected_value} {selected_type}")
        # noinspection PyProtectedMember
        cloned_task._update_script(script=data_script)

    Task.enqueue(cloned_task.id, queue_name=queue)
    owner, repo = payload.get("repository", {}).get("full_name", "").split("/")
    if owner and repo:
        gh = login(token=os.getenv("GITHUB_TOKEN"))
        if gh:
            issue = gh.issue(owner, repo, payload.get("issue", {}).get("number"))
            if issue:
                issue.create_comment(f"New task, id:{cloned_task.id} is in queue {queue_name}")
            else:
                print(f'can not comment issue, {payload.get("issue", {}).get("number")}')
        else:
            print(f"can not log in to gh, {os.getenv('GITHUB_TOKEN')}")
    return cloned_task


if __name__ == "__main__":
    # Get the user input
    base_task_id = os.getenv('INPUT_TASK_ID')
    queue_name = os.getenv('INPUT_QUEUE_NAME')
    os.environ["TRAINS_API_ACCESS_KEY"] = os.getenv('INPUT_TRAINS_API_ACCESS_KEY')
    os.environ["TRAINS_API_SECRET_KEY"] = os.getenv('INPUT_TRAINS_API_SECRET_KEY')
    os.environ["TRAINS_API_HOST"] = os.getenv('INPUT_TRAINS_API_HOST')
    cloned_task = clone_and_queue(template_task=base_task_id, queue=queue_name)
    print(f'::set-output name=CLONED_TASK::{cloned_task.id}')
    print(f'::set-output name=TASK_STATUS::{cloned_task.get_status()}')
