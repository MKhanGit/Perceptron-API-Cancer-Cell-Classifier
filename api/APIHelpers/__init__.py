from enum import Enum


class APIResponseStatus(Enum):
    OK = 'OK'
    NOK = 'NOK'
    ERROR = 'error'
    VALUE_ERROR = 'error_invalid_values'
    NO_ID_ERROR = 'error_no_network_id_provided'
    MISSING_ARGS = 'error_missing_arguments'
    ERROR_DUPLICATE_ENTRY = 'error_entry_already_exists'
    NO_UNCOMMITED_CHANGES = 'no_cached_changes'
    NO_RECORD = 'record_doesnt_exist'
    DEBUG_DISABLED = 'debug_endpoints_disabled'
    NOT_FOUND_404 = '404_NOT_FOUND'
