import ctypes
from comtypes import GUID, COMMETHOD, HRESULT, IUnknown
from comtypes.client import CreateObject

class ITaskbarList3(IUnknown):
    
    _case_insensitive_ = True
    _iid_ = GUID('{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}')
    _methods_ = [
                COMMETHOD([], HRESULT, 'HrInit'),
                    COMMETHOD([], HRESULT, 'AddTab', (['in'], ctypes.c_void_p, 'hwnd')),
                    COMMETHOD([], HRESULT, 'DeleteTab', (['in'], ctypes.c_void_p, 'hwnd')),
                    COMMETHOD([], HRESULT, 'ActivateTab', (['in'], ctypes.c_void_p, 'hwnd')),
                    COMMETHOD([], HRESULT, 'SetActiveAlt', (['in'], ctypes.c_void_p, 'hwnd')),
                    COMMETHOD([], HRESULT, 'MarkFullscreenWindow', (['in'], ctypes.c_void_p, 'hwnd'), (['in'], ctypes.c_int, 'fFullscreen')),
                    COMMETHOD([], HRESULT, 'SetProgressValue', (['in'], ctypes.c_void_p, 'hwnd'), (['in'], ctypes.c_ulonglong, 'ullCompleted'), (['in'], ctypes.c_ulonglong, 'ullTotal')),
                    COMMETHOD([], HRESULT, 'SetProgressState', (['in'], ctypes.c_void_p, 'hwnd'), (['in'], ctypes.c_int, 'tbpFlags'))
                ]
                
def get_taskbar():
    obj = CreateObject('{56FDF344-FD6D-11D0-958A-006097C9A090}', interface=ITaskbarList3)
    obj.HrInit()
    return obj