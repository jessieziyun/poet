import json
import os
import numpy as np
import tensorflow as tf

from poetry_generator import model
from poetry_generator import sample
from poetry_generator import encoder

class Generator:
    def generate_poetry(self, temp):
        model_name='poet'
        seed=None
        nsamples=1
        batch_size=1
        length=50
        temperature=temp
        top_k=40
        top_p=1

        self.response = ""

        cur_path = os.path.dirname(__file__) + "/models" + "/" + model_name
        enc = encoder.get_encoder(model_name)
        hparams = model.default_hparams()
        with open(cur_path + '/hparams.json') as f:
            hparams.override_from_dict(json.load(f))

        if length > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        with tf.Session(graph=tf.Graph()) as sess:
            np.random.seed(seed)
            tf.set_random_seed(seed)

            output = sample.sample_sequence(
                hparams=hparams, length=length,
                start_token=enc.encoder['<|endoftext|>'],
                batch_size=batch_size,
                temperature=temperature, top_k=top_k, top_p=top_p
            )[:, 1:]

            saver = tf.train.Saver()
            ckpt = tf.train.latest_checkpoint(cur_path)
            saver.restore(sess, ckpt)

            generated = 0
            while nsamples == 0 or generated < nsamples:
                out = sess.run(output)
                for i in range(batch_size):
                    generated += batch_size
                    text = enc.decode(out[i])
                    # print(text)
                    self.response = text

        return self.response

poet = Generator()