import os

from django.conf import settings
from git import Repo

from functions.constants import KUBE_JOB
from functions.models import ServerlessFunction
from kubernetes import client, config
from kubernetes.client.rest import ApiException


config.load_kube_config()
batch_v1 = client.BatchV1Api()


def push_folder_changes(name, version, add=False):
    try:
        repo_path = f"{os.path.join(settings.BASE_DIR)}"
        folder_path = f"{os.path.join(settings.BASE_DIR, "argo")}"  # Specific folder to push

        repo = Repo(repo_path)

        folder_relative_path = os.path.relpath(folder_path, repo_path)
        if add:
            repo.git.add(folder_relative_path)

        if repo.is_dirty(untracked_files=True):
            commit_message = f"added/modified {name}:{version}"
            repo.index.commit(commit_message)

            origin = repo.remote(name="origin")
            origin.push()
    except Exception as e:
        print(e)


def create_kubernetes_job(function: ServerlessFunction):
    context = {
        "name": function.name,
        "docker_image": f"apurvchaudhary/{function.name}:{function.version}",
        "id": function.id,
    }
    with open(f"argo/{function.name}-{function.id}.yaml", "a+") as kubefile:
        kubefile.write(KUBE_JOB.format(**context))
    push_folder_changes(function.name, function.version)


def remove_completed_jobs():
    files_to_be_remove = []
    try:
        jobs = batch_v1.list_namespaced_job("serverless")
        for job in jobs.items:
            if job.status.succeeded == 1:
                files_to_be_remove.append(job.metadata.name)
    except ApiException:
        pass
    finally:
        return files_to_be_remove


def remove_file_from_repo():
    files = remove_completed_jobs()
    if files:
        commit = False
        for file in files:
            yaml_path = f"argo/{file}.yaml"
            if os.path.exists(yaml_path):
                os.remove(yaml_path)
                commit = True
        if commit:
            push_folder_changes("removal", "removed")
