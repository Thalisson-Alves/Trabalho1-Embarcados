import traceback

def try_log(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(f'Failed on {f.__name__}. {e}')
            traceback.print_exc()
    inner.__annotations__ = f.__annotations__
    return inner
