from django.test import TestCase

from .utils import calculate_sensitivity_index


# Create your tests here.
class SensitivityAnalysisTest(TestCase):
    """ """

    test_string = "Today is a very nice day"
    test_string2 = "I dont really like how this is going."

    def test_get_sensitivity_index(self):
        test1 = calculate_sensitivity_index(self.test_string)
        test2 = calculate_sensitivity_index(self.test_string2)
        self.assertGreaterEqual(test1, 0.5, "Positive test pass")
        self.assertLessEqual(test2, 0.5, "Negative test pass")
