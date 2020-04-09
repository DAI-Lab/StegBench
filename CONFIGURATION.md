
# CONFIGURATION SPECIFICATION

<b>For examples of configuration options, please look at the examples/configs folder. We have providede a number of different configuration options that should be able to help you when you write your own.</b>

Stegtest works by processing configuration files that contain information about each of the algorithms in the system. This allows StegTest to be a highly interoperable and modular system that can easily integrate into existing steganographic pipelines. Configuration files specify how a specific steganographic or steganalysis tool operates on your machine. You pass in several parameters that determine the following

- <b>Compatibility</b>: The compatibility of the tool for different operating mechanisms
- <b>Command Execution</b>: The commands that must be used to execute the tool. 

Configuration files are specified by the file format .ini. The tool's name is given by the header of the configuration. In any configuration file, there can be a number of configurations for different tools. They are uniquely identified by the header, which is the name the system designates to that tool. In general, all configuration specifications will have the following:

- <b>algorithm_type</b>: The algorithm type of the tool. The only options are 'embeddor' or 'detector'.
- <b>compatible_types</b>: A list of strings of different file formats that the tool can work with. The image formats allowed are 'png', 'pgm', 'tiff', 'jpeg', 'jpg', 'bmp'.
- <b>command_type</b>: The only options here are 'native' or 'docker'. We will detail the extra specification needed for docker commands below.
- <b>run</b>: This command will be translated by our machine interepreter to execute your command. We detail specficications for the run command below.
- <b>working_dir</b>: If this is set, the command will execute at this location. This is necessary for certain tools that need specific asset files to run. 
- <b>post_run</b>: This command will be run after all the run commands for your tool have been executed. It is interpreted exactly like the regular run command but just run in sequence. This might be necessary for post-processing for some tools. 

## Command Types

### Native Commands

Native commands are commands that can be executed natively in your environment. You can consider python commands or bash commands or other command that are of a similar nature to be native commands. Traditionally, this means that the command/tool can be executed via a bash terminal. Native commands are specified by their designation of command_type=native 

### Docker Commmands

Docker commands are commands that are executed via a docker image. There are a number of publicaly available tools that will not be supported on your machine. Instead, you may prefer to use Docker to be able to execute those tools. In this case, we provide several configuration options for your docker command. They are the following:

- <b>docker_image</b>: This is the name of the docker image that your tool is located in. The docker image must be available on your computer

We make use of the Docker Python SDK to execute in the docker environment. We make sure to clean up all the docker containers after we have used them for execution. Remember to increase resources to your Docker system if you want more resources. 

## Command Generation

We now explain the specific flags that you will require for writing your commands in the StegTest configuration specification. These flags are specific to the algorithm type that you are using. So, we will explain the flags for both embeddors and detectors. Later on, we will walk through several examples so that you can see how we write these configuration specifications. 

### Embeddor Command Generation

There are flags that are specific to embeddor command generation. These flags tell the StegTest system what to substitute for certain fields when generating the commands from the run command that you provide. The reason for these flags is that embedding procedures require operating on large image datasets and there are tools that operate on the entire dataset while there are tools that will only operate on one image. Furthermore, additional constraints on how these tools embed messages necessitate flags in the run command so that the system can properly substitute values and generate proper commands. The flags that are available to embeddor commands are the following:

#### Input Image Path

The following are the flags used for when the system is telling your tool which image to embed. Your command must have one of the flags below:

- <b>INPUT_IMAGE_PATH</b>: Substituted for the path to an image being embedded.
- <b>INPUT_IMAGE_DIRECTORY</b>: Substituted for the path to the image directory of images being embedded.

#### Secret Message 

The following are the flags that are used when you are providing how your tool will embed secret messages. Either SECRET_TXT_FILE or SECRET_TXT_PLAINTEXT or PAYLOAD must be selected for an embeddor. Otherwise, the system will not be able to figure out how to provide the message that is being embedded. 

- <b>SECRET_TXT_FILE</b>: Substituted for the path to a text file containing the string that will be embedded
- <b>SECRET_TXT_PLAINTEXT</b>: Substituted for a string that will be embedded
- <b>PASSWORD</b>: Substituted with a randomly generated password 
- <b>PAYLOAD</b>: Subsituted with the embedding ratio required during the embedding operation. 

#### Output Image Path

The following are the flags used for when the system is telling your tool where to output embedded images. Your command must have one of the flags below:

- <b>OUTPUT_IMAGE_PATH</b>: Substitued for the path to the output image. 
- <b>OUTPUT_IMAGE_DIRECTORY</b>: Subsituted for the path to the output image directory. 

An example steganographic image tool may have the following run command: 
```
run = tool_executable INPUT_IMAGE_PATH SECRET_TXT_PLAINTEXT OUTPUT_IMAGE_PATH
```

If our tool was being used to generate a steganographic image database on some directory, our engine would generate run commands for each of the images being embedded. For example, if one of the embedding operations has the requirements: INPUT_IMAGE_PATH=/path/to/image, SECRET_TXT_PLAINTEXT='secret', OUTPUT_IMAGE_PATH='/path/to/output', our command generation engine would create the following command that would then be executed

```
tool_executable /path/to/image secret /path/to/output
```

### Detector Command Generation

There are flags that are specific to detector command generation. These flags tell the StegTest system what to substitute for certain fields when generating the commands from the run command that you provide. The reason for these flags is that detection procedures require operating on large image datasets and that there are tools that operate on the entire dataset while there are tools that will only operate on one image. Furthermore, additional constraints on how these tools detect if an image is steganographic or not necessitate flags in the run command so that the system can properly substitute values and generate proper commmands. The flags that are available to detector commands are the following:

#### Input Image Path

The following are the flags used for when the system is telling your tool which image to detect. Your command must have one of the flags below:

- <b>INPUT_IMAGE_PATH</b>: Substituted for the path to an image being detected. 
- <b>INPUT_IMAGE_DIRECTORY</b>: Substited for the path to the image directory of images being detected. 

#### Result File Path

The following are the flags used for the when the system is telling your tool where to output the results of the tool's detection algorithm. Your run or post_run command must include a RESULT_TXT_FILE or a RESULT_CSV_FILE flag.

- <b>RESULT_TXT_FILE</b>: Substited for the path to the result text file where the result from the command is stored.
- <b>TEMP_CSV_FILE</b>: Substituted for the path to a temporary CSV file. Usually, there is a post_run command that will then process this temp_csv_file into the proper format for the result. Only necessary for a subset of tools. 
- <b>RESULT_CSV_FILE</b>: Subsituted for the path to a result CSV file. 

## Embeddor Specific Configurations

The embeddor configuration has two extra specific configuration options. Remember a configuration is considered to be an embeddor, if the algorithm_type is set to 'embeddor'. The first is the following:

- <b>max_embedding_ratio</b>: The maximum embedding ratio (measured in either bits per pixel for spatial images or bits per nonzero AC DC coefficients for transform images) that the tool can support.

The other extra configuration option is a verify command, that we now discuss below. 

### Verify command 

The verify command is used to check if a steganographic database was properly generated. To do this, our system requires you to pass a skeleton command, similar to how you passed one for the run command. This command must end in outputting an extracted message from an input image. The flags available to the verify command are the following:

#### Input Image

The following are the flags used for when the system is telling your tool which image to extract a message from. Your command must include the flag below:

- <b>INPUT_IMAGE_PATH</b>: Substituted for the path to an image being detected. 

#### Secret Message Extraction

The following are the flags that are used when your tool requires a password to decrypt the message that it extracts. 

- <b>PASSWORD</b>: Substituted with a randomly generated password 

#### Result

There are two options here. Your command must either include the following flag

- <b>VERIFY_TXT_FILE</b>: Substituted with the extracted message from the image.

Or, your configuration must include the following parameter:

```
pipe_output = True
```

The pipe_output configuration will pipe the output from your command to a text file that will then be used for verification. 


## Detector Specific Configurations 


There are several extra detector-specific configuration options. The first extra option specifies what type of detector you are using. This will decide if the results collector will either classify the result as categorical (steganographic or cover) or a probabilistic measure (likelihood of being steganographic). The configuration option for this is:

- <b>detector_type</b>: The detector type of the detector. The only options are 'binary' or 'probability'.

They next few configuration options are relate to how we collect results. 

### Result Specification

For detectors that operate on individual images rather than an entire directory, we have the following configuraiton option:

```
pipe_output = True
```

If this is set to true, the output from the run command will be piped to a text result file that will then be analyzed. This is identical to the pipe_output we found in the verification command.

To collect results from StegTest, there are two options. Your specification can choose one of the following paths: 

- <b>text file result</b>: pipe_output = True or using the RESULT_TXT_FILE in your run or post_run command. 
- <b>csv file result</b>: RESULT_CSV_FILE in your run or post_run command. 

Whichever option you choose for your tool, you will also have to provide two additional configuration options that let our system know if your tool has decided that the result is steganographic or cover. <b>Note that only binary detectors are required to have a regex filter</b>. Namely, we provide you with two regex configuration options that are the following:

- <b>regex_filter_yes</b>: If this regex matches to the contents of the result file the image is considered to be a steganographic image. 
- <b>regex_filter_yes</b>: If this regex matches to the contents of the result file the image is considered to be a cover image. 

If your command chooses option 2, which returns in a csv file, then you have the additional option of providing an output_file configuration.

- <b> output_file </b>: If this configuration is provided, the StegTest system will use this information to match the image names outputted in your tool's CSV file with repsect to the image input that was provided to your tool.

To clarify this configuration, if your tool was told to run detection on /path/to/image and when it returned the result in the csv it returned 'image , True', our system would need to be able to match /path/to/image with image. To do this, you can use the flag INPUT_IMAGE_NAME which relates the path to the file name. An example of this is shown with StegExpose. 

Finally, if you choose to end with a result_csv_file, it is important that your file follow the following format <b>Result CSV files must only have two columns with no headers. The first column should be the image file path or name as specified by output_file that is being detected. The second column will be the actual result that will pass through the regex filter.</b>

## Embeddor Configuration Examples

Let us walk through several embeddor configuration file examples. 

### Example #1: Native Command

First we have SteganoGAN, available here http://github.com/DAI-Lab/SteganoGAN/. 

![](bin/img_assets/steganogan.png)

As we can see, steganoGAN is an embeddor, that can operate on png and pgm image formats. Furthemore, it has a maximum embedding ratio of 4.0 bits per pixel. Next, it is a native command which means it can be executed natively without docker. The run command shows us that SteganoGAN when used as a tool will take in the input image path, the plaintext of the message to be embedded, and the output image path. Finally, we see that steganoGAN has a function to extract the embedded message and only requires the INPUT_IMAGE_PATH. The pipe_output flag is turned on so that the result from the verify command will be piped into a verification text file. 

### Example #2: Docker Command

Next, we look at LSBSteg, a tool that is available here https://github.com/DominicBreuker/stego-toolkit. This repository provides a number of tools via a Docker Image. 

![](bin/img_assets/LSBSteg.png)

As we can see, LSBSteg is an embeddor that operates on png or bmp image types. It has a max ratio of 0.5 bits per pixel. It uses a docker command to run, which means that a docker image name must be provided. As we can see, it is and the docker image name is 'local/stego'. We see that the run command uses similar flags to the SteganoGAN command. In comparison, the verify command does not use the pipe output configuration option but rather provides the file to which the function should pipe output to. Usually, the pipe output configuration option is only used for tools that only print to console. 

## Detector Configuration Examples

Let us walk through several detector configruation file examples. 

### Example #1: Classification Detector

First, we look at StegExpose, a tool that is available at https://github.com/b3dk7/StegExpose. 

![](bin/img_assets/StegExpose.png)

As we can see, StegExpose is a detector tool that operates as a binary detector. This means it is categorical. We see that it can operate on png or bmp image formats and that it executes natively without Docker. Next, we see that the run command uses java to call a .jar file. Furthermore, the run command takes in an INPUT_IMAGE_DIRECTORY and outputs a TEMP_CSV_FILE. Since a detector configuration must always include either a RESULT_TXT_FILE/pipe_output or a RESULT_CSV_FILE, we should expect one of these options in the post_run. A

nd as expected, we do see a RESULT_CSV_FILE in the post_run. The post_run calls a custom processing script (available in the examples/ folder) that converts the TEMP_CSV_FILE into a csv file that matches the specifications described above. Since this operation is using a RESULT_CSV_FILE, we also exepct an output_file configuration that specifies the name of the images in the first column. In this case, the tool outputs images with their file name and not their file path as specified by output_file = INPUT_IMAGE_NAME


### Example #2: Probablistic Detector

Finally, we look at a YeNet model that comes from the StegDetect library, a tool that is privately available at https://github.com/DAI-Lab/StegDetect.

![](bin/img_assets/YeNet.png)

As we can see, YeNet is a probabilistic detector that operates on png, pgm jpeg, and jpg image file formats. It executes natively via a script that is available in the examples folder. The configuration meets specification requirements since the run command includes a RESULT_TXT_FILE. Note that this configuration does not require a regex filter since it is for a probabilistic detector.  

