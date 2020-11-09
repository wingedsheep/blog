import shutil
import uuid
import tensorflow as tf

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.regularizers import l2
import tensorflow.keras.backend as K


class ModelManager:

    @staticmethod
    def masked_huber_loss(mask_value, clip_delta):
        def f(y_true, y_pred):
            error = y_true - y_pred
            cond = K.abs(error) < clip_delta
            mask_true = K.cast(K.not_equal(y_true, mask_value), K.floatx())
            masked_squared_error = 0.5 * K.square(mask_true * (y_true - y_pred))
            linear_loss = mask_true * (clip_delta * K.abs(error) - 0.5 * (clip_delta ** 2))
            huber_loss = tf.where(cond, masked_squared_error, linear_loss)
            return K.sum(huber_loss) / K.sum(mask_true)

        f.__name__ = 'masked_huber_loss'
        return f

    @staticmethod
    def create_model(inputs, outputs, learning_rate, regularization_factor):
        model = Sequential([
            Dense(256, input_shape=(inputs, ), activation="relu", kernel_regularizer=l2(regularization_factor)),
            Dense(128, activation="relu", kernel_regularizer=l2(regularization_factor)),
            Dense(128, activation="relu", kernel_regularizer=l2(regularization_factor)),
            Dense(outputs, activation='linear', kernel_regularizer=l2(regularization_factor))
        ])

        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(optimizer=optimizer, loss=ModelManager.masked_huber_loss(0.0, 1.0))

        return model

    @staticmethod
    def copy_model(model):
        backup_file = 'backup_' + str(uuid.uuid4())
        model.save(backup_file)
        new_model = load_model(backup_file,
                               custom_objects={'masked_huber_loss': ModelManager.masked_huber_loss(0.0, 1.0)})
        shutil.rmtree(backup_file)
        return new_model
