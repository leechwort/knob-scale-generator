#! /usr/bin/python
'''
Copyright (C) 2017 Artem Synytsyn a.synytsyn@gmail.com

#TODO: Code cleaning and refactoring

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import inkex
import simplestyle, sys
from simpletransform import computePointInNode
from math import *
# The simplestyle module provides functions for style parsing.
from simplestyle import *

#SVG element generation routine
def draw_SVG_square((w,h), (x,y), parent):

    style = {   'stroke'        : 'none',
                'stroke-width'  : '1',
                'fill'          : '#000000'
            }
                
    attribs = {
        'style'     : simplestyle.formatStyle(style),
        'height'    : str(h),
        'width'     : str(w),
        'x'         : str(x),
        'y'         : str(y)
        }
    circ = inkex.etree.SubElement(parent, inkex.addNS('rect','svg'), attribs )


def draw_SVG_circle(r, cx, cy, width, fill, parent):
    
    style = { 'stroke': '#000000', 'stroke-width':str(width), 'fill': fill }
    circ_attribs = {
            'style':simplestyle.formatStyle(style),
            'cx':str(cx),
            'cy':str(cy),
            'r':str(r)
            }
    circle = inkex.etree.SubElement(parent, inkex.addNS('circle','svg'), circ_attribs )



def draw_text(textvalue, radius, angular_position, text_size, parent):
    # Create text element
    text = inkex.etree.Element(inkex.addNS('text','svg'))
    text.text = textvalue
    
    # Set text position to center of document.
    text.set('x', str(radius*cos(angular_position)))
    text.set('y', str(radius*sin(angular_position) + text_size/2))

    # Center text horizontally with CSS style.
    style = {
            'text-align' : 'center',
             'text-anchor': 'middle',
             'alignment-baseline' : 'center',
             'font-size' : str(text_size) + 'px',
             'vertical-align' : 'middle'
             }
    
    text.set('style', formatStyle(style))
    parent.append(text)
    


def draw_SVG_ellipse((rx, ry), (cx, cy), parent, start_end=(0.5*pi,pi), transform='' ):

    style = {   'stroke'        : '#000000',
                'stroke-width'  : '1',
                'fill'          : 'none'            }
    ell_attribs = {'style':simplestyle.formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(rx),
        inkex.addNS('ry','sodipodi')        :str(ry),
        inkex.addNS('start','sodipodi')     :str(start_end[0]),
        inkex.addNS('end','sodipodi')       :str(start_end[1]),
        inkex.addNS('open','sodipodi')      :'true',    #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :transform
        
            }
    ell = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )

class Knob_Scale(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        # General settings
        self.OptionParser.add_option("--radius",
                        action="store", type="int", 
                        dest="radius", default=100.0,
                        help="Radius of the knob in px")
        self.OptionParser.add_option("--linewidth",
                        action="store", type="int", 
                        dest="linewidth", default=1,
                        help="")        
        self.OptionParser.add_option("--angle",
                        action="store", type="float", 
                        dest="angle", default=260.0,
                        help="Angle of the knob scale in degrees")
        self.OptionParser.add_option("--draw_arc", 
                        action="store", type="inkbool",
                        dest="draw_arc", default='True',
                        help="")
        # Tick settings
        self.OptionParser.add_option("--n_ticks",
                        action="store", type="int", 
                        dest="n_ticks", default=5,
                        help="")
        self.OptionParser.add_option("--ticksize",
                        action="store", type="int", 
                        dest="ticksize", default=10,
                        help="")
        self.OptionParser.add_option("--n_subticks",
                        action="store", type="int", 
                        dest="n_subticks", default=10,
                        help="")
        self.OptionParser.add_option("--subticksize",
                        action="store", type="int", 
                        dest="subticksize", default=5,
                        help="")
        self.OptionParser.add_option("--style",
                        action="store", type="string", 
                        dest="style", default='marks_outwards',
                        help="Style of marks")
        # Label settings
        self.OptionParser.add_option("--labels_enabled", 
                        action="store", type="inkbool",
                        dest="labels_enabled", default='False',
                        help="")
        self.OptionParser.add_option("--rounding_level", 
                        action="store", type="int",
                        dest="rounding_level", default=0,
                        help="")
        self.OptionParser.add_option("--text_size",
                        action="store", type="int", 
                        dest="text_size", default=1,
                        help="")
        self.OptionParser.add_option("--text_offset",
                        action="store", type="int", 
                        dest="text_offset", default=20,
                        help="")
        self.OptionParser.add_option("--start_value",
                        action="store", type="float", 
                        dest="start_value", default=0,
                        help="")
        self.OptionParser.add_option("--stop_value",
                        action="store", type="float", 
                        dest="stop_value", default=10,
                        help="")
        # Dummy
        self.OptionParser.add_option("","--tab")

    def draw_knob_arc(self, radius, (cx, cy), parent, angle, transform='' ):

        start_point_angle = (angle - pi)/2.0
        end_point_angle = pi - start_point_angle
        
        style = {   'stroke'        : '#000000',
                    'stroke-width'  : str(self.options.linewidth),
                    'fill'          : 'none'            }
        ell_attribs = {'style':simplestyle.formatStyle(style),
            inkex.addNS('cx','sodipodi')        :str(cx),
            inkex.addNS('cy','sodipodi')        :str(cy),
            inkex.addNS('rx','sodipodi')        :str(radius),
            inkex.addNS('ry','sodipodi')        :str(radius),
            inkex.addNS('start','sodipodi')     :str(end_point_angle),
            inkex.addNS('end','sodipodi')       :str(start_point_angle),
            inkex.addNS('open','sodipodi')      :'true',    #all ellipse sectors we will draw are open
            inkex.addNS('type','sodipodi')      :'arc',
            'transform'                         :transform
            
                }
        ell = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )    
    
    def draw_circle_mark(self, radius, mark_angle, mark_length, parent):    
        
        cx = radius*cos(mark_angle)
        cy = radius*sin(mark_angle)
        r = mark_length / 2.0
        
        style = { 
                'stroke': '#000000',
                'stroke-width':'0',
                'fill': '#000000' 
                }
        
        circ_attribs = {
                'style':simplestyle.formatStyle(style),
                'cx':str(cx),
                'cy':str(cy),
                'r':str(r)
                }
        circle = inkex.etree.SubElement(parent, inkex.addNS('circle','svg'), circ_attribs )
        
    def draw_knob_line_mark(self, radius, mark_angle, mark_length, parent):    
        x1 = radius*cos(mark_angle)
        y1 = radius*sin(mark_angle)
        x2 = (radius + mark_length)*cos(mark_angle)
        y2 = (radius + mark_length)*sin(mark_angle)
        
        line_style   = { 'stroke': '#000000',
                         'stroke-width': str(self.options.linewidth),
                         'fill': 'none'
                       }
    
        line_attribs = {'style' : simplestyle.formatStyle(line_style),
                        inkex.addNS('label','inkscape') : "none",
                        'd' : 'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}
    
        line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )
    
    def draw_tick(self, radius, mark_angle, mark_size, parent):
        if (self.options.style == 'marks_inwards') or (self.options.style == 'marks_outwards'):
            self.draw_knob_line_mark(radius, mark_angle, mark_size, parent)
        elif self.options.style == 'marks_circles':
            self.draw_circle_mark(radius, mark_angle, mark_size, parent)
    
    def effect(self):
        
        parent = self.current_layer
        offset = computePointInNode(list(self.view_center), self.current_layer) #the offset require to centre the triangle
        self.options.radius = self.unittouu(str(self.options.radius) + 'px')
        
        radius = self.options.radius
        angle = self.options.angle*pi/180.0
        n_ticks = self.options.n_ticks
        n_subticks = self.options.n_subticks
        is_outer = True
        if self.options.style == 'marks_inwards':
            is_outer = False

        tick_length = self.options.ticksize
        subtick_length = self.options.subticksize
        subtick_radius = radius
        arc_radius = radius
        
        
        # Labeling settings
        start_num = self.options.start_value
        end_num = self.options.stop_value
        text_spacing = self.options.text_offset
        text_size = self.options.text_size

        if not is_outer:
            subtick_radius = radius + tick_length - subtick_length
            arc_radius = radius + tick_length
        
        if self.options.draw_arc:
            self.draw_knob_arc(arc_radius, (0, 0), parent, angle)
        
        ticks_delta = angle / (n_ticks - 1)
        start_ticks_angle = 1.5*pi - 0.5*angle
        for tick in range(n_ticks):            
            self.draw_tick(radius, start_ticks_angle + ticks_delta*tick, 
                                tick_length, parent)        
            
            if self.options.labels_enabled:                
                if self.options.rounding_level > 0:
                    tick_text = str(round(start_num + 
                                          float(tick) * (end_num - start_num) / n_ticks, 
                                          self.options.rounding_level))
                else:
                    tick_text = str(int(start_num + float(tick) * (end_num - start_num) / n_ticks))
                    
                draw_text(tick_text, radius + tick_length + text_spacing, 
                          start_ticks_angle + ticks_delta*tick, 
                          text_size,
                          parent)
            
            if tick == (n_ticks - 1):
                break
            
            subticks_delta = ticks_delta / (n_subticks + 1)
            subtick_start_angle = start_ticks_angle + ticks_delta*tick + subticks_delta            
            for subtick in range(n_subticks):
                self.draw_tick(subtick_radius, subtick_start_angle + subticks_delta*subtick, 
                                    subtick_length, parent)
        
        
        
        
        

if __name__ == '__main__':
    e = Knob_Scale()
    e.affect()

