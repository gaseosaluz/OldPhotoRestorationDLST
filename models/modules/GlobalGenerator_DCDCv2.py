import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, BatchNormalization, ReLU, Lambda
from tensorflow.keras.activations import tanh

from ..layers import *


class GlobalGenerator_DCDCv2(tf.keras.layers.Layer):

    def _build_encoder(self):
        encoder = tf.keras.Sequential(\
        [
            ReflectionPadding2D(padding=3),
            Conv2D(filters=min(self.ngf, self.opts.mc), kernel_size=7, padding=(0, 0)),
            self.norm_layer(),
            self.activation_layer()
        ])

        for i in range(self.opts.start_r):
            mult = 2**i

            encoder.add(Conv2D(filters=min(self.ngf * mult * 2, self.opts.mc),
                               kernel_size=self.k_size,
                               strides=2,
                               padding=(1, 1)))
            encoder.add(self.norm_layer())
            encoder.add(self.activation_layer())

        for i in range(self.opts.start_r, self.n_downsampling - 1):
            mult = 2**i

            encoder.add(Conv2D(filters=min(self.ngf * mult * 2, self.opts.mc),
                               kernel_size=self.k_size,
                               strides=2,
                               padding=(1, 1)))
            encoder.add(self.norm_layer())
            encoder.add(self.activation_layer())
            encoder.add(ResnetBlock(min(self.ngf * mult * 2, self.opts.mc),
                                    padding_type=self.padding_type,
                                    norm_layer=self.norm_layer,
                                    activation_layer=self.activation_layer))
            encoder.add(ResnetBlock(min(self.ngf * mult * 2, self.opts.mc),
                                    padding_type=self.padding_type,
                                    norm_layer=self.norm_layer,
                                    activation_layer=self.activation_layer))

        mult = 2**(self.n_downsampling - 1)

        if self.opts.spatio_size == 32:
            encoder.add(Conv2D(filters=min(self.ngf * mult * 2, self.opts.mc), kernel_size=self.k_size, strides=2, padding=(1, 1)))
            encoder.add(self.norm_layer())
            encoder.add(self.activation_layer())
        elif self.opts.spatio_size == 64:
            encoder.add(ResnetBlock(min(self.ngf * mult * 2, self.opts.mc),
                                    padding_type=self.padding_type,
                                    norm_layer=self.norm_layer,
                                    activation_layer=self.activation_layer))

        encoder.add(ResnetBlock(min(self.ngf * mult * 2, self.opts.mc),
                                padding_type=self.padding_type,
                                norm_layer=self.norm_layer,
                                activation_layer=self.activation_layer))

        if self.opts.feat_dim > 0:
            encoder.add(Conv2D(min(self.ngf * mult * 2, self.opts.mc), kernel_size=1, strides=1))

        return encoder

    def _build_decoder(self):
        decoder = tf.keras.Sequential()

        if self.opts.feat_dim > 0:
            decoder.add(Conv2D(min(self.ngf * mult * 2, self.opts.mc), kernel_size=1, strides=1))

        o_pad = 0 if self.k_size == 4 else 1
        mult = 2**self.n_downsampling

        decoder.add(ResnetBlock(min(self.ngf * mult, self.opts.mc), padding_type=self.padding_type, norm_layer=self.norm_layer, activation_layer=self.activation_layer))

        if self.opts.spatio_size == 32:
            decoder.add(Conv2DTranspose(filters=min((self.ngf * mult) // 2, self.opts.mc), kernel_size=self.k_size, strides=2, padding=(1, 1), output_padding=o_pad))
            decoder.add(self.norm_layer())
            decoder.add(self.activation_layer())
        elif self.opts.spatio_size == 64:
            decoder.add(ResnetBlock(min(self.ngf * mult, self.opts.mc), padding_type=self.padding_type, norm_layer=self.norm_layer, activation_layer=self.activation_layer))

        for i in range(1, self.n_downsampling - self.opts.start_r):
            mult = 2**(self.n_downsampling - i)

            decoder.add(ResnetBlock(min(self.ngf * mult, self.opts.mc), padding_type=self.padding_type, norm_layer=self.norm_layer, activation_layer=self.activation_layer))
            decoder.add(ResnetBlock(min(self.ngf * mult, self.opts.mc), padding_type=self.padding_type, norm_layer=self.norm_layer, activation_layer=self.activation_layer))
            decoder.add(Conv2DTranspose(min((self.ngf * mult) // 2, self.opts.mc), kernel_size=self.k_size, strides=2, padding=(1, 1), output_padding=o_pad))
            decoder.add(self.norm_layer())
            decoder.add(self.activation_layer())

        for i in range(self.n_downsampling - self.opts.start_r, self.n_downsampling):
            mult = 2**(self.n_downsampling - i)

            decoder.add(Conv2DTranspose(filters=(self.ngf * mult) // 2, kernel_size=self.k_size, strides=2, padding=(1, 1), output_padding=o_pad))
            decoder.add(self.norm_layer())
            decoder.add(self.activation_layer())

        decoder.add(ReflectionPadding2D(padding=3))
        decoder.add(Conv2D(filters=self.output_nc, kernel_size=7, padding=(0, 0)))

        if not self.opts.use_segmentation_model:
            decoder.add(Lambda(lambda x: tanh(x)))

        return decoder


    def __init__(self, opts, input_nc, output_nc, ngf=64, k_size=3, n_downsampling=8, padding_type='reflect',
                 norm_layer=BatchNormalization, activation_layer=ReLU):
        super().__init__()

        self.opts = opts
        self.input_nc = input_nc
        self.output_nc = output_nc
        self.ngf = ngf
        self.k_size = k_size
        self.n_downsampling = n_downsampling
        self.padding_type = padding_type
        self.norm_layer = norm_layer
        self.activation_layer = activation_layer

    def build(self, input_shape):
        self.encoder = self._build_encoder()
        self.decoder = self._build_decoder()

    def get_config(self):
        pass

    def call(self, inputs):
        x, flow = inputs
        flow = flow.lower()

        if flow == 'enc':
            return self.encoder(x)
        elif flow == 'dec':
            return self.decoder(x)
        elif flow == 'enc_dec':
            return self.decoder(self.encoder(x))
        else:
            raise NotImplementedError("Unsupported flow specified!")