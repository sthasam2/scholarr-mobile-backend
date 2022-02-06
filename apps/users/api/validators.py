from ..utils import check_email_existence, check_username_existence


def check_email_username_valid(email: str, username: str) -> bool:
    """
    checks whether email and/or username already exists
    """
    email_exists = check_email_existence(email)
    username_exists = check_username_existence(username)
    if not email_exists and not username_exists:
        return False
    else:
        return True


# class RequestValidater:

#     def validate_req_data(req_body, required_fields, *args, **kwargs):
#         """
#         """

#         for key, value in req_body
