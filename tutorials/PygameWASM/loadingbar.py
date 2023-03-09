import asyncio
import sys

import pygame

screen = pygame.display.set_mode([1024, 600], pygame.SRCALPHA, 32)
screen.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
screen.fill((0, 0, 0, 0))
if web := sys.platform in ("emscripten", "wasi"):
    from platform import window


async def main():
    global ctx, web
    rng = 10  # resolution of progress bar
    slot = (1024 - 200) / rng
    for i in range(rng):
        marginx = 100
        marginy = 200
        pygame.draw.rect(
            screen, (10, 10, 10), (marginx - 10, marginy - 10, (rng * slot) + 20, 110)
        )
        pygame.draw.rect(screen, (0, 255, 0), (marginx, marginy, (1 + i) * slot, 90))
        pygame.display.update()
        if web:
            window.chromakey(None, *screen.get_colorkey(), 30)
        await asyncio.sleep(1)


asyncio.run(main())
