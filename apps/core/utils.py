from random import choice
from string import ascii_lowercase

#########################
# String methods
#########################


class CodeGenerator:
    """"""

    def random_string(self) -> str:
        """
        generates random string
        """
        return "".join(choice(ascii_lowercase) for i in range(5))

    def generate_classgroup_code(self):
        """generate unique string code"""

        return f"{self.random_string()}-{self.random_string()}"

    def generate_classroom_code(self):
        """generate unique string code"""

        return f"{self.random_string()}-{self.random_string()}-{self.random_string()}"

    def check_token_code_uniqueness(self, token: str) -> bool:
        """check if given token is unique or not by matching with database"""

        return True

        pass  # TODO Implement
