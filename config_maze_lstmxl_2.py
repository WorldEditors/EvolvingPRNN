#!/usr/bin/env python
# coding=utf8
# File: config.py
import os
import math
import random
import numpy
from envs.env_maze import  MazeTask
from envs.env_maze import gen_task
from envs.env_maze import output_to_action
from envs.env_maze import obs_to_input
from epann.utils import categorical
from models_zoo import ModelRNNBase1, ModelLSTMBase1, ModelFCBase2
from models_zoo import ModelPRNNPreMod, ModelPRNNAfterMod, ModelPRNNNoMod
from models_zoo import ModelPFCPreMod, ModelPFCAfterMod, ModelPFCNoMod
from gen_train_test_patterns import resample_maze9, resample_maze15, resample_maze21, import_mazes

root = "./results"
directory = root + "/workspace_maze15x15_lstmxl_2/"
directory_load = root + "/workspace_maze15x15_lstmxl_2/"

# Model Structure for EPRNN
#model = ModelFCBase2(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', init_scale=0.05)
model = ModelLSTMBase1(input_shape=(15,), output_shape=(5,), hidden_size=128, extra_hidden_size=64, output_activation="none", init_scale=0.05)
#model = ModelRNNBase1(input_shape=(15,), output_shape=(5,), hidden_size=32, output_activation="none", initialize_settings='R', init_scale=0.05)

#model = ModelPFCNoMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)
#model = ModelPFCPreMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)
#model = ModelPFCAfterMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)

#model = ModelPRNNNoMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)
#model = ModelPRNNPreMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)
# Hebbian-Type: 1. alpha ABCD; 2. Eligibility Traces; 3. Decomposed Plasticity; 4. Evolving & Merging
#model = ModelPRNNAfterMod(input_shape=(15,), output_shape=(5,), hidden_size=64, output_activation="none", initialize_settings='R', hebbian_type=3, init_scale=0.05)

# Refer to config_SeqPred_task.py for other configurations

#If no load_model is specified, the model is random initialized
#load_model = "./results/workspace_maze_l_decprnn_cdn/models/model.000500.dat"
#load_model = "./models/maze21_l_decprnn_cdn.dat"
load_model = directory_load + "/models/model.000500.dat"

#Address for xparl servers, do "xparl start " in your server
server = "localhost:8010"
#server = "10.216.186.16:8010"

#True Batch size = Actor_number * batch_size
actor_number = 380
batch_size = 1
task_sub_iterations = 1
inner_rollouts = [(0.0, "TRAIN", True), (0.0, "TRAIN", True), (0.16, "TEST", True),
        (0.22, "TEST", True), (0.36, "TEST", True), (0.64, "TEST", True),
        (0.8, "TEST", True), (1.0, "TEST", True)
        ]

#The task pattern are kept still for that much steps
pattern_renew = 12
pattern_retain_iterations = 1

#Select the inner-loop type, for PRNN / RNN / LSTM / EPMLP select "forward", for ES-MAML select "policy_gradient_continuous"
adapt_type = "forward"
ent_factor = 1.0e-6

evolution_pool_size = 360
evolution_topk_size = 180
# CMA-ES initial noise variance
evolution_step_size = 0.025
# CMA-ES hyper-parameter
evolution_lr = 0.02

# Model Saving Intervals
save_iter = 500
# Maximum Iterations
max_iter = 14500
# Intervals for meta-testing
test_iter = 100

#Sampled Tasks for meta-training
def train_patterns(n_step=0):
    #if(n_step < -6000):
    #    return resample_maze21(n=pattern_renew)
        #return resample_maze15(n=pattern_renew)
        #return resample_maze9(n=pattern_renew)
    #elif(n_step < -4000):
    #    return resample_maze21(n=pattern_renew + 2)
        #return resample_maze15(n=pattern_renew + 2)
        #return resample_maze9(n=pattern_renew * 4)
    #else:
    return resample_maze15(n=pattern_renew)
    #return resample_maze15(n=pattern_renew * 4)
    #return resample_maze9(n=pattern_renew * 2)

#Sampled Tasks for meta-testing
def valid_patterns(pattern_number=1024):
    return import_mazes(n=1024, file_name="./demo/tasks/1024_maze15.dat")

def game():
    return MazeTask()
