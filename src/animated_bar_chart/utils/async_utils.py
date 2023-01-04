import asyncio

import aiohttp


# Ensure that a list of awaitables are started at a specific rate in requests per minute.
async def rate_limit(awaitables, rpm):
	wait_period = 60 / rpm
	tasks = []
	results = []

	for awaitable in awaitables:
		task = asyncio.ensure_future(awaitable)
		tasks.append(task)

		await asyncio.sleep(wait_period)

	for task in tasks:
		results.append(await task)

	return results

async def json_request(url):
	headers = {"Accept": "application/json"}

	async with aiohttp.ClientSession(headers=headers) as sess:
		async with sess.get(url) as res:
			return await res.json()