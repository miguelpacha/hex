from hex import HexBoard

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models

class Agent:
    def vector_from_board(self, board, player, i=None, j=None):
        #return np.concatenate([board.ravel(), ([0,1] if player else [1,0])])
        new_board = np.array(board, copy=True)
        if i is not None:
            new_board[player, i, j] = 1
        #return np.moveaxis(new_board,0,-1)
        vec = board[player]-board[1-player]
        return np.expand_dims(vec,axis=-1)

    def __init__(self, x, y, opt, nn, lamda):
        self.x, self.y = x, y
        self.nn =nn
        self.opt = opt
        self.lamda = lamda
        self.weights_size = len(nn.trainable_weights)

        @tf.function
        def _get_jacobian(input_vector):
            with tf.GradientTape() as tape:
                    Y_ = nn(input_vector, training=True)[0]
            J_ = tape.jacobian(Y_, nn.trainable_weights)
            return Y_, J_
        self.get_jacobian = _get_jacobian

    def train_one_game(self):
        Y, J = {}, {}
        game = HexBoard(x, y)
        t, player = 0, 0
        losses = []

        while game.winner is None:
            # Calculate Y[t] and the gradient wrt the weights
            input_vector = np.expand_dims(self.vector_from_board(game.board, player), axis = 0)
            
            Y[t], J[t] = self.get_jacobian(input_vector)

            # Choose next move and calculate Y[t+1]
            plays = list(game.generate_legal_moves())
            batch = np.stack([self.vector_from_board(game.board, 1-player, i=i, j=j) for (i,j) in plays], axis=0)
            predictions = self.nn(batch, training=True)
            best = np.argmax( predictions[:,player] - predictions[:,1-player])
            Y[t+1] = predictions[best]
            game.play(player, *plays[best])

            # -- Update weights --
            if game.winner is None:
                loss = (Y[t+1]-Y[t]).numpy()
            else:
                z = np.array([1-game.winner, game.winner])
                loss = (z-Y[t]).numpy()
            losses.append(loss)
            jacobian = [0 for _ in range(self.weights_size)]
            for i in range(self.weights_size):
                for k in range(t+1):
                    discount = self.lamda**(t-k)
                    jacobian[i] += discount*np.moveaxis(J[k][i].numpy(),0,-2)
                    #jacobian[i] += discount*J[k][i].numpy()
            gradients = [-loss.dot(j) for j in jacobian]

            opt.apply_gradients(zip(gradients, nn.trainable_weights))

            player = 1 - player
            t += 1
        return np.stack(losses), game.winner, t
    
    def play(self, game, player):
        plays = list(game.generate_legal_moves())
        batch = np.stack([self.vector_from_board(game.board, 1-player) for play in plays], axis=0)
        predictions = self.nn(batch, training=True)
        best = np.argmax( predictions[:,player] - predictions[:,1-player])
        game.play(player, *plays[best])

class Random_AI:
    def play(self, game, player):
        plays = list(game.generate_legal_moves())
        r = np.random.randint(len(plays))
        game.play(player, *plays[r])


x, y = 9, 9
nn = models.Sequential()
nn.add(layers.Conv2D(8, 3, activation='relu', input_shape=(x,y,1)))
nn.add(layers.MaxPool2D())
nn.add(layers.Conv2D(4, 3, activation='relu'))
nn.add(layers.Flatten())
nn.add(layers.Dense(2,activation="sigmoid",))
opt = keras.optimizers.SGD(learning_rate=5e-4)
lamda = .4

AI1 = Agent(x, y, opt, nn, lamda)
AI2 = Agent(x, y, opt, nn, lamda)
Random = Random_AI()


import matplotlib.pyplot as plt

avg_loss = []
plys = []
N = 10000
for _ in range(N):
    losses, winner, ply = AI2.train_one_game()
    avg_loss.append(np.abs(losses).mean())
    plys.append(ply)
    if _ % 10 == 0:
        print(_, avg_loss[-1], plys[-1])
plt.figure()
plt.plot(avg_loss)
plt.savefig("loss")
plt.figure()
plt.plot(plys)
plt.savefig("result")
nn.save("nn")
quit()
