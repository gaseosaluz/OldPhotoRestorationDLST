# Tensorflow v2+Keras implementation of 'Old Photo Restoration via Deep Latent Space Translation', CVPR 2020 paper
This is an Tensorflow v2+Keras inference ONLY implemention of [a CVPR 2020 paper](https://arxiv.org/abs/2004.09484) that restores old photos that suffer from degradations like faded colors, scratches and color spots by jointly the learning from the latent spaces of paired artificial degraded images with real degraded photos.

Official PyTorch implementation can be found at: https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life .

# Results
TODO

# To improve
The output images might have a gradient of grey border which I think might have been caused by accumulation of floating point differences from the implementation of Tensorflow and PyTorch's Instance Normalization layer.

# Requirements
The following software versions were used for testing the code in this repo. Other version combination of software might also work but have not been tested on.
* Python 3.7
* PyTorch 1.8 (for weights conversion)
* Tensorflow 2.4.1
* CUDA 11.1
* Pip 21.0.1
* Microsoft Visual Studio 2019 (if using .sln file)
* Other required python libraries are in 'requirements.txt'

# Getting started
Download all PyTorch and dlib weights from official repo (see top). Convert PyTorch weights to Tensorflow format weights using:

`python convert_weights_for_tf.py --input_weights netG_A <Path to VAE_A weights folder>/latest_net_G.pth netG_B <Path to VAE_B weights folder>/latest_net_G.pth mapping_net <Path to mapping net weights folder>/latest_net_mapping_net.pth --stage 1 --output_weights ./weights/Photo_Enhancement/tf_keras/out.weights`

Then you can run inference using:

`python main.py --input_folder <Folder with images> --checkpoint .\weights\Photo_Enhancement\tf_keras\out.weights --gpu_id 0`

# License
>Any part of this source code should ONLY be reused for research purposes. This repo contains some modified source code from other sources who have been credited in source file where they are used.


# References
>Wan, Ziyu and Zhang, Bo and Chen, Dongdong and Zhang, Pan and Chen, Dong and Liao, Jing and Wen, Fang, 2020. Bringing Old Photos Back to Life. In proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (pp. 2747-2757)