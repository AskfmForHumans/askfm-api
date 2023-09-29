# askfm-api

[![PyPI version](https://img.shields.io/pypi/v/askfm-api.svg)](https://pypi.org/project/askfm-api)
[![PyPI status](https://img.shields.io/pypi/status/askfm-api.svg)](https://pypi.org/project/askfm-api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

> **WARNING!**  
> This library is outdated and doesn't support much of ASKfm's new functionality.  
> It is based on reverse-engineering ASKfm Android app v4.67.1 (API version 1.18) from the year **2020**.

This aims to be a powerful Python wrapper around the undocumented ASKfm API for its mobile apps.

The core logic is quite complete, but only a small subset of API methods have helpers in the `askfm_api.requests` module so far.


## Feature highlights

- iterators for paginated requests
- full error hierarchy based on semantics
- automatic session refreshing

## Usage

The code should be self-explanatory so I won't go into great detail here. A quick example:

```python
from askfm_api import AskfmApi, AskfmApiError
from askfm_api import requests as r

try:
    api = AskfmApi("<signing key>")
    me = api.log_in("<username>", "<password>")
    print(me)
    # {'uid': 'jgrdlgrd', 'fullName': 'Снег не растает', 'location': 'my empire of dirt', ...}

    qs = api.request_iter(r.fetch_questions())
    print(next(qs))
    # {'type': 'daily', 'body': 'Hi?', 'answer': None, 'author': None, 'qid': 153352, ...}

    res = api.request(
        r.post_answer(question_type="daily", question_id=153352, text="Hi there!")
    )
    print(res)
    # {'question': {...}, 'answer': {...}}
except AskfmApiError as e:
    print(e)
    # error code returned by the API, e. g. 'session_expired'
```

### Signing key

All requests are signed using a secret key (unique per app version) that is stored inside the official app in an obfuscated manner.
I don't find it ethical to publish it, so if you want to use this library, your options are:
- extract the key by yourself
  - *hint 1:* use APK version 4.67.1
  - *hint 2:* if you found `"YKhyxNvWDwMhHxPpmHMZecqsXCKzS"` — that's not the key, but you are on the right path :)
- contact [me](https://github.com/snowwm), explain your use case and ask for the key

## Todo

- feat: Add more method helpers
- tests: Add tests

## Related work / See also

- a similar library (currently outdated): https://github.com/Hexalyse/pyAskFm  
- blog post with a more in-depth explanation of reverse-engineering ASKfm API: https://hexaly.se/2017/06/14/how-i-reverse-engineered-the-ask-fm-api-part-1/

## Contributing

Any activity is welcome, but I would be especially grateful if someone wrote tests for this code.
