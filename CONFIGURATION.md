
# CONFIGURATION SPECIFICATION

Stegtest works by processing configuration files that contain information about each of the algorithms in the system. This allows StegTest to be a highly interoperable and modular system that can easily integrate into existing steganographic pipelines. Configuration files specify how a specific steganographic or steganalysis tool operates on your machine. You pass in several parameters that determine the following

- <b>Compatibility</b>: The compatibility of the tool for different operating mechanisms
- <b>Command Execution</b>: The commands that must be used to execute the tool. 

## Embeddor Configuration 

### Example #1: Native Command

Let us walk through the example of creating a configuration file for SteganoGAN, available here http://github.com/DAI-Lab/SteganoGAN/. 

![](bin/img_assets/steganogan.png)

### Example #2: Docker Command

Now, let us figure out how to create an embeddor configuration file for a command that runs inside a docker image. In this case we choose LSBSteg, a tool that is available here https://github.com/DominicBreuker/stego-toolkit. 

![](bin/img_assets/LSBSteg.png)

## Detector Configuration

There are two types of detectors. They are the following:

- <b>Classification</b>: The classification detector classifies steganographic and cover images as yes/no.
- <b>Probabilistic</b>: The probabilistic detector returns the probability that an image is steganographic 

### Example #1: Classification Detector

Now, let us figure out how to create a detector configuration file for a detector that runs natively as a classification detector. In this case, we will use the StegExpose tool, a tool that is available at https://github.com/b3dk7/StegExpose. 

![](bin/img_assets/StegExpose.png)

### Example #2: Probablistic Detector

Finally, we will figure out how to create a detector configuration file for a detector that is a probabilistic detector. In this case, we will use the YeNet model that comes from the StegDetect library, a tool that is privately available at https://github.com/DAI-Lab/StegDetect.

![](bin/img_assets/YeNet.png)

