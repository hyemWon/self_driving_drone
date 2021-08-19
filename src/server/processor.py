import asyncio
from util.data import Data
# from util.drone_inference import run


class ImageProcessor:
    def __init__(self):
        # self.alphapose = AlphaPose
        self.data = Data().instance()
        self.lock = self.data.lock

    def run(self):
        # start image processing
        asyncio.run(self.start_processing())

    async def start_processing(self):
        results = await asyncio.gather(self.person_detection(),
                                       self.skeleton_detection(),
                                       self.obstacle_detection())

        print(results)
        # TODO : Processing Results and Sending results to client

    async def person_detection(self):
        pass

    async def skeleton_detection(self):
        pass

    async def obstacle_detection(self):
        pass



