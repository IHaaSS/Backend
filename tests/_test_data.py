from backend.storage import ethereum as eth
import os
os.chdir('..')


test_incident='tests/data/incident.json'
incident1 = 'QmfZHCWcVB53ePuZjR4agvMtrn5Zo4WX3nH9ixDtEzhQmS'
incident2 = 'QmYuLA4kf18DTxYCt7VgsU5R4hu9Zvm79yjDyy4mffargJ'
comment1 = 'QmTi6118Xjx6RxXgWwP2CotcUEzUd8FY4VKH3mnvURa89B'
comment2 = 'QmaUkBZ6D6WfPn2AJqpPtk6gKQc2MfJoHVR6oeakk6sXQg'
attachment = 'QmVVwTBhbaU2qrWLxM538Ap4fXjwpvqfS6dpoqCVhdRXEn'
incident1b = eth.ipfs2bytes(incident1)
incident2b = eth.ipfs2bytes(incident2)
comment1b = eth.ipfs2bytes(comment1)
comment2b = eth.ipfs2bytes(comment2)
attachb = eth.ipfs2bytes(attachment)
test_file='images/dataInstruction.png'
