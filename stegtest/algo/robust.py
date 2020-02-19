import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

from art.attacks import FastGradientMethod, ElasticNet, BasicIterativeMethod, ProjectedGradientDescent, SaliencyMapMethod
from art.classifiers import PyTorchClassifier
from art.utils import load_mnist

import stegtest.utils.lookup as lookup
import stegtest.db.processor as processor

import torch

def load_data_for_attack(db_uuid, ttv_split=None):
	if ttv_split:
		raise NotImplementedError

	raise NotImplementedError

def get_attack_method(attack_method):
	return {
		lookup.attack_FGM: FastGradientMethod,
		lookup.attack_EAD: ElasticNet,
		lookup.attack_BIM: BasicIterativeMethod,
		lookup.attack_PGD: ProjectedGradientDescent,
		lookup.attack_JSMA: SaliencyMapMethod,
	}[attack_method]

def apply_attack(model_path, attack_method, configurations, dataset):
	raise NotImplementedError

	input_shape = configurations[lookup.input_shape]
	criterion = configurations[lookup.criterion]
	optimizer = configurations[lookup.optimizer]
	nb_classes = configurations[lookup.nb_classes]

	#dependent on the model type, need to properly load it
	#for now we only support PyTorch
	model = torch.load(model_path)

	#TODO, might need to do something special to get the actual model, like we did for StegDetect
	classifier = PyTorchClassifier(model=model, input_shape=input_shape, loss=criterion, optimizer=optimizer, nb_classes=nb_classes)

	x = dataset[0]
	y = dataset[1]

	predictions = classifier.predict(x)
	accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y, axis=1)) / len (y)


	attack_function = get_attack_method(attack_method)
	attack_configuration = configurations[lookup.attack_configuration]
	attack_instance = attack_function(classifier=classifier, *attack_configuration)

	x_adv = attack.generate(x=x)

	# Step 7: Evaluate the ART classifier on adversarial test examples

	predictions = classifier.predict(x_adv)
	accuracy = np.sum(np.argmax(predictions, axis=1) == np.argmax(y, axis=1)) / len(y)
	print('Accuracy on adversarial test examples: {}%'.format(accuracy * 100))