"""Loading of the vendored Maia (Leela Chess Zero) Keras model.

The saved network relies on two custom LCZero layers, so it must be loaded
with matching ``custom_objects``. See ``third_party/maia`` for attribution.
"""

import tensorflow as tf

import maia.tf2.lc0_az_policy_map as lc0_az_policy_map


class ApplySqueezeExcitation(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(ApplySqueezeExcitation, self).__init__(**kwargs)

    def build(self, input_shape):
        self.reshape_size = input_shape[1][1]

    def call(self, inputs):
        x = inputs[0]
        excited = inputs[1]
        gammas, betas = tf.split(
            tf.reshape(excited, [-1, self.reshape_size, 1, 1]), 2, axis=1
        )
        return tf.nn.sigmoid(gammas) * x + betas


class ApplyPolicyMap(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(ApplyPolicyMap, self).__init__(**kwargs)
        self.fc1 = tf.constant(lc0_az_policy_map.make_map())

    def call(self, inputs):
        h_conv_pol_flat = tf.reshape(inputs, [-1, 80 * 8 * 8])
        return tf.matmul(h_conv_pol_flat, tf.cast(self.fc1, h_conv_pol_flat.dtype))


def load_model(path):
    return tf.keras.models.load_model(
        path,
        custom_objects={
            "ApplySqueezeExcitation": ApplySqueezeExcitation,
            "ApplyPolicyMap": ApplyPolicyMap,
        },
    )
