import pcbnew
from pcbnew import EDA_ANGLE

import os
import json
import os
import re
import math

import traceback

import wx
import wx.xrc
import wx.dataview

from . import kle


''' Label index
┌─────────────────┐
│ ┌─────────────┐ │
│ │ 0    1    2 │ │
│ │             │ │
│ │ 3    4    5 │ │
│ │             │ │
│ │ 6    7    8 │ │
│ └─────────────┘ │
│   9   10   11   │
└─────────────────┘'''
_NAMEINDEX = 10

sw_reference = 'SW'
d_reference = 'D'
anchor = 1
mirror = False
rawdata = ''

# grid size
x_unit = 19.05
y_unit = 19.05

# offset relative to switch
diode_x_offset = 8.334375#3.25
diode_y_offset = 0#3
diode_rotation = 90


def PlaceSwitches(refpoint_name, layout, x_unit, y_unit, angle_multiplier):
    pcb = pcbnew.GetBoard()

    keys = kle.deserialize(layout)

    x_offset = 0
    y_offset = 0

    for key in keys:
        if len(key['labels']) > _NAMEINDEX and key['labels'][_NAMEINDEX] == refpoint_name:
            x_offset = key['x'] + (key['width'] - 1) / 2
            y_offset = key['y'] + (key['height'] - 1) / 2

    refpoint = pcb.FindFootprintByReference(refpoint_name).GetPosition()

    sw_missing = []
    d_missing = []

    for key in keys:
        # wx.MessageBox(str(key))
        key_name = key['labels'][_NAMEINDEX]
        sw = pcb.FindFootprintByReference(key_name)
        if sw:
            # Switch placement and rotation
            if key_name != refpoint_name:
                sw.SetPosition(refpoint + pcbnew.VECTOR2I_MM((key['x'] + (key['width'] - 1) / 2 - x_offset) * x_unit, (key['y'] + (key['height'] - 1) / 2 - y_offset) * y_unit))
            sw.SetOrientationDegrees(0)
            if key['rotation_angle'] != 0:
                sw.Rotate(refpoint + pcbnew.VECTOR2I_MM((key['rotation_x'] - .5 - x_offset) * x_unit, (key['rotation_y'] - .5 - y_offset) * y_unit),  pcbnew.EDA_ANGLE(key['rotation_angle'] * angle_multiplier, 1))
            
            # Diode placement and rotation
            diode = pcb.FindFootprintByReference(key_name.replace(sw_reference, d_reference))
            if diode:
                pass
                diode.SetPosition(sw.GetPosition() + pcbnew.VECTOR2I_MM(diode_x_offset, diode_y_offset))
                diode.SetOrientationDegrees(diode_rotation)
                diode.Rotate(sw.GetPosition(), pcbnew.EDA_ANGLE(sw.GetOrientationDegrees(), 1))
            else:
                d_missing.append(key_name.replace(sw_reference, d_reference))

            # Led placement and rotation
            # led = pcb.FindFootprintByReference(key_name.replace(sw_reference, 'LED'))
            # if led:
            #     led.SetPosition(sw.GetPosition() + pcbnew.VECTOR2I_MM(0, 5.08))
            #     led.SetOrientationDegrees(0.0)
            #     led.Rotate(sw.GetPosition(), pcbnew.EDA_ANGLE(sw.GetOrientationDegrees(), 1))
            # else:
            #     d_missing.append(key_name.replace(sw_reference, 'L'))
        else:
            sw_missing.append(key_name)
    pcbnew.Refresh()

    msg_missing = 'Some footprints might be missing'
    if sw_missing:
        msg_missing += '\n\nPossible switches missing: {}'.format(', '.join(sw_missing))
    if d_missing:
        msg_missing += '\n\nPossible diodes missing: {}'.format(', '.join(d_missing))
    if sw_missing or d_missing:
        wx.MessageBox(msg_missing.strip())


class SwitchPlacerDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"KLE Switch Placer", pos = wx.DefaultPosition, size = wx.Size( 640,400 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.Size( 640,400 ), wx.DefaultSize )

        bSizerMain = wx.BoxSizer( wx.VERTICAL )

        bSizerCustomize = wx.BoxSizer( wx.HORIZONTAL )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Switch reference:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )

        bSizer13.Add( self.m_staticText1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textSWReference = wx.TextCtrl( self, wx.ID_ANY, sw_reference, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer13.Add( self.m_textSWReference, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer13, 0, wx.EXPAND, 5 )

        bSizer141 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText41 = wx.StaticText( self, wx.ID_ANY, u"Anchor switch:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText41.Wrap( -1 )

        bSizer141.Add( self.m_staticText41, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textAnchor = wx.TextCtrl( self, wx.ID_ANY, str(anchor), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer141.Add( self.m_textAnchor, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer141, 1, wx.EXPAND, 5 )

        bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Diode reference:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        bSizer14.Add( self.m_staticText4, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textDReference = wx.TextCtrl( self, wx.ID_ANY, d_reference, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer14.Add( self.m_textDReference, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer14, 0, wx.EXPAND, 5 )


        bSizerCustomize.Add( bSizer6, 0, wx.EXPAND, 5 )

        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizerCustomize.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"X spacing:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )

        bSizer11.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textXunit = wx.TextCtrl( self, wx.ID_ANY, str(x_unit), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.m_textXunit, 0, wx.ALL, 5 )


        bSizer9.Add( bSizer11, 0, wx.EXPAND, 5 )

        bSizer12 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Y spacing:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )

        bSizer12.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textYunit = wx.TextCtrl( self, wx.ID_ANY, str(y_unit), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer12.Add( self.m_textYunit, 0, wx.ALL, 5 )


        bSizer9.Add( bSizer12, 0, wx.EXPAND, 5 )


        bSizerCustomize.Add( bSizer9, 0, wx.EXPAND, 5 )

        self.m_staticline31 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizerCustomize.Add( self.m_staticline31, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer91 = wx.BoxSizer( wx.VERTICAL )

        bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, u"D x-offset:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )

        bSizer111.Add( self.m_staticText21, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textDXoffset = wx.TextCtrl( self, wx.ID_ANY, str(diode_x_offset), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer111.Add( self.m_textDXoffset, 0, wx.ALL, 5 )


        bSizer91.Add( bSizer111, 1, wx.EXPAND, 5 )

        bSizer121 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"D y-offset:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText31.Wrap( -1 )

        bSizer121.Add( self.m_staticText31, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textDYoffset = wx.TextCtrl( self, wx.ID_ANY, str(diode_y_offset), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer121.Add( self.m_textDYoffset, 0, wx.ALL, 5 )


        bSizer91.Add( bSizer121, 1, wx.EXPAND, 5 )

        bSizer1211 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText311 = wx.StaticText( self, wx.ID_ANY, u"D rotation:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText311.Wrap( -1 )

        bSizer1211.Add( self.m_staticText311, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_textDRotation = wx.TextCtrl( self, wx.ID_ANY, str(diode_rotation), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1211.Add( self.m_textDRotation, 0, wx.ALL, 5 )


        bSizer91.Add( bSizer1211, 1, wx.EXPAND, 5 )


        bSizerCustomize.Add( bSizer91, 0, wx.EXPAND, 5 )


        bSizerMain.Add( bSizerCustomize, 0, wx.EXPAND, 5 )

        bSizerKLE = wx.BoxSizer( wx.HORIZONTAL )

        self.m_RawData = wx.TextCtrl( self, wx.ID_ANY, rawdata, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
        bSizerKLE.Add( self.m_RawData, 1, wx.ALL|wx.EXPAND, 5 )


        bSizerMain.Add( bSizerKLE, 1, wx.EXPAND, 5 )

        bSizerExecute = wx.BoxSizer( wx.HORIZONTAL )

        self.m_checkMirror = wx.CheckBox( self, wx.ID_ANY, u"Mirror placement", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkMirror.SetValue(mirror)
        bSizerExecute.Add( self.m_checkMirror, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizerExecute.Add( self.m_staticline1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.m_Execute = wx.Button( self, wx.ID_ANY, u"Execute", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerExecute.Add( self.m_Execute, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizerMain.Add( bSizerExecute, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )
        
        # Connect Events
        self.Bind( wx.EVT_CLOSE, self.OnClose )
        self.Bind( wx.EVT_BUTTON, self.OnExecute )

    def __del__( self ):
        pass
    
    # Event handlers
    def OnClose( self, event ):
        self.EndModal(wx.ID_OK)
    
    def OnExecute( self, event ):
        global x_unit, y_unit, sw_reference, d_reference, mirror, rawdata, diode_x_offset, diode_y_offset, diode_rotation, anchor
        try:
            x_unit = float(self.m_textXunit.GetLineText(0))
            y_unit = float(self.m_textYunit.GetLineText(0))
            sw_reference = self.m_textSWReference.GetLineText(0)
            d_reference = self.m_textDReference.GetLineText(0)
            mirror = self.m_checkMirror.IsChecked()
            diode_x_offset = float(self.m_textDXoffset.GetLineText(0))
            diode_y_offset = float(self.m_textDYoffset.GetLineText(0))
            diode_rotation = float(self.m_textDRotation.GetLineText(0))
            anchor = int(self.m_textAnchor.GetLineText(0))
            rawdata = ''
            for line in range(self.m_RawData.GetNumberOfLines()):
                rawdata += self.m_RawData.GetLineText(line)
            layout = json.loads(re.sub(r'(\w+):', r'"\1":', '['+rawdata.strip()+']'), strict=False)
            # wx.MessageBox(rawdata)
            PlaceSwitches(f'{sw_reference}{anchor}', layout, -x_unit if mirror else x_unit, y_unit, 1 if mirror else -1)
        except Exception as e:
            tb = traceback.format_exc()
            wx.MessageBox(tb)
        self.EndModal(wx.ID_OK)


class SwitchPlacer(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Switch Placer"
        self.category = "A descriptive category name"
        self.description = "A description of the plugin and what it does"
        self.show_toolbar_button = True # Optional, defaults to False
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./kle_logo.png")


    def Run(self):
        gui = SwitchPlacerDialog( None )
        gui.Show()


SwitchPlacer().register() # Instantiate and register to Pcbnew