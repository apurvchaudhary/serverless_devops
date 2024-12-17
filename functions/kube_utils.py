import os

from django.conf import settings
from git import Repo

from functions.constants import KUBE_JOB
from functions.models import ServerlessFunction
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from functions.cmd import run_cmd


config.load_kube_config()
batch_v1 = client.BatchV1Api()
core_v1 = client.CoreV1Api()


def push_folder_changes(name, version):
    try:
        repo_path = f"{os.path.join(settings.BASE_DIR)}"
        folder_path = (
            f"{os.path.join(settings.BASE_DIR, "argo")}"  # Specific folder to push
        )

        repo = Repo(repo_path)

        folder_relative_path = os.path.relpath(folder_path, repo_path)
        repo.git.add(folder_relative_path)

        if repo.is_dirty(untracked_files=True):
            commit_message = f"added/modified {name}:{version}"
            repo.index.commit(commit_message)

            origin = repo.remote(name="origin")
            origin.push()
    except Exception as e:
        print(e)


def run_argo_cmds():
    login_command = "argocd login localhost:8080 --username admin --password icbEDa9adZnKq32Z --insecure"
    sync_command = "argocd app sync serverless-devops --prune"
    run_cmd(login_command)
    run_cmd(sync_command)


def create_kubernetes_job(function: ServerlessFunction):
    context = {
        "name": function.name,
        "docker_image": f"apurvchaudhary/{function.name}:{function.version}",
        "id": function.id,
    }
    with open(f"argo/{function.name}-{function.id}.yaml", "a+") as kubefile:
        kubefile.write(KUBE_JOB.format(**context))
    push_folder_changes(function.name, function.version)
    run_argo_cmds()


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
            run_argo_cmds()


def get_pod_name_from_job(job_name):
    try:
        pods = core_v1.list_namespaced_pod(namespace="serverless")
        for pod in pods.items:
            if pod.metadata.owner_references:
                for owner in pod.metadata.owner_references:
                    if owner.kind == "Job" and owner.name == job_name:
                        return pod.metadata.name
        return None
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return None


def stream_pod_logs(function):
    pod_name = get_pod_name_from_job(f"{function.name}-{function.id}")
    if pod_name:
        try:
            logs = core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace="serverless",
                follow=True,
                _preload_content=False,
            )
            for line in logs.stream():
                yield f"{line.decode('utf-8')}"
        except Exception as e:
            yield f"Error retrieving logs: {e}"
    else:
        yield f"Function : {function.name}:{function.version} is not running currently"
