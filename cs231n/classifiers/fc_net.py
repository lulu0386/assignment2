from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - dropout: Scalar between 0 and 1 giving dropout strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian with standard deviation equal to   #
        # weight_scale, and biases should be initialized to zero. All weights and  #
        # biases should be stored in the dictionary self.params, with first layer  #
        # weights and biases using the keys 'W1' and 'b1' and second layer weights #
        # and biases using the keys 'W2' and 'b2'.                                 #
        ############################################################################
        weights1 = np.random.normal(weight_scale, weight_scale, (input_dim, hidden_dim))
        weights2 = np.random.normal(weight_scale, weight_scale, (hidden_dim, num_classes)) 
        bias1 = np.zeros(hidden_dim)
        bias2 = np.zeros(num_classes)
        self.params = {'W1' : weights1, 'W2' : weights2, 'b1' : bias1, 'b2' : bias2}
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        scores1, cache1 = affine_relu_forward(X, self.params['W1'], self.params['b1'])
        scores, cache = affine_forward(scores1, self.params['W2'], self.params['b2'])
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dout = softmax_loss(scores, y)
        dout2, dw2, db2 = affine_backward(dout,cache)
        dout1, dw1, db1 = affine_relu_backward(dout2, cache1)
        reg = self.reg
        grads = {'W2' : dw2 + reg * self.params['W2'] , 'b2' : db2 , 'W1' : dw1 + reg * self.params['W1'] , 'b1' : db1 } 
        loss += 0.5 * reg * np.sum(self.params['W2'] * self.params['W2']) + 0.5 * reg * np.sum(self.params['W1'] * self.params['W1'])
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0, use_batchnorm=False, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
          the network should not use dropout at all.
        - use_batchnorm: Whether or not the network should use batch normalization.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.use_batchnorm = use_batchnorm
        self.use_dropout = dropout > 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}
        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution with standard deviation equal to  #
        # weight_scale and biases should be initialized to zero.                   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to one and shift      #
        # parameters should be initialized to zero.                                #
        ############################################################################

        if self.num_layers == 1 :
                weights = np.random.normal(0, weight_scale, (input_dim, num_classes)) 
                bias = np.zeros(num_classes)
                self.params["W1"] = weights
                self.params["b1"] = bias
                
        else :
            for i in range(1, self.num_layers + 1) :
                key1 = 'W' + str(i)
                key2 = 'b' + str(i)
                key3 = 'gamma' + str(i)
                key4 = 'beta' + str(i)
                if i == 1 :
                    weights = np.random.normal(0, weight_scale, (input_dim, hidden_dims[i - 1])) 
                    bias = np.zeros(hidden_dims[i - 1])
                elif i == self.num_layers:
                    weights = np.random.normal(0, weight_scale, (hidden_dims[i - 2], num_classes)) 
                    bias = np.zeros(num_classes)
                else :
                    weights = np.random.normal(0, weight_scale, (hidden_dims[i - 2], hidden_dims[i - 1])) 
                    bias = np.zeros(hidden_dims[i - 1])
                self.params[key1] = weights
                self.params[key2] = bias
                if self.use_batchnorm == True and i != self.num_layers :
                    self.params[key3] = np.ones((1,1))
                    self.params[key4] = np.zeros((1,1))

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.use_batchnorm:
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.use_batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode

        scores = None
        cache = {}
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        key1 = 'W'
        key2 = 'b'
        key3 = 'gamma'
        key4 = 'beta'
        for i in range(1, self.num_layers + 1) :
            curkey1 = key1 + str(i)
            curkey2 = key2 + str(i)
            curkey3 = key3 + str(i)
            curkey4 = key4 + str(i)
            if i == 1:
                if i == self.num_layers:
                        scores, cache[i] = affine_forward(X, self.params[curkey1], self.params[curkey2])  
                        #print ("no relu")
                else :  
                        if self.use_batchnorm == False :
                            scores, cache[i] = affine_relu_forward(X, self.params[curkey1], self.params[curkey2])
                        else :
                             scores, cache[i] = affine_batch_relu_forward(X, self.params[curkey1],          self.params[curkey2], self.params[curkey3], self.params[curkey4], self.bn_params[i - 1]) 
                             
                        #print ("relu")
                '''print (curkey1)
                print (curkey2)
                print (len(cache[i]))'''
            elif i == self.num_layers :    
                scores, cache[i] = affine_forward(scores, self.params[curkey1], self.params[curkey2])
                #print (self.params[curkey1].shape)
                #print (self.params[curkey2].shape)
                #print (
                '''print ("no relu")
                print (curkey1)
                print (curkey2)
                print (len(cache[i]))'''
            else :
                if self.use_batchnorm == False :
                    scores, cache[i] = affine_relu_forward(scores, self.params[curkey1], self.params[curkey2])
                else :
                    scores, cache[i] = affine_batch_relu_forward(scores, self.params[curkey1],         self.params[curkey2], self.params[curkey3], self.params[curkey4], self.bn_params[i - 1]) 
                '''print ("relu")
                print (curkey1)
                print (curkey2)
                print (len(cache[i]))'''
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        
        key1 = 'W'
        key2 = 'b'
        key3 = 'gamma'
        key4 = 'beta'
        dw = None
        dout = None
        db = None
        dgamma = None
        dbeta = None
        loss, dout = softmax_loss(scores, y)
        for i in range(1, self.num_layers + 1) :
            curi = self.num_layers + 1 - i
            curkey1 = key1 + str(curi)
            curkey2 = key2 + str(curi)
            if curi == self.num_layers :
                   dout, dw, db = affine_backward(dout,cache[curi]) 
            else :
                   if self.use_batchnorm == False :
                           dout, dw, db = affine_relu_backward(dout, cache[curi])
                   else :
                           dout, dw, db, dgamma, dbeta = affine_batch_relu_backward(dout, cache[curi])
                           grads[key3 + str(curi)] = np.sum(dgamma, axis = 0)
                           grads[key4 + str(curi)] = np.sum(dbeta, axis = 0)
            grads[curkey1] = dw + self.reg * self.params[curkey1]
            grads[curkey2] = db 
            loss += 0.5 * self.reg * np.sum(self.params[curkey1] * self.params[curkey1])
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
