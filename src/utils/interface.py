from enum import IntEnum


class CentralRequestType(IntEnum):
    UPDATE_STATE = 0


class ClientRequestType(IntEnum):
    SET_DEVICE = 0
    SET_ALARM_MODE = 1
