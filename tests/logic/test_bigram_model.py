from mocks import *
from logic.bigram_model import BigramModel


class TestBigramModel(BotTestCase):
    module_prefix = 'logic.bigram_model.'

    def setUp(self):
        self.m_ModelStore = self.patch_module('ModelStore')
        self.m_model_store = self.m_ModelStore.return_value
        self.testee = BigramModel()

    def test_set_model_uid(self):
        # given
        self.testee._model_uid = 'something'
        self.assertEqual(self.testee.model_uid, 'something')

        # when
        self.testee.set_model_uid('aNotherThing')

        # then
        self.assertEqual(self.testee.model_uid, 'aNotherThing')

    def test_init_model(self):
        # given
        uid = self.unique('YouAyeDee')

        # when
        self.testee.init_model(uid)

        #then
        self.m_ModelStore.assert_called_once_with(uid)
        self.assertEqual(self.testee.model_uid, uid)
        self.assertEqual(self.testee.model, self.m_model_store.get_model.return_value)
        self.assertEqual(self.testee.corpus, self.m_model_store.get_corpus.return_value)
        self.assertEqual(self.testee.thresh, self.testee.DEFAULT_TRESH)

    def test_train_string(self):
        # given
        corpus = 'hello once !\nhello again ?\nhello again'

        # when
        self.testee.train_string(corpus)

        # then
        self.assertCountEqual(self.testee.corpus, ['hello', 'once', 'hello', 'again', 'hello', 'again'])
        self.assertCountEqual(self.testee.model['hello'], ['once', 'again', 'again'])
        self.assertCountEqual(self.testee.model['once'], ['!'])
        self.assertCountEqual(self.testee.model['again'], ['END', '?'])
        self.assertCountEqual(self.testee.model['?'], ['END'])
        self.assertCountEqual(self.testee.model['!'], ['END'])
        self.assertCountEqual(self.testee.model['end'], ['hello', 'hello', 'hello'])
        self.assertEqual(self.testee.thresh, 3)

    def test_dont_change_predefined_thresh(self):
        # given
        self.testee._thresh = 42

        # when
        self.testee.train_string('given when\n then')

        # then
        self.assertEqual(self.testee.thresh, 42)

    def test_order_seeds(self):
        # given
        self.testee.corpus = ['ziff', 'bla', 'lab', 'ziff']

        # when
        ordered = self.testee.order_seeds(['ziff', 'lab', 'bla', 'lab',])

        # then
        self.assertEqual(ordered, ['lab', 'bla', 'lab', 'ziff'])

    def test_generate__no_seed(self):
        # given
        self.testee.corpus = ['ziff']
        self.testee.model = {'ziff': ['bang'], 'bang': ['biff'], 'biff': ['END']}

        # when
        sentence = self.testee.generate()

        # then
        self.assertEqual(sentence, 'ziff bang biff')

    def test_generate__yes_seed(self):
        # given
        self.set_frequency_order(['ziff', 'bang'])
        self.testee.model = {'ziff': ['bang'], 'bang': ['biff'],
                             'biff': ['END']}

        # when
        sentence = self.testee.generate('ziff')

        # then
        self.assertEqual(sentence, 'ziff bang biff')

    def test_generate_again_if_too_short(self):
        # given
        self.set_frequency_order(['bang', 'ziff'])
        self.testee.model = {'ziff': ['bang'], 'bang': ['biff'],
                             'biff': ['else']}
        self.testee._thresh = 4

        # when
        sentence = self.testee.generate('bang ziff')

        # then
        self.assertEqual(sentence, 'ziff bang biff else')

    def test_seed_not_in_corpus(self):
        # given
        self.testee.corpus = ['ziff']
        self.testee.model = {'ziff': ['bang'], 'bang': ['biff'], 'biff': ['END']}

        # when
        sentence = self.testee.generate('NI')

        # then
        self.assertEqual(sentence, 'ziff bang biff')

    def test_try_again_sometimes(self):
        # given
        m_random = self.patch_module('random')
        m_random.choice.side_effect = ['ziff', 'bang', 'END'] * 2
        m_random.randint.side_effect = [2, 1]
        self.testee.model = {'ziff': ['bang'], 'bang': ['END']}

        # when
        sentence = self.testee.generate()

        # then
        self.assertEqual(sentence, 'ziff bang ziff bang')
        self.assertEqual(m_random.choice.call_count, 6)  # ziff, bang, END * 2
        self.assertEqual(m_random.randint.call_count, 2)
        m_random.randint.assert_called_with(1, self.testee.thresh)

    def test_save_model(self):
        # given
        uid = self.unique('YouEyeDee')
        self.testee._model_uid = uid

        # when
        self.testee.save_model()

        # then
        self.m_ModelStore.assert_called_once_with(self.testee.model_uid)
        self.m_model_store.save_model.assert_called_once_with(json.dumps(self.testee.model))
        self.m_model_store.save_corpus.assert_called_once_with(json.dumps(self.testee.corpus))

    def test__no_uid_no_model(self):
        # given
        self.testee._model_uid = None

        # when, then
        with self.assertRaises(RuntimeError):
            self.testee.save_model()

    def set_frequency_order(self, seq):
        self.testee.corpus = []
        for i, word in enumerate(seq, start=1):
            self.testee.corpus += [word] * i









