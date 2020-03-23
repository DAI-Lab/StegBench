import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import collections

from art.attacks import FastGradientMethod, ElasticNet, BasicIterativeMethod, ProjectedGradientDescent, SaliencyMapMethod
from art.classifiers import PyTorchClassifier
from art.utils import load_mnist

from os.path import join, abspath

import stegtest.utils.lookup as lookup
import stegtest.db.processor as processor
import stegtest.db.images as images
import stegtest.utils.filesystem as fs

import torch

def get_attack_method(attack_method):
	return {
		lookup.attack_FGM: FastGradientMethod,
		lookup.attack_EAD: ElasticNet,
		lookup.attack_BIM: BasicIterativeMethod,
		lookup.attack_PGD: ProjectedGradientDescent,
		lookup.attack_JSMA: SaliencyMapMethod,
	}[attack_method]

def get_criterion_options():
	return {
		'cross_entropy': 'cross_entropy'
	}

def get_optimizer_options():
	return {
		'SGD': 'SGD',
		'Adam': 'Adam',
	}

def get_model_arguments():
	arguments = collections.OrderedDict({})
	arguments[lookup.input_shape] = list([int])
	arguments[lookup.criterion] = get_criterion_options()
	arguments[lookup.optimizer] = get_optimizer_options()
	arguments[lookup.nb_classes] = int

	return arguments

def apply_attack(model_path, dataset, model_attack_config):
	model = torch.load(model_path, map_location='cpu').model

	input_shape = model_attack_config[lookup.input_shape]
	criterion = model_attack_config[lookup.criterion]
	optimizer = model_attack_config[lookup.optimizer]
	nb_classes = model_attack_config[lookup.nb_classes]
	attack_method = model_attack_config[lookup.attack_method]

	if criterion == 'cross_entropy':
		criterion = nn.CrossEntropyLoss()
	else:
		raise ValueError

	if optimizer == 'SGD':
		optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
	elif optimizer == 'Adam':
		optimizer = optim.Adam(model.parameters(), lr=1e-4)
	else:
		raise ValueError

	#TODO, might need to do something special to get the actual model, like we did for StegDetect
	classifier = PyTorchClassifier(model=model, input_shape=input_shape, loss=criterion, optimizer=optimizer, nb_classes=nb_classes)

	x = np.array([x_element.numpy()[0] for x_element in dataset[0]])
	y = np.array(dataset[1])

	print(x.shape)

	# x = np.reshape(x, (-1, *input_shape))
	x_train = x.astype(np.float32)

	predictions = classifier.predict(x_train)
	accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y, axis=1)) / len (y)
	print('Accuracy on benign test examples: {}%'.format(accuracy * 100))

	attack_function = get_attack_method(attack_method)
	attack_instance = attack_function(classifier=classifier)
	x_adv = attack_instance.generate(x=x)

	# Step 7: Evaluate the ART classifier on adversarial test examples

	predictions = classifier.predict(x_adv)
	accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y, axis=1)) / len(y)
	print('Accuracy on adversarial test examples: {}%'.format(accuracy * 100))

	path_to_directory = join(abspath(lookup.get_db_dirs()[lookup.dataset]), fs.get_uuid())
	fs.make_dir(path_to_directory)

	processor.convert_to_image(path_to_directory, x_adv)

	print(path_to_directory)

	return path_to_directory