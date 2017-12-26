#!/usr/bin/env python
import socket, sys
import thread
import re
import time
import xml.etree.ElementTree as ET
import select

max_conn = 30
buffer_size = 4096
listening_port = int(sys.argv[3])
fake_ip = sys.argv[4]
DEBUG = False
alp= float(sys.argv[2])

def start():
  try:
    print("start")
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #initiate socket
    soc.bind(("", listening_port))
    soc.listen(max_conn)
    print("Server Started Successfully")
  except Exception, e:
    print "Unable to initialize Socket"
    sys.exit(2)

  while True:
    try:
      conn, address = soc.accept() #the connection from client
      print conn
      print 'Receive data from: ' + address[0]
      thread.start_new_thread(server,(conn,address)) #thread to handle requests
    except KeyboardInterrupt:
      soc.close()
      print "Proxy Server Down"
      sys.exit(1)

  s.close()

s_final = ""

def server(conn,address):
  
  global T_cur
  global s_final
  data = conn.recv(buffer_size) # the data from browser
  t_start = time.time()
  print t_start
  print "t_start"
  bitrate = 0
  try:     
    httpsoc = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #creat a socket to connect to the server
    httpsoc.connect((sys.argv[5],8080))
    
    # change from bunny.f4m to bunny_nolist.f4m
    if 'big_buck_bunny.f4m' in data:
     pre = re.compile('big_buck_bunny.f4m')
     data = pre.sub('big_buck_bunny_nolist.f4m',data)
     print data
     print "data"
   
    # modify the HTTP request's Request_URI
    if 'Seg' in data:
     if T_cur >= 1500:
       bitrate = 1000
       if 'vod/1000' in data:
         #re.sub(r'vod/1000','vod/1000',str(data))
         #pre = re.compile('vod/1000')
         #data = pre.sub('',data)
         pass
       elif 'vod/10' in data:
         pre = re.compile('vod/10')
         data = pre.sub('vod/1000',data)       
       elif 'vod/100' in data:
         pre = re.compile('vod/100')
         data = pre.sub('vod/1000',data)       
         #re.sub(r'vod/100','vod/1000',str(data))
       elif 'vod/500' in data:
         pre = re.compile('vod/500')
         data = pre.sub('vod/1000',data)      
         #re.sub(r'vod/500','vod/1000',str(data))
     elif T_cur >= 750 and T_cur < 1500:
       bitrate = 500
       if 'vod/1000' in data:
         pre = re.compile('vod/1000')
         data = pre.sub('vod/500',data)     
         #re.sub(r'vod/1000','vod/500',str(data))
       elif 'vod/10' in data:
         #re.sub(r'vod/10','vod/500',str(data))
         pre = re.compile('vod/10')
         data = pre.sub('vod/500',data)  
       elif 'vod/100' in data:
         #re.sub(r'vod/100','vod/500',str(data))
         pre = re.compile('vod/100')
         data = pre.sub('vod/500',data)
       elif 'vod/500' in data:
         #pre = re.compile('vod/500')
         #data = pre.sub('vod/500',data)   
         pass
         #re.sub(r'vod/500','vod/500',str(data))
     elif T_cur >= 150 and T_cur < 750:
       bitrate = 100
       if 'vod/1000' in data:
         pre = re.compile('vod/1000')
         data = pre.sub('vod/100',data)  
         #re.sub(r'vod/1000','vod/100',str(data))
       elif 'vod/10' in data:
         pre = re.compile('vod/10')
         data = pre.sub('vod/100',data) 
         #re.sub(r'vod/10','vod/100',str(data))
       elif 'vod/100' in data:
         #pre = re.compile('vod/100')
         #data = pre.sub('vod/100',data)
         pass
         #re.sub(r'vod/100','vod/100',str(data))
       elif 'vod/500' in data:
         pre = re.compile('vod/500')
         data = pre.sub('vod/100',data)
         #re.sub(r'vod/500','vod/100',str(data))
     else:
       bitrate = 10
       if 'vod/1000' in data:
         pre = re.compile('vod/1000')
         data = pre.sub('vod/10',data)
         #re.sub(r'vod/1000','vod/10',str(data))
       elif 'vod/10' in data:
         #pre = re.compile('vod/10')
         #data = pre.sub('vod/10',data)
         #re.sub(r'vod/10','vod/10',str(data))
         pass
       elif 'vod/100' in data:
         pre = re.compile('vod/100')
         data = pre.sub('vod/10',data)
         #re.sub(r'vod/100','vod/10',str(data))
       elif 'vod/500' in data:
         pre = re.compile('vod/500')
         data = pre.sub('vod/10',data)
         #re.sub(r'vod/500','vod/10',str(data))

    table = data.split(" ")
    '''
    ll = [httpsoc]
    read, write, exceptional = select.select(ll, [], [], 20)
    if len(read)==0:
      print "non available socket"
      pass
    print "ok we  gor one"
    scc = read[0]
    '''
    httpsoc.sendall(data) # send requet to webserver
    length = -2
    body = -1

    while True:
      ll = [httpsoc]
      read, write, exceptional = select.select(ll, [], [], 20)
      if len(read)==0:
        print "non available socket"
        continue
      print "ok we  gor one"
      scc = read[0]
      http_data = scc.recv(buffer_size) #receive from web server => 200 OK
      print "t_start:" + str(t_start)

      if (body>0):
          
        conn.send(http_data) # send video and needed information to browser
        body += len (http_data)
       
      if length==body:                # receive the completed chunk break for receiving next chunk 
        break     
      
      #take Content-Length
      if 'Content-Length' in http_data:
       #print "3333"
       temp = re.compile(r'Content-Length: (\d*)')
       length = int (temp.findall(http_data)[0])
       body = len(http_data.split('\r\n\r\n')[-1])
       conn.send(http_data)
      
      print "length is :" + str(length)
      print "body is :" + str(body)
      print "t_start:" + str(t_start)

    t_end = time.time ()
    print "t_start:" + str(t_start)
    print "t_end:" + str(t_end)

    t_new = (t_end - t_start) 
    print t_new
    T_new = (length*8)/(1000*(t_new)) #Kbps
    print T_new
    if(T_cur<0): #Current T-put through EWMA
     T_cur = (alp*T_new) + ((1-alp)*10)
    else:
     T_cur = (alp*T_new) + ((1-alp)*T_cur)

    print "T_cur is  : "+str(T_cur)
    httpsoc.close()
    conn.close()
    
    #Logging
    ss = str(t_start) + " " + str(t_new) +" " + str(T_new)+" "+str(T_cur) + " " + str(bitrate)+" "+str(sys.argv[5])+" "+table[1]+ "\n"  
    s_final+=ss 
    f = open(sys.argv[1],'w+')
    f.write(s_final)
    f.close()
  
  except socket.error, (value, message):
    if httpsoc:
      httpsoc.close()
    if conn:
      conn.close()
    print "Runtime Error:", message
    sys.exit(1)
      
if __name__ == '__main__':
  
  T_cur = -1
  start()  
