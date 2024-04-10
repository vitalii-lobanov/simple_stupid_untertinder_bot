import asyncio

async def async_sleep_demo(delay):
    print(f"Task started, will sleep for {delay} seconds.")
    await asyncio.sleep(delay)
    print(f"Task completed after sleep for {delay} seconds.")

# This is the asynchronous main function that will run the async_sleep_demo coroutine.
async def main():
    # Run the async_sleep_demo coroutine with a delay of 5 seconds
    #await async_sleep_demo(36000)

    await asyncio.gather(
    async_sleep_demo(5),
    async_sleep_demo(3),
    async_sleep_demo(1),
)

# To run the main coroutine and effectively start the program, you need to use asyncio.run():
# asyncio.run() is the main entry point for asynchronous programs in Python 3.7+
asyncio.run(main())