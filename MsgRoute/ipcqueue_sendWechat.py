from ipcqueue import posixmq

# create msg queue
#q = posixmq.Queue('/ipcmsg')

# recv message block and no timeout
#rcvMsg = q.get()
# send wechat
#itchat.send(rcvMsg[1], 'filehelper')

# send message 
q = posixmq.Queue('/ipcmsg')
q.put([1, "Hi, I'm still here"])
q.close()
