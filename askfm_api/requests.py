import functools

import askfm_api

# Note: typechecking this mess seems impossible.
# See https://github.com/python/mypy/issues/3157#issue-221120895, section "Messing with the return type".


def make_req(method, path, **req_kwargs):
    def decorator(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            params = func(*args, **kwargs)
            return askfm_api.Request(method, path, params, name=name, **req_kwargs)

        return wrapper

    return decorator


# === My profile ===


@make_req(
    "GET",
    "/notifications",
    unwrap_key="notifications_ext",
    paginated=True,
    item_id_key="entityId",
)
def fetch_notifs(filter=""):
    return {"type": filter}


@make_req(
    "PUT",
    "/notifications/mark_read",
)
def mark_notifs_as_read(filter=""):
    return {"type": filter}


@make_req("POST", "/users/hashtags", unwrap_key="hashtag")
def add_hashtag(hashtag):
    return {"hashtag": hashtag}


@make_req("DELETE", "/users/hashtags")
def delete_hashtag(hashtag):
    return {"hashtag": hashtag}


# === My questions ===


@make_req(
    "GET", "/my/questions", unwrap_key="questions", paginated=True, item_id_key="qid"
)
def fetch_questions(*, skip_shoutouts=False):
    return {"skip_shoutouts": skip_shoutouts}


@make_req("DELETE", "/my/questions")
def delete_question(question_type, question_id):
    return {
        "qid": question_id,
        "type": question_type,
    }


@make_req("POST", "/my/questions/answer")
def post_answer(question_type, question_id, text):
    return {
        "qid": question_id,
        "type": question_type,
        "answer": {
            "type": "text",
            "body": text,
        },
    }


# === Users ===


@make_req(
    "GET",
    "/users/hashtags/search",
    unwrap_key="users",
    paginated=True,
    item_id_key="uid",
)
def search_users_by_hashtag(*hashtags):
    return {"hashtags": ",".join(hashtags)}


@make_req("GET", "/users/details", unwrap_key="user")
def fetch_profile(uname):
    return {"uid": uname}


@make_req("POST", "/users/questions")
def send_question(users, text, anon=False):
    return {
        "users": users,
        "question": {
            "type": "anonymous" if anon else "user",
            "body": text,
        },
    }


# === Util ===


@make_req("GET", "/token", unwrap_key="accessToken")
def fetch_access_token(device_id):
    return {"did": device_id}


@make_req("POST", "/authorize")
def login(uname, passwd, device_id):
    return {
        "uid": uname,
        "pass": passwd,
        "did": device_id,
        "guid": device_id,
    }
