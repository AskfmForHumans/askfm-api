from __future__ import annotations

from typing import Type

import askfm_api


class AskfmApiError(Exception):
    """Base class for all errors in askfm_api."""

    def __init__(self, response: askfm_api.Response) -> None:
        code = response["error"]
        super().__init__(code)
        self.response = response
        self.code = code

    @staticmethod
    def from_response(response: askfm_api.Response) -> AskfmApiError:
        code = response["error"]
        cls = ERROR_CODE_MAP.get(code, UnknownError)
        return cls(response)


class UnknownError(AskfmApiError):
    """Error for which we don't know it's category."""


class TryAgainError(AskfmApiError):
    """The server asks us to retry."""


class RequestError(AskfmApiError):
    """Incorrect API usage, network problems, banned IP, and so on."""


class OperationError(AskfmApiError):
    """Error performing the requested operation."""


class SessionError(RequestError):
    """Error that should go away after refreshing the session token."""


# I tried my best at guessing the meanings of these codes, but didn't check it.
ERROR_CODE_MAP: dict[str, Type[AskfmApiError]] = {
    "account_banned": OperationError,  # account_banned
    "account_disabled": OperationError,  # account_disabled
    "already_exist": OperationError,  # pinned_answer_already_added
    "already_taken": OperationError,  # already_taken
    "argument_missing": RequestError,  # argument_missing
    "bad_email": OperationError,  # wrong_email_format
    "bad_login": OperationError,  # username_invalid_chars
    "cancelled": AskfmApiError,  # action_cancelled
    "existing_login": OperationError,  # username_taken
    "file_size_error": OperationError,  # file_size_error
    "file_upload_error": RequestError,  # file_upload_error
    "generic_error": AskfmApiError,  # generic_error
    "hashtag_already_exists": OperationError,  # interest_already_exists
    "hashtag_too_long": OperationError,  # interest_too_long
    "illegal_action": RequestError,  # illegal_action
    "incorrect_password": OperationError,  # incorrect_password
    "invalid_access_token": SessionError,  # invalid_access_token
    "invalid_auth": SessionError,  # invalid_auth
    "invalid_data": RequestError,  # invalid_data
    "invalid_email": OperationError,  # wrong_email_format
    "invalid_login": OperationError,  # username_invalid_chars
    "invalid_name": OperationError,  # invalid_name
    "invalid_password": OperationError,  # incorrect_password
    "invalid_request_token": SessionError,  # invalid_request_token
    "invalid_signature": RequestError,  # invalid_signature
    "invalid_user_credentials": OperationError,  # invalid_user_credentials
    "ip_banned": RequestError,  # ip_banned
    "limit_exceeded": OperationError,  # pinned_answers_limit_exceeded
    "network_error": RequestError,  # network_error
    "not_allowed": RequestError,  # not_allowed
    "session_expired": SessionError,  # session_expired
    "session_invalid": SessionError,  # session_invalid
    "social_error": OperationError,  # generic_social
    "something_went_wrong": AskfmApiError,  # something_went_wrong
    "spam_login": OperationError,  # username_forbidden
    "too_many_hashtags": OperationError,  # too_many_interests
    "try_again": TryAgainError,  # try_again
    "unable_to_follow": OperationError,  # unable_to_follow
    "user_not_found": OperationError,  # user_not_found
    "weak_password": OperationError,  # weak_password
    "wrong_format": OperationError,  # wrong_format
    "wrong_hashtag_format": OperationError,  # invalid_interest
}
