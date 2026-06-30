class EmployeeNotFoundError(Exception):
    pass


class ShiftNotFoundError(Exception):
    pass


class EmployeeTypeAlreadyExistsError(Exception):
    pass


class ShiftAlreadyAssignedErrorToEmployee(Exception):
    pass
