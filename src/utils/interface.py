from enum import IntEnum


class CentralRequestType(IntEnum):
    UPDATE_STATE = 0
    PROPAGATE = 1


class ClientRequestType(IntEnum):
    SET_DEVICE = 0
    SET_ALARM_MODE = 1
    SET_ALL = 2
