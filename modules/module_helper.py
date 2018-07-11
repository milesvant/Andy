class ModuleHelper:

    def __init__(self):
        """A base class for each of the submodule helpers which turn commands
            into translated lables.

        Attributes:
            positive_words: a list of words which are affirmative responses to
                questions
            negative_words: a list of words which are negative responses to
                questions
            number_dict: a dictionary from string words to their corresponding
                ints
        """
        self.positive_words = ["yes", "sure", "ok"]
        self.negative_words = ["no", "nope"]
        self.number_dict = self.init_number_dict()

    def init_number_dict(self):
        """Creates a dictionary from strings of numbers to the corresponding
            ints."""
        d = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
        }

        inverse_d = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
            7: 'seven',
            8: 'eight',
            9: 'nine',
        }

        for i in range(1, 10):
            d["twenty" + " " + inverse_d[i]] = 20 + i
        for i in range(1, 10):
            d["thirty" + " " + inverse_d[i]] = 30 + i
        for i in range(1, 10):
            d["fourty" + " " + inverse_d[i]] = 40 + i
        return d
