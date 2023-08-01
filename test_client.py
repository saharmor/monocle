import asyncio
from brilliant_monocle_driver import Monocle

def a_touch():
    print("A touch!")

def b_touch():
    print("B touch!")

async def execute():
    mono = Monocle()
    async with mono:
        await mono.install_touch_events()
        mono.set_a_touch_callback(a_touch)
        mono.set_b_touch_callback(b_touch)

        await asyncio.sleep(30000)

asyncio.run(execute())
