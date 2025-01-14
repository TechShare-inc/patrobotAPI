# -*- coding: utf-8 -*-

#2.7系で動作するように古臭い記法を含む

import websockets
import json
import time
from threading import Thread

MSGTYPE_INITIAL_CONNECTION = "INITIAL_CONNECTION"
PROCESS_HEADER = "process"

MSGTYPE_COMMAND = "COMMAND"
MSGTYPE_RESPONSE = "RESPONSE"

COMMAND_CHARGING_START = "CHARGING_START"
COMMAND_INSERT = "INSERT"
COMMAND_CHARGING_FINISHED = "CHARGING_FINISHED"
COMMAND_PLUG_OUT = "PLUG_OUT"

INSERT_COMMAND_PARAM_KEY_SUCCESS = "success"

####### BaseMessage #######
class BaseMessage:
  def __init__(self, sender = "", duration = 120, msgtype=""):
    self.sender = sender
    self.duration = duration
    self.msgtype = msgtype

  def create_message(self):
    data = {"sender": self.sender, 
            "duration": self.duration, 
            "msgtype": self.msgtype}
    message_str = json.dumps({"message": data})
    return message_str


######### PROCESS MESSAGE ###############
class ProcessMessage(BaseMessage, object):
  def __init__(self, sender = "", msg_type="", duration =0, systemctl = ""):
    super(ProcessMessage, self).__init__(sender, duration, msg_type)
    self.systemctl = systemctl 

  def create_message(self):
    data = {"sender": self.sender, 
            "duration": self.duration, 
            "msgtype": self.msgtype, 
            "systemctl": self.systemctl}
    message_str = json.dumps({"process": data})
    return message_str
  
######### PICTURE MESSAGE ###############
class PictureMessage(BaseMessage, object):
  def __init__(self, sender = "", msg_type="", duration =0, type_ = "", date=None):
    super(PictureMessage, self).__init__(sender, duration, msg_type)
    self.type = type_ 
    self.date = date
  def create_message(self):
    if self.date is None:
      data = {"sender": self.sender, 
              "duration": self.duration, 
              "msgtype": self.msgtype, 
              "type": self.type}
    else:
      data = {"sender": self.sender, 
              "duration": self.duration, 
              "msgtype": self.msgtype, 
              "type": self.type,
              "date": self.date}
    message_str = json.dumps({"picture": data})
    return message_str

######### NAVIGATION MESSAGE ###############
class NavigationMessage(BaseMessage, object):
  def __init__(self, sender = "", msg_type="", duration =0, x =0.0, y=0.0, yaw=0.0):
    super(NavigationMessage, self).__init__(sender, duration, msg_type)
    self.x = x 
    self.y = y 
    self.yaw = yaw 

  def create_message(self):
    data = {"sender": self.sender, 
            "duration": self.duration, 
            "msgtype": self.msgtype, 
            "x": self.x,
            "y": self.y,
            "yaw": self.yaw}
    message_str = json.dumps({"navigation": data})
    return message_str