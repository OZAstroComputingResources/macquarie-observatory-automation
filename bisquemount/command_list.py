# Given a list of functions and a list of strings, this program 
# is designed to find the function matching a given string.
# As this has to be done in principle when "compiling", the C way
# to do this is to have a list of functions and a list of strings.
#
# Function lists may have to be imported from many places, but
# within the same global scope. With the "simple server" mentality, 
# this can be passed a single object that contains the function 
# definitions, as a single object should be enough to contain all
# pieces of hardware (which should be 1).
#
# The idea is that a single call to:
# execute_command(command)
# ... returns a string for successful execution, or a useful string
#
# Try: 
# ./make_command_list dummy_functions.py 
# import dummy_functions as d
# import command_list as cl
# print cl.execute_command("one",d)
# print cl.execute_command("help",d)
# print cl.execute_command("oops",d)

import string
import pydoc

def execute_command(the_command, m):
    '''Find the_command amongst the list of commands like cmd_one in module m
    
    This returns a string containing the response, or a -1 if a quit is commanded.'''
    the_functions = dict(focusGoToPosition=m.cmd_focusGoToPosition,focusReadPosition=m.cmd_focusReadPosition,focusReadStateRegister=m.cmd_focusReadStateRegister,focusReadIdentityRegister=m.cmd_focusReadIdentityRegister,focusWriteMaxTravelRegister=m.cmd_focusWriteMaxTravelRegister,focusWritePositionSpeedRegister=m.cmd_focusWritePositionSpeedRegister,focusWriteMoveSpeedRegister=m.cmd_focusWriteMoveSpeedRegister,focusWriteShuttleSpeedRegister=m.cmd_focusWriteShuttleSpeedRegister,focusSetZeroPosition=m.cmd_focusSetZeroPosition,focusMove=m.cmd_focusMove,fs=m.cmd_fs,focusTelescope=m.cmd_focusTelescope,focusSetAmount=m.cmd_focusSetAmount,resetGuidingStats=m.cmd_resetGuidingStats,find=m.cmd_find,objInfo=m.cmd_objInfo,slewToObject=m.cmd_slewToObject,getTargetRaDec=m.cmd_getTargetRaDec,mountGetRaDec=m.cmd_mountGetRaDec,SkyDomeGetAz=m.cmd_SkyDomeGetAz,SkyDomeForceTrack=m.cmd_SkyDomeForceTrack,domeAz=m.cmd_domeAz,getRA=m.cmd_getRA,getDec=m.cmd_getDec,mountGetAzAlt=m.cmd_mountGetAzAlt,getAzimuth=m.cmd_getAzimuth,getAltitude=m.cmd_getAltitude,moveTelescope=m.cmd_moveTelescope,findHome=m.cmd_findHome,jog=m.cmd_jog,park=m.cmd_park,runQuery=m.cmd_runQuery,setParkPosition=m.cmd_setParkPosition,s=m.cmd_s,slewToRaDec=m.cmd_slewToRaDec,slewToAzAlt=m.cmd_slewToAzAlt,tracking=m.cmd_tracking,sendSomething=m.cmd_sendSomething,telescopeConnect=m.cmd_telescopeConnect,IsDomeGoToComplete=m.cmd_IsDomeGoToComplete,IsSlewComplete=m.cmd_IsSlewComplete)
    commands = string.split(the_command)
    if len(commands) == 0:
        return ""
    if commands[0] == "help":
        if (len(commands) == 1):
            return 'focusGoToPosition\nfocusReadPosition\nfocusReadStateRegister\nfocusReadIdentityRegister\nfocusWriteMaxTravelRegister\nfocusWritePositionSpeedRegister\nfocusWriteMoveSpeedRegister\nfocusWriteShuttleSpeedRegister\nfocusSetZeroPosition\nfocusMove\nfs\nfocusTelescope\nfocusSetAmount\nresetGuidingStats\nfind\nobjInfo\nslewToObject\ngetTargetRaDec\nmountGetRaDec\nSkyDomeGetAz\nSkyDomeForceTrack\ndomeAz\ngetRA\ngetDec\nmountGetAzAlt\ngetAzimuth\ngetAltitude\nmoveTelescope\nfindHome\njog\npark\nrunQuery\nsetParkPosition\ns\nslewToRaDec\nslewToAzAlt\ntracking\nsendSomething\ntelescopeConnect\nIsDomeGoToComplete\nIsSlewComplete'
        elif commands[1] in the_functions:
            td=pydoc.TextDoc()
            return td.docroutine(the_functions[commands[1]])
        else:
            return "ERROR: "+commands[1]+" is not a valid command."
    elif commands[0] == 'exit' or commands[0] == 'bye' or commands[0] == 'quit':
        return -1
    elif commands[0] in the_functions:
        return the_functions[commands[0]](the_command)
    else:
        return "ERROR: Command not found."

