# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 13:03:21 2017

@author: frans
"""

#!/usr/bin/env python

import asyncio
import websockets
import json
import signal
import html

from Indexer import Indexer
from AuthorMatcher import AuthorMatcher

# Close on Ctrl+c under windows
signal.signal(signal.SIGINT, signal.SIG_DFL)

index = Indexer()
matcher = AuthorMatcher(index.ix)

async def retrieve_result(websocket, path):
    print("Received connection")
    user_msg = await websocket.recv()
    
    if user_msg.startswith("query:"):
        user_query = user_msg[len("query:"):]

        print("Received message: {}".format(user_query))
        await websocket.send(json.dumps({
            'type': 'state',
            'msg': 'Returning search results for \'{}\'...'.format(user_query),
        }))
    
        results = matcher.query(user_query)
        print("Result: {}".format(results))
        for n, result in enumerate(results):
            print(str(result))
            await websocket.send(json.dumps({
                'type': 'result',
                'title': 'Search result #{}'.format(n),
                'content': html.escape(str(result)),
            }))
        
        await websocket.send(json.dumps({
            'type': 'state',
            'msg': 'All results returned',
        }))

start_server = websockets.serve(retrieve_result, 'localhost', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()