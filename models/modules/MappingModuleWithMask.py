import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, BatchNormalization, ReLU, Lambda

from ..layers import ResnetBlock


class MappingModuleWithMask(tf.keras.layers.Layer):
    def __init__(self, opts, nc, mc=64, n_blocks=3, padding_type='reflect', norm_layer=BatchNormalization, activation_layer=ReLU, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.opts = opts
        self.nc = nc
        self.mc = mc
        self.n_blocks = n_blocks
        self.padding_type = padding_type
        self.norm_layer = norm_layer
        self.activation_layer = activation_layer

    def build(self, input_shape):
        model = tf.keras.Sequential(name='model')
        tmp_nc = 64
        n_up = 4

        for i in range(n_up):
            ic = min(tmp_nc * 2**i, self.mc)
            oc = min(tmp_nc * 2**(i + 1), self.mc)
            model.add(Conv2D(filters=oc, kernel_size=3, padding='same'))
            model.add(self.norm_layer())
            model.add(self.activation_layer())

        self.before_NL = model

        for i in range(self.n_blocks):
            self.model.add(ResnetBlock(self.mc,
                                       padding_type=self.padding_type,
                                       norm_layer=self.norm_layer,
                                       activation_layer=self.activation_layer,
                                       dilation=self.opts.mapping_net_dilation))

        for i in range(n_up - 1):
            ic = min(64 * 2**(4 - i), self.mc)
            oc = min(64 * 2**(3 - i), self.mc)
            self.model.add(Conv2D(filters=oc, kernel_size=3, padding='same'))
            self.model.add(self.norm_layer())
            self.model.add(self.activation_layer())
        self.model.add(Conv2D(filters=(tmp_nc * 2), kernel_size=3, padding='same'))

        if self.opts.feat_dim > 0 and opt.feat_dim < 64:
            self.model.add(self.norm_layer())
            self.model.add(self.activation_layer())
            self.model.add(Conv2D(filters=opts.feat_dim, kernel_size=1))

    def call(self, inputs):
        return self.model(inputs)