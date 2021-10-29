from collections import defaultdict
from os.path import abspath, join

import stegbench.executor.runner as runner
import stegbench.utils.filesystem as fs
import stegbench.utils.generator as generator
import stegbench.utils.lookup as lookup


def update_write_file(algorithm_info, cmd, to_detect_list):
    defaultdict(None)

    update = None
    if lookup.RESULT_CSV_FILE in cmd:
        file_type = 'csv'
        temp = False
        update = lookup.RESULT_CSV_FILE
    elif lookup.TEMP_CSV_FILE in cmd:
        file_type = 'csv'
        temp = True
        update = lookup.TEMP_CSV_FILE
    elif lookup.RESULT_TXT_FILE in cmd:
        file_type = 'txt'
        temp = False
        update = lookup.RESULT_TXT_FILE
    elif lookup.TEMP_TXT_FILE in cmd:
        file_type = 'txt'
        temp = True
        update = look.RESULT_CSV_FILE

    if update:
        for to_detect in to_detect_list:
            write_file = generator.generate_result_file(algorithm_info, to_detect, file_type, temp)
            to_detect[update] = write_file

#### NATIVE ####


def preprocess_native(algorithm_info, to_detect_list):
    # probably need to transform from directory to list, vice versa.
    pre_cmd = lookup.get_pre_cmd(algorithm_info)
    cmd = lookup.get_cmd(algorithm_info)
    updated_detect_list = to_detect_list

    if pre_cmd:
        update_write_file(algorithm_info, pre_cmd, updated_detect_list)
    if lookup.INPUT_IMAGE_DIRECTORY in cmd:
        updated_detect_list = generator.get_directories(to_detect_list)
    update_write_file(algorithm_info, cmd, updated_detect_list)

    return [], updated_detect_list


def generate_native_cmd(algorithm_info, to_detect):
    # need to do regular substitutions
    cmd = lookup.get_cmd(algorithm_info)
    new_cmd = generator.replace(cmd, to_detect)

    if lookup.PIPE_OUTPUT in algorithm_info:
        result_file = generator.generate_result_file(algorithm_info, to_detect, 'txt')
        write_to_result_cmd = ' > ' + result_file

        new_cmd += write_to_result_cmd

    if lookup.WORKING_DIR in algorithm_info:
        wdir = algorithm_info[lookup.WORKING_DIR]
        new_cmd = ['(', 'cd', wdir, '&&', new_cmd, ')']
        new_cmd = ' '.join(new_cmd)

    return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [new_cmd]}


def postprocess_native(algorithm_info, detected_list):
    post_cmds = []
    post_cmd = lookup.get_post_cmd(algorithm_info)
    if post_cmd is None:
        return post_cmds

    update_write_file(algorithm_info, post_cmd, detected_list)

    for to_detect in detected_list:
        generated_post_cmd = generator.replace(post_cmd, to_detect)
        post_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                         lookup.COMMAND: [generated_post_cmd]})

    return post_cmds


def termination_native(algorithm_info, detected_list):
    termination_cmds = []

    if lookup.PIPE_OUTPUT in algorithm_info:
        lookup.get_cmd(algorithm_info)
        for detected in detected_list:
            result_file = generator.generate_result_file(algorithm_info, detected, 'txt')
            removal_cmd = ' '.join([lookup.removal_prefix, result_file])

            termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                                    lookup.COMMAND: [removal_cmd]})

    for detected in detected_list:
        if lookup.TEMP_CSV_FILE in detected:
            removal_cmd = ' '.join([lookup.removal_prefix, detected[lookup.TEMP_CSV_FILE]])
            termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                                    lookup.COMMAND: [removal_cmd]})
        if lookup.TEMP_TXT_FILE in detected:
            removal_cmd = ' '.join([lookup.removal_prefix, detected[lookup.TEMP_TXT_FILE]])
            termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                                    lookup.COMMAND: [removal_cmd]})
        if lookup.RESULT_CSV_FILE in detected:
            removal_cmd = ' '.join([lookup.removal_prefix, detected[lookup.RESULT_CSV_FILE]])
            termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                                    lookup.COMMAND: [removal_cmd]})
        if lookup.RESULT_TXT_FILE in detected:
            removal_cmd = ' '.join([lookup.removal_prefix, detected[lookup.RESULT_TXT_FILE]])
            termination_cmds.append({lookup.COMMAND_TYPE: lookup.NATIVE,
                                    lookup.COMMAND: [removal_cmd]})

    return termination_cmds

##### DOCKER ####


def preprocess_docker(algorithm_info, to_detect_list):
    """starts docker command and updates parameters appropriately"""
    image_name = algorithm_info[lookup.DOCKER_IMAGE]
    cmd = lookup.get_cmd(algorithm_info)
    volumes = {}

    if lookup.INPUT_IMAGE_DIRECTORY in cmd:
        updated_detect_list = generator.get_directories(to_detect_list)
        for updated_detect in updated_detect_list:
            docker_directory = '/' + fs.get_uuid()
            volumes[updated_detect[lookup.INPUT_IMAGE_DIRECTORY]] = {
                'bind': docker_directory, 'mode': 'rw'}
            updated_detect[lookup.INPUT_IMAGE_DIRECTORY] = docker_directory
    elif lookup.INPUT_IMAGE_PATH in cmd:
        for to_detect in to_detect_list:
            original_input_path = to_detect[lookup.INPUT_IMAGE_PATH]
            original_input_path = abspath(original_input_path)

            local_input_dir = fs.get_directory(original_input_path)
            volumes[local_input_dir] = {'bind': lookup.input_dir, 'mode': 'rw'}

            input_filename = fs.get_filename(original_input_path)
            new_input_path = join(lookup.input_dir, input_filename)
            to_detect[lookup.INPUT_IMAGE_PATH] = new_input_path

    result_directory = abspath(lookup.get_algo_asset_dirs()[lookup.detector])
    assert(fs.dir_exists(result_directory))

    volumes[result_directory] = {'bind': lookup.result_dir, 'mode': 'rw'}

    container_id = runner.start_docker(image_name, volumes=volumes)
    for to_detect in to_detect_list:
        to_detect[lookup.container_id] = container_id

    return [], to_detect_list


def generate_docker_cmd(algorithm_info, to_detect):
    cmd = lookup.get_cmd(algorithm_info)
    new_cmd = generator.replace(cmd, to_detect)

    if lookup.PIPE_OUTPUT in algorithm_info:
        # need to return a native command for now -- HACKY FIX!!
        result_file_path = generator.generate_result_file(algorithm_info, to_detect, 'txt')
        write_to_result_cmd = ' > ' + result_file_path

        docker_cmd = [lookup.docker_exec_prefix]
        if lookup.WORKING_DIR in algorithm_info:
            docker_cmd.append('-w ' + algorithm_info[lookup.WORKING_DIR])

        docker_cmd += [str(to_detect[lookup.container_id]), new_cmd, write_to_result_cmd]
        docker_cmd = ' '.join(docker_cmd)
        return {lookup.COMMAND_TYPE: lookup.NATIVE, lookup.COMMAND: [docker_cmd]}

    params = [to_detect[lookup.container_id], new_cmd]
    if lookup.WORKING_DIR in algorithm_info:
        params.append(algorithm_info[lookup.WORKING_DIR])

    return {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}


def postprocess_docker(algorithm_info, detected_list):
    # need to end the docker process
    post_cmds = []
    post_cmd = lookup.get_post_cmd(algorithm_info)

    if post_cmd:
        for detected in detected_list:
            new_cmd = generator.replace(post_cmd, detected)
            params = [detected[lookup.container_id], new_cmd]
            if lookup.WORKING_DIR in algorithm_info:
                params.append(algorithm_info[lookup.WORKING_DIR])

            docker_cmd = {lookup.COMMAND_TYPE: lookup.DOCKER, lookup.COMMAND: params}
            post_cmds.append(docker_cmd)

    return post_cmds


def terimination_docker(algorithm_info, detected_list):
    termination_cmds = []
    docker_containers = list(
        set(list(map(lambda detector: detector[lookup.container_id], detected_list))))
    for container_id in docker_containers:
        termination_cmds.append({lookup.COMMAND_TYPE: lookup.END_DOCKER,
                                lookup.COMMAND: [container_id]})

    return termination_cmds


def generate_native(algorithm_info, to_detect_list):
    pre_cmds, updated_detect_list = preprocess_native(algorithm_info, to_detect_list)
    cmds = [generate_native_cmd(algorithm_info, to_detect) for to_detect in updated_detect_list]
    post_cmds = postprocess_native(algorithm_info, updated_detect_list)
    termination_cmds = termination_native(algorithm_info, updated_detect_list)
    return pre_cmds, cmds, post_cmds, termination_cmds


def generate_docker(algorithm_info, to_detect_list):
    pre_cmds, updated_detect_list = preprocess_docker(algorithm_info, to_detect_list)
    cmds = [generate_docker_cmd(algorithm_info, to_detect) for to_detect in updated_detect_list]
    post_cmds = postprocess_docker(algorithm_info, updated_detect_list)
    termination_cmds = terimination_docker(algorithm_info, updated_detect_list)
    return pre_cmds, cmds, post_cmds, termination_cmds


def generate_commands(algorithm_info, to_detect_list):
    command_type = algorithm_info[lookup.COMMAND_TYPE]
    generate_function = {
        lookup.DOCKER: generate_docker,
        lookup.NATIVE: generate_native,
    }[command_type]

    return generate_function(algorithm_info, to_detect_list)
