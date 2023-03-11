#!/usr/bin/env python3

from threading import Event, Thread


import PySimpleGUI as sg
import json
import base64


from PySimpleGUI.PySimpleGUI import Text

import os

import uuid


from flask import Flask
import requests
from flask import request

import threading

from easysettings import EasySettings


import qrcode
import socket

import pyperclip
import glob

import ast
import copy


WSPORT = 5000
device_url=None

#Helper procedures for working with lists on the screen

def get_synonym(elements,key):
    if key in elements:
        return  elements[key]
    else:
        return key    

def get_key(elements,value):
    for key, val in elements.items():
        if val == value:
            return key
    return value        

def get_title_list(elements):
    result =[]
    for  val in elements.items():
        result.append(val[1])      
    return result


#settings object
settings_global = EasySettings("uiconfigfile.conf") 

jlocale={}

#Loading translations from a file 
locale_filename =  settings_global.get("locale_filename")
if len(locale_filename) == 0:
    locale_filename='en_locale.json'

with open(locale_filename, 'r',encoding='utf-8') as file:
    data = file.read()
    
    jlocale  =json.loads(data)

#translation by current setting
def get_locale(key):
    if key in jlocale:
        return jlocale.get(key,key)
    else:    
        return key

#global variables
conf_filename=None
handlers_filename=None

current_uid=None

window = None

configuration_json={"ClientConfiguration":{"Processes":[]}}

jcurrent_process=None
jcurrent_screen=None
jcurrent_screen_line=None
jcurrent_layout=None
jcurrent_style=None
jcurrent_recognition=None
jcurrent_sql_on_start=None
jcurrent_mainmenu=None
jcurrent_timers=None
jcurrent_pyfiles=None
jcurrent_mediafiles=None

data_mediafiles=[]
data_pyfiles=[]
data_pyfilenames=[]
data_timers=[]
data_sql_on_start=[]
data_mainmenu=[]
data_screen_lines = []
columns = ['','','']

code_files={}

columns_handlers = ['','','','']
data_screen_handlers = []
data_screen_handlers.append(columns_handlers)

data_common_handlers = []
data_common_handlers.append(columns_handlers)

#screen list elemrnts
data_screen_lines.append(columns)

headings_screen_lines = [get_locale("screen_element"),get_locale("value"),get_locale("variable")]
headings_screen_handlers = [get_locale("event"),get_locale("action"),get_locale("listener"),get_locale("handlertype"),get_locale("method"),get_locale("postExecute")]
headings_common_handlers = [get_locale("alias"),get_locale("event"),get_locale("action"),get_locale("listener"),get_locale("handlertype"),get_locale("method"),get_locale("postExecute")]

action_elements = {"run":get_locale("run"),"runasync":get_locale("runasync")}
captions_action_elements = get_title_list(action_elements)

event_elements = {"onStart":get_locale("onStart"),"onPostStart":get_locale("onPostStart"),"onInput":get_locale("onInput")}
captions_event_elements = get_title_list(event_elements)

common_event_elements = {"onLaunch":get_locale("onLaunch"),"onIntentBarcode":get_locale("onIntentBarcode"),"onBluetoothBarcode":get_locale("onBluetoothBarcode"),"onBackgroundCommand":get_locale("onBackgroundCommand"),"onRecognitionListenerResult":get_locale("onRecognitionListenerResult"),
"onIntent":get_locale("onIntent"),"onWebServiceSyncCommand":get_locale("onWebServiceSyncCommand"),"onSQLDataChange":get_locale("onSQLDataChange"),"onSQLError":get_locale("onSQLError"),"onOpenFile":get_locale("onOpenFile")}
captions_common_event_elements = get_title_list(common_event_elements)

#,"onNotificationReply":get_locale("onNotificationReply")

event_elements_cv = {"OnCreate":get_locale("OnCreate"),"OnObjectDetected":get_locale("OnObjectDetected"),"OnTouch":get_locale("OnTouch"),"OnInput":get_locale("OnInput")}
captions_event_elements_cv = get_title_list(event_elements_cv)


handler_elements = {"python":get_locale("python"),"online":get_locale("online"),"http":get_locale("http"),"sql":get_locale("sql"),"httpworker":get_locale("httpworker"),"worker":get_locale("worker"),"set":get_locale("set")}
captions_handler_elements = get_title_list(handler_elements)


all_screen_lines_list = []
all_screen_handlers_list = []

all_common_handlers_list = []

screen_elements = {"LinearLayout":get_locale("layout"),"barcode":get_locale("barcode"),"HorizontalGallery":get_locale("horizontal_gallery"),
"voice":get_locale("voice_input"),"photo":get_locale("camera_capture"),"photoGallery":get_locale("gallery"),"voice":get_locale("tts"),"signature":get_locale("signature"),
"Vision":get_locale("ocr"),"Cart":get_locale("cart"),"Tiles":get_locale("tiles"),"ImageSlider":get_locale("image_slider"),"MenuItem":get_locale("menu_item"),"Tabs":get_locale("Tabs"),"Tab":get_locale("Tab")}
captions_screen_elements = get_title_list(screen_elements)

layout_elements = {"LinearLayout":get_locale("layout"),"Tabs":get_locale("Tabs"),"Tab":get_locale("Tab"),"TextView":get_locale("title"),"Button":get_locale("button"),
"EditTextText":get_locale("string_input"),"EditTextNumeric":get_locale("numeric_input"),"EditTextPass":get_locale("password_input"),"EditTextAuto":get_locale("event_input"),"EditTextAutocomplete":get_locale("autocompete_input"),
"ModernEditText":get_locale("modern_input"),"Picture":get_locale("picture"),"CheckBox":get_locale("checkbox"),"Gauge":get_locale("gauge"),"Chart":get_locale("chart"),"SpinnerLayout":get_locale("spinner"),"TableLayout":get_locale("table"),"CartLayout":get_locale("cart"),
"MultilineText":get_locale("multiline"),"CardsLayout":get_locale("cards"),"CButtons":get_locale("buttons_list"),"CButtonsHorizontal":get_locale("horizontal_buttons_list"),"DateField":get_locale("date_input"),"ProgressButton":get_locale("progress_button"),"html":get_locale("HTML"),"map":get_locale("map"),"file":get_locale("file")}
captions_layout_elements =get_title_list(layout_elements)

detector_elements = {"Barcode":get_locale("barcodes"),"OCR":get_locale("ocr"),"Objects_Full":get_locale("ocr_and_barcodes"),"Objects_OCR":get_locale("objects_ocr"),
"Objects_Barcode":get_locale("objects_barcode"),"Objects_f1":get_locale("face_detection"),"multiscanner":get_locale("multiscanner")}
captions_detector_elements = get_title_list(detector_elements)

visual_mode_elements = {"list_only":get_locale("list_only"),"green_and_grey":get_locale("green_and_grey"),"green_and_red":get_locale("green_and_red"),"list_and_grey":get_locale("list_and_grey")}
captions_visual_mode_elements = get_title_list(visual_mode_elements)

resolution_elements = ['HD1080','HD720','VGA','QVGA']

start_screen_elements = {"Menu":get_locale("operations_menu"),"Tiles":get_locale("tiles_menu")}
captions_start_screen_elements  = get_title_list(start_screen_elements)

detector_mode_elements = {"train":get_locale("training") ,"predict":get_locale("prediction")}
captions_detector_mode_elements = get_title_list(detector_mode_elements)

camera_mode_elements = {"Back":get_locale("rear"),"Front":get_locale("front")}
captions_camera_mode_elements = get_title_list(camera_mode_elements)

orientation_elements = {"vertical":get_locale("vertical"),"horizontal":get_locale("horizontal")}
captions_orientation_elements =get_title_list(orientation_elements)

scale_elements = {"match_parent":get_locale("mach_parent") ,"wrap_content":get_locale("wrap_content"),"manual":get_locale("manual")}
captions_scale_elements = get_title_list(scale_elements)

recognition_elements = {"Text":get_locale("ocr"),"Number":get_locale("number_recognition"),"Date":get_locale("date_recognition"),"PlateNumber":get_locale("car_platenumber")}
captions_recognition_elements = get_title_list(recognition_elements)

gravity_elements = {"left":get_locale("left"),"right":get_locale("right"),"center":get_locale("center")}
captions_gravity_elements = get_title_list(gravity_elements)

vertical_gravity_elements = {"top":get_locale("top"),"bottom":get_locale("bottom"),"center":get_locale("center")}
captions_vertical_gravity_elements = get_title_list(vertical_gravity_elements)

#updating python handlers code in SimpleUI configuration in thread
class CodeUpdateThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(1):
            if not  handlers_filename ==None:
                if len(handlers_filename)>0:
                    read_handlers_file(handlers_filename)

                    #additional python file update
                    
                    if len(data_pyfilenames)>0:
                        configuration_json['ClientConfiguration']['PyFiles']=[]
                        for py_file in data_pyfilenames:
                            if len(py_file['filename'])>0:
                                with open(py_file['filename'], 'r',encoding='utf-8') as file:
                                    data = file.read()
                                base64file  = base64.b64encode(data.encode('utf-8')).decode('utf-8')  
                                configuration_json['ClientConfiguration']['PyFiles'].append({"PyFileKey":py_file['key'],"PyFileData":base64file})
                            


#updating SimpleUI configuration properties
def update_conf(write_file=True):
    global window
    global configuration_json
    global conf_filename

    isPython = False
    isOnline = False
    isCV=False

    if 'PyHandlers' in configuration_json['ClientConfiguration']:
        if len(configuration_json['ClientConfiguration']['PyHandlers'])>0:
            isPython=True
  
    if 'DefServiceConfiguration' in configuration_json['ClientConfiguration']:
        if len(configuration_json['ClientConfiguration']['DefServiceConfiguration'])>0:
            isPython=True  

    if 'OnlineServiceConfiguration' in configuration_json['ClientConfiguration']:
        if len(configuration_json['ClientConfiguration']['OnlineServiceConfiguration'])>0:
            isOnline=True            
            

    if 'Processes' in configuration_json['ClientConfiguration']:        
        for process in configuration_json['ClientConfiguration']['Processes']:
            if process['type']=='Process' and 'Operations' in process:
                for operation in process['Operations']:
                    if len(operation.get('PythonOnCreate',''))>0 or len(operation.get('PythonOnInput',''))>0 or len(operation.get('DefOnCreate',''))>0 or len(operation.get('DefOnInput',''))>0 :
                        isPython=True
                        if len(operation.get('PythonOnCreate',''))>0 or len(operation.get('DefOnCreate',''))>0:
                            operation['send_when_opened']=True
                    if len(operation.get('DefOnlineOnCreate',''))>0  :
                        operation['onlineOnStart']=True
                        operation['send_when_opened']=True
                        isOnline=True
                    else:
                        operation['onlineOnStart']=False 

                    if len(operation.get('DefOnAfterCreate',''))>0  :
                        isPython=True
                        if len(operation.get('DefOnAfterCreate',''))>0:
                            operation['send_after_opened']=True
                    if len(operation.get('DefOnlineOnAfterCreate',''))>0  :
                        operation['onlineOnAfterStart']=True
                        operation['send_after_opened']=True
                        isOnline=True
                    else:
                        operation['onlineOnAfterStart']=False      
                          
                    if len(operation.get('DefOnlineOnInput',''))>0 :
                        operation['onlineOnInput']=True
                        isOnline=True    
                    else:    
                        operation['onlineOnInput']=False
            if process['type']=='CVOperation' and 'CVFrames' in process:
                for operation in process['CVFrames']:
                        isCV=True
                        if len(operation.get('CVFrameOnlineOnCreate',''))>0 or len(operation.get('CVFrameOnlineOnNewObject',''))>0 or len(operation.get('CVFrameOnlineAction',''))>0 or len(operation.get('CVFrameOnlineOnTouch',''))>0 :
                            operation['CVOnline']=True
                            isOnline=True
                        else:
                            operation['CVOnline']=False    
                        if len(operation.get('CVFrameDefOnCreate',''))>0 or len(operation.get('CVFrameDefOnNewObject',''))>0 or len(operation.get('CVFrameDefAction',''))>0 or len(operation.get('CVFrameDefOnTouch',''))>0  or len(operation.get('CVFramePythonOnCreate',''))>0 or len(operation.get('CVFramePythonOnNewObject',''))>0 or len(operation.get('CVFramePythonAction',''))>0 or len(operation.get('CVFramePythonOnTouch',''))>0 :
                            isPython=True
                           

    if isPython:
        configuration_json['ClientConfiguration']['RunPython']  =True   

            
    tags=[]
    if isPython:
        tags.append('Py') 
        tags.append('off-line')        
    if isOnline:
        tags.append('Online')        
    if isCV:
        tags.append('ActiveCV®')    

    configuration_json['ClientConfiguration']['ConfigurationTags']=",".join(tags)        

    if window!=None:
        window['json_multiline'].update(json.dumps(configuration_json,ensure_ascii=False,indent=4, separators=(',', ': ')))

    if not conf_filename==None:
        if len(conf_filename)>0:
            if write_file :
                with open(conf_filename, 'w', encoding='utf-8') as f:
                    json.dump(configuration_json, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        


#Main screen layout

icon_elements = ['forward','backward','run','cancel','edit','picture','info','settings','plus','save','search','send','done']

create_handler_text='<'+get_locale("create_handler")+'>'
create_handler_tooltip=get_locale("create_handler")

layout_common_screen = [[sg.Text(get_locale("screen_name"),size=35),sg.Input(do_not_clear=True, key='screen_name',enable_events=True,expand_x=True)],
[sg.Checkbox(get_locale("screen_timer"),key='cb_screen_timer',enable_events=True)],
[sg.Checkbox(get_locale("screen_no_scroll"),key='cb_screen_no_scroll',enable_events=True)],
[sg.Checkbox(get_locale("hide_buttons_bar"),key='cb_screen_hide_bottom_bar',enable_events=True)],
[sg.Checkbox(get_locale("hide_top_bar") ,key='cb_screen_hide_toolbar',enable_events=True)],
[sg.Checkbox(get_locale("close_no_confirm") ,key='cb_screen_no_confirmation',enable_events=True)],
[sg.Checkbox(get_locale("attach_keyboard") ,key='cb_screen_keyboard',enable_events=True)]
]



layout_listener_online = [
               [sg.Text(get_locale("function_onstart_screen_online") ,size=50),sg.Input(key='screen_def_oncreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_onafterstart_screen_online") ,size=50),sg.Input(key='screen_def_onaftercreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_oninput_screen_online") ,size=50),sg.Input(key='screen_def_oninput',enable_events=True,expand_x=True)],
               [sg.T("")],
               [sg.Text(get_locale("function_onstart_screen_python") ,size=50),sg.Input(key='screen_defpython_oncreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_onafterstart_screen_python") ,size=50),sg.Input(key='screen_defpython_onaftercreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_oninput_screen_python") ,size=50),sg.Input(key='screen_defpython_oninput',enable_events=True,expand_x=True)]

              ]  

layout_new_handlers = [
    [sg.Button(get_locale("add_screen_handler"),key='btn_add_screen_handler'),sg.Button(get_locale("delete_screen_handler"),key='btn_delete_screen_handler')],
    [
               sg.Table(values=data_screen_handlers, headings=headings_screen_handlers,auto_size_columns=True,
                   
                    display_row_numbers=False,
                    num_rows=10,
                    
                    key='ScreenHandlersTable',
                    selected_row_colors='red on yellow',
                                      
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key =True,
                    
                    expand_x=True,expand_y=True) ]

              ] 

layout_common_new_handlers = [
    [sg.Button(get_locale("add_common_handler"),key='btn_add_common_handler'),sg.Button(get_locale("delete_common_handler"),key='btn_delete_common_handler')],
    [
               sg.Table(values=data_common_handlers, headings=headings_common_handlers,auto_size_columns=True,
                   
                    display_row_numbers=False,
                    num_rows=10,
                    
                    key='CommonHandlersTable',
                    selected_row_colors='red on yellow',
                                      
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key =True,
                    
                    expand_x=True,expand_y=True) ]

              ]               

layout_handler_element =[
    [sg.Text(get_locale("alias"),size=50 ),sg.Input(do_not_clear=True, key='common_handlers_alias',enable_events=True,size=200)],
     [sg.Text(get_locale("event"),size=50),sg.Combo(captions_event_elements,key='common_handlers_alias',enable_events=True,size=200)],
    [sg.Text(get_locale("action"),size=50),sg.Combo(captions_action_elements,key='common_handlers_alias',enable_events=True,size=200)],
    [sg.Text(get_locale("handlerslistener"),size=50 ),sg.Input(do_not_clear=True, key='common_handlers_alias',enable_events=True,size=200)],
    [sg.Text(get_locale("handlertype"),size=50),sg.Combo(captions_handler_elements,key='common_handlers_alias',enable_events=True,size=200)],
    [sg.Text(get_locale("handlersmetod") ,size=50),sg.Input(do_not_clear=True, key='common_handlers_alias',enable_events=True,size=200)],
    [sg.Text(get_locale("postExecute"),size=50),sg.Input(do_not_clear=True, key='common_handlers_alias',enable_events=True,size=200)]
     
    ] 



layout_handler_element_cv =[
     [sg.Text(get_locale("event"),size=50),sg.Combo(captions_event_elements_cv,key='handlers_event',enable_events=True,size=200)],
    [sg.Text(get_locale("action"),size=50),sg.Combo(captions_action_elements,key='handlers_action',enable_events=True,size=200)],
     [sg.Text(get_locale("handlerslistener") ,size=50),sg.Input(do_not_clear=True, key='handlers_listener',enable_events=True,size=200)],
    [sg.Text(get_locale("handlertype"),size=50),sg.Combo(captions_handler_elements,key='handlers_type',enable_events=True,size=200)],
    [sg.Text(get_locale("handlersmetod") ,size=50),sg.Input(do_not_clear=True, key='handlers_method',enable_events=True,size=200)],
    [sg.Text(get_locale("postExecute"),size=50),sg.Input(do_not_clear=True, key='handlers_postExecute',enable_events=True,size=200)]
     
    ]           

data_recognition=[]
layout_common_cv =[
    [sg.Text(get_locale("cv_step_name") ),sg.Input(do_not_clear=True, key='step_name',enable_events=True)],
    [sg.Text(get_locale("detector")),sg.Combo(captions_detector_elements,key='CVFrame_detector',enable_events=True)],
    [sg.Text(get_locale("resolution")),sg.Combo(resolution_elements,key='CVResolution',enable_events=True)],
    [sg.Text(get_locale("display_mode")),sg.Combo(captions_visual_mode_elements,key='CVMode',enable_events=True)],
    [sg.Text(get_locale("action_buttons") ),sg.Input(do_not_clear=True, key='CVActionButtons',enable_events=True)],
    [sg.Text(get_locale("action_header")),sg.Input(do_not_clear=True, key='CVAction',enable_events=True)],
    [sg.Text(get_locale("info_header")),sg.Input(do_not_clear=True, key='CVInfo',enable_events=True)],
    [sg.Text(get_locale("camera_mode")),sg.Combo(captions_camera_mode_elements, key='CVCameraDevice',enable_events=True)],
    [sg.Text(get_locale("detector_mode")),sg.Combo(captions_detector_mode_elements, key='CVDetectorMode',enable_events=True)],
    [sg.Text(get_locale("mask")),sg.Input( key='CVMask',enable_events=True)],
    [sg.Text(get_locale('recognition_template'),size=35),sg.Combo(data_recognition,key='cvrecognition_type',enable_events=True,expand_x=True)]        
    
    ]

 

cv_layout_listener_online = [
               [sg.Text(get_locale("function_onstart_cv_online") ,size=50),sg.Input(key='CVFrameOnlineOnCreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_found_new_object_cv_online") ,size=50),sg.Input(key='CVFrameOnlineOnNewObject',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_touch_object_cv_online") ,size=50),sg.Input(key='CVFrameOnlineOnTouch',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_action_buttons_cv_online") ,size=50),sg.Input(key='CVFrameOnlineAction',enable_events=True,expand_x=True)],
               [sg.T("")],
               [sg.Text(get_locale("function_onstart_cv_python"),size=50),sg.Input(key='CVFrameDefOnCreate',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_found_new_object_cv_python"),size=50),sg.Input(key='CVFrameDefOnNewObject',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_touch_object_cv_python"),size=50),sg.Input(key='CVFrameDefOnTouch',enable_events=True,expand_x=True)],
               [sg.Text(get_locale("function_action_buttons_cv_python"),size=50),sg.Input(key='CVFrameDefAction',enable_events=True,expand_x=True)]
                            
              ]   
cv_layout_new_handlers = [
                   [sg.Button(get_locale("add_screen_handler"),key='btn_add_screen_handler_cv'),sg.Button(get_locale("delete_screen_handler"),key='btn_delete_screen_handler_cv')],
    [
               sg.Table(values=data_screen_handlers, headings=headings_screen_handlers,auto_size_columns=True,
                   
                    display_row_numbers=False,
                    num_rows=10,
                    
                    key='ScreenHandlersTableCV',
                    selected_row_colors='red on yellow',
                                      
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key =True,
                    
                    expand_x=True,expand_y=True) ]
                            
              ]

layout_lines = [[sg.Button(get_locale("add_screen_element"),key='btn_add_screen_line'),sg.Button(get_locale("delete_screen_element"),key='btn_delete_screen_line'),sg.Button(get_locale("insert_from_clipboard"),key='btn_insert_from_clipboard_screen_line')],[

                  sg.Table(values=data_screen_lines[1:][:], headings=headings_screen_lines,auto_size_columns=True,
                   
                    display_row_numbers=False,
                    
                    num_rows=10,
                    
                    key='ScreenLinesTable',
                    selected_row_colors='red on yellow',
                    #enable_events=True,
                                     
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key =True,
                    
                    expand_x=True,expand_y=True)  

          ]
           ]



tab_layout_screen = [
    [sg.TabGroup([[sg.Tab(get_locale("common") ,layout_common_screen),sg.Tab(get_locale("structure") ,layout_lines),sg.Tab(get_locale("screen_handlers"),layout_listener_online,key="screen_handlers"),sg.Tab(get_locale("new_screen_handlers"),layout_new_handlers)]],expand_x=True,expand_y=True) ]
               ]

tab_layout_CVFrame = [
    [sg.TabGroup([[sg.Tab(get_locale("common_cv") ,layout_common_cv),sg.Tab(get_locale("handlers_cv") ,cv_layout_listener_online,key="handlers_cv"),sg.Tab(get_locale("new_handlers_cv") ,cv_layout_new_handlers)]],expand_x=True,expand_y=True) ] 
               ]               



sg.theme('SystemDefault')

def normalizefilename(fn):
    validchars = "-_.() "
    out = ""
    for c in fn:
      if str.isalpha(c) or str.isdigit(c) or (c in validchars):
        out += c
      else:
        out += "_"
    return out 

#swich visibility between any types of processes
def set_visibility(jcurrent_screen):
    global window
    if window !=None:
        

      

        if jcurrent_screen['type']=="CVFrame":
            window['tab_screen'].update(visible=False)
            window['tab_cv'].update(visible=True)
            window['tab_cv'].select()


            window['step_name'].update(jcurrent_screen['Name'])
            window['CVFrame_detector'].update(get_synonym(detector_elements,jcurrent_screen.get('CVDetector')))

            window['CVActionButtons'].update(jcurrent_screen.get('CVActionButtons',''))
            window['CVAction'].update(jcurrent_screen.get('CVAction',''))
            window['CVInfo'].update(jcurrent_screen.get('CVInfo',''))
            window['CVMode'].update(get_synonym(visual_mode_elements ,jcurrent_screen.get('CVMode','')))
            window['CVCameraDevice'].update(get_synonym(camera_mode_elements,jcurrent_screen.get('CVCameraDevice','')))
            window['CVResolution'].update(jcurrent_screen.get('CVResolution'))
            window['CVDetectorMode'].update(get_synonym(detector_mode_elements,jcurrent_screen.get('CVDetectorMode','')))

            window['CVMask'].update(jcurrent_screen.get('CVMask',''))
            
            window['CVFrameOnlineOnCreate'].update(jcurrent_screen.get('CVFrameOnlineOnCreate',''))
            window['CVFrameOnlineOnNewObject'].update(jcurrent_screen.get('CVFrameOnlineOnNewObject',''))
            window['CVFrameOnlineAction'].update(jcurrent_screen.get('CVFrameOnlineAction',''))
            window['CVFrameOnlineOnTouch'].update(jcurrent_screen.get('CVFrameOnlineOnTouch',''))

            window['CVFrameDefOnCreate'].update(jcurrent_screen.get('CVFrameDefOnCreate',''))
            window['CVFrameDefOnNewObject'].update(jcurrent_screen.get('CVFrameDefOnNewObject',''))
            window['CVFrameDefAction'].update(jcurrent_screen.get('CVFrameDefAction',''))
            window['CVFrameDefOnTouch'].update(jcurrent_screen.get('CVFrameDefOnTouch',''))

            data_recognition = []
            if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
               for elem in configuration_json['ClientConfiguration']['RecognitionTemplates']:
                        data_recognition.append(elem['name'])

            window['cvrecognition_type'].update(values = data_recognition)
          
            window['cvrecognition_type'].update(jcurrent_screen.get('RecognitionTemplate'))

        else:
            window['tab_screen'].update(visible=True)
            window['tab_screen'].select()
            window['tab_cv'].update(visible=False)

            window['screen_name'].update(jcurrent_screen.get('Name'))

            window['cb_screen_timer'].update(jcurrent_screen.get('Timer'))
            window['cb_screen_hide_bottom_bar'].update(jcurrent_screen.get('hideBottomBarScreen'))
            window['cb_screen_no_scroll'].update(jcurrent_screen.get('noScroll'))

            window['cb_screen_hide_toolbar'].update(jcurrent_screen.get('hideToolBarScreen'))
            window['cb_screen_no_confirmation'].update(jcurrent_screen.get('noConfirmation'))
            window['cb_screen_keyboard'].update(jcurrent_screen.get('handleKeyUp'))

            window['screen_def_oncreate'].update(jcurrent_screen.get('DefOnlineOnCreate',''))
            window['screen_def_onaftercreate'].update(jcurrent_screen.get('DefOnlineOnAfterCreate',''))
            window['screen_def_oninput'].update(jcurrent_screen.get('DefOnlineOnInput',''))

            window['screen_defpython_oncreate'].update(jcurrent_screen.get('DefOnCreate',''))
            window['screen_defpython_onaftercreate'].update(jcurrent_screen.get('DefOnAfterCreate',''))
            window['screen_defpython_oninput'].update(jcurrent_screen.get('DefOnInput',''))




#read process lists from SimpleUI configuration
def load_processes(SetCurrent=False):
    global jcurrent_process
    data.clear()
    columns = [get_locale('headings_processes')]
    data.append(columns)
    
    all_processes_list.clear()

    if configuration_json!=None:
        for elem in configuration_json['ClientConfiguration']['Processes']:
            all_processes_list.append(elem)
            type = elem['type']
            if type =="Process":
                row=[elem['ProcessName']]

            elif type =="CVOperation":
                row=[elem['CVOperationName']]
            data.append(row)

    if len(all_processes_list)>0 and (jcurrent_process==None or SetCurrent):
        jcurrent_process=all_processes_list[0]    
    
    update_conf(False)

#read screen lists from SimpleUI configuration
def load_screens(SetCurrent=False):
    #data_screens = []
    global jcurrent_screen

    data_screens.clear()
    columns = [get_locale("screens")]
    data_screens.append([columns])
    all_screens_list.clear()
    
    if jcurrent_process!=None:
        if jcurrent_process['type']=="CVOperation":
            for elem in jcurrent_process['CVFrames']:
                all_screens_list.append(elem)
                type = elem['type']
                if type =="CVFrame":
                    row=[elem['Name']]
                data_screens.append(row)
        else:    
            for elem in jcurrent_process['Operations']:
                all_screens_list.append(elem)
                type = elem['type']
                if type =="Operation":
                    row=[elem['Name']]
                data_screens.append(row)

    if len(all_screens_list)>0  and (jcurrent_screen==None or SetCurrent):
        jcurrent_screen=all_screens_list[0]   
        set_visibility(jcurrent_screen)

             
#read ActiveCV steps lists from SimpleUI configuration
def load_cvsteps(SetCurrent=False):
    
    global jcurrent_screen

    data_screens.clear()
    columns = [get_locale("cv_steps")]
    data_screens.append([columns])
    all_screens_list.clear()
    if jcurrent_process!=None:
        for elem in jcurrent_process['CVFrames']:
            all_screens_list.append(elem)
            type = elem['type']
            if type =="CVFrame":
                row=[elem['Name']]
            data_screens.append(row)

    if len(all_screens_list)>0  and (jcurrent_screen==None or SetCurrent):
        jcurrent_screen=all_screens_list[0]
        set_visibility(jcurrent_screen)  

#read screen layout from SimpleUI configuration
def load_screen_lines(is_CV=False,SetCurrent=False):
    global jcurrent_screen_line

    data_screen_lines.clear()
    columns = ['','','']
    data_screen_lines.append([columns])
    all_screen_lines_list .clear()

    if not is_CV:
        if jcurrent_screen!=None:
            if 'Elements' in jcurrent_screen:

                for elem in jcurrent_screen['Elements']:
                    all_screen_lines_list.append(elem)
                    value =''
                    var=''
                    if 'Value' in elem:
                        value = elem['Value']
                    if 'Variable' in elem:
                        var =  elem['Variable']   
                    row=[get_synonym(screen_elements,elem.get('type','')),value,var]
                    data_screen_lines.append(row)  

        if len(all_screen_lines_list)>0 and (jcurrent_screen_line==None or SetCurrent):
            jcurrent_screen_line=all_screen_lines_list[0]                 

def load_screen_handlers():
    

    data_screen_handlers.clear()
    columns = ['','','','','']
    data_screen_handlers.append([columns])
    all_screen_handlers_list .clear()

   
    if jcurrent_screen!=None:
        if 'Handlers' in jcurrent_screen:
            for elem in jcurrent_screen['Handlers']:
                all_screen_handlers_list.append(elem)
                method =''
                postExecute=''
                if 'method' in elem:
                    method = elem['method']
                if 'postExecute' in elem:
                    postExecute =  elem['postExecute']   
                row=[get_synonym(screen_elements,elem.get('event','')),get_synonym(screen_elements,elem.get('action','')),elem.get('listener',''),get_synonym(screen_elements,elem.get('type','')),method,postExecute]
                data_screen_handlers.append(row)  

def load_common_handlers():
    

    data_common_handlers.clear()
    columns = ['','','','','','']
    data_common_handlers.append([columns])
    all_common_handlers_list .clear()

   
    
    if 'CommonHandlers' in configuration_json['ClientConfiguration']:
            for elem in configuration_json['ClientConfiguration']['CommonHandlers']:
                all_common_handlers_list.append(elem)
                method =''
                postExecute=''
                if 'method' in elem:
                    method = elem['method']
                if 'postExecute' in elem:
                    postExecute =  elem['postExecute']   
                row=[elem.get('alias',''),get_synonym(screen_elements,elem.get('event','')),get_synonym(screen_elements,elem.get('action','')),elem.get('listener',''),get_synonym(screen_elements,elem.get('type','')),method,postExecute]
                data_common_handlers.append(row)  

        
   

data = []
all_processes_list = []
all_styles_list = []
all_recognition_list = []


headings = [get_locale('headings_processes')]
headings_screens = [get_locale('screens')]
headings_svsteps = [get_locale('cv_steps')]


data_screens = []
columns = [get_locale('screens')]
data_screens.append(columns)
all_screens_list = []





def Collapsible(layout, key, title='', arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP), collapsed=False):

    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key+'-BUTTON-'),
                       sg.T(title, enable_events=True, key=key+'-TITLE-')],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0,0))

#Helper fuction for visualization
def show_scale_invisible(f,jelement,caption):
    if jelement==None:
       
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'wrap_content'),enable_events=True),sg.Input(key=f+'_value',visible=False,enable_events=True)] 
       
    else:
        if jelement.get(f)=='match_parent' or jelement.get(f)=='wrap_content' :
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value=get_synonym(scale_elements, jelement[f]),enable_events=True),sg.Input(key=f+'_value',visible=False,enable_events=True)] 
        else:
            if f in jelement:
                layout = [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'manual'),enable_events=True),sg.Input(key=f+'_value',default_text= jelement[f],enable_events=True)]
            else:
                layout = [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'manual'),enable_events=True),sg.Input(key=f+'_value',enable_events=True)]    
        
    return layout



def show_scale(f,jelement,caption):
    if jelement==None:
       
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'wrap_content'),enable_events=True)] 
       
    else:
        if jelement.get(f,'')=='match_parent' or jelement.get(f,'')=='wrap_content' :
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,jelement[f]),enable_events=True)] 
        else:
            if f in jelement:
                layout = [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'manual'),enable_events=True),sg.Input(key=f+'_value',default_text= jelement[f])]
            else:
                layout = [sg.Text(caption,size=35),sg.Combo(captions_scale_elements,key=f,default_value= get_synonym(scale_elements,'manual'),enable_events=True),sg.Input(key=f+'_value')]    
        
    return layout

def show_type_recognition(f,jelement,caption):
    if jelement==None:
       
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_recognition_elements,key=f,default_value= get_synonym(recognition_elements,'Text'),enable_events=True)] 
       
    else:
        
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_recognition_elements,key=f,default_value= get_synonym(recognition_elements,jelement.get(f)),enable_events=True)] 
        
        
    return layout

def show_horizontal_gravity(f,jelement,caption):
    if jelement==None:
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_gravity_elements,key=f,default_value= get_synonym(gravity_elements,'center'),enable_events=True)] 
    else:
        if f in jelement:
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_gravity_elements,key=f,default_value= get_synonym(gravity_elements,jelement[f]),enable_events=True)] 
        else:
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_gravity_elements,key=f,default_value= get_synonym(gravity_elements,'center'),enable_events=True)]     
    return layout

def show_vertical_gravity(f,jelement,caption):
    if jelement==None:
        layout =  [sg.Text(caption,size=35),sg.Combo(captions_vertical_gravity_elements,key=f,default_value= get_synonym(vertical_gravity_elements,'center'),enable_events=True)] 
    else:
        if f in jelement:
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_vertical_gravity_elements,key=f,default_value= get_synonym(vertical_gravity_elements,jelement[f]),enable_events=True)] 
        else:
            layout =  [sg.Text(caption,size=35),sg.Combo(captions_vertical_gravity_elements,key=f,default_value= get_synonym(vertical_gravity_elements,'center'),enable_events=True)]     
    return layout    

def show_icon(f,jelement,caption):
    if jelement==None:
        layout =  [sg.Text(caption,size=35),sg.Combo(icon_elements,key=f,enable_events=True)] 
    else:
        if f in jelement:
            layout =  [sg.Text(caption,size=35),sg.Combo(icon_elements,key=f,default_value= jelement[f],enable_events=True)] 
        else:
            layout =  [sg.Text(caption,size=35),sg.Combo(icon_elements,key=f,enable_events=True)] 
    return layout



def show_input(f,jelement,caption):
    if jelement==None:
       
       if f=='NumberPrecision':
        layout =  [sg.Text(caption,size=35),sg.Input(key=f,enable_events=True,default_text='-1')] 
       else: 
        layout =  [sg.Text(caption,size=35),sg.Input(key=f,enable_events=True)]    
       
    else:
        if f=='NumberPrecision':
            layout = [sg.Text(caption,size=35),sg.Input(key=f,default_text= jelement.get(f,'-1'),enable_events=True)]
        else: 
            layout =  [sg.Text(caption,size=35),sg.Input(key=f,enable_events=True,default_text= jelement.get(f))]     
            if f=='query' :
                q=''
                try:
                    q =  b64=base64.b64decode(jelement.get(f).encode('utf-8')).decode('utf-8')
                except:
                    q=jcurrent_recognition.get('query')
                layout =  [sg.Text(caption,size=35),sg.Input(key=f,enable_events=True,default_text= q)]         
            else:
                layout =  [sg.Text(caption,size=35),sg.Input(key=f,enable_events=True,default_text= jelement.get(f))]         

    return layout

def show_checkbox(f,jelement,caption):
    if jelement==None:
        layout =  [sg.Checkbox(caption,key=f,enable_events=True) ]
    else:
        layout = [sg.Checkbox(caption,key=f,default=jelement.get(f),enable_events=True)]
    return layout

 
def get_data_container_lines(jelement):
    data_container_lines = []
    columns = [get_locale('layout_structure_'),'','']
    data_container_lines.append([columns])
    #all_screen_lines_list .clear()
    if jelement!=None:
       for elem in jelement['Elements']:
                #all_screen_lines_list.append(elem)
                        
            row=[get_synonym(layout_elements,elem['type']),elem.get('Value',''),elem.get('Variable','')]
            data_container_lines.append(row) 
    
    return  data_container_lines           

#Edit screen line window
def show_edit(type,editwindow,jelement,is_layout=False):
    if type=='LinearLayout' or type=="Tabs" or type=="Tab" :

        if not 'Elements' in jelement:
            jelement['Elements']=[]

         

        data_container_lines = get_data_container_lines(jelement)
        headings_container = [get_locale('element'),get_locale('value'),get_locale('variable')]


        if is_layout:
            default_value= get_synonym(layout_elements,type)
        else:
            default_value= get_synonym(screen_elements,type)


        layout = [[sg.Text(get_locale('type_of_element'),size=35),sg.Combo(captions_screen_elements,key='type',enable_events=True,default_value= default_value)],
        #[sg.Text(get_synonym(screen_elements ,'КОНТЕЙНЕР')), sg.Text('', key='_OUTPUT_')],
        [sg.Text(get_locale('variable'),size=35),sg.Input(do_not_clear=True, key='variable',default_text=jelement.get('Variable',''),enable_events=True)],
        [sg.Text(get_locale('background_color'),size=35),sg.Input(do_not_clear=True, key='background_color',default_text=jelement.get('BackgroundColor',''),enable_events=True)],
        [sg.Text(get_locale('stroke_width'),size=35),sg.Input(do_not_clear=True, key='stroke_width',default_text=jelement.get('StrokeWidth',''),enable_events=True)],
        [sg.Text(get_locale('padding'),size=35),sg.Input(do_not_clear=True, key='padding',default_text=jelement.get('Padding',''),enable_events=True)],
         [sg.Text(get_locale('orientation'),size=35),sg.Combo(captions_orientation_elements,key='orientation',default_value= get_synonym(orientation_elements,jelement.get('orientation','')))],
        [show_scale('height',jelement,get_locale('height') )],
        [show_scale('width',jelement,get_locale('width') )],
        show_horizontal_gravity('gravity_horizontal',jelement,get_locale('gravity_horizontal') ),
        show_vertical_gravity('gravity_vertical',jelement,get_locale('gravity_vertical') ),
        [sg.Text(get_locale('weight'),size=35),sg.Input(key='weight',default_text= jelement.get('weight',0))],
        [sg.Button(get_locale('add_element'),key='btn_add_layout_line'),sg.Button(get_locale('copy_element'),key='btn_copy_layout_line'),sg.Button(get_locale('up'),key='btn_up_layout_line'),sg.Button(get_locale('down'),key='btn_down_layout_line'),sg.Button(get_locale('delete'),key='btn_delete_layout_line'),sg.Button(get_locale('insert_from_clipboard'),key='btn_insert_from_clipboard_layout_line')],
        [sg.Table(values=data_container_lines[1:][:], headings=headings_container,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='left',
                    num_rows=10,
                   
                    key='LayoutTable',
                    selected_row_colors='red on yellow',
                    #enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key=True,
                    #enable_click_events=True,           
                    tooltip='This is a table')],
                    [sg.Button(get_locale('save_layout'),key='btn_save_layout_line'),sg.Button(get_locale('copy_to_clipboard') ,key='btn_get_layout_base')]
                    ]                    
        window1 = sg.Window(get_locale("layout"),icon='ic_32.ico',modal=True).Layout(layout)
        if editwindow !=None: 
            editwindow.Close()
        editwindow = window1    
    else:

        style_elements=[]
        if 'StyleTemplates' in configuration_json['ClientConfiguration']:
            for jstyle in configuration_json['ClientConfiguration']['StyleTemplates']:
                style_elements.append(jstyle['name'])

        if not 'Value' in jelement:
             jelement['Value']=''
        if not 'Variable' in jelement:
             jelement['Variable']=''

        layoutStyle=[]
        #if 'height' in jelement or is_layout or 'width' in jelement:
        if is_layout:
            layoutStyle = [

                show_scale_invisible('height',jelement,get_locale('height')),
                show_scale_invisible('width',jelement,get_locale('width')),
                show_input('weight',jelement,get_locale('weight')) ,
                show_input('BackgroundColor',jelement,get_locale('background_color')) ,
                show_input('TextSize',jelement,get_locale('text_size')) ,
                show_input('TextColor',jelement,get_locale('text_color')) ,
                show_checkbox('TextBold',jelement,get_locale('bold')),
                show_checkbox('TextItalic',jelement,get_locale('italic')),
                show_horizontal_gravity('gravity_horizontal',jelement,get_locale('gravity_horizontal') ),
                show_icon('drawable',jelement,get_locale('icon')),
                show_input('NumberPrecision',jelement,get_locale('number_decimal')) 

                ]

        data_recognition = []
        if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
            for elem in configuration_json['ClientConfiguration']['RecognitionTemplates']:
                data_recognition.append(elem['name'])

        layoutRecognition=[]
        if type=='Vision':    
            layoutRecognition = [[sg.Text(get_locale('recognition_template'),size=35),sg.Combo(data_recognition,key='recognition_type',enable_events=True,default_value=jelement.get('RecognitionTemplate'))]]        

        if is_layout:
            default_value= get_synonym(layout_elements,type)
            combo_elements = captions_layout_elements
            
        else:
            default_value= get_synonym(screen_elements,type)
            combo_elements = captions_screen_elements

        layout = [[sg.Text(get_locale('element'),size=35),sg.Combo(combo_elements,key='type',enable_events=True,default_value= default_value)],
        #[sg.Text('ВСЕ ОСТАЛЬНОЕ'), sg.Text('', key='_OUTPUT_')],
        [sg.Text(get_locale('value'),size=35),sg.Input(do_not_clear=True, key='value',default_text=jelement['Value'],enable_events=True)],
        [sg.Text(get_locale('variable'),size=35),sg.Input(do_not_clear=True, key='variable',default_text=jelement['Variable'],enable_events=True)],
        [sg.Text('Шаблон стиля',size=35),sg.Combo(style_elements,key='style_name',enable_events=True,default_value= jelement.get('style_name',''),size = 35)],
        layoutStyle,
        layoutRecognition,
        [sg.Button(get_locale('save'),key='btn_save_layout_line')]
        ]
        
        window1 = sg.Window(get_locale('screen_element'),icon='ic_32.ico',modal=True).Layout(layout)
        if editwindow !=None: 
            editwindow.Close()
        editwindow = window1   

           

    return editwindow  





#Style templae funtions
def set_visibility_style(swindow,jcurrent_style,element_form=False,islayout=False):


    if swindow==None:
        return

    if element_form!=True:
        swindow['style_name'].update('')
    
    
    swindow['height'].update('')
    swindow['width'].update('')
    swindow['weight'].update('0')
    swindow['height_value'].update('',visible=False)
    swindow['width_value'].update('',visible=False)
    swindow['row'].update('')
    swindow['use_as_class'].update(False)

    if not islayout:
        swindow['BackgroundColor'].update('')
        swindow['TextSize'].update('')
        swindow['TextColor'].update('')
        swindow['TextBold'].update('')
        swindow['TextItalic'].update('')
        swindow['gravity_horizontal'].update('')
        swindow['drawable'].update('')
        swindow['NumberPrecision'].update('')
        
    


    if jcurrent_style!=None:
        if element_form!=True:
            swindow['style_name'].update(jcurrent_style.get('name'),disabled=False)
        
        swindow['height'].update(jcurrent_style.get('height'),disabled=False)
        swindow['width'].update(jcurrent_style.get('width'),disabled=False)
        swindow['weight'].update(jcurrent_style.get('weight'),disabled=False)
        
        swindow['row'].update(jcurrent_style.get('row'),disabled=False)
        swindow['use_as_class'].update(jcurrent_style.get('use_as_class'),disabled=False)

        if jcurrent_style.get('height')=='manual':
            swindow['height_value'].update(jcurrent_style.get('height_value'),visible=True)
        if jcurrent_style.get('width')=='manual':
            swindow['width_value'].update(jcurrent_style.get('width_value'),visible=True)


        if not islayout:
            swindow['BackgroundColor'].update(jcurrent_style.get('BackgroundColor'),disabled=False)
            swindow['TextSize'].update(jcurrent_style.get('TextSize'),disabled=False)
            swindow['TextColor'].update(jcurrent_style.get('TextColor'),disabled=False)
            swindow['TextBold'].update(jcurrent_style.get('TextBold'),disabled=False)
            swindow['TextItalic'].update(jcurrent_style.get('TextItalic'),disabled=False)
            swindow['gravity_horizontal'].update(jcurrent_style.get('gravity_horizontal'),disabled=False)
            swindow['drawable'].update(jcurrent_style.get('drawable'),disabled=False)
            swindow['NumberPrecision'].update(jcurrent_style.get('NumberPrecision'),disabled=False)

        

    else:
        if element_form!=True:    
            swindow['style_name'].update('',disabled=True)
        
        swindow['height'].update('',disabled=True)
        swindow['width'].update('',disabled=True)
        swindow['weight'].update('',disabled=True)

        if not islayout:
            swindow['BackgroundColor'].update('',disabled=True)
            swindow['TextSize'].update('',disabled=True)
            swindow['TextColor'].update('',disabled=True)
            swindow['TextBold'].update('',disabled=True)
            swindow['TextItalic'].update('',disabled=True)
            swindow['gravity_horizontal'].update('',disabled=True)
            swindow['drawable'].update('',disabled=True)
            swindow['NumberPrecision'].update('',disabled=True)



def update_styles(window,SetCurrent=False):
    global jcurrent_style
    global all_styles_list

    data_styles = []
    #columns = ['']
    #data_styles.append(columns)

    all_styles_list = []
    
    if 'StyleTemplates' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['StyleTemplates']:
              data_styles.append([elem['name']])
              all_styles_list.append(elem)

    if len(all_styles_list)>0 and SetCurrent:
        jcurrent_style = all_styles_list[0]
        set_visibility_style(window,jcurrent_style)

    return  data_styles         

def save_style_values_event( jcurrent_style,event,values,write_conf=False,isstyle=False):

    if event==  'value':  
                jcurrent_style['Value'] = values['value'] 
  
    if event==  'variable':  
                jcurrent_style['Variable'] = values['variable'] 
  

    if event==  'height':  

                

                if 'height' in values and write_conf:    

                    #if isinstance(values.get('height_value',''), int)   

                    if get_key(scale_elements,values.get('height',''))=='manual':
                        if len(str(values.get('height_value','')))>0:
                            jcurrent_style['height']=int(values['height_value'])
                        else:
                            jcurrent_style['height']=0;    
                    else:
                        jcurrent_style['height']=get_key(scale_elements,values['height'])  

                #jcurrent_style['height'] = get_key(scale_elements,values['height']) 
    if event==  'width':  
                if 'width' in values and write_conf:    
                    if get_key(scale_elements,values.get('width',''))=='manual' :
                        if len(str(values.get('width_value','')))>0:
                           jcurrent_style['width']=int(values['width_value'])
                        else: 
                           jcurrent_style['width']=0  
                    else:
                        jcurrent_style['width']=get_key(scale_elements,values['width'] ) 

                #jcurrent_style['width'] = get_key(scale_elements,values['width']) 
    if event==  'weight':  
                jcurrent_style['weight'] = values['weight'] 
    if isstyle:
        if event==  'row':  
                    jcurrent_style['row'] = values['row'] 

        if event==  'use_as_class':  
                    jcurrent_style['use_as_class'] = values['use_as_class']                        
                
    if event==  'background_color':  
                jcurrent_style['BackgroundColor'] = values['background_color'] 

    if event==  'stroke_width':  
                jcurrent_style['StrokeWidth'] = values['stroke_width']
    
    if event==  'padding':  
                jcurrent_style['Padding'] = values['padding']

    if event==  'BackgroundColor':  
                jcurrent_style['BackgroundColor'] = values['BackgroundColor']                        

    if event==  'TextSize':  
                jcurrent_style['TextSize'] = values['TextSize'] 

    if event==  'TextColor':  
                jcurrent_style['TextColor'] = values['TextColor'] 
    if event==  'TextBold':  
                jcurrent_style['TextBold'] = values['TextBold'] 
    if event==  'TextItalic':  
                jcurrent_style['TextItalic'] = values['TextItalic'] 
    if event==  'gravity_horizontal':  
                jcurrent_style['gravity_horizontal'] = get_key(gravity_elements,values['gravity_horizontal'] )

    if event==  'gravity_vertical':  
                jcurrent_style['gravity_vertical'] = get_key(vertical_gravity_elements,values['gravity_vertical'] )

    if event==  'drawable':  
                jcurrent_style['drawable'] = values['drawable'] 
    if event==  'NumberPrecision':  
                jcurrent_style['NumberPrecision'] = values['NumberPrecision']                                                                                                                                                                                 
    if event==  'height_value':  
                jcurrent_style['height_value'] = values['height_value'] 

                if 'height' in values and write_conf:    
                    if get_key(scale_elements,values.get('height',''))=='manual' and len(values.get('height_value',''))>0:
                        jcurrent_style['height']=int(values['height_value'])
                    else:
                        jcurrent_style['height']=get_key(scale_elements,values['height'])     

    if event==  'width_value':  
                jcurrent_style['width_value'] = values['width_value']  

                if 'width' in values and write_conf:    
                    if get_key(scale_elements,values.get('width',''))=='manual' and len(values.get('width_value',''))>0:
                        jcurrent_style['width']=int(values['width_value'])
                    else:
                        jcurrent_style['width']=get_key(scale_elements,values['width'] )               
            

                
        
    update_conf()

def window_styles():
    global jcurrent_style

    headings_styles=[get_locale('template')]
    
    data_styles = update_styles(None)


    layout_styles =[[sg.Button(get_locale('add_template') ,key="btn_add_style_template"), sg.Button(get_locale('delete_template') ,key="btn_delete_style_template")],
                    [sg.Table(values=data_styles, headings=headings_styles,def_col_width=50,col_widths=[50],auto_size_columns=False,
                    
                    display_row_numbers=False,
                    justification='left',
                    num_rows=10,
                    expand_y=True,
                    expand_x=True,
                    key='StylesTable',
                    selected_row_colors='red on yellow',
                    enable_events=True,
                    
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    enable_click_events=True),
                    sg.Column([[sg.Text(get_locale('name')),sg.Input(do_not_clear=True, key='style_name',enable_events=True)],
                    [sg.Checkbox(get_locale('use_as_class') ,key='use_as_class',enable_events=True)],
                    
                    show_scale_invisible('height',jcurrent_style,get_locale('height')),
                    show_scale_invisible('width',jcurrent_style,get_locale('width')),
                    show_input('weight',jcurrent_style,get_locale('weight') ) ,
                    show_input('BackgroundColor',jcurrent_style,get_locale('background_color') ) ,
                    show_input('TextSize',jcurrent_style,get_locale('text_size') ) ,
                    show_input('TextColor',jcurrent_style,get_locale('text_color')) ,
                    show_checkbox('TextBold',jcurrent_style,get_locale('bold')),
                    show_checkbox('TextItalic',jcurrent_style,get_locale('italic')),
                    show_horizontal_gravity('gravity_horizontal',jcurrent_style,get_locale('gravity_horizontal')),
                    show_icon('drawable',jcurrent_style,get_locale('icon') ),
                    show_input('NumberPrecision',jcurrent_style,get_locale('number_decimal') ), 
                    [sg.Text(get_locale('row'),size=35)],
                    [sg.Multiline(key='row',enable_events=True, expand_x=True, expand_y=True,size=(150,20))] 
                    ])
                    
                    ]
          ]
    window_styles = sg.Window(get_locale('style_templates') ,resizable=True).Layout(layout_styles)

    window_styles.finalize()

    set_visibility_style(window_styles,jcurrent_style)

        # ------ Event Loop ------
    while True:
        s_event, s_values = window_styles.read()
            #print(event, values)
        if s_event == sg.WIN_CLOSED:
                break

        if s_event == "btn_add_style_template":    
            new_syle = {"name":get_locale('new_style_template')}
            if not 'StyleTemplates' in configuration_json['ClientConfiguration']:
                 configuration_json['ClientConfiguration']['StyleTemplates']=[]

            configuration_json['ClientConfiguration']['StyleTemplates'].append(new_syle)
            data_styles = update_styles(window_styles,True)
            window_styles['StylesTable'].update(values=data_styles)
            jcurrent_style= configuration_json['ClientConfiguration']['StyleTemplates'][len(configuration_json['ClientConfiguration']['StyleTemplates'])-1]
            #set_visibility_style(window_styles,jcurrent_style)
            window_styles['style_name'].update(jcurrent_style['name'])

            window_styles['StylesTable'].update(select_rows =[len(configuration_json['ClientConfiguration']['StyleTemplates'])-1])

            set_visibility_style(window_styles,jcurrent_style)
            update_conf()
        if s_event in ['height','width','weight','BackgroundColor','TextSize','TextColor','TextBold','TextItalic','gravity_horizontal','drawable','NumberPrecision','height_value','width_value','row','use_as_class']:
            save_style_values_event(jcurrent_style,s_event,s_values,False,True)
            set_visibility_style(window_styles,jcurrent_style)
            update_conf()
        if s_event == 'StylesTable':
            
            row_selected = s_values['StylesTable'][0]
            jcurrent_style = all_styles_list[row_selected]

            window_styles['style_name'].update(jcurrent_style['name'])
            set_visibility_style(window_styles,jcurrent_style)
            update_conf()
        if s_event=='style_name':
            jcurrent_style['name']=s_values['style_name']
            
            data_styles = update_styles(window_styles)
            window_styles['StylesTable'].update(values=data_styles)

   
    window_styles.close()  


#recognition templates functions
def set_visibility_recognition(rwindow,jcurrent_recognition,element_form=False):

    if rwindow==None:
        return

    if element_form!=True:
        rwindow['settings_name'].update('')
        rwindow['query'].update('')
        rwindow['values_list'].update('')
        rwindow['mesure_qty'].update('')
        rwindow['min_freq'].update('')
        rwindow['fmin_length'].update('')
        rwindow['max_length'].update('')
        rwindow['count_objects'].update('')
        rwindow['ReplaceO'].update('')
        rwindow['ToUpcase'].update('')

        rwindow['TypeRecognition'].update('')

        
        rwindow['control_field'].update('')
        rwindow['result_field'].update('')
        rwindow['result_var'].update('')
    
    



    if jcurrent_recognition!=None:
        if element_form!=True:
            
            rwindow['colummn_recognition'].update(visible=True) 

            rwindow['settings_name'].update(jcurrent_recognition.get('name'),disabled=False)
            rwindow['TypeRecognition'].update(get_synonym(recognition_elements,jcurrent_recognition.get('TypeRecognition')),disabled=False)
  
             
            
            rwindow['ocr_frame'].update(visible=False)
        if jcurrent_recognition.get('TypeRecognition')==None or jcurrent_recognition.get('TypeRecognition')=='':
            rwindow['recognition_frame'].update(visible=False)
        else:    
            rwindow['recognition_frame'].update(visible=True) 



        if get_key(recognition_elements,jcurrent_recognition.get('TypeRecognition'))=='Text':
            #if get_key(recognition_elements,jcurrent_recognition.get('TypeRecognition'))=='Text':
                
                
                rwindow['ocr_frame'].update(visible=True)

        q=""
        if jcurrent_recognition.get('query')!=None:
            try:
            
                q =  base64.b64decode(jcurrent_recognition.get('query').encode('utf-8')).decode('utf-8')
            except:
                q=jcurrent_recognition.get('query')

        rwindow['query'].update(q,disabled=False)
        rwindow['values_list'].update(jcurrent_recognition.get('values_list'),disabled=False)
        rwindow['mesure_qty'].update(jcurrent_recognition.get('mesure_qty'),disabled=False)
        rwindow['min_freq'].update(jcurrent_recognition.get('min_freq'),disabled=False)
        rwindow['fmin_length'].update(jcurrent_recognition.get('min_length'),disabled=False)
        rwindow['max_length'].update(jcurrent_recognition.get('max_length'),disabled=False)
        rwindow['count_objects'].update(jcurrent_recognition.get('count_objects'),disabled=False)
        rwindow['ReplaceO'].update(jcurrent_recognition.get('ReplaceO'),disabled=False)
        rwindow['ToUpcase'].update(jcurrent_recognition.get('ToUpcase'),disabled=False)
        rwindow['control_field'].update(jcurrent_recognition.get('control_field'),disabled=False)
        rwindow['result_field'].update(jcurrent_recognition.get('result_field'),disabled=False)
        rwindow['result_var'].update(jcurrent_recognition.get('result_var'),disabled=False)            

    else:
        rwindow['colummn_recognition'].update(visible=False)

        rwindow['recognition_frame'].update(visible=False)  

        if element_form!=True:    
            rwindow['settings_name'].update(disabled=True)
            rwindow['TypeRecognition'].update(disabled=True)
  
      

def update_recognition(window,SetCurrent=True):
    global jcurrent_recognition
    global all_recognition_list

    data_recognition = []


    all_recognition_list = []
    
    if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['RecognitionTemplates']:
              data_recognition.append([elem['name']])
              all_recognition_list.append(elem)

    if len(all_recognition_list)>0 and SetCurrent:
        jcurrent_recognition = all_recognition_list[0]
        set_visibility_recognition(window,jcurrent_recognition,True)

    return  data_recognition         

def save_recognition_values_event( jcurrent_recognition,event,values,element=False):
    
    if element: 
        source = values
    else:
        source = jcurrent_recognition    

    if event==  'settings_name':  
                jcurrent_recognition['name'] = values['settings_name'] 
    if event==  'TypeRecognition':  

           

        jcurrent_recognition['TypeRecognition'] = get_key(recognition_elements,source.get('TypeRecognition')) 

        if get_key(recognition_elements,jcurrent_recognition.get('TypeRecognition')) =="Number":
                jcurrent_recognition['NumberRecognition'] =True
        else:
                jcurrent_recognition['NumberRecognition'] =False    


        if  get_key(recognition_elements,source.get('TypeRecognition')) =="Date":
                jcurrent_recognition['DateRecognition'] =True  
        else:
            jcurrent_recognition['DateRecognition']=False


        if  get_key(recognition_elements,source.get('TypeRecognition')) =="PlateNumber":
                jcurrent_recognition['PlateNumberRecognition'] =True  
        else:        
            jcurrent_recognition['PlateNumberRecognition'] =False 


    if event==  'query':  
                b64=base64.b64encode(source['query'] .encode('utf-8')).decode('utf-8')
                jcurrent_recognition['query'] = b64
    elif event==  'values_list':  
                jcurrent_recognition['values_list'] = source['values_list'] 
                if 'cursor' in jcurrent_recognition:
                    jcurrent_recognition.pop("cursor")
    elif event==  'mesure_qty':  
                jcurrent_recognition['mesure_qty'] = source['mesure_qty'] 
    elif event==  'min_freq':  
                jcurrent_recognition['min_freq'] = source['min_freq'] 
    elif event==  'max_length':  
                jcurrent_recognition['max_length'] = source['max_length'] 
    elif event==  'fmin_length':  
                jcurrent_recognition['min_length'] = source['fmin_length']             
    elif event==  'count_objects':  
                jcurrent_recognition['count_objects'] = source['count_objects'] 
    elif event==  'ReplaceO':  
                jcurrent_recognition['ReplaceO'] = source['ReplaceO'] 
    elif event==  'ToUpcase':  
                jcurrent_recognition['ToUpcase'] = source['ToUpcase'] 
    elif event==  'control_field':  
                jcurrent_recognition['control_field'] = source['control_field'] 
    elif event==  'result_field':  
                jcurrent_recognition['result_field'] = source['result_field'] 
                if not 'values_list' in jcurrent_recognition:
                    if 'cursor' in jcurrent_recognition:
                            cursorstr =  jcurrent_recognition['cursor'][0]
                            cursorstr['field'] =source['result_field']
                    else:
                            jcurrent_recognition['cursor']=[]    
                            jcurrent_recognition['cursor'].append({"field":source['result_field']})

    elif event==  'result_var':  
                jcurrent_recognition['result_var'] = source['result_var'] 
                
                if not 'values_list' in jcurrent_recognition:
                    if 'cursor' in jcurrent_recognition:
                        cursorstr =  jcurrent_recognition['cursor'][0]
                        cursorstr['var'] =source['result_var']
                    else:
                        jcurrent_recognition['cursor']=[] 
                        jcurrent_recognition['cursor'].append({"var":source['result_var']})

      
def window_recognition():
    global jcurrent_recognition
    global configuration_json

    headings_recognition=[get_locale('name')]
    
    data_recognition = update_recognition(None)

    layout_recognition =[[sg.Button(get_locale('add_template'),key="btn_add_recognition_template"), sg.Button(get_locale('delete_template'),key="btn_delete_recognition_template")],
                    [sg.Table(values=data_recognition, headings=headings_recognition,def_col_width=50,col_widths=[50],auto_size_columns=False,
                    
                    display_row_numbers=False,
                    justification='left',
                    num_rows=10,
                    #alternating_row_color='lightyellow',
                    key='RecognitionTable',
                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    enable_click_events=True),
                    sg.Column([[sg.Text(get_locale('Name')),sg.Input(do_not_clear=True, key='settings_name',enable_events=True)],
                    
                    show_type_recognition('TypeRecognition',jcurrent_recognition,get_locale('type_of_recognition') ),
                    
                    [sg.Frame("Общее",[ show_input('mesure_qty',jcurrent_recognition,get_locale('number_of_measurements') ) ,
                    show_input('min_freq',jcurrent_recognition,get_locale('minimum_frequency')) ,
                    show_input('fmin_length',jcurrent_recognition,get_locale('minimum_length')) ,
                    show_input('max_length',jcurrent_recognition,get_locale('maximum_length')) ,
                    show_input('count_objects',jcurrent_recognition,get_locale('number_of_objects')) ],key='recognition_frame')],
                    
                    [sg.Frame("OCR",[
                         show_input('query',jcurrent_recognition,get_locale('sql_query')) ,
                    show_input('values_list',jcurrent_recognition,get_locale('list_of_values')) ,
                    show_checkbox('ReplaceO',jcurrent_recognition,get_locale('replase_zero')),
                    show_checkbox('ToUpcase',jcurrent_recognition,get_locale('convert_to_uppercase')),
                    
                    show_input('control_field',jcurrent_recognition,get_locale('validated_field')),
                    show_input('result_field',jcurrent_recognition,get_locale('table_SQL_field')),
                    show_input('result_var',jcurrent_recognition,get_locale('result_variable'))  
                    ],key="ocr_frame")],
                   
                    
                    ],key='colummn_recognition')
                    
                    ],
          ]
    window_recognition = sg.Window(get_locale('recognition_templates'),resizable=True).Layout(layout_recognition)

    window_recognition.finalize()

    set_visibility_recognition(window_recognition,jcurrent_recognition)

        # ------ Event Loop ------
    while True:
        s_event, s_values = window_recognition.read()
            #print(event, values)
        if s_event == sg.WIN_CLOSED:
                break

        if s_event == "btn_add_recognition_template":    
            new_rec = {"name":get_locale('new_recognition_template') }
            if not 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
                 configuration_json['ClientConfiguration']['RecognitionTemplates']=[]

            configuration_json['ClientConfiguration']['RecognitionTemplates'].append(new_rec)
            data_recognition = update_recognition(window_recognition,True)
            window_recognition['RecognitionTable'].update(values=data_recognition)
            jcurrent_recognition= configuration_json['ClientConfiguration']['RecognitionTemplates'][len(configuration_json['ClientConfiguration']['RecognitionTemplates'])-1]
            
            window_recognition['settings_name'].update(jcurrent_recognition['name'])

            window_recognition['RecognitionTable'].update(select_rows =[len(configuration_json['ClientConfiguration']['RecognitionTemplates'])-1])

            set_visibility_recognition(window_recognition,jcurrent_recognition,True)

            update_conf()

        if s_event in ['TypeRecognition','query','values_list','mesure_qty','min_freq','fmin_length','max_length','count_objects','ReplaceO','ToUpcase','control_field','result_field','result_var']:
            save_recognition_values_event(jcurrent_recognition,s_event,s_values,True)
            set_visibility_recognition(window_recognition,jcurrent_recognition,True)
        if s_event == 'RecognitionTable':
            
            row_selected = s_values['RecognitionTable'][0]
            jcurrent_recognition = all_recognition_list[row_selected]

            window_recognition['settings_name'].update(jcurrent_recognition['name'])
            set_visibility_recognition(window_recognition,jcurrent_recognition,True)
        if s_event=='settings_name':
            jcurrent_recognition['name']=s_values['settings_name']
            
            data_recognition = update_recognition(window_recognition,False)
            window_recognition['RecognitionTable'].update(values=data_recognition)

        if jcurrent_recognition.get('name','')!='':
            for process in configuration_json['ClientConfiguration']['Processes']:
                if process.get("type")=="CVOperation":
                    for step in process['CVFrames']:
                        if step.get("RecognitionTemplate")==jcurrent_recognition['name']:
                            step['CVRecognitionSettings']=json.dumps(jcurrent_recognition,ensure_ascii=False)
                else:            
                    for oper in process['Operations']:
                        if 'Elements' in oper:
                            for el in oper['Elements']:
                                if el.get("RecognitionTemplate")==jcurrent_recognition['name']:
                                    el['VisionSettings']=json.dumps(jcurrent_recognition,ensure_ascii=False)
   
    window_recognition.close()  

#screen layout functions
def save_layout_line(elements,e_values,is_layout):
    global window

    if is_layout:
        elements['type']=get_key(layout_elements,e_values.get('type',''))
    else:    
        elements['type']=get_key(screen_elements,e_values.get('type','')) 

    if 'variable' in e_values:
                    elements['Variable']=e_values['variable']
    if  'value' in e_values:   
                    elements['Value']=e_values['value']
    if  'background_color' in e_values:   
                    elements['BackgroundColor']=e_values['background_color']

    if  'stroke_width' in e_values:   
                    elements['StrokeWidth']=e_values['stroke_width']

    if  'padding' in e_values:   
                    elements['Padding']=e_values['padding']


    if 'orientation' in e_values:
                    elements['orientation']=get_key(orientation_elements,e_values['orientation'])
    if 'weight' in e_values:
                    elements['weight']=e_values['weight']    

    if 'height' in e_values:    
        if get_key(scale_elements,e_values.get('height',''))=='manual' and len(e_values.get('height_value',''))>0:
            elements['height']=int(e_values['height_value'])
        else:
            elements['height']=get_key(scale_elements,e_values['height'])     

    if 'width' in e_values:    
        if get_key(scale_elements,e_values.get('width',''))=='manual' and len(e_values.get('width_value',''))>0:
            elements['width']=int(e_values['width_value'])
        else:
            elements['width']=get_key(scale_elements,e_values['width'] )    


    load_screen_lines()
    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])

def edit_element_form(row,elements,is_layout=False):                   
        global window

        editwindow =None

        if row==None:
            editwindow = show_edit(get_locale('select_type'),None,elements,is_layout) 
        else:      
            
            editwindow = show_edit(elements['type'],None,elements,is_layout) 

        #editwindow.finalize()

        #if elements['type']!='LinearLayout':
        #    set_visibility_style(editwindow,elements,True) 
        
        
        # ------ Event Loop ------
        while True:
            e_event, e_values = editwindow.read()
            #print(event, values)
            if e_event == sg.WIN_CLOSED:
                break

            if e_event == 'btn_save_layout_line':
                
                save_layout_line(elements,e_values,is_layout)
                
                
                break

            if e_event == 'btn_get_layout_base':
                
                pyperclip.copy(json.dumps(jcurrent_screen_line,ensure_ascii=False,indent=4, separators=(',', ': ')).replace("true","True").replace("false","False"))
                #spam = pyperclip.paste()
                                
                   

            if e_event == 'btn_delete_screen_line':

                jcurrent_screen['Elements'].remove(jcurrent_screen_line)
                #update_code(configuration_json)
                update_conf()
                load_screen_lines(False,True)
                window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])
                break
            if e_event == 'btn_add_layout_line':
                save_layout_line(elements,e_values,is_layout)
                new_element = {"type":"TextView","height":"wrap_content","width":"wrap_content","weight":0}

                elements['Elements'].append(new_element)
                edit_element_form(None,elements['Elements'][-1],True) 
               
                data_container_lines = get_data_container_lines(elements)
                editwindow['LayoutTable'].update(values=data_container_lines[1:][:])

            if e_event == 'btn_insert_from_clipboard_layout_line':
                save_layout_line(elements,e_values,is_layout)
                try:
                    new_element = json.loads(pyperclip.paste().replace("True","true").replace("False","false"))  

                    elements['Elements'].append(new_element)
                                
                    data_container_lines = get_data_container_lines(elements)
                    editwindow['LayoutTable'].update(values=data_container_lines[1:][:])
                except Exception as e:  # This is the correct syntax
                                sg.popup('Wrong clipboard content',  e,   grab_anywhere=True)


            if e_event == 'btn_up_layout_line':
                
                if len(e_values['LayoutTable'])>0:
                    current_position = e_values['LayoutTable'][0]
                    if current_position>0: 
                        elements['Elements'].insert(current_position-1,elements['Elements'].pop(current_position))
               
                data_container_lines = get_data_container_lines(elements)
                editwindow['LayoutTable'].update(values=data_container_lines[1:][:])  

            if e_event == 'btn_delete_layout_line':
                
                if len(e_values['LayoutTable'])>0:
                    current_position = e_values['LayoutTable'][0]
                    
                    elements['Elements'].pop(current_position)
               
                data_container_lines = get_data_container_lines(elements)
                editwindow['LayoutTable'].update(values=data_container_lines[1:][:])      

            if e_event == 'btn_down_layout_line':
                
                if len(e_values['LayoutTable'])>0:
                    current_position = e_values['LayoutTable'][0]
                    if current_position<len(elements['Elements']): 
                        elements['Elements'].insert(current_position+1,elements['Elements'].pop(current_position))
               
                data_container_lines = get_data_container_lines(elements)
                editwindow['LayoutTable'].update(values=data_container_lines[1:][:])   

            if e_event == 'btn_copy_layout_line':
                
                if len(e_values['LayoutTable'])>0:
                    current_position = e_values['LayoutTable'][0]
                    if current_position<len(elements['Elements']): 
                        current_element = elements['Elements'][current_position]
                        elements['Elements'].append(copy.deepcopy(current_element))
               
                data_container_lines = get_data_container_lines(elements)
                editwindow['LayoutTable'].update(values=data_container_lines[1:][:])            

            if e_event == 'height':
               save_style_values_event(elements,e_event,e_values,True)
               if  e_values['height'] ==get_synonym(scale_elements,'manual'):
                if not 'height_value' in e_values:
                    e_values['height_value']=0   
                elements['height']=e_values['height_value']
               else:   
                elements['height']=get_key(scale_elements,e_values['height']) 
               editwindow =show_edit(get_key(screen_elements,e_values['type']),editwindow,elements,is_layout)
            if e_event == 'width':
                
               if  e_values['width'] ==get_synonym(scale_elements,'manual'):
                if not 'width_value' in e_values:
                    e_values['width_value']=0
                elements['width']=e_values['width_value']
               else:   
                elements['width']=get_key(scale_elements,e_values['width']) 
               editwindow =show_edit(get_key(screen_elements,e_values['type']),editwindow,elements,is_layout)    
            if e_event == 'type':
                
                if get_key(screen_elements,e_values['type'])=='LinearLayout' or  get_key(screen_elements,e_values['type'])=='Tabs' or  get_key(screen_elements,e_values['type'])=='Tab':
                    if not 'weight' in elements:
                        elements['weight']=0
                    if not 'height' in elements:
                        elements['height']='wrap_content'
                    if not 'width' in elements:
                        elements['width']='wrap_content'
                    if not 'orientation' in elements:
                        elements['orientation']='vertical'    
                else:
                    elements['type']=get_key(layout_elements,e_values['type']) 
                #    is_layout=True
                #else:        
                #    is_layout=False

                editwindow =show_edit(get_key(screen_elements,e_values['type']),editwindow,elements,is_layout)
                 
                if not(get_key(screen_elements,e_values['type'])=='LinearLayout' or  get_key(screen_elements,e_values['type'])=='Tabs' or  get_key(screen_elements,e_values['type'])=='Tab'): 
                    elements['type']=get_key(layout_elements,e_values['type'])

                if get_key(screen_elements,e_values['type'])=='Vision':
                    elements['type']='Vision'  

                update_conf()
            if e_event in ['height','width','weight','BackgroundColor','TextSize','TextColor','TextBold','TextItalic','gravity_horizontal','gravity_vertical','drawable','NumberPrecision','height_value','width_value','value','variable','background_color','stroke_width','padding']:
                save_style_values_event(elements,e_event,e_values,True)
                #set_visibility_style(editwindow,elements,True,elements.get('type')=='LinearLayout')
                update_conf()
            if e_event=='recognition_type':
                #Временное решение
                if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
                
                
                
                    elements["VisionSettings"]=json.dumps(next(item for item in configuration_json['ClientConfiguration']['RecognitionTemplates'] if item["name"] == e_values['recognition_type']),ensure_ascii=False,indent=4, separators=(',', ': '))
                    elements["RecognitionTemplate"]=  e_values['recognition_type']
            if e_event == 'LayoutTable':
                #print(e_event)
                if len(e_values['LayoutTable'])>0:
                    row_selected = e_values['LayoutTable'][0]
                    jcurrent_layout = elements['Elements'][row_selected] 
                    edit_element_form(row_selected,jcurrent_layout,True) 

                    data_container_lines = get_data_container_lines(elements)
                    editwindow['LayoutTable'].update(values=data_container_lines[1:][:])

                    update_conf()    
            if  e_event == 'style_name':
                elements['style_name']=e_values['style_name']

                jstyle=None
                for st in  configuration_json['ClientConfiguration']['StyleTemplates']:
                    if st['name']==e_values['style_name']:
                        jstyle=st
                        break
                css=False    
                if "use_as_class" in jstyle:
                  if jstyle.get("use_as_class")==True:
                    css=True
                
                if css:
                    elements['style_name']=e_values['style_name']
                    elements['style_class']=e_values['style_name']
                
                else:              
                    for key in jstyle.keys():
                        save_style_values_event(elements,key,jstyle,True)

                editwindow =show_edit(get_key(screen_elements,e_values['type']),editwindow,elements,is_layout)

                update_conf()

        load_screen_lines()
        window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])     

        editwindow.close()  


def edit_common_handler_form(row,elements,isCV=False):                   
        global window

        captions_event=captions_common_event_elements
        
       
        if not  row ==None:
            
            editwindowh = sg.Window(get_locale("handler"),icon='ic_32.ico',modal=True).Layout([
    [sg.Text(get_locale("alias") ,size=35),sg.Input(do_not_clear=True, key='handlers_alias',enable_events=True,default_text=elements.get('alias',''),size=125)],            
    [sg.Text(get_locale("event"),size=35),sg.Combo(captions_event,key='handlers_event',enable_events=True,default_value=get_synonym(common_event_elements,elements.get('event','')),size=125)],            
    [sg.Text(get_locale("listener"),size=35),sg.Input(do_not_clear=True, key='handlers_listener',enable_events=True,default_text=elements.get('listener',''))],
    [sg.Text(get_locale("action"),size=35),sg.Combo(captions_action_elements,key='handlers_action',enable_events=True,default_value=get_synonym(action_elements,elements.get('action','')),size=125)],
    
    [sg.Text(get_locale("handlertype"),size=35),sg.Combo(captions_handler_elements,key='handlers_type',enable_events=True,default_value=get_synonym(handler_elements,elements.get('type','')),size=125)],
    [sg.Text(get_locale("handlersmethod") ,size=35),sg.Input(do_not_clear=True, key='handlers_method',enable_events=True,default_text=elements.get('method',''),size=125)],
    [sg.Button(get_locale('edit_post_execute'),key='btn_pe')],
    [sg.Text(get_locale("postExecute"),size=35),sg.Input(do_not_clear=True, key='handlers_postExecute',enable_events=True,default_text=elements.get('postExecute',''),size=125)],
    [sg.Button(get_locale('save'),key='btn_save')]
     
    ]              )
    
        else:
            editwindowh = sg.Window(get_locale("handler"),icon='ic_32.ico',modal=True).Layout([
            [sg.Text(get_locale("handlersalias") ,size=35),sg.Input(do_not_clear=True, key='handlers_alias',enable_events=True,size=125)],    
            [sg.Text(get_locale("event"),size=35),sg.Combo(captions_event,key='handlers_event',enable_events=True,size=125)],
            [sg.Text(get_locale("action"),size=35),sg.Combo(captions_action_elements,key='handlers_action',enable_events=True,size=125)],
            [sg.Text(get_locale("listener") ,size=35),sg.Input(do_not_clear=True, key='handlers_listener',enable_events=True,default_text=elements.get('listener',''),size=125)],
            [sg.Text(get_locale("handlertype"),size=35),sg.Combo(captions_handler_elements,key='handlers_type',enable_events=True,size=125)],
            [sg.Text(get_locale("handlersmetod") ,size=35),sg.Input(do_not_clear=True, key='handlers_method',enable_events=True,size=125)],
            [sg.Button(get_locale('edit_post_execute'),key='btn_pe')],
            [sg.Text(get_locale("postExecute"),size=35),sg.Input(do_not_clear=True, key='handlers_postExecute',enable_events=True,size=125)],
            [sg.Button(get_locale('save'),key='btn_save')]
     
    ]              )


        # ------ Event Loop ------
        while True:
            e_event, e_values = editwindowh.read()
            #print(event, values)
            if e_event == sg.WIN_CLOSED:
                break

    
            if e_event == 'handlers_action':
                elements['action']=get_key(action_elements,e_values['handlers_action'])  
                update_conf()
            if e_event == 'handlers_type':
                elements['type']=get_key(handler_elements,e_values['handlers_type'])
                update_conf()
            if e_event == 'handlers_event':
                  
                elements['event']=get_key(common_event_elements,e_values['handlers_event'])      
                update_conf()
            if e_event == 'handlers_listener':
                elements['listener']=e_values['handlers_listener']      
                update_conf()
            if e_event == 'handlers_alias':
                elements['alias']=e_values['handlers_alias']      
                update_conf()

            if e_event == 'handlers_method':
                elements['method']=e_values['handlers_method']      
                update_conf()    
            if e_event == 'handlers_postExecute':
                elements['postExecute']=e_values['handlers_postExecute'] 
                update_conf()
            if e_event == 'btn_save':         
                break
            if e_event=='btn_pe':
                if elements.get('postExecute','')=='' :
                    dpe = {}
                    edit_handler_form(None,dpe) 
                    pe=[dpe]
                         
                else:   
                    pe =json.loads(elements.get('postExecute')) 
                    edit_handler_form(editwindowh,pe[0])      
                
                elements['postExecute']=json.dumps(pe)
                update_conf()
                editwindowh['handlers_postExecute'].update(elements['postExecute'])


           
        load_common_handlers()
          
        window['CommonHandlersTable'].update(values=data_common_handlers[1:][:])     

        editwindowh.Close() 

def edit_handler_form(row,elements,isCV=False):                   
        global window

        if isCV:
            captions_event=captions_event_elements_cv
        else:
            captions_event=captions_event_elements
        
       
        if not  row ==None:
            
            editwindowh = sg.Window(get_locale("handler"),icon='ic_32.ico',modal=True).Layout([
    [sg.Text(get_locale("event"),size=35),sg.Combo(captions_event,key='handlers_event',enable_events=True,default_value=get_synonym(event_elements,elements.get('event','')),size=125)],            
    [sg.Text(get_locale("listener"),size=35),sg.Input(do_not_clear=True, key='handlers_listener',enable_events=True,default_text=elements.get('listener',''))],
    [sg.Text(get_locale("action"),size=35),sg.Combo(captions_action_elements,key='handlers_action',enable_events=True,default_value=get_synonym(action_elements,elements.get('action','')),size=125)],
    
    [sg.Text(get_locale("handlertype"),size=35),sg.Combo(captions_handler_elements,key='handlers_type',enable_events=True,default_value=get_synonym(handler_elements,elements.get('type','')),size=125)],
    [sg.Text(get_locale("handlersmethod") ,size=35),sg.Input(do_not_clear=True, key='handlers_method',enable_events=True,default_text=elements.get('method',''),size=125)],
    [sg.Button(get_locale('edit_post_execute'),key='btn_pe')],
    [sg.Text(get_locale("postExecute"),size=35),sg.Input(do_not_clear=True, key='handlers_postExecute',enable_events=True,default_text=elements.get('postExecute',''),size=125)],
    [sg.Button(get_locale('save'),key='btn_save')]
     
    ]              )
    
        else:
            editwindowh = sg.Window(get_locale("handler"),icon='ic_32.ico',modal=True).Layout([
            [sg.Text(get_locale("event"),size=35),sg.Combo(captions_event,key='handlers_event',enable_events=True,size=125)],
            [sg.Text(get_locale("action"),size=35),sg.Combo(captions_action_elements,key='handlers_action',enable_events=True,size=125)],
            [sg.Text(get_locale("listener") ,size=35),sg.Input(do_not_clear=True, key='handlers_listener',enable_events=True,default_text=elements.get('listener',''),size=125)],
            [sg.Text(get_locale("handlertype"),size=35),sg.Combo(captions_handler_elements,key='handlers_type',enable_events=True,size=125)],
            [sg.Text(get_locale("handlersmetod") ,size=35),sg.Input(do_not_clear=True, key='handlers_method',enable_events=True,size=125)],
            [sg.Button(get_locale('edit_post_execute'),key='btn_pe')],
            [sg.Text(get_locale("postExecute"),size=35),sg.Input(do_not_clear=True, key='handlers_postExecute',enable_events=True,size=125)],
            [sg.Button(get_locale('save'),key='btn_save')]
     
    ]              )


        # ------ Event Loop ------
        while True:
            e_event, e_values = editwindowh.read()
            #print(event, values)
            if e_event == sg.WIN_CLOSED:
                break

    
            if e_event == 'handlers_action':
                elements['action']=get_key(action_elements,e_values['handlers_action'])  
                update_conf()
            if e_event == 'handlers_type':
                elements['type']=get_key(handler_elements,e_values['handlers_type'])
                update_conf()
            if e_event == 'handlers_event':
                if isCV:
                    elements['event']=get_key(event_elements_cv,e_values['handlers_event'])      
                else:    
                    elements['event']=get_key(event_elements,e_values['handlers_event'])      
                update_conf()
            if e_event == 'handlers_listener':
                elements['listener']=e_values['handlers_listener']      
                update_conf()
            if e_event == 'handlers_method':
                elements['method']=e_values['handlers_method']      
                update_conf()    
            if e_event == 'handlers_postExecute':
                elements['postExecute']=e_values['handlers_postExecute'] 
                update_conf()
            if e_event == 'btn_save':         
                break
            if e_event=='btn_pe':
                if elements.get('postExecute','')=='' :
                    dpe = {}
                    edit_handler_form(None,dpe) 
                    pe=[dpe]
                         
                else:   
                    pe =json.loads(elements.get('postExecute')) 
                    edit_handler_form(editwindowh,pe[0])      
                
                elements['postExecute']=json.dumps(pe)
                update_conf()
                editwindowh['handlers_postExecute'].update(elements['postExecute'])


           
        load_screen_handlers()
        if isCV:
            window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])     
        else:    
            window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])     

        editwindowh.Close()          

#SimpleUI configuration initialization
def load_OfflineOnCreate():
    global data_sql_on_start
    data_sql_on_start=[['']]
    if 'OfflineOnCreate' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['OfflineOnCreate']:
            data_sql_on_start.append([elem['Query']])
    window['sql_on_start_table'].update(values=data_sql_on_start[1:][:])

def load_MainMenu():
    global data_mainmenu
    data_mainmenu=[['','','','']]
    if 'MainMenu' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['MainMenu']:
            data_mainmenu.append([elem['MenuTitle'],elem['MenuItem'],elem['MenuId'],elem['MenuTop']])
    window['mainmenu_table'].update(values=data_mainmenu[1:][:])

def load_timers():
    global data_timers
    data_timers=[['','','','']]
    if 'PyTimerTask' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['PyTimerTask']:
            data_timers.append([elem['PyTimerTaskKey'],elem['PyTimerTaskPeriod'],elem['PyTimerTaskBuilIn'],elem['PyTimerTaskDef']])
    window['timers_table'].update(values=data_timers[1:][:])   

def load_pyfiles():
    global data_pyfiles
    global data_pyfilenames
    global current_uid
    
    data_pyfiles=[['','','']]
    pyfiles_settings = []

    if 'PyFiles' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['PyFiles']:
            
            filename_string = next((x for x in data_pyfilenames if x['key'] == elem['PyFileKey']), None) 
            filename=''
            if not filename_string ==None:
                filename=filename_string['filename']
            data_pyfiles.append([elem['PyFileKey'],filename,elem['PyFileData']])
            pyfiles_settings.append({"alias":elem['PyFileKey'],"filename":filename})

    window['pyfiles_table'].update(values=data_pyfiles[1:][:])   
    settings_global.set("handlers_list"+current_uid, json.dumps(pyfiles_settings))
    settings_global.save()

def load_mediafiles():
    global data_mediafiles
    data_mediafiles=[['','']]
    if 'Mediafile' in configuration_json['ClientConfiguration']:
        for elem in configuration_json['ClientConfiguration']['Mediafile']:
            data_mediafiles.append([elem['MediafileKey'],elem['MediafileData']])
    window['mediafiles_table'].update(values=data_mediafiles[1:][:])            

def init_configuration(window):
    global data_sql_on_start
    
    #for process_elem in configuration_json['ClientConfiguration']['Processes']:
            # if process_elem['type'] =="Process":
            #     processname=process_elem['ProcessName']
            #     for screen_elem in process_elem['Operations']:
            #         screenname = screen_elem['Name']
            #         update_code(False,processname,screenname,"OnCreate",screen_elem['PythonOnCreate'],screen_elem)
            #         update_code(False,processname,screenname,'OnInput',screen_elem['PythonOnInput'],screen_elem)
                    
            # elif process_elem['type'] =="CVOperation":
            #     processname=process_elem['CVOperationName']
            #     for step_elem in process_elem['CVFrames']:
            #         stepname = step_elem['Name']
            #         update_code(False,processname,stepname,'OnCreate',step_elem['CVFramePythonOnCreate'],screen_elem)
            #         update_code(False,processname,stepname,'OnNewObject',step_elem['CVFramePythonOnNewObject'],screen_elem)
            #         update_code(False,processname,stepname,'Action',step_elem['CVFramePythonAction'],screen_elem)
            #         update_code(False,processname,stepname,'OnTouch',step_elem['CVFramePythonOnTouch'],screen_elem)



    load_processes(True)
    window['ConfigurationTable'].update(values=data[1:][:])
    if(len(data[1:][:])>0):
        window['ConfigurationTable'].update(select_rows =[0])

    load_screens(True)
    window['ScreensTable'].update(values=data_screens[1:][:]) 
    if(len(data_screens[1:][:])>0):
        window['ScreensTable'].update(select_rows =[0])
       
    load_screen_lines(False,True)
    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 
    if(len(data_screen_lines[1:][:])>0):    
        window['ScreenLinesTable'].update(select_rows =[0])

    load_screen_handlers()

    load_OfflineOnCreate()
    load_MainMenu() 
    load_timers()
    #load_pyfiles()
    load_mediafiles()
    load_common_handlers()

    window['CommonHandlersTable'].update(values=data_common_handlers[1:][:])

def read_handlers_file(filename):
    
    global configuration_json

    data=''

    if len(filename)>0:
        with open(filename, 'r',encoding='utf-8') as file:
            data = file.read()

        base64file  = base64.b64encode(data.encode('utf-8')).decode('utf-8')   

        configuration_json['ClientConfiguration']['PyHandlers'] =base64file

def save_screen_values(values):
    global jcurrent_screen
    if jcurrent_screen['type']=='Operation':

            #update_code(False,jcurrent_process['ProcessName'],jcurrent_screen['Name'],"OnCreate",screen_elem['PythonOnCreate'],jcurrent_screen)
            #update_code(False,jcurrent_process['ProcessName'],jcurrent_screen['Name'],'OnInput',screen_elem['PythonOnInput'],jcurrent_screen)

            jcurrent_screen['Name']= values['screen_name']

            jcurrent_screen['Timer'] = values['cb_screen_timer'] 
            jcurrent_screen['hideToolBarScreen'] = values['cb_screen_hide_bottom_bar'] 
            jcurrent_screen['noScroll'] = values['cb_screen_hide_bottom_bar'] 
            jcurrent_screen['cb_screen_hide_toolbar'] = values['cb_screen_no_scroll'] 
            jcurrent_screen['hideToolBarScreen'] = values['cb_screen_hide_toolbar'] 
            jcurrent_screen['noConfirmation'] = values['cb_screen_no_confirmation'] 
            jcurrent_screen['handleKeyUp'] = values['cb_screen_keyboard'] 

            jcurrent_screen['DefOnlineOnCreate'] = values['screen_def_oncreate']  
            jcurrent_screen['DefOnlineOnAfterCreate'] = values['screen_def_onaftercreate']  
            jcurrent_screen['DefOnlineOnInput'] = values['screen_def_oninput'] 

            jcurrent_screen['DefOnCreate'] = values['screen_defpython_oncreate']  
            jcurrent_screen['DefOnAfterCreate'] = values['screen_defpython_onaftercreate']  
            jcurrent_screen['DefOnInput'] = values['screen_defpython_oninput']  

                    
            jcurrent_screen['onlineOnStart']=len(jcurrent_screen['DefOnlineOnCreate'])>0
            jcurrent_screen['onlineOnAfterStart']=len(jcurrent_screen['DefOnlineOnAfterCreate'])>0
            jcurrent_screen['onlineOnInput']=len(jcurrent_screen['DefOnlineOnInput'])>0
            jcurrent_screen['send_when_opened']=len(jcurrent_screen.get('DefOnlineOnCreate',''))>0 or len(jcurrent_screen.get('DefOnCreate',''))>0
            jcurrent_screen['send_after_opened']=len(jcurrent_screen.get('DefOnlineOnAfterCreate',''))>0 or len(jcurrent_screen.get('DefOnAfterCreate',''))>0
            

            load_screens()
            window['ScreensTable'].update(values=data_screens[1:][:])   
    elif  jcurrent_screen['type']=='CVFrame':
             jcurrent_screen['CVDetector'] = get_key(detector_elements,values['CVFrame_detector'])
             jcurrent_screen['Name']= values['step_name']

             jcurrent_screen['CVActionButtons'] = values['CVActionButtons']   
             jcurrent_screen['CVAction'] = values['CVAction']   
             jcurrent_screen['CVInfo'] = values['CVInfo']   
             jcurrent_screen['CVCameraDevice'] = get_key(camera_mode_elements,values['CVCameraDevice'])   
             jcurrent_screen['CVMode'] = get_key(visual_mode_elements,values['CVMode'])   
             jcurrent_screen['CVResolution'] = values['CVResolution']   
             jcurrent_screen['CVMask'] = values['CVMask']   

             jcurrent_screen['CVDetectorMode'] = get_key(detector_mode_elements,values['CVDetectorMode'])   
   
             jcurrent_screen['CVFrameOnlineOnCreate'] = values['CVFrameOnlineOnCreate']     
             jcurrent_screen['CVFrameOnlineOnNewObject'] = values['CVFrameOnlineOnNewObject']  
             jcurrent_screen['CVFrameOnlineAction'] = values['CVFrameOnlineAction']  
             jcurrent_screen['CVFrameOnlineOnTouch'] = values['CVFrameOnlineOnTouch']  

             jcurrent_screen['CVFrameDefOnCreate'] = values['CVFrameDefOnCreate']     
             jcurrent_screen['CVFrameDefOnNewObject'] = values['CVFrameDefOnNewObject']  
             jcurrent_screen['CVFrameDefAction'] = values['CVFrameDefAction']  
             jcurrent_screen['CVFrameDefOnTouch'] = values['CVFrameDefOnTouch']  

             if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
                 
                    jcurrent_screen["CVRecognitionSettings"]=json.dumps(next(item for item in configuration_json['ClientConfiguration']['RecognitionTemplates'] if item["name"] == values['cvrecognition_type']),ensure_ascii=False,indent=4, separators=(',', ': '))
                    jcurrent_screen["RecognitionTemplate"]=  values['cvrecognition_type']


          
             load_cvsteps()
             window['ScreensTable'].update(values=data_screens[1:][:]) 
    update_conf()         

def save_screen_values_event(event,values):
    global jcurrent_screen
    if jcurrent_screen['type']=='Operation':

            if event==  'screen_name':         
                jcurrent_screen['Name']= values['screen_name']
                load_screens()
                window['ScreensTable'].update(values=data_screens[1:][:])   

            if event==  'cb_screen_timer':  
                jcurrent_screen['Timer'] = values['cb_screen_timer'] 

            if event==  'cb_screen_hide_bottom_bar':      
                jcurrent_screen['hideBottomBarScreen'] = values['cb_screen_hide_bottom_bar'] 
            if event==  'cb_screen_no_scroll':  
                jcurrent_screen['noScroll'] = values['cb_screen_no_scroll'] 
            if event==  'cb_screen_hide_toolbar':  
                jcurrent_screen['hideToolBarScreen'] = values['cb_screen_hide_toolbar'] 
            if event==  'cb_screen_no_confirmation':  
                jcurrent_screen['noConfirmation'] = values['cb_screen_no_confirmation'] 
            if event==  'cb_screen_keyboard':  
                jcurrent_screen['handleKeyUp'] = values['cb_screen_keyboard'] 
            if event==  'screen_def_oncreate':  
                jcurrent_screen['DefOnlineOnCreate'] = values['screen_def_oncreate'] 
                jcurrent_screen['onlineOnStart']=len(jcurrent_screen['DefOnlineOnCreate'])>0 
                jcurrent_screen['send_when_opened']=len(jcurrent_screen.get('DefOnlineOnCreate',''))>0 or len(jcurrent_screen.get('DefOnCreate',''))>0
            if event==  'screen_def_onaftercreate':  
                jcurrent_screen['DefOnlineOnAfterCreate'] = values['screen_def_onaftercreate'] 
                jcurrent_screen['onlineOnAfterStart']=len(jcurrent_screen['DefOnlineOnAfterCreate'])>0 
                jcurrent_screen['send_after_opened']=len(jcurrent_screen.get('DefOnlineOnAfterCreate',''))>0 or len(jcurrent_screen.get('DefOnAfterCreate',''))>0    

            if event==  'screen_def_oninput':  
                jcurrent_screen['DefOnlineOnInput'] = values['screen_def_oninput'] 
                jcurrent_screen['onlineOnInput']=len(jcurrent_screen['DefOnlineOnInput'])>0 
           
            if event==  'screen_defpython_oncreate':  
                jcurrent_screen['DefOnCreate'] = values['screen_defpython_oncreate'] 
                jcurrent_screen['send_when_opened']=len(jcurrent_screen.get('DefOnlineOnCreate',''))>0 or len(jcurrent_screen.get('DefOnCreate',''))>0

            if event==  'screen_defpython_onaftercreate':  
                jcurrent_screen['DefOnAfterCreate'] = values['screen_defpython_onaftercreate'] 
                jcurrent_screen['send_after_opened']=len(jcurrent_screen.get('DefOnlineOnAfterCreate',''))>0 or len(jcurrent_screen.get('DefOnAfterCreate',''))>0    

            if event==  'screen_defpython_oninput':  
                jcurrent_screen['DefOnInput'] = values['screen_defpython_oninput'] 
               
                
                 
 
            
    elif  jcurrent_screen['type']=='CVFrame':
             if event==  'CVFrame_detector':   
                jcurrent_screen['CVDetector'] = get_key(detector_elements,values['CVFrame_detector'])
             if event==  'step_name':
                jcurrent_screen['Name']= values['step_name']
                load_cvsteps()
                window['ScreensTable'].update(values=data_screens[1:][:])    
             if event==  'CVActionButtons':   
                jcurrent_screen['CVActionButtons'] = values['CVActionButtons']   
             if event==  'CVAction':
                jcurrent_screen['CVAction'] = values['CVAction']   
             if event==  'CVInfo':
                jcurrent_screen['CVInfo'] = values['CVInfo']   
             if event==  'CVCameraDevice':
                jcurrent_screen['CVCameraDevice'] = get_key(camera_mode_elements,values['CVCameraDevice'])   
             if event==  'CVMode':
                jcurrent_screen['CVMode'] = get_key(visual_mode_elements,values['CVMode'])   
             if event==  'CVResolution':
                jcurrent_screen['CVResolution'] = values['CVResolution']   
             if event==  'CVMask':
                jcurrent_screen['CVMask'] = values['CVMask']      
             if event==  'CVDetectorMode':
                jcurrent_screen['CVDetectorMode'] = get_key(detector_mode_elements,values['CVDetectorMode'])   
             if event==  'CVFrameOnlineOnCreate':   
                jcurrent_screen['CVFrameOnlineOnCreate'] = values['CVFrameOnlineOnCreate']     
             if event==  'CVFrameOnlineOnNewObject':
                jcurrent_screen['CVFrameOnlineOnNewObject'] = values['CVFrameOnlineOnNewObject']  
             if event==  'CVFrameOnlineAction':
                jcurrent_screen['CVFrameOnlineAction'] = values['CVFrameOnlineAction']  
             if event==  'CVFrameOnlineOnTouch':
                jcurrent_screen['CVFrameOnlineOnTouch'] = values['CVFrameOnlineOnTouch']  

             if event==  'CVFrameDefOnCreate':   
                jcurrent_screen['CVFrameDefOnCreate'] = values['CVFrameDefOnCreate']     
             if event==  'CVFrameDefOnNewObject':
                jcurrent_screen['CVFrameDefOnNewObject'] = values['CVFrameDefOnNewObject']  
             if event==  'CVFrameDefAction':
                jcurrent_screen['CVFrameDefAction'] = values['CVFrameDefAction']  
             if event==  'CVFrameDefOnTouch':
                jcurrent_screen['CVFrameDefOnTouch'] = values['CVFrameDefOnTouch']     


             if event==  'cvrecognition_type':   
                if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
                 
                    jcurrent_screen["CVRecognitionSettings"]=json.dumps(next(item for item in configuration_json['ClientConfiguration']['RecognitionTemplates'] if item["name"] == values['cvrecognition_type']),ensure_ascii=False,indent=4, separators=(',', ': '))
                    jcurrent_screen["RecognitionTemplate"]=  values['cvrecognition_type']
   

    update_conf()

def write_cofiguration_property(event,value,values):
    
    if not 'ConfigurationSettings' in configuration_json['ClientConfiguration']: 
        configuration_json['ClientConfiguration']['ConfigurationSettings']={}
        jconfiguration_settings = configuration_json['ClientConfiguration']['ConfigurationSettings']
    else:
        jconfiguration_settings = configuration_json['ClientConfiguration']['ConfigurationSettings']

    if type(jconfiguration_settings)== str:    
        jconfiguration_settings = json.loads(jconfiguration_settings)

    if event == 'conf_name':
         configuration_json['ClientConfiguration']['ConfigurationName']=value
    elif event == 'conf_version':
         configuration_json['ClientConfiguration']['ConfigurationVersion']=value     
    elif event == 'conf_description':
         configuration_json['ClientConfiguration']['ConfigurationDescription']=value     
    elif event == 'conf_backservice':
         configuration_json['ClientConfiguration']['ForegroundService']=value     
    elif event == 'conf_backservice_exit':
         configuration_json['ClientConfiguration']['StopForegroundServiceOnExit']=value     
    elif event == 'conf_intent':
         configuration_json['ClientConfiguration']['BroadcastIntent']=value     
    elif event == 'conf_intent_var':
         configuration_json['ClientConfiguration']['BroadcastVariable']=value     
    elif event == 'conf_url_face_recognition':
         configuration_json['ClientConfiguration']['FaceRecognitionURL']=value     
    elif event == 'conf_keyboard_menu':
         configuration_json['ClientConfiguration']['OnKeyboardMain']=value     
    
    elif event == 'launch_process':
         configuration_json['ClientConfiguration']['LaunchProcess']=value     
    elif event == 'launch_variable':
         configuration_json['ClientConfiguration']['LaunchVar']=value     
    elif event == 'menu_web_template':
         configuration_json['ClientConfiguration']['MenuWebTemplate']=value     
    elif event == 'Launch':
         configuration_json['ClientConfiguration']['Launch']=get_key(start_screen_elements,value)     
    elif event == 'def_service_online':
         configuration_json['ClientConfiguration']['OnlineServiceConfiguration']=value     
    elif event == 'def_service_python':
         configuration_json['ClientConfiguration']['DefServiceConfiguration']=value
    #elif event == 'web_handlers_python':
    #     configuration_json['ClientConfiguration']['WebHandlersFile']=value          
    
    elif event == 'confoptions_dictionaries':
         jconfiguration_settings['dictionaries']=value
    elif event == 'confoptions_vendor':
         if not 'ConfigurationSettings' in configuration_json['ClientConfiguration']: configuration_json['ClientConfiguration']['ConfigurationSettings']={}
         jconfiguration_settings['vendor']=value     
    elif event == 'confoptions_vendor_url':
         jconfiguration_settings['vendor_url']=value     
    elif event == 'confoptions_vendor_login':
        
        if 'confoptions_vendor_login' in values and 'confoptions_vendor_password' in values:
            authstring =  values['confoptions_vendor_login']+":"+ values['confoptions_vendor_password']
            jconfiguration_settings['vendor_auth']= 'Basic '+ base64.b64encode(authstring.encode('utf-8')).decode('utf-8') 
    elif event == 'confoptions_vendor_password':
        
        if 'confoptions_vendor_login' in values and 'confoptions_vendor_password' in values:
            authstring =values['confoptions_vendor_login']+":"+ values['confoptions_vendor_password']
            jconfiguration_settings['vendor_auth']=  'Basic '+   base64.b64encode(authstring.encode('utf-8')).decode('utf-8') 
    elif event == 'confoptions_vendor_auth':
         jconfiguration_settings['vendor_auth']=value     
    elif event == 'conf_split_mode':
         jconfiguration_settings['handler_split_mode']=value     
    elif event == 'confoptions_client_code':
         jconfiguration_settings['handler_code']=value     
    elif event == 'confoptions_handlers_url':
         jconfiguration_settings['handler_url']=value     
    elif event == 'confoptions_handlers_login':
        if 'confoptions_handlers_login' in values and 'confoptions_handlers_password' in values:
            authstring =  values['confoptions_vendor_login']+":"+ values['confoptions_vendor_password']
            jconfiguration_settings['handler_auth']= 'Basic '+  base64.b64encode(authstring.encode('utf-8')).decode('utf-8') 
       
    elif event == 'confoptions_handlers_password':
        if 'confoptions_handlers_login' in values and 'confoptions_handlers_password' in values:
           authstring =  values['confoptions_vendor_login']+":"+ values['confoptions_vendor_password']
           jconfiguration_settings['handler_auth']= 'Basic '+ base64.b64encode(authstring.encode('utf-8')).decode('utf-8')  
     
    elif event == 'confoptions_handlers_auth':
         jconfiguration_settings['handler_auth']=value     
       

    configuration_json['ClientConfiguration']['ConfigurationSettings'] = jconfiguration_settings

def load_configuration_properties():
    global window
    global current_uid

    if 'Launch' in configuration_json['ClientConfiguration']:
        window['Launch'].update(get_synonym(start_screen_elements,configuration_json['ClientConfiguration']['Launch']))
    else:    
        window['Launch'].update(get_synonym(start_screen_elements,'Menu'))

    if 'LaunchProcess' in configuration_json['ClientConfiguration']:
        window['launch_process'].update(configuration_json['ClientConfiguration']['LaunchProcess'])
    else:    
        window['launch_process'].update('')

    if 'LaunchVar' in configuration_json['ClientConfiguration']:
        window['launch_variable'].update(configuration_json['ClientConfiguration']['LaunchVar'])
    else:    
        window['launch_variable'].update('') 

    if 'MenuWebTemplate' in configuration_json['ClientConfiguration']:
        window['menu_web_template'].update(configuration_json['ClientConfiguration']['MenuWebTemplate'])
    else:    
        window['menu_web_template'].update('')     

    if 'DefServiceConfiguration' in configuration_json['ClientConfiguration']:
        window['def_service_python'].update(configuration_json['ClientConfiguration']['DefServiceConfiguration'])
    else:
        window['def_service_python'].update('')


    #if 'WebHandlersFile' in configuration_json['ClientConfiguration']:
    #    window['web_handlers_python'].update(configuration_json['ClientConfiguration']['WebHandlersFile'])
    #else:
    #    window['web_handlers_python'].update('')    


    if 'OnlineServiceConfiguration' in configuration_json['ClientConfiguration']:
        window['def_service_online'].update(configuration_json['ClientConfiguration']['OnlineServiceConfiguration'])
    else:    
        window['def_service_online'].update('')


    if 'ConfigurationName' in configuration_json['ClientConfiguration']:
        window['conf_name'].update(configuration_json['ClientConfiguration']['ConfigurationName'])
    else:    
        window['conf_name'].update('')
    
    if 'ConfigurationVersion' in configuration_json['ClientConfiguration']:
        window['conf_version'].update(configuration_json['ClientConfiguration']['ConfigurationVersion'])
    else:    
        window['conf_version'].update('')

    if 'ConfigurationDescription' in configuration_json['ClientConfiguration']:
        window['conf_description'].update(configuration_json['ClientConfiguration']['ConfigurationDescription'])
    else:    
        window['conf_description'].update('')

    if 'ForegroundService' in configuration_json['ClientConfiguration']:
        window['conf_backservice'].update(configuration_json['ClientConfiguration']['ForegroundService'])
    else:    
        window['conf_backservice'].update('')

    if 'StopForegroundServiceOnExit' in configuration_json['ClientConfiguration']:
        window['conf_backservice_exit'].update(configuration_json['ClientConfiguration']['StopForegroundServiceOnExit'])
    else:    
        window['conf_backservice_exit'].update('')

    if 'BroadcastIntent' in configuration_json['ClientConfiguration']:
        window['conf_intent'].update(configuration_json['ClientConfiguration']['BroadcastIntent'])
    else:    
        window['conf_intent'].update('')

    if 'BroadcastVariable' in configuration_json['ClientConfiguration']:
        window['conf_intent_var'].update(configuration_json['ClientConfiguration']['BroadcastVariable'])
    else:    
        window['conf_intent_var'].update('') 

    if 'FaceRecognitionURL' in configuration_json['ClientConfiguration']:
        window['conf_url_face_recognition'].update(configuration_json['ClientConfiguration']['FaceRecognitionURL'])
    else:    
        window['conf_url_face_recognition'].update('')

    if 'OnKeyboardMain' in configuration_json['ClientConfiguration']:
        window['conf_keyboard_menu'].update(configuration_json['ClientConfiguration']['OnKeyboardMain'])
    else:    
        window['conf_keyboard_menu'].update('')

    if 'ConfigurationSettings' in configuration_json['ClientConfiguration']:

        

        confsettings = configuration_json['ClientConfiguration']['ConfigurationSettings']
        if type(confsettings)==str:
            jconfsettings  =json.loads(confsettings)
        else:    
            jconfsettings  =confsettings

        current_uid =  jconfsettings['uid']   

        if 'vendor' in jconfsettings:
            window['confoptions_vendor'].update(jconfsettings['vendor'])
        else:    
            window['confoptions_vendor'].update('')

        if 'dictionaries' in jconfsettings:
            window['confoptions_dictionaries'].update(jconfsettings['dictionaries'])
        else:    
            window['confoptions_dictionaries'].update('')
        

        if 'vendor_url' in jconfsettings:
            window['confoptions_vendor_url'].update(jconfsettings['vendor_url'])
        else:    
            window['confoptions_vendor_url'].update('')    


        if 'vendor_auth' in jconfsettings:
            window['confoptions_vendor_auth'].update(jconfsettings['vendor_auth'])

            if "Basic" in jconfsettings['vendor_auth']:
                authstring = base64.b64decode(jconfsettings['vendor_auth'][6:]).decode('utf-8')
            
                window['confoptions_vendor_login'].update(authstring[:authstring.index(':')])
                window['confoptions_vendor_password'].update(authstring[authstring.index(':')+1:])

        else:    
            window['confoptions_vendor_auth'].update('')
            window['confoptions_vendor_login'].update('')
            window['confoptions_vendor_password'].update('')

        if 'handler_split_mode' in jconfsettings:
            window['conf_split_mode'].update(jconfsettings['handler_split_mode'])
        else:    
            window['conf_split_mode'].update('')


        if 'handler_code' in jconfsettings:
            window['confoptions_client_code'].update(jconfsettings['handler_code'])
        else:    
            window['confoptions_client_code'].update('')

        if 'handler_url' in jconfsettings:
            window['confoptions_handlers_url'].update(jconfsettings['handler_url'])
        else:    
            window['confoptions_handlers_url'].update('')

        if 'handler_auth' in jconfsettings:
            window['confoptions_handlers_auth'].update(jconfsettings['handler_auth'])
            

            if "Basic" in jconfsettings['handler_auth']:
                authstring = base64.b64decode(jconfsettings['handler_auth'][6:]).decode('utf-8')
            
                window['confoptions_handlers_login'].update(authstring[:authstring.index(':')])
                window['confoptions_handlers_password'].update(authstring[authstring.index(':')+1:])

        else:
            window['confoptions_handlers_auth'].update('')
            window['confoptions_handlers_login'].update('')
            window['confoptions_handlers_password'].update('')

def set_visibility_main_tabs(visibility):
    global window
    window['tab_configuration_common'].update(visible=visibility)
    window['tab_configuration_menu'].update(visible=visibility)
    window['tab_configuration_sql_on_start'].update(visible=visibility)
    window['tab_configuration_json'].update(visible=visibility)
    window['tab_layout_start_screen'].update(visible=visibility)
    window['tab_configuration_options'].update(visible=visibility)
    window['tab_layout_conf_handlers'].update(visible=visibility)
    window['tab_layout_timers'].update(visible=visibility)
    window['tab_layout_conf_handlers'].update(visible=visibility)
    window['tab_layout_timers'].update(visible=visibility)
    window['tab_layout_pyfiles'].update(visible=visibility)
    window['tab_layout_mediafiles'].update(visible=visibility)
    window['main_tabs'].update(visible=visibility)

    window['process_column_left'].update(visible=visibility)
    window['process_column'].update(visible=visibility)
    window['screen_column_left'].update(visible=visibility)
    window['screen_column'].update(visible=visibility)
    window['tab_layout_common_handlers'].update(visible=visibility)
    #window['menu_column'].update(visible=visibility)

def init_variables():
    global window
    global handlers_filename
    global data_mediafiles
    global data_pyfiles
    global data_pyfilenames
    global data_timers
    global data_sql_on_start
    global data_mainmenu
    global data_screen_lines

    global jcurrent_process
    global jcurrent_screen
    global jcurrent_screen_line
    global jcurrent_layout
    global jcurrent_mainmenu
    global jcurrent_mediafiles
    global jcurrent_pyfiles
    global jcurrent_sql_on_start
    global jcurrent_timers
    global jcurrent_style
    global jcurrent_common_handlers 

    window['timers_table'].update(values=[['','','','']])
    window['pyfiles_table'].update('')

    handlers_filename=None
    data_mediafiles=[]
    data_pyfiles=[]
    data_pyfilenames=[]
    data_timers=[]
    data_sql_on_start=[]
    data_mainmenu=[]
    data_screen_lines = []

    jcurrent_process=None
    jcurrent_screen=None
    jcurrent_screen_line=None
    jcurrent_layout=None
    jcurrent_mainmenu=None
    jcurrent_mediafiles=None
    jcurrent_pyfiles=None
    jcurrent_sql_on_start=None
    jcurrent_timers=None
    jcurrent_style=None
    jcurrent_common_handlers=None    
    
def create_project():
    global window
    global configuration_json
    global jcurrent_screen
    global conf_filename

    conf_filename = sg.popup_get_file(get_locale('create_file_project'), save_as=True,no_window=True,file_types=[("Simple UI configuration text files (*.ui)", "*.ui")])    

    if not conf_filename == None:
        if len(conf_filename)>0:
            window.set_title(conf_filename) 

                #set_visibility_main_tabs(True)


            init_variables()

                #generating new uuid for SimpleUI configuration
            current_uid = uuid.uuid4().hex
                #create simple template of SimpleUi configuration
            configuration_json={"ClientConfiguration":
            {"ConfigurationName": get_locale('new_configuration'),"ConfigurationDescription": get_locale('new_configuration_decription'), "ConfigurationVersion": "0.0.1", "Processes":[
                                {
                            "type": "Process",
                            "ProcessName": get_locale('new_process'),
                            "PlanFactHeader": get_locale('plan_fact'),
                            "DefineOnBackPressed": False,
                            "hidden": False,
                            "login_screen": False,
                            "SC": False,
                            "Operations": [
                            {
                                "type": "Operation",
                                "Name": get_locale('new_screen') ,
                                "Timer": False,
                                "hideToolBarScreen": False,
                                "noScroll": False,
                                "handleKeyUp": False,
                                "noConfirmation": False,
                                "hideBottomBarScreen": False,
                                "onlineOnStart": False,
                                "send_when_opened": False,
                                "send_after_opened": False,
                                "onlineOnInput": False,
                                "DefOnlineOnCreate": "",
                                "DefOnlineOnInput": "",
                                "DefOnCreate": "",
                                "DefOnInput": "",
                                "Elements":[]
                            }
                                ]
                    }
                ]
                ,
                "ConfigurationSettings":   {
                    "uid": current_uid
                }
                }
                }
                
                #Visualizing the configuration structure
            load_configuration_properties()    
            load_processes(True)
            load_screens(True)
            load_screen_lines(False,True)  
            load_screen_handlers()  
            set_visibility(jcurrent_screen)    
            init_configuration(window)

            update_conf()

            arch2_visibility(True)
 
def open_project():
    global window
    global configuration_json
    global jcurrent_screen
    global conf_filename
    global handlers_filename
    
    conf_filename = sg.popup_get_file(get_locale("file_open_dialog"),no_window=True,file_types=[("Simple UI configuration text files (*.ui)", "*.ui")])    

    if not conf_filename==None:

                #set_visibility_main_tabs(True)
        
        if len(conf_filename)>0:
            window.set_title(conf_filename)

            with open(conf_filename, encoding="utf-8") as json_file:
                configuration_json = json.load(json_file)
                    
                init_variables()

                load_configuration_properties()    
                load_processes()
                load_screens()
                load_screen_lines()    
                load_screen_handlers()
                set_visibility(jcurrent_screen)    
                init_configuration(window)

                if 'arch2' in configuration_json['ClientConfiguration']:
                    arch2_visibility( configuration_json['ClientConfiguration']['arch2'])
                else:
                    arch2_visibility(False)    

                data_recognition = []
                if 'RecognitionTemplates' in configuration_json['ClientConfiguration']:
                    for elem in configuration_json['ClientConfiguration']['RecognitionTemplates']:
                        data_recognition.append(elem['name'])

                window['cvrecognition_type'].update(values = data_recognition)

                update_conf(False)  

                if not current_uid==None:
                    handlers_filename =  settings_global.get("handlers_filename"+current_uid)
                    if not handlers_filename == None:
                        window['conf_file_python'].update(handlers_filename)

                    shandlers_list = settings_global.get("handlers_list"+current_uid)
                    if not shandlers_list==None:
                        try:
                            if len(shandlers_list)>0:
                                jhandlers_list = json.loads(shandlers_list)
                                
                                for elem in jhandlers_list:
                                        data_pyfilenames.append({"key":elem['alias'],"filename":elem['filename']})

                                load_pyfiles()

                        except Exception:
                                print("Error reading settings...")        



#web server initialization for configuration translation
app = Flask(__name__)

@app.route("/get_conf", methods=['GET'])
def get_conf():
    global device_url
    device_url  = request.remote_addr+':8095'
    return  json.dumps(configuration_json,ensure_ascii=False,indent=4, separators=(',', ': '))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if not func is None:
        
        func()
    

@app.route('/shutdown', methods=['POST'])
def shutdown():
    
    shutdown_server()
    return 'Server shutting down...'

web_thr=None
server =None       

def arch2_visibility(arch_value):

    global window 
    global configuration_json

    visibility = not arch_value

    window['tab_configuration_sql_on_start'].update(visible=visibility)
    window['handlers_cv'].update(visible=visibility)
    window['screen_handlers'].update(visible=visibility)
    window['tab_layout_conf_handlers'].update(visible=visibility)

    if arch_value==True:
        configuration_json['ClientConfiguration']['arch2']  =True 
   

if __name__ == "__main__":
        


    #run Flask-server in thread
    web_thr =  threading.Thread(target=app.run,kwargs=dict(host='0.0.0.0', port=WSPORT, debug=False)).start() 


    load_processes(True)
    load_screens(True)
    load_screen_lines(False,True)
    load_screen_handlers()

    #layoutFile = [[sg.T("")], [sg.Text("Файл конфигурации: "), sg.Input(key="conf_file",enable_events=True), sg.FileBrowse()]]
    
    #creating main screen layout
    tab_layout_common = [[sg.Text(get_locale('conf_name'),size=35),sg.Input(do_not_clear=True, key='conf_name',enable_events=True,expand_x=True)],
                        [sg.Text(get_locale('version'),size=35),sg.Input(do_not_clear=True, key='conf_version',enable_events=True,expand_x=True)],
                        [sg.Text(get_locale('description'),size=35),sg.Input(do_not_clear=True, key='conf_description',enable_events=True,expand_x=True)],
                        [sg.Checkbox(get_locale('enable_event_service'),key='conf_backservice',enable_events=True,size=35),sg.Checkbox(get_locale('stop_service'),key='conf_backservice_exit',enable_events=True,size=50)],
                        [sg.Text(get_locale('nosql_database_name'),size=35),sg.Input(do_not_clear=True, key='conf_nosql_name',enable_events=True,expand_x=True)],
                        [sg.Text(get_locale('intent_broadcast'),size=35),sg.Input(do_not_clear=True, key='conf_intent',enable_events=True,expand_x=True)],
                        [sg.Text(get_locale('intent_broadcast_variable'),size=35),sg.Input(do_not_clear=True, key='conf_intent_var',enable_events=True,expand_x=True)],
                        [sg.Text(get_locale('face_recognition_url'),size=35),sg.Input(do_not_clear=True, key='conf_url_face_recognition',enable_events=True,expand_x=True)],
                        [sg.Checkbox(get_locale('keyboard_reading_in_main_menu') ,key='conf_keyboard_menu',enable_events=True)]
        ]

    tab_layout_sql_on_start=[[sg.Button(get_locale('add'),key='add_sql_on_start'), sg.Button(get_locale('delete'),key="delete_sql_on_start")],[sg.Table(values=[['']],headings=[get_locale('command')],key='sql_on_start_table',enable_events=True,expand_x=True)]]
    tab_layout_menu=[[sg.Button(get_locale('add'),key='add_mainmenu'), sg.Button(get_locale('delete'),key="delete_mainmenu")],[sg.Table(values=[['','','','']],headings=[get_locale('name') ,get_locale('key'),'ID',get_locale('show_in_toolbar')],key='mainmenu_table',enable_events=True,expand_x=True,expand_y=True,auto_size_columns=True)]]
    tab_layout_options=[[sg.Text(get_locale('configuration_vendor'),size=35),sg.Input(do_not_clear=True, key='confoptions_vendor',enable_events=True)],
    [sg.Text(get_locale('vendor_url'),size=35),sg.Input(do_not_clear=True, key='confoptions_vendor_url',enable_events=True,expand_x=True)],
    [sg.Text(get_locale('vendor_login_basic') ,size=35),sg.Input(do_not_clear=True, key='confoptions_vendor_login',enable_events=True),sg.Text(get_locale('vendor_password_basic') ),sg.Input(do_not_clear=True, key='confoptions_vendor_password',enable_events=True),sg.Text(get_locale('vendor_authorization_string') ),sg.Input(do_not_clear=True, key='confoptions_vendor_auth',enable_events=True)],
    [sg.Checkbox(get_locale('split_mode') ,key='conf_split_mode',enable_events=True)],
    [sg.Text(get_locale('client_code') ,size=35),sg.Input(do_not_clear=True, key='confoptions_client_code',enable_events=True,expand_x=True)],
    [sg.Text(get_locale('handlers_url') ,size=35),sg.Input(do_not_clear=True, key='confoptions_handlers_url',enable_events=True,expand_x=True)],
    [sg.Text(get_locale('handlers_login'),size=35),sg.Input(do_not_clear=True, key='confoptions_handlers_login',enable_events=True),sg.Text(get_locale('handlers_password') ),sg.Input(do_not_clear=True, key='confoptions_handlers_password',enable_events=True),sg.Text(get_locale('handlers_authorization_string')),sg.Input(do_not_clear=True, key='confoptions_handlers_auth',enable_events=True)],
    [sg.Text(get_locale('dictionaries'),size=35),sg.Input(do_not_clear=True, key='confoptions_dictionaries',enable_events=True,expand_x=True)]
    
    ]

    tab_layout_timers=[[sg.Button(get_locale('add') ,key='add_timers'), sg.Button(get_locale('delete'),key="delete_timers")],[sg.Table(values=[['','','','']],headings=[get_locale('key'),get_locale('period'),get_locale('built_in_handler'),get_locale('handler_name')],key='timers_table',enable_events=True,expand_x=True,expand_y=True,auto_size_columns=True)]]

    tab_layout_pyfiles=[[sg.Text(get_locale('python_handlers_file'),size=50), sg.Input(key="conf_file_python",enable_events=True,expand_x=True), sg.FileBrowse(file_types=[("Python files (*.py)", "*.py")])],[sg.T('')]
    ,
        [sg.Button(get_locale('add'),key='add_pyfiles'), sg.Button(get_locale('delete'),key="delete_pyfiles"),sg.Button(get_locale('update'),key="update_pyfiles")],[sg.Table(values=[['','','']],headings=['Имя','Путь','base64'],key='pyfiles_table',enable_events=True,expand_x=True,auto_size_columns=True)]]

    tab_layout_mediafiles=[[sg.Button(get_locale('add'),key='add_mediafiles'), sg.Button(get_locale('delete'),key="delete_mediafiles")],[sg.Table(values=[['','']],headings=['Имя','base64'],key='mediafiles_table',enable_events=True,expand_x=True,expand_y=True,auto_size_columns=True)]]

    

    layoutFileHandlers= [sg.Text(get_locale('python_handlers_file') ), sg.Input(key="conf_file_python",enable_events=True,expand_x=True), sg.FileBrowse(file_types=[("Python files (*.py)", "*.py")])]

    tab_layout_conf_handlers=[
    [sg.Text(get_locale('service_handler_python') ,size=50),sg.Input(do_not_clear=True, key='def_service_python',enable_events=True)],
    [sg.Text(get_locale('service_handler_online') ,size=50),sg.Input(do_not_clear=True, key='def_service_online',enable_events=True,expand_x=True)],
    [sg.Text(get_locale('reply_handler_python') ,size=50),sg.Input(do_not_clear=True, key='def_notification_python',enable_events=True,expand_x=True)],
    [sg.Text(get_locale('income_content_handler_python') ,size=50),sg.Input(do_not_clear=True, key='def_content_python',enable_events=True,expand_x=True)]

    ]

    tab_layout_start_screen=[
        
        [sg.Text(get_locale('menu_type'),size=35),sg.Combo(captions_start_screen_elements, key='Launch',enable_events=True,expand_x=True)],
        [sg.Text(get_locale('menu_process_with_layouts') ,size=35),sg.Input(do_not_clear=True, key='launch_process',enable_events=True,expand_x=True)],
        [sg.Text(get_locale('menu_variable_of_tiles'),size=35),sg.Input(do_not_clear=True, key='launch_variable',enable_events=True,expand_x=True)],
        [sg.Text(get_locale('menu_web_template'),size=35),sg.Input(do_not_clear=True, key='menu_web_template',enable_events=True,expand_x=True)],

    ]


    tab_layout_common_handlers = [
    [sg.Button(get_locale("add_common_handler"),key='btn_add_common_handler'),sg.Button(get_locale("delete_common_handler"),key='btn_delete_common_handler')],
    [
               sg.Table(values=data_common_handlers, headings=headings_common_handlers,auto_size_columns=True,
                   
                    display_row_numbers=False,
                    num_rows=10,
                    
                    key='CommonHandlersTable',
                    selected_row_colors='red on yellow',
                                      
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    bind_return_key =True,
                    
                    expand_x=True,expand_y=True) ]

              ] 

    tab_layout_json = [[sg.Multiline('',key='json_multiline',expand_x=True,expand_y=True)]    ]

    layout_configuration_options = [sg.TabGroup([[sg.Tab(get_locale('common'),tab_layout_common,key='tab_configuration_common'),
    sg.Tab(get_locale('sql_on_start'),tab_layout_sql_on_start,key='tab_configuration_sql_on_start'),
    sg.Tab(get_locale('main_menu') ,tab_layout_menu,key='tab_configuration_menu'),
    sg.Tab(get_locale('source'),tab_layout_json,key='tab_configuration_json'),
    sg.Tab(get_locale('start_screen'),tab_layout_start_screen,key='tab_layout_start_screen'),
    sg.Tab(get_locale('configuration_properties') ,tab_layout_options,key='tab_configuration_options'),
    sg.Tab(get_locale('handlers'),tab_layout_conf_handlers,key='tab_layout_conf_handlers'),
    sg.Tab(get_locale('handlers_shedule') ,tab_layout_timers,key='tab_layout_timers'),
    sg.Tab(get_locale('additional_modules') ,tab_layout_pyfiles,key='tab_layout_pyfiles'),
    sg.Tab(get_locale('mediafiles') ,tab_layout_mediafiles,key='tab_layout_mediafiles'),
    sg.Tab(get_locale('common_handlers') ,tab_layout_common_handlers,key='tab_layout_common_handlers')
    ]],key='main_tabs',enable_events=True,expand_x=True)]




    data=[[get_locale('headings_processes')],['']]
    data_screens=[[get_locale('screens') ],['']]

    menu_def = [['&'+get_locale("file"), ['&'+get_locale('create_project'),'&'+get_locale("open_project"),get_locale("create_debug"),get_locale("qr_settings"),get_locale("sql_console"),get_locale("language"),get_locale("arch2")]],['&'+get_locale("project_templates"), ['&'+get_locale("style_templates"),'&'+get_locale("recognition_templates")]],
                    ]
    

    empty_layout = [[sg.Menu(menu_def)]]
    layout = [[sg.Menu(menu_def)],
    layout_configuration_options, 
    
                        
    [                    

     sg.Column([

    [sg.Button(get_locale('add_process'),key="btn_add_process"),sg.Button(get_locale('add_process_cv'),key="btn_add_process_cv"), sg.Button(get_locale('delete_process'),key="btn_delete_process"), sg.Button(get_locale('copy_to_clipboard'),key="btn_copy_process"), sg.Button(get_locale('paste_from_clipboard'),key="btn_paste_process")],
    [sg.Table(values=data[1:][:], headings=headings,
                        
                        display_row_numbers=False,
                        justification='left',
                        num_rows=6,
                        #alternating_row_color='lightyellow',
                        key='ConfigurationTable',
                        selected_row_colors='red on yellow',
                        
                        enable_events=True,

                        def_col_width=75,col_widths=[75],auto_size_columns=False,                       
                        
                        
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        
                       
                    # enable_click_events=True,           # Comment out to not enable header and other clicks
                        )
                        ]


     ],key='process_column_left'),

                        sg.Column([[sg.Text(get_locale('process_name'),size=35),sg.Input(do_not_clear=True, key='process_name',enable_events=True,expand_x=True)],
                        [sg.Checkbox(text=get_locale('do_not_display'),key="p_not_show",enable_events=True)],
                        [sg.Checkbox(text=get_locale('override_back_button'),key="DefineOnBackPressed",enable_events=True)],
                        [sg.Checkbox(text=get_locale('run_at_start') ,enable_events=True,key='login_screen')],
                        [sg.Text(get_locale('plan_fact_header') ,key='pf_header',size=35),sg.Input(do_not_clear=True, key='PlanFactHeader',enable_events=True,expand_x=True)],
                        [sg.Checkbox( text=get_locale('independent_process'),key="SC",enable_events=True)],
                        #[sg.Button(get_locale('process_to_clipboard') ,key='btn_get_process_base')]
                        
                        ],key='process_column',expand_x=True)
                        
                        ],
           # [sg.HorizontalSeparator()],
            [sg.Column([

            [sg.Button(get_locale('add_screen_step'),key="btn_add_screen"), sg.Button(get_locale('delete_screen') ,key="btn_delete_screen"), sg.Button(get_locale('copy_to_clipboard') ,key="btn_copy_screen"), sg.Button(get_locale('paste_from_clipboard') ,key="btn_paste_screen")],
            [sg.Table(values=data_screens[1:][:], headings=headings_screens,def_col_width=75,col_widths=[75],auto_size_columns=False,
                        #auto_size_columns=True,
                        display_row_numbers=False,
                        justification='left',
                        
                        #alternating_row_color='lightyellow',
                        key='ScreensTable',
                        selected_row_colors='red on yellow',
                        enable_events=True,
                        expand_y=True,
                        
                        select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    # enable_click_events=True,           # Comment out to not enable header and other clicks
                        )]

            ],vertical_alignment='top',key='screen_column_left'),        
            
                        
                        sg.Column([
                        [sg.TabGroup([[sg.Tab(get_locale('screen') ,tab_layout_screen,key='tab_screen',expand_x=True,expand_y=True),sg.Tab(get_locale('cv'),tab_layout_CVFrame,key='tab_cv',visible=False,expand_x=True,expand_y=True)]],expand_x=True,expand_y=True)],
                    
                        
                        ],expand_x=True,expand_y=True,key='screen_column')                         
            
            ]
            ]
            

    #main_layout=[[sg.Column([[sg.Multiline(key='OUTPUT', pad=(0, 0), font=(sg.DEFAULT_FONT, 12))]]),sg.Column(layout)]]

    # ------ Create Main Editor Window ------
    window = sg.Window('Simple UI Editor', layout,
                    
                    resizable=True,icon='ic_32.ico')
    window.finalize()

    #set_visibility_main_tabs(False)

    if jcurrent_screen!=None:
        set_visibility(jcurrent_screen)


    #Run code updating thread
    stopFlag = Event()
    thread = CodeUpdateThread(stopFlag)
    thread.start()

        

    rlayout = [
            [sg.Text(get_locale("create_or_open"))],
            [sg.Text()],
            [sg.Button(get_locale(get_locale('create_project')),key='start_createproject',expand_x=True), sg.Button(get_locale(get_locale('open_project')),key='start_openproject',expand_x=True)]
            ]
    
    startwindow = sg.Window(get_locale("edit_record"), rlayout,icon='ic_32.ico',modal=True)
    startevent, rvalues = startwindow.read()
    startwindow.close()  

    exit=False
    if startevent=='Cancel' or  startevent==None:
        exit=True    
    elif startevent=='start_createproject':
        create_project()
    elif startevent=='start_openproject':
        open_project()   
              

    # ------ Event Loop ------
    while True and not exit:
        event, values = window.read()
        #print(event, values)
        if event == sg.WIN_CLOSED:
            break

        update_conf(False)    
        
        #Main menu- Create Project
        if event==get_locale('create_project') :
            create_project()  
                 
         
        #----------Creating debug Flask-based *.py-file
        if event==get_locale('create_debug'):
            debug_template_filename = "_debug_template.py"
            debug_output_filename='debug_handlers.py'
            code=''
            handlerscode=''
            outputcode=''

            list_of_debug=[]

            if 'CommonHandlers' in configuration_json['ClientConfiguration']:    
                for handler in  configuration_json['ClientConfiguration']['CommonHandlers']:
                        if handler.get('type')=='python' and  handler.get('method','') [0:1]=="_": 
                              list_of_debug.append(handler.get('method',''))  

            if 'Processes' in configuration_json['ClientConfiguration']:        

                

                for process in configuration_json['ClientConfiguration']['Processes']:

                   

                    if process['type']=='Process' and 'Operations' in process:
                        for operation in process['Operations']:

                            if 'Handlers' in operation:
                                for handler in  operation['Handlers']:
                                    if handler.get('type')=='python' and  handler.get('method','') [0:1]=="_": 
                                        list_of_debug.append(handler.get('method',''))  

                            if  len(operation.get('DefOnCreate',''))>1: 
                                if operation.get('DefOnCreate','')[0:1]=="_":
                                    list_of_debug.append(operation.get('DefOnCreate',''))
                            if  len(operation.get('DefOnInput',''))>1: 
                                if operation.get('DefOnInput','')[0:1]=="_":
                                    list_of_debug.append(operation.get('DefOnInput',''))
                           
                            
                    if process['type']=='CVOperation' and 'CVFrames' in process:
                        for operation in process['CVFrames']:

                                if 'Handlers' in operation:
                                    for handler in  operation['Handlers']:
                                        if handler.get('type')=='python' and  handler.get('method','') [0:1]=="_": 
                                            list_of_debug.append(handler.get('method',''))  
                                                                 
                                if len(operation.get('CVFrameDefOnCreate',''))>0 :
                                    if operation.get('CVFrameDefOnCreate','')[0:1]=="_":
                                        list_of_debug.append(operation.get('CVFrameDefOnCreate',''))

                                if len(operation.get('CVFrameDefAction',''))>0 :
                                    if operation.get('CVFrameDefAction','')[0:1]=="_":
                                        list_of_debug.append(operation.get('CVFrameDefAction',''))

                                if len(operation.get('CVFrameDefOnTouch',''))>0 :
                                    if operation.get('CVFrameDefOnTouch','')[0:1]=="_":
                                        list_of_debug.append(operation.get('CVFrameDefOnTouch',''))

                                if len(operation.get('CVFrameDefOnNewObject',''))>0 :
                                    if operation.get('CVFrameDefOnNewObject','')[0:1]=="_":
                                        list_of_debug.append(operation.get('CVFrameDefOnNewObject',''))

                           

            if os.path.isfile(handlers_filename):
                with open(handlers_filename, 'r', encoding='utf-8') as f:
                    handlerscode = f.read()
            node = ast.parse(handlerscode)
            
            begincode=''
            endcode=''

            if os.path.isfile(debug_template_filename):
                with open(debug_template_filename, 'r', encoding='utf-8') as f:
                    code = f.read()
                    if code.find("#-BEGIN CUSTOM HANDLERS")>0:
                        begincode = code[0:code.find("#-BEGIN CUSTOM HANDLERS")+len("#-BEGIN CUSTOM HANDLERS")]+os.linesep
                        endcode = code[code.find("#-END CUSTOM HANDLERS"):]
                        #print(code[])
                for _funcname in list_of_debug:
                    funcname = _funcname[1:]

                    for x in ast.walk(node):
                        if isinstance(x, ast.FunctionDef):
                            if x.name==funcname:    
                                ch = ast.get_source_segment(handlerscode, x)

                                ch = ch.replace(funcname,_funcname)
                                ch = ch.replace("(hashMap,_files=None,_data=None)","()")
                               

                                begincode+=os.linesep+ch+os.linesep


                outputcode=begincode+endcode
            
                with open(debug_output_filename, 'w', encoding='utf-8') as f:
                    f.write(outputcode)
                    f.close()

        #----------Create SimpleUI configuration settings QR code for device connection. 
        # The URL of the service must be encoded in the QR code. 
        # This is the IP address of the computer running the constructor and the port of the Flask server.
        if event==get_locale('qr_settings'):
            sg.popup(get_locale("vpn_note"),     keep_on_top=True)    
            jqr = {
            "RawConfigurationURL":"http://"+ socket.gethostbyname(socket.gethostname())+":"+str(WSPORT)+"/get_conf",
            "RawConfigurationServiceAuth": "",
            "RawConfigurationServiceON": True,
            "OnlineSplitMode": True,
            }

            img = qrcode.make(json.dumps(jqr))
            img.show()

        #SQL for queries to the SQLite database on the device through the application's web service
        if event ==get_locale("sql_console"):
            
            sqllayout = [
                [sg.Text(get_locale("sql_query") , size =(15, 1)), sg.Input(default_text="SELECT name FROM sqlite_master WHERE type='table'",key='query',expand_x=True)],
                [sg.Text(get_locale("sql_params") , size =(15, 1)), sg.Input(key='params',expand_x=True)],
                [sg.Text(get_locale("DB_Name") , size =(15, 1)), sg.Input(default_text="SimpleWMS",key='db_name',expand_x=True)],
                
                [sg.Multiline(key='sql_output',size=(150,20))],
                [sg.Button(get_locale("send_select"),key='send_select'),sg.Button(get_locale("send_execute"),key='send_execute'), sg.Cancel()]
                ]   
    
            sqlwindow = sg.Window('SQL' , sqllayout,icon='ic_32.ico')
            
            
            #Event loop for SQL-console
            while True:
                sqlevent, sqlvalues = sqlwindow.read()
                #print(event, values)
                if sqlevent == sg.WIN_CLOSED:
                    break

                #Select -queryes  (SELECT FROM...)  
                if sqlevent==get_locale("send_select"):
                    
                    if device_url==None:
                        sg.popup('Device not connected', '' ,   grab_anywhere=True)
                    else:    

                        try:
                            sqlresponse = requests.post(
                            'http://'+device_url+'/?mode=SQLQueryText&query='+sqlvalues['query']+'&params='+sqlvalues['params']+'&db_name='+sqlvalues['db_name'],
                            
                            headers={'Content-Type': 'Application/json; charset=utf-8'}
                            )

                            if sqlresponse.status_code==200:    
                                sqlwindow['sql_output'].update(sqlresponse.text)
                        except requests.exceptions.RequestException as e:  # This is the correct syntax
                                sg.popup('Device connection error',  e,   grab_anywhere=True)

                #execute commands (delete,create etc.)    
                if sqlevent==get_locale("send_execute"):
                    
                    if device_url==None:
                        sg.popup('Device not connected', '' ,   grab_anywhere=True)
                    else:    

                        try:
                            sqlresponse = requests.post(
                            'http://'+device_url+'/?mode=ExecSQL&params='+sqlvalues['params'],
                            data=sqlvalues['query'],
                            headers={'Content-Type': 'Application/json; charset=utf-8'}
                            )

                            if sqlresponse.status_code==200:    
                                sqlwindow['sql_output'].update(sqlresponse.text)
                        except requests.exceptions.RequestException as e:  # This is the correct syntax
                                sg.popup('Device connection error',  e,   grab_anywhere=True)
                    

            sqlwindow.close()  

        #Set editor language
        if event ==get_locale("language"):
            localeList = glob.glob('*_locale.json')
            rlayout = [
        
                [sg.Text(get_locale("language") , size =(15, 1)), sg.Combo(localeList,key='locale_filename',default_value=locale_filename)],
                [sg.Ok(), sg.Cancel()]
                ]   
    
            lwindow = sg.Window('Language' , rlayout,icon='ic_32.ico')
            revent, rvalues = lwindow.read()
            lwindow.close()  

            if revent=='Ok':
                settings_global.set("locale_filename", rvalues['locale_filename'])
                settings_global.save()

                sg.popup(get_locale("restart_note"),     keep_on_top=True) 
        
        if event==get_locale("arch2") :
            arch2_visibility(True)

        #open project from file
        if event==get_locale("open_project") :
            open_project()
            
        if event=='main_tabs':
            activeTab = window['main_tabs'].Get()
            if activeTab == 'tab_configuration_json':
                update_conf()

        if event in ['conf_name','conf_version','conf_description','conf_backservice','conf_backservice_exit','conf_nosql_name','conf_intent','conf_intent_var','conf_url_face_recognition','conf_keyboard_menu',
        'confoptions_vendor','confoptions_vendor_url','confoptions_vendor_login','confoptions_vendor_password','confoptions_vendor_auth','conf_split_mode','confoptions_client_code','confoptions_handlers_url','confoptions_handlers_login','confoptions_handlers_password','confoptions_handlers_auth',
        'Launch','launch_process','launch_variable','def_service_python','def_service_online','confoptions_dictionaries','menu_web_template','web_handlers_python'] :
        
            write_cofiguration_property(event,values[event],values)

            update_conf()

        if event == 'delete_mediafiles':
            if jcurrent_mediafiles!=None: 
                configuration_json['ClientConfiguration']['Mediafile'].remove(jcurrent_mediafiles) 
            
                load_mediafiles()

                update_conf()

        if event == 'mediafiles_table':
            
            row_clicked =  values['mediafiles_table'][0]
            jcurrent_mediafiles = configuration_json['ClientConfiguration']['Mediafile'][row_clicked]

        
        if event=='btn_add_common_handler' :
            
                new_handlers_line = {"alias":"","event":"","action":"","type":"","method":"","postExecute":""}   
                if not  'CommonHandlers' in configuration_json['ClientConfiguration']:
                    configuration_json['ClientConfiguration']['CommonHandlers']=[]

                configuration_json['ClientConfiguration']['CommonHandlers'].append(new_handlers_line)
                edit_common_handler_form(None,configuration_json['ClientConfiguration']['CommonHandlers'][-1]) 

                update_conf()     
              
        if event=='btn_delete_common_handler' :
            
                if len(values['CommonHandlersTable'])>0:
                    current_position = values['CommonHandlersTable'][0]
                    
                    configuration_json['ClientConfiguration']['CommonHandlers'].pop(current_position)
                

                    update_conf()  

                    load_common_handlers()
                    window['CommonHandlersTable'].update(values=data_common_handlers[1:][:])   
        
        if event == 'CommonHandlersTable':
            #print(event)
            if len(values['CommonHandlersTable'])>0:
                row_clicked =  values['CommonHandlersTable'][0]
                jcurrent_screen_line = all_common_handlers_list[row_clicked]
                
                edit_common_handler_form(row_clicked,jcurrent_screen_line)

        if event == 'add_mediafiles':
                rlayout = [
        
                [sg.Text(get_locale("key") , size =(15, 1)), sg.InputText(key='mediafiles_key')],
                [sg.Text(get_locale("file"), size =(15, 1)), sg.Input(key='mediafiles_file'), sg.FileBrowse()],
        
                [sg.Ok(), sg.Cancel()]
                ]   
    
                rwindow = sg.Window(get_locale("edit_record") , rlayout,icon='ic_32.ico')
                revent, rvalues = rwindow.read()
                rwindow.close()  

                if revent=='Ok':
                    if not 'Mediafile' in configuration_json['ClientConfiguration']:
                        configuration_json['ClientConfiguration']['Mediafile']=[]

                    data=''
                    ext=''
                    with open(rvalues['mediafiles_file'], 'rb') as file:
                        data = file.read()
                        ext= os.path.splitext(rvalues['mediafiles_file'])[1][1:]
                    base64file  = base64.b64encode(data).decode('utf-8')   

                    configuration_json['ClientConfiguration']['Mediafile'].append({"MediafileKey":rvalues['mediafiles_key'],"MediafileData":base64file,"MediafileExt":ext})
                    load_mediafiles()

                    update_conf()     

        if event == 'delete_pyfiles':
            if jcurrent_pyfiles!=None: 
                configuration_json['ClientConfiguration']['PyFiles'].remove(jcurrent_pyfiles) 
            
                load_pyfiles()

                update_conf()

         #+++ Василий  Кнопка "перезагрузить модули питона"
        if event == 'update_pyfiles':
            handlers_filename = values['conf_file_python']
            if len(handlers_filename) > 0:
                read_handlers_file(handlers_filename)
            if not current_uid == None:
                settings_global.set("handlers_filename" + current_uid, handlers_filename)
                settings_global.save()
            configuration_json['ClientConfiguration']['PyFiles'] = []

            #Добавим лист уже загруженных
            already_loaded =[]
            for el in data_pyfilenames: #.append({"key": rvalues['pyfiles_key'], "filename": rvalues['pyfiles_file']})
                if el['key'] in already_loaded:
                    continue #Каждый файл загружаем только один раз
                with open(el['filename'], 'r', encoding='utf-8') as file:
                    data = file.read()
                    base64file = base64.b64encode(data.encode('utf-8')).decode('utf-8')


                    configuration_json['ClientConfiguration']['PyFiles'].append(
                        {"PyFileKey": el['key'], "PyFileData": base64file})
                    already_loaded.append(el['key'])
            load_pyfiles()
            update_conf()
        #-----------------        

        if event == 'pyfiles_table':
            
            if not values['pyfiles_table']: #+++Василий Исправление вылета
                row_clicked = 0
            else:
                row_clicked = values['pyfiles_table'][0]
                
            jcurrent_pyfiles = configuration_json['ClientConfiguration']['PyFiles'][row_clicked]

        if event == 'add_pyfiles':
            rlayout = [
        
            [sg.Text('Ключ', size =(15, 1)), sg.InputText(key='pyfiles_key')],
            [sg.Text('Файл', size =(15, 1)), sg.Input(key='pyfiles_file'), sg.FileBrowse(file_types=[("Python files (*.py)", "*.py")])],
        
            [sg.Ok(), sg.Cancel()]
            ]
    
            rwindow = sg.Window(get_locale("edit_record"), rlayout,icon='ic_32.ico')
            revent, rvalues = rwindow.read()
            rwindow.close()  

            if revent=='Ok':
                if not 'PyFiles' in configuration_json['ClientConfiguration']:
                    configuration_json['ClientConfiguration']['PyFiles']=[]

                data=''
                with open(rvalues['pyfiles_file'], 'r',encoding='utf-8') as file:
                    data = file.read()
                base64file  = base64.b64encode(data.encode('utf-8')).decode('utf-8')   

                data_pyfilenames.append({"key":rvalues['pyfiles_key'],"filename":rvalues['pyfiles_file']})
                configuration_json['ClientConfiguration']['PyFiles'].append({"PyFileKey":rvalues['pyfiles_key'],"PyFileData":base64file})
                load_pyfiles()

                update_conf()

        if event == 'delete_timers':
            if jcurrent_timers!=None: 
                configuration_json['ClientConfiguration']['PyTimerTask'].remove(jcurrent_timers) 
            
                load_timers()

                update_conf()

        if event == 'timers_table':
            
            row_clicked =  values['timers_table'][0]
            jcurrent_timers = configuration_json['ClientConfiguration']['PyTimerTask'][row_clicked]

        if event == 'add_timers':
            rlayout = [
            [sg.Text(get_locale("handler"))],
            [sg.Text(get_locale("key"), size =(15, 1)), sg.InputText(key='timers_key')],
            [sg.Text(get_locale("period"), size =(15, 1)), sg.InputText(key='timers_period')],
            [sg.Text(get_locale("handler_name") , size =(15, 1)), sg.InputText(key='timers_def')],
            [sg.Checkbox("Built-in",key='timers_builin')],
            [sg.Ok(), sg.Cancel()]
            ]
    
            rwindow = sg.Window(get_locale("edit_record"), rlayout,icon='ic_32.ico')
            revent, rvalues = rwindow.read()
            rwindow.close()  

            if revent=='Ok':
                if not 'PyTimerTask' in configuration_json['ClientConfiguration']:
                    configuration_json['ClientConfiguration']['PyTimerTask']=[]

                configuration_json['ClientConfiguration']['PyTimerTask'].append({"PyTimerTaskKey":rvalues['timers_key'],"PyTimerTaskDef":rvalues['timers_def'],"PyTimerTaskPeriod":rvalues['timers_period'],"PyTimerTaskBuilIn":rvalues['timers_builin']})
                load_timers()

                update_conf()

        if event == 'delete_mainmenu':
            if jcurrent_mainmenu!=None: 
                configuration_json['ClientConfiguration']['MainMenu'].remove(jcurrent_mainmenu) 
            
                load_MainMenu()

                update_conf()

        if event == 'mainmenu_table':
            
            row_clicked =  values['mainmenu_table'][0]
            jcurrent_mainmenu = configuration_json['ClientConfiguration']['MainMenu'][row_clicked]

        if event == 'add_mainmenu':
            rlayout = [
            [sg.Text(get_locale("menu_item") )],
            [sg.Text(get_locale("name") , size =(15, 1)), sg.InputText(key='menu_name')],
            [sg.Text(get_locale("key"), size =(15, 1)), sg.InputText(key='menu_key')],
            [sg.Text('ID', size =(15, 1)), sg.InputText(key='menu_ID')],
            [sg.Checkbox(get_locale("show_in_toolbar"),key='menu_toolbar')],
            [sg.Ok(), sg.Cancel()]
            ]

            
    
            rwindow = sg.Window(get_locale("edit_record"), rlayout,icon='ic_32.ico')
            revent, rvalues = rwindow.read()
            rwindow.close()  

            if revent=='Ok':
                if not 'MainMenu' in configuration_json['ClientConfiguration']:
                    configuration_json['ClientConfiguration']['MainMenu']=[]

                configuration_json['ClientConfiguration']['MainMenu'].append({"MenuItem":rvalues['menu_key'],"MenuTitle":rvalues['menu_name'],"MenuId":rvalues['menu_ID'],"MenuTop":rvalues['menu_toolbar']})
                load_MainMenu()
                update_conf()

        if event == 'delete_sql_on_start':
            if jcurrent_sql_on_start!=None: 
                configuration_json['ClientConfiguration']['OfflineOnCreate'].remove(jcurrent_sql_on_start) 
            


                load_OfflineOnCreate()

                update_conf()

        if event == 'sql_on_start_table':
            
            row_clicked =  values['sql_on_start_table'][0]
            jcurrent_sql_on_start = configuration_json['ClientConfiguration']['OfflineOnCreate'][row_clicked]

        if event == 'add_sql_on_start':
            rlayout = [
            [sg.Text(get_locale("enter_sql"))],
            [sg.Text(get_locale("sql_command") , size =(15, 1)), sg.InputText(key='sql_on_start_command')],
            [sg.Ok(), sg.Cancel()]
            ]
    
            rwindow = sg.Window(get_locale("edit_record"), rlayout,icon='ic_32.ico')
            revent, rvalues = rwindow.read()
            rwindow.close()  

            if revent=='Ok':
                if not 'OfflineOnCreate' in configuration_json['ClientConfiguration']:
                    configuration_json['ClientConfiguration']['OfflineOnCreate']=[]

                configuration_json['ClientConfiguration']['OfflineOnCreate'].append({"Query":rvalues['sql_on_start_command']})
                load_OfflineOnCreate()
                
                #data_sql_on_start.append([rvalues['sql_on_start_command']])

                #window['sql_on_start_table'].update(values=data_sql_on_start[0:][:])  

                update_conf()
        

        if event=='conf_file_python':
            handlers_filename=values['conf_file_python']
            if len(handlers_filename)>0:
                read_handlers_file(handlers_filename)
            if not current_uid == None:
                settings_global.set("handlers_filename"+current_uid, handlers_filename)
                settings_global.save()

        if event=='process_name':    
            if  jcurrent_process['type']=="Process":
                jcurrent_process['ProcessName']= values['process_name']
            elif  jcurrent_process['type']=="CVOperation":     
                jcurrent_process['CVOperationName']= values['process_name']
            load_processes()
            window['ConfigurationTable'].update(values=data[1:][:])
            
            update_conf()
            
        if event=='p_not_show':
            if  jcurrent_process['type']=="Process":
                jcurrent_process['hidden']= values['p_not_show']
            elif  jcurrent_process['type']=="CVOperation":     
                jcurrent_process['hidden']= values['p_not_show']

                update_conf()
        if event=='DefineOnBackPressed':
            if  jcurrent_process['type']=="Process":
                jcurrent_process['DefineOnBackPressed']= values['DefineOnBackPressed']   

                update_conf()
        if event=='login_screen':
            if  jcurrent_process['type']=="Process":
                jcurrent_process['login_screen']= values['login_screen']    

                update_conf()
        if event=='SC':
            if  jcurrent_process['type']=="Process":
                jcurrent_process['SC']= values['SC']    
                
                update_conf()

        if event=='PlanFactHeader':
            if  jcurrent_process['type']=="Process":
                jcurrent_process['PlanFactHeader']= values['PlanFactHeader']    

                update_conf()    

        if event=='btn_save_screen':  
            if jcurrent_screen['type']=='Operation':

                #update_code(False,jcurrent_process['ProcessName'],jcurrent_screen['Name'],"OnCreate",screen_elem['PythonOnCreate'],jcurrent_screen)
                #update_code(False,jcurrent_process['ProcessName'],jcurrent_screen['Name'],'OnInput',screen_elem['PythonOnInput'],jcurrent_screen)

                save_screen_values(values)

                update_conf()
        
        if event in ['screen_name','cb_screen_timer','cb_screen_hide_bottom_bar','cb_screen_no_scroll','cb_screen_hide_toolbar','cb_screen_no_confirmation','cb_screen_keyboard','screen_def_oncreate','screen_def_onaftercreate','screen_def_oninput','screen_defpython_oncreate','screen_defpython_onaftercreate','screen_defpython_oninput','CVFrame_detector',
                'step_name','CVActionButtons','CVAction','CVInfo','CVCameraDevice','CVMode','CVResolution','CVMask','CVDetectorMode','CVFrameOnlineOnCreate','CVFrameOnlineOnNewObject','CVFrameOnlineAction','CVFrameOnlineOnTouch','CVFrameDefOnCreate','CVFrameDefOnNewObject','CVFrameDefAction','CVFrameDefOnTouch','cvrecognition_type']:
            save_screen_values_event(event,values)  
            
     


        if event=='btn_add_process':    
            new_process={"ProcessName":get_locale("new_process"),"type":"Process","Operations":[]}
            configuration_json['ClientConfiguration']['Processes'].append(new_process) 
            
            load_processes(True)
            window['ConfigurationTable'].update(values=data[1:][:])
            window['ConfigurationTable'].update(select_rows =[(len(configuration_json['ClientConfiguration']['Processes'])-1)])

            jcurrent_process= configuration_json['ClientConfiguration']['Processes'][len(configuration_json['ClientConfiguration']['Processes'])-1] 
            load_screens(True)
            window['ScreensTable'].update(values=data_screens[1:][:]) 
            
            load_screen_lines(False,True)
            window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 

            load_screen_handlers()

            update_conf()

        
        if event=='btn_add_process_cv':   
            new_process={"CVOperationName":get_locale("new_active_cv_operation"),"type":"CVOperation","CVFrames":[]}
            configuration_json['ClientConfiguration']['Processes'].append(new_process) 
            
            load_processes(True)
            window['ConfigurationTable'].update(values=data[1:][:])
            window['ConfigurationTable'].update(select_rows =[(len(configuration_json['ClientConfiguration']['Processes'])-1)])

            jcurrent_process= configuration_json['ClientConfiguration']['Processes'][len(configuration_json['ClientConfiguration']['Processes'])-1] 
            load_cvsteps(True)
            window['ScreensTable'].update(values=data_screens[1:][:]) 
            
            
            update_conf()


        if event=='btn_paste_process':   

            try:
                new_process = json.loads(pyperclip.paste().replace("True","true").replace("False","false"))    
                
                
                if new_process.get('type')=='Process':    
      
                    configuration_json['ClientConfiguration']['Processes'].append(new_process) 
            
                    load_processes(True)
                    window['ConfigurationTable'].update(values=data[1:][:])
                    window['ConfigurationTable'].update(select_rows =[(len(configuration_json['ClientConfiguration']['Processes'])-1)])

                    jcurrent_process= configuration_json['ClientConfiguration']['Processes'][len(configuration_json['ClientConfiguration']['Processes'])-1] 
                    load_screens(True)
                    window['ScreensTable'].update(values=data_screens[1:][:]) 
                    
                    load_screen_lines(False,True)
                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 

                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:]) 

                    update_conf()

                elif new_process.get('type')=='CVOperation':    
                
                    configuration_json['ClientConfiguration']['Processes'].append(new_process) 
            
                    load_processes(True)
                    window['ConfigurationTable'].update(values=data[1:][:])
                    window['ConfigurationTable'].update(select_rows =[(len(configuration_json['ClientConfiguration']['Processes'])-1)])

                    jcurrent_process= configuration_json['ClientConfiguration']['Processes'][len(configuration_json['ClientConfiguration']['Processes'])-1] 
                    load_cvsteps(True)
                    window['ScreensTable'].update(values=data_screens[1:][:]) 
                    
                    load_screen_handlers()
                    window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])

                    update_conf()


            except Exception as e:  # This is the correct syntax
                                sg.popup('Wrong clipboard content',  e,   grab_anywhere=True)   



        if event=='btn_delete_process':    
        
            configuration_json['ClientConfiguration']['Processes'].remove(jcurrent_process) 
            if len(configuration_json['ClientConfiguration']['Processes'])>0:
                jcurrent_process= configuration_json['ClientConfiguration']['Processes'][len(configuration_json['ClientConfiguration']['Processes'])-1]
                load_processes(True)
                window['ConfigurationTable'].update(values=data[1:][:])
                if len(configuration_json['ClientConfiguration']['Processes'])>0:
                    window['ConfigurationTable'].update(select_rows =[(len(configuration_json['ClientConfiguration']['Processes'])-1)])
                
                load_screens(True)
                window['ScreensTable'].update(values=data_screens[1:][:]) 

                load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 

                load_screen_handlers()
                window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])

            update_conf()

        if event=='btn_get_process_base' or event=='btn_copy_process':    
        
            pyperclip.copy(json.dumps(jcurrent_process,ensure_ascii=False,indent=4, separators=(',', ': ')))
            #spam = pyperclip.paste()
           


        if event=='btn_add_screen': 

            if jcurrent_process.get('type')=='Process':    
                new_screen={"Name":get_locale("new_screen"),"type":"Operation","Elements":[],"Timer":False,"hideToolBarScreen":False,"noScroll":False,"handleKeyUp":False,"handleKeyUp":False,"hideBottomBarScreen":False}
                jcurrent_process['Operations'].append(new_screen) 
                jcurrent_screen= jcurrent_process['Operations'][-1]
                set_visibility(jcurrent_screen) 
                load_screens(True)
                window['ScreensTable'].update(values=data_screens[1:][:]) 
                window['ScreensTable'].update(select_rows =[(len(jcurrent_process['Operations'])-1)])

                load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 

                update_conf()

            elif jcurrent_process.get('type')=='CVOperation':    
                new_step={"Name":get_locale("new_active_cv_step"),"type":"CVFrame"}
                jcurrent_process['CVFrames'].append(new_step) 
                jcurrent_screen= jcurrent_process['CVFrames'][-1]
                set_visibility(jcurrent_screen) 
                
                load_cvsteps()
                window['ScreensTable'].update(values=data_screens[1:][:]) 

                update_conf()

        if event=='btn_paste_screen': 

            try:
                new_screen = json.loads(pyperclip.paste().replace("True","true").replace("False","false"))    
                
                
                if jcurrent_process.get('type')=='Process':    
      
                    jcurrent_process['Operations'].append(new_screen) 
                    jcurrent_screen= jcurrent_process['Operations'][-1]
                    set_visibility(jcurrent_screen) 
                    load_screens(True)
                    window['ScreensTable'].update(values=data_screens[1:][:]) 
                    window['ScreensTable'].update(select_rows =[(len(jcurrent_process['Operations'])-1)])

                    load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:]) 

                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:]) 

                    update_conf()

                elif jcurrent_process.get('type')=='CVOperation':    
                
                    jcurrent_process['CVFrames'].append(new_screen) 
                    jcurrent_screen= jcurrent_process['CVFrames'][-1]
                    set_visibility(jcurrent_screen) 
                    
                    load_cvsteps()
                    window['ScreensTable'].update(values=data_screens[1:][:]) 

                    load_screen_handlers()
                    window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:]) 

                    update_conf()


            except Exception as e:  # This is the correct syntax
                                sg.popup('Wrong clipboard content',  e,   grab_anywhere=True)    

     

        if event=='btn_copy_screen': 
            pyperclip.copy(json.dumps(jcurrent_screen,ensure_ascii=False,indent=4, separators=(',', ': ')).replace("true","True").replace("false","False"))
            

        if event=='btn_delete_screen':    
            if jcurrent_process['type']=="CVOperation":
                jcurrent_process['CVFrames'].remove(jcurrent_screen) 
                if len(jcurrent_process['CVFrames'])>0:
                    jcurrent_screen= jcurrent_process['CVFrames'][-1]
                
                    load_cvsteps(True)
                    window['ScreensTable'].update(values=data_screens[1:][:]) 

                    load_screen_handlers()
                    window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])    
                
            else:    
                jcurrent_process['Operations'].remove(jcurrent_screen) 
                if len(jcurrent_process['Operations'])>0:
                    jcurrent_screen= jcurrent_process['Operations'][-1]
                
                    load_screens(True)
                    window['ScreensTable'].update(values=data_screens[1:][:]) 

                    load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])

                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])  

            update_conf()

        if event=='btn_add_screen_line':
            if not jcurrent_screen==None:
                new_screen_line = {"Value":"","Variable":"","type":"LinearLayout"}    
                jcurrent_screen['Elements'].append(new_screen_line)
                edit_element_form(None,jcurrent_screen['Elements'][-1]) 

                update_conf()  



        if event=='btn_delete_screen_line':
            if not jcurrent_screen==None:
                if len(values['ScreenLinesTable'])>0:
                    current_position = values['ScreenLinesTable'][0]
                    
                    jcurrent_screen['Elements'].pop(current_position)
                

                    update_conf()  

                    load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])
        if event == 'btn_insert_from_clipboard_screen_line':
            try:
                new_screen_line = json.loads(pyperclip.paste().replace("True","true").replace("False","false"))    
                jcurrent_screen['Elements'].append(new_screen_line)
                
                update_conf()  

                load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])
            except Exception as e:  # This is the correct syntax
                                sg.popup('Wrong clipboard content',  e,   grab_anywhere=True)

        if event=='btn_add_screen_handler' :
            if not jcurrent_screen==None:
                new_handlers_line = {"event":"","action":"","type":"","method":"","postExecute":""}   
                if not  'Handlers' in jcurrent_screen:
                    jcurrent_screen['Handlers']=[]

                jcurrent_screen['Handlers'].append(new_handlers_line)
                edit_handler_form(None,jcurrent_screen['Handlers'][-1]) 

                update_conf()     
        if  event=='btn_add_screen_handler_cv':
            if not jcurrent_screen==None:
                new_handlers_line = {"event":"","action":"","type":"","method":"","postExecute":""}   
                if not  'Handlers' in jcurrent_screen:
                    jcurrent_screen['Handlers']=[]

                jcurrent_screen['Handlers'].append(new_handlers_line)
                edit_handler_form(None,jcurrent_screen['Handlers'][-1],True) 

                update_conf()             
        if event=='btn_delete_screen_handler' :
            if not jcurrent_screen==None:
                if len(values['ScreenHandlersTable'])>0:
                    current_position = values['ScreenHandlersTable'][0]
                    
                    jcurrent_screen['Handlers'].pop(current_position)
                

                    update_conf()  

                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])     
        if  event=='btn_delete_screen_handler_cv':
            if not jcurrent_screen==None:
                if len(values['ScreenHandlersTableCV'])>0:
                    if 'Handlers' in jcurrent_screen:
                        current_position = values['ScreenHandlersTableCV'][0]
                        
                        jcurrent_screen['Handlers'].pop(current_position)
                    

                        update_conf()  

                        load_screen_handlers()
                        window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])                    

        if event == 'ConfigurationTable':
            if len(values['ConfigurationTable'])>0:
                data_selected = [data[row] for row in values[event]]
                row_selected = values['ConfigurationTable'][0]
                jcurrent_process = all_processes_list[row_selected]
                if jcurrent_process['type']=='CVOperation':
                    window['process_name'].update(jcurrent_process.get('CVOperationName'))
                    window['p_not_show'].update(jcurrent_process.get('hidden'))

                    window['DefineOnBackPressed'].update(visible=False)
                    window['login_screen'].update(visible=False)
                    window['SC'].update(visible=False)
                    window['PlanFactHeader'].update(visible=False)
                    window['pf_header'].update(visible=False)

                    load_cvsteps(True)
                    window['ScreensTable'].update(values=data_screens[1:][:])

                    if(len(data_screens[1:][:])>0):
                        window['ScreensTable'].update(select_rows =[0])

                    load_screen_handlers()
                    window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])

                else:
                    window['process_name'].update(jcurrent_process['ProcessName'])

                    window['p_not_show'].update(jcurrent_process.get('hidden'))

                    window['DefineOnBackPressed'].update(visible=True)
                    window['login_screen'].update(visible=True)
                    window['SC'].update(visible=True)
                    window['PlanFactHeader'].update(visible=True)
                    window['pf_header'].update(visible=True)

                    window['DefineOnBackPressed'].update(jcurrent_process.get('DefineOnBackPressed'))
                    window['login_screen'].update(jcurrent_process.get('login_screen'))
                    window['SC'].update(jcurrent_process.get('SC'))
                    window['PlanFactHeader'].update(jcurrent_process.get('PlanFactHeader'))


                    load_screens(True)
                    window['ScreensTable'].update(values=data_screens[1:][:])
                    load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])

                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])

                    if(len(data_screens[1:][:])>0):
                        window['ScreensTable'].update(select_rows =[0])


                    window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])
                    if(len(data_screen_lines[1:][:])>0):
                        window['ScreenLinesTable'].update(select_rows =[0])

        if event == get_locale("style_templates"):
            window_styles()
        if event == get_locale("recognition_templates"):
            window_recognition()    
        if event == 'ScreensTable':
            data_selected = [data_screens[row] for row in values[event]]
            if len(values['ScreensTable'])>0:
                row_selected = values['ScreensTable'][0]
                jcurrent_screen = all_screens_list[row_selected]
                set_visibility(jcurrent_screen)

                load_screen_lines(jcurrent_screen['type']=="CVFrame",True)
                window['ScreenLinesTable'].update(values=data_screen_lines[1:][:])

                if jcurrent_screen.get('type')=='CVFrame':
                    load_screen_handlers()
                    window['ScreenHandlersTableCV'].update(values=data_screen_handlers[1:][:])
                else:    
                    load_screen_handlers()
                    window['ScreenHandlersTable'].update(values=data_screen_handlers[1:][:])

            
        if event == 'ScreenLinesTable':
            #print(event)
            if len(values['ScreenLinesTable'])>0:
                row_clicked =  values['ScreenLinesTable'][0]
                jcurrent_screen_line = all_screen_lines_list[row_clicked]
                
                edit_element_form(row_clicked,jcurrent_screen_line)

        if event == 'ScreenHandlersTable':
            #print(event)
            if len(values['ScreenHandlersTable'])>0:
                row_clicked =  values['ScreenHandlersTable'][0]
                jcurrent_screen_line = all_screen_handlers_list[row_clicked]
                
                edit_handler_form(row_clicked,jcurrent_screen_line)
        if event == 'ScreenHandlersTableCV':
            #print(event)
            if len(values['ScreenHandlersTableCV'])>0:
                row_clicked =  values['ScreenHandlersTableCV'][0]
                jcurrent_screen_line = all_screen_handlers_list[row_clicked]
                
                edit_handler_form(row_clicked,jcurrent_screen_line,True)                
    
    requests.post('http://127.0.0.1:5000/shutdown')    
    
    window.close()
