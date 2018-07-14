class ModuleHelper:
    """A base class for each of the submodule helpers which turn commands
        into translated lables.

    Attributes:
        positive_words: a list of words which are affirmative responses to
            questions
        negative_words: a list of words which are negative responses to
            questions
        number_dict: a dictionary from string words to their corresponding
            ints
        int_to_weekday: a dictionary from ints to the corresponding string
            of the day of the week (where Monday is 0 and Sunday is 6)
        weekeday_to_int: a dictionary from string names of the days of the
            week to their corresponding index in the week
            (i.e. 0 -> monday)
    """

    def __init__(self):
        self.positive_words = ["yes", "sure", "ok", "correct", "yep"]
        self.negative_words = ["no", "nope"]
        self.number_dict = self.init_number_dict()
        self.int_to_weekday = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        self.weekday_to_int = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

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
