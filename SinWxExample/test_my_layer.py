import numpy as np
import tensorflow as tf
import random
from tensorflow.python.framework import ops
import matplotlib
import os
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# get current working directory
cwd = os.getcwd()
print(cwd)

# load .so for our custom op
_sinwx_module = tf.load_op_library(os.path.join(cwd,'sin_wx.so') )
sin_wx = _sinwx_module.sin_wx

# register the gradient for the custom op
@ops.RegisterGradient("SinWx")
def _sin_wx_grad(op, grad):
	grad_x, grad_w = _sinwx_module.sin_wx_grad(op.inputs[0], op.inputs[1], grad)
	print (grad_x)
	return [grad_x, grad_w]

DIMENSION = 2
LENGTH = 100

# create samples
gt_weight = np.random.random((1, DIMENSION))
data = np.random.random((LENGTH, DIMENSION))
gt = np.sin(np.dot(data, np.transpose(gt_weight)))

# define the network
gt_input = tf.placeholder(tf.float32, shape = [DIMENSION])
gt_output = tf.placeholder(tf.float32, shape = [1])
with tf.variable_scope('weight'):
	initializer = tf.truncated_normal_initializer(0.0, stddev = 0.01)
	weight = tf.get_variable(
		name = 'weight',
		shape = [DIMENSION],
		initializer = initializer)

# use custom op in the graph
output = sin_wx(gt_input, weight)
loss = tf.reduce_mean(tf.square(output - gt_output))
opt = tf.train.GradientDescentOptimizer(learning_rate = 0.01).minimize(loss)


loss_curve = []

# optimize
max_step = 1000
with tf.Session() as session:
	session.run(tf.global_variables_initializer())
	print ('weight iteration:')
	for step in range(max_step):
		_, training_loss = session.run([opt, loss], feed_dict = {
			gt_input: data[step % len(data)],
			gt_output: gt[step % len(data)]
			})
		loss_curve.append(training_loss)

	print (weight.eval())
	print (gt_weight)

# store loss plot on disk
plt.figure()
plt.plot(loss_curve)
plt.savefig('loss.png')
