"""
Useful Tools for the project
"""
import numpy
import pickle
import sys
import os
import time
import parl
from copy import deepcopy
import random as rand
import scipy
import numpy.random as random

def categorical(p):
    res = numpy.asarray(p)
    return (res.cumsum(-1) >= numpy.random.uniform(size=res.shape[:-1])[..., None]).argmax(-1)

def make_dir(model_directory):
    if(not os.path.exists(model_directory)):
        os.makedirs(model_directory)

def discretize(val, benchmarks):
    ret = numpy.zeros_like(benchmarks)
    if(val > benchmarks[-1]):
        ret[-1] = 1.0
        return ret
    idx = 0
    while val > benchmarks[idx] and idx < len(benchmarks):
        idx += 1
    if(idx <= 0):
        ret[0] = 1.0
        return ret
    ret[idx] = (val - benchmarks[idx - 1]) / (benchmarks[idx] - benchmarks[idx - 1])
    ret[idx - 1] = 1.0 - ret[idx]
    return ret

def group_discretize(val_dic, benchmarks):
    ret = dict()
    for key in val_dic:
        ret[key] = discretize(val_dic[key], benchmarks)
    return ret

def partition(data_list,begin,end):
    partition_key = data_list[end]
    index = begin 
    for i in range(begin,end):
        if data_list[i] < partition_key: 
            data_list[i],data_list[index] = data_list[index],data_list[i] 
            index+=1
    data_list[index],data_list[end] = data_list[end],data_list[index] 
    return index

def remove_meta_change(params):
    for key in params:
        if(key.find("meta") >= 0):
            params[key] *= 0.0

def step_func(val, thresholds, values):
    assert len(values) > len(thresholds)
    i = 0
    while i < len(thresholds) and val > thresholds[i]:
        i += 1
    return values[i]

def add_params(p_1, p_2):
    res = dict()
    for key in p_1.keys():
        if(key in p_2):
            res[key] = p_1[key] + p_2[key]
        else:
            res[key] = numpy.copy(p_1[key])
    return res

def diff_params(p_1, p_2):
    res = dict()
    for key in p_1.keys():
        if(key in p_2):
            res[key] = p_1[key] - p_2[key]
        else:
            res[key] = numpy.copy(p_1[key])
    return res

def multiply_params(p, factor):
    res = dict()
    for key in p:
        res[key] = factor * p[key]
    return res

def sum_params(grads):
    res = dict()
    for grad in grads:
        for key in grad:
            if key not in res:
                res[key] = numpy.copy(grad[key])
            else:
                res[key] += grad[key]
    return res

def mean_params(grads):
    alpha = 1.0 / len(grads)
    res = sum_params(grads)
    for key in res:
        res[key] *= alpha
    return res

def noise_like(parameters, noise_factor):
    noise = dict()
    for key in parameters:
        if(key in noise_factor):
            noise[key] = noise_factor[key] * numpy.random.normal(size=numpy.shape(parameters[key]), loc=0.0, scale=1.0) 
    return noise

def param_norm(parameters):
    size = 0.0
    norm = 0.0
    for key in parameters:
        if(len(numpy.shape(parameters[key])) > 0):
            size += numpy.product(parameters[key].shape)
        else:
            size += 1
        norm += numpy.sum(parameters[key] * parameters[key])
    return numpy.sqrt(norm/size)

def param_norm_2(parameters):
    norm = 0.0
    if(isinstance(parameters, dict)):
        for key in parameters:
            norm += numpy.mean(parameters[key] * parameters[key])
        norm /= len(parameters)
    else:
        norm = numpy.mean(parameters * parameters)
    return numpy.sqrt(norm)

def param_max(parameters):
    size = 0.0
    norm = 0.0
    if(isinstance(parameters, dict)):
        for key in parameters:
            norm = max(numpy.max(numpy.abs(parameters[key])), norm)
    else:
        norm = numpy.max(numpy.abs(parameters))
    return norm

def check_validity(parameters):
    for key in parameters:
        if(numpy.sum(numpy.isnan(parameters[key])) > 0 or numpy.sum(numpy.isinf(parameters[key])) > 0):
            return False
    return True

def entropy(distribution):
    entropy = - numpy.sum(numpy.log(numpy.maximum(distribution, 1.0e-6)) * distribution)
    if(numpy.isnan(entropy) or numpy.isinf(entropy)):
        raise Exception("There is nan in entropy calculation: %s"%distribution)
    return entropy

def reset_weights_axis(weights, neural_structure):
    i = 0
    for connect_type,number,_,_,_ in neural_structure:
        i += 1
        if(connect_type == "recursive"):
            weights["W_%d"%i][range(number), range(number)] = 0.0

# Moving Average on Axis 0
def moving_average(tensor, window):
    gamma = 0.90
    conv = [gamma**(window - i) for i in range(window)]
    conv = conv + [1.0] + list(reversed(conv))
    conv = numpy.array(conv)
    conv *= 1.0/numpy.sum(conv)
    l = 2 * window + 1
    pad_b = numpy.expand_dims(tensor[0], axis=0)#numpy.sum(conv[-l:] * tensor[:l], axis=0)
    pad_e = numpy.expand_dims(tensor[-1], axis=0)#numpy.sum(conv[:l] * tensor[-l:], axis=0)
    pad_b = numpy.repeat(pad_b, window, axis=0)
    pad_e = numpy.repeat(pad_e, window, axis=0)
    n_tensor = numpy.concatenate([pad_b, tensor, pad_e], axis=0)
    #ema = numpy.convolve(n_tensor, conv, mode="valid")
    ema = scipy.ndimage.uniform_filter1d(tensor, size=l, axis=0, mode='constant')
    return ema
    
