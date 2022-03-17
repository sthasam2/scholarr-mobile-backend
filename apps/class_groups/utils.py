from apps.class_groups.models import ClassGroup
from apps.core.exceptions import NoneExistenceError, UrlParameterError

#########################
#       Model Methods
#########################


def get_url_id_classgroup_or_raise(id=None):
    """Get class groups"""

    if id:

        try:
            return ClassGroup.objects.get(id=id)

        except (TypeError, ValueError, OverflowError, ClassGroup.DoesNotExist):
            raise NoneExistenceError(
                cause="ClassGroup",
                status_code=400,
                message="Non existence",
                verbose=f"ClassGroup(id={id}) does not exist!",
            )

    else:
        raise UrlParameterError(
            cause="ClassGroup id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )
