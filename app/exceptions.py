from fastapi import HTTPException


class MyAllExceptions(Exception):
    detail = "Общая ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class InvalidDateRangeError(MyAllExceptions):
    detail = "Дата начала не может быть позже даты конца."


class TypeIdNotFoundError(MyAllExceptions):
    detail = "Указанный type_id не найден."


class ObjectNotFoundException(MyAllExceptions):
    detail = "Объект не найден"


class DataBaseIntegrityException(MyAllExceptions):
    detail = "Ошибка добавления/удаления/изменения"


class ObjectAlreadyExistException(MyAllExceptions):
    detail = "Объект уже существует"


class MyHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, *args, **kwargs):
        super().__init__(
            status_code=self.status_code, detail=self.detail, *args, **kwargs
        )


class DBIntegrityHTTPException(MyHTTPException):
    status_code = 409
    detail = "Нужно сначала удалить взаимосвязанные данные"


class ObjectNotFoundHTTPException(MyHTTPException):
    status_code = 404
    detail = "Объект не найден"
