import subprocess 
import docker

import stegtest.utils.lookup as lookup
from pathos.multiprocessing import ProcessingPool as Pool

client = docker.from_env()

def start_docker(image_name, volumes):
	container_id = client.containers.run(image_name, volumes=volumes, tty=True, detach=True)
	return container_id

def stop_docker(container_id):
	container = client.containers.get(container_id)
	container.stop()

def run_native(cmd, print_cmd=False):
	if print_cmd:
		print(cmd)
	subprocess.run(cmd, shell=True)

def run_docker(container_id, cmd, wdir=None):
	container = client.containers.get(container_id)
	if wdir:
		container.run_exec(cmd, detach=True, workdir=wdir)
	else:
		container.run_exec(cmd, detach=True)

def run_class(cmd):
	raise NotImplementedError

def run_rest(cmd):
	raise NotImplementedError

def run(cmd, *args):
	cmd_type = cmd[lookup.COMMAND_TYPE]
	{
		lookup.DOCKER: run_docker,
		lookup.NATIVE: run_native,
		lookup.REST: run_rest,
		lookup.CLASS: run_class,
	}[cmd_type](args)

	return True

def run_pool(cmd_list, threads=None):
	if threads:
		pool = Pool(threads)
	else:
		pool = Pool()

	pool.map(run, cmd_list)