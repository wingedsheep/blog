from tensorflow.keras.models import load_model

from skipbo.skipbo_env import SkipboEnv
from skipbo.trained_dqn_agent import TrainedDqnAgent

emily_model = load_model("models/Emily/56000.h5", custom_objects={'masked_huber_loss': None})
james_model = load_model("models/James/56000.h5", custom_objects={'masked_huber_loss': None})

emily = TrainedDqnAgent("Emily", emily_model)
james = TrainedDqnAgent("James", james_model)

environment = SkipboEnv()
for i in range(10000):
    environment.play([emily, james], {"episode": i})
