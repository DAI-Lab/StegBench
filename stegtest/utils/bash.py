import subprocess 

def replace_cmd(cmd:str, replacements):
	cmd = cmd.split()
	cmd = [subpart if subpart not in replacements.keys() else replacements[subpart] for subpart in cmd]
	return ' '.join(cmd)

def run_cmd(cmd, print_cmd=False):
	if print_cmd:
		print(cmd)
	subprocess.run(cmd, shell=True)
