from apps.classroom_contents.models import Classwork, Resource

CLASSWORK_TYPE = [choice[0] for choice in Classwork.ClassworkChoices.choices]
RESOURCE_TYPE = [choice[0] for choice in Resource.ResourceChoices.choices]
