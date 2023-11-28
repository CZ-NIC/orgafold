from inspect import get_annotations
from inquirer import Checkbox, List, prompt


def _get_bool_params(o, params: tuple | list[tuple] | None = None):
    default = None
    if params is None:
        # get_annotations(o.__class__).items() if issubclass(type_, bool)]
        par = [attr for attr, type_ in vars(o).items() if isinstance(type_, bool)]
        choices = [(attr, attr) for attr in par]
        default = [attr for attr in par if getattr(o, attr)]
    elif len(params):
        if (isinstance(params[0], tuple)):
            par = [attr for _, attr in params]
            choices = params
            default = [attr for _, attr in params if getattr(o, attr)]
        else:
            par = params
            choices = [(attr, attr) for attr in params]
            default = [attr for attr in params if getattr(o, attr)]
    return par, choices, default


def checkboxes(o: object, params: tuple | list[tuple] | None = None, title="Choose"):
    """Change the bool attributes of object.

    :param o: Object whose parameters will get updated
    :param params: Choose these params only. Otherwise all bool annotated class attributes will be inquired.
        Either: tuple of param names, or list of tuples (label, param name).
    :return: The object or False if the user wants to leave.
    """
    params, choices, default = _get_bool_params(o, params)
    question = Checkbox(
        'internal',
        message=title,
        choices=choices,
        default=default
    )
    try:
        answers = prompt([question])["internal"]
    except:
        return False
    else:
        [setattr(o, p, p in answers) for p in params]
        return o


def radio(o: object, params: tuple | list[tuple] | None = None, title="Pick"):
    """Set one of the bool attributes of an object to True, other to False.

    :param o: Object whose parameters will get updated
    :param params: Choose these params only. Otherwise all bool typed instance vars will be inquired.
        Either: tuple of param names, or list of tuples (label, param name).
    :return: The object or False if the user wants to leave.
    """
    params, choices, _ = _get_bool_params(o, params)
    try:
        action = prompt([List('internal',
                              message=title,
                              choices=choices,
                              ),
                         ])["internal"]
    except:
        return False
    else:
        [setattr(o, p, False) for p in params]
        setattr(o, action, True)
        return o
