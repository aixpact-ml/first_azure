from threading import Thread
import asyncio

import asyncio
import time


def fire_and_forget(f):
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)
    return wrapper


async def asyncify(f):
    """https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support"""
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
    return await wrapper


def asyncr(f):
    """https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support"""
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
