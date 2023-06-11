# import asyncio
#
#
# async def asynchronous_function():
#     print("Starting asynchronous function")
#     print("Doing some work...")
#     await asyncio.sleep(3)  # Simulate a time-consuming operation asynchronously
#     print("Asynchronous function completed")
#
#
# async def main():
#     print("Before calling asynchronous_function")
#     await asynchronous_function()
#     print("After calling asynchronous_function")
#
#
# asyncio.run(main())
import redis

r = redis.Redis(host='127.0.0.1', port=6379)
r.ping()