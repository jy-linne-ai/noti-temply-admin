"""예외 클래스 모듈"""


class LayoutNotFoundError(Exception):
    """레이아웃 관련 예외 클래스"""

    pass


class LayoutAlreadyExistsError(Exception):
    """레이아웃 관련 예외 클래스"""

    pass


class PartialNotFoundError(Exception):
    """부분 레이아웃 관련 예외 클래스"""

    pass


class PartialAlreadyExistsError(Exception):
    """부분 레이아웃 관련 예외 클래스"""

    pass


class TemplateNotFoundError(Exception):
    """템플릿 관련 예외 클래스"""

    pass


class TemplateAlreadyExistsError(Exception):
    """템플릿 관련 예외 클래스"""

    pass
