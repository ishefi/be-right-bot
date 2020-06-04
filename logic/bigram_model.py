import json
import random
from collections import defaultdict
from typing import TYPE_CHECKING
from base.logger import logger

try:
    from nltk.tokenize import word_tokenize
    word_tokenize('hello')  # verify we can tokenize
except:
    logger.exception("COULD NOT IMPORT WORD TOKENIZE. SPLITTING.")
    word_tokenize = str.split

from logic.model_store import ModelStore

if TYPE_CHECKING:
    from typing import List


class BigramModel(object):
    DEFAULT_TRESH = 7

    def __init__(self, thresh=None):
        self._thresh = thresh
        self.model = []
        self.corpus = []
        self._model_uid = None

    @property
    def thresh(self):
        return self._thresh or self.DEFAULT_TRESH

    @property
    def model_uid(self):
        return self._model_uid

    def set_model_uid(self, value):
        self._model_uid = value

    def init_model(self, model_uid):
        store = ModelStore(model_uid)
        self.set_model_uid(model_uid)
        self.model = store.get_model()
        self.corpus = store.get_corpus()
        self._thresh = self.DEFAULT_TRESH

    def save_model(self):
        if not self.model_uid:
            raise RuntimeError('Need uid for model!')
        store = ModelStore(self.model_uid)
        store.save_model(json.dumps(self.model))
        store.save_corpus(json.dumps(self.corpus))

    def train_string(self, s):
        s = 'END {} END'.format(s)
        s = s.replace('\n', ' END ')
        unigrams = word_tokenize(s)
        bigrams = defaultdict(list)
        for i in range(len(unigrams) - 1):
            bigrams[unigrams[i].lower()].append(unigrams[i + 1])
        self.model = bigrams
        self.corpus = self._clean_corpus(unigrams)
        if self._thresh is None:
            self._thresh = self._calculate_thresh(unigrams)

    def _clean_corpus(self, dirty_corpus):
        return list(filter(lambda x: x not in ['END', '.', '!', '?'], dirty_corpus))

    def _calculate_thresh(self, dirty_corpus):
        return len(dirty_corpus) / dirty_corpus.count('END')

    def order_seeds(self, seeds):
        # type: (List[str]) -> List[str]
        """ Orders word list from the least common to the most common.

        Args:
            seeds: List of words to order.

        Returns:
            Same list of words but ordered.

        Example:
            >>> self.order_seeds(['ziff', 'ziff', 'bang', 'nag'])
            ['bang', 'nag', 'ziff', 'ziff']

        """
        known_seeds = list(filter(lambda w: w in self.corpus, seeds))
        return sorted(known_seeds, key=lambda w: self.corpus.count(w))

    def generate(self, seedstr=''):
        """generates an length-long string using `self.model`"""
        seedlist = self.order_seeds(word_tokenize(seedstr))
        if seedlist:
            new_word = seedlist.pop(0)
        else:
            new_word = random.choice(self.corpus)
        text = []
        while True:
            text.append(new_word)
            if new_word not in self.model:
                if len(text) < self.thresh:
                    return self.generate(' '.join(seedlist))
                else:
                    return self._stringify(text)
            new_word = self._choose_word(new_word)
            if new_word == 'END':
                return self._stringify(text)

    def _choose_word(self, cur_word):
        new_word = random.choice(self.model[cur_word])
        if new_word == 'END' and not self._should_stop():
            return self._choose_word(cur_word)
        return new_word

    def _should_stop(self):
        return random.randint(1, self.thresh) == 1

    def _stringify(self, str_list):
        string = ''
        for i, w in enumerate(str_list):
            if i != 0 and len(w) > 1:
                w = ' ' + w
            string += w
        return string


