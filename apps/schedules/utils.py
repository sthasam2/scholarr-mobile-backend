from apps.core.exceptions import NoneExistenceError, UrlParameterError
from apps.schedules.models import Schedule


def get_url_id_schedule_or_raise(id=None):
    if id:
        try:
            return Schedule.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, Schedule.DoesNotExist):
            raise NoneExistenceError(
                cause="Schedule",
                status_code=400,
                message="Non existence",
                verbose=f"Schedule(id={id}) does not exist!",
            )
    else:
        raise UrlParameterError(
            cause="schedule_id in URL",
            status_code=400,
            message="URL parameter wrong",
            verbose="[id] must be provided!",
        )
