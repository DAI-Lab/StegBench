import subprocess

import docker
import tqdm
from pathos.multiprocessing import ProcessingPool as Pool

import stegbench.utils.lookup as lookup

client = docker.from_env()


def start_docker(image_name, volumes):
    container = client.containers.run(image_name, volumes=volumes, tty=True, detach=True)
    return container.id


def get_container(container_id):
    container = None
    while container is None:
        try:
            container = client.containers.get(container_id)
        except BaseException:
            pass

    return container


def stop_docker(container_id):
    container = get_container(container_id)
    container.stop()


def run_native(cmds):
    subprocess.run(cmds, shell=True)


def run_docker(container_id, cmd, wdir=None):
    container = get_container(container_id)
    if wdir:
        container.exec_run(cmd, workdir=wdir)
    else:
        container.exec_run(cmd)


def run(cmd_info):
    cmd_type = cmd_info[lookup.COMMAND_TYPE]
    run_function = {
        lookup.DOCKER: run_docker,
        lookup.NATIVE: run_native,
        lookup.END_DOCKER: stop_docker,
    }[cmd_type]

    run_info = cmd_info[lookup.COMMAND]
    run_function(*run_info)


def run_pool(cmd_list, threads=None):
    if threads:
        pool = Pool(threads)
    else:
        pool = Pool(1)

    list(tqdm.tqdm(pool.imap(run, cmd_list), total=len(cmd_list)))
