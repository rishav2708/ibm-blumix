from flask import session
from flask.ext.socketio import emit, join_room, leave_room
from .. import socketio
import requests
import json
import pymongo
from pymongo import MongoClient
client= MongoClient('localhost',27017)
db=client["IBM"]
url="http://192.168.1.30:9200/"
@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    u=url+room+"/_search"
    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    coll=db[room]
    chat=coll.find()
    for c in chat:
        emit('message',{'msg':c['name']+": "+c['message']})
    '''
    try:
        resp=requests.get(u).json()['hits']['hits']
        for i in resp:
    	   print i['_source']['message']
           emit('message',{'msg':i['_source']['message']})
    except:
        emit('message',{'msg':"no data yet"},room=room)
    '''
@socketio.on('text', namespace='/chat')
def left(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message', {'msg': session.get('name') + ':' + message['msg']}, room=room)
    u=url+room+'/data/'
    coll=db[room]
    d={"name":session.get('name'),"message":message['msg']}
    try:
        coll.insert(d)
    except:
        print ""
    #print requests.post(u,data=json.dumps(d))

@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

