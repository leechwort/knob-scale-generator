#! /usr/bin/python
'''
Copyright (C) 2007 John Beard john.j.beard@gmail.com

##This extension allows you to draw a triangle given certain information
## about side length or angles.

##Measurements of the triangle

         C(x_c,y_c)                              
        /`__                                     
       / a_c``--__                               
      /           ``--__ s_a                     
 s_b /                  ``--__                   
    /a_a                    a_b`--__             
   /--------------------------------``B(x_b, y_b)
  A(x_a,y_a)         s_b                         


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


#draw an SVG line segment between the given (raw) points
def draw_knob_line_mark(radius, mark_angle, mark_length, parent):    
    x1 = radius*cos(mark_angle)
    y1 = radius*sin(mark_angle)
    x2 = (radius + mark_length)*cos(mark_angle)
    y2 = (radius + mark_length)*sin(mark_angle)
    
    line_style   = { 'stroke': '#000000',
                     'stroke-width': '1',
                     'fill': 'none'
                   }

    line_attribs = {'style' : simplestyle.formatStyle(line_style),
                    inkex.addNS('label','inkscape') : "none",
                    'd' : 'M '+str(x1)+','+str(y1)+' L '+str(x2)+','+str(y2)}

    line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

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
    
def draw_knob_arc(radius, (cx, cy), parent, angle, transform='' ):

    start_point_angle = (angle - pi)/2.0
    end_point_angle = pi - start_point_angle
    
    style = {   'stroke'        : '#000000',
                'stroke-width'  : '1',
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
        self.OptionParser.add_option("--radius",
                        action="store", type="int", 
                        dest="radius", default=100.0,
                        help="Radius of the knob in px")
        self.OptionParser.add_option("--n_ticks",
                        action="store", type="int", 
                        dest="n_ticks", default=5,
                        help="Radius of the knob in px")
        self.OptionParser.add_option("--n_subticks",
                        action="store", type="int", 
                        dest="n_subticks", default=10,
                        help="Radius of the knob in px")
        self.OptionParser.add_option("--angle",
                        action="store", type="float", 
                        dest="angle", default=260.0,
                        help="Angle of the knob scale in degrees")
    
    def effect(self):
        
        parent = self.current_layer
        offset = computePointInNode(list(self.view_center), self.current_layer) #the offset require to centre the triangle
        self.options.radius = self.unittouu(str(self.options.radius) + 'px')
        
        radius = self.options.radius
        angle = self.options.angle*pi/180.0
        n_ticks = self.options.n_ticks
        n_subticks = self.options.n_subticks
        is_outer = False
        tick_length = 10
        subtick_length = 5
        subtick_radius = radius
        arc_radius = radius
        
        
        # Labeling settings
        start_num = 0
        end_num = 5
        text_spacing = 10
        text_size = 10
        rounding_level = 0

        if not is_outer:
            subtick_radius = radius + tick_length - subtick_length
            arc_radius = radius + tick_length
        draw_knob_arc(arc_radius, (0, 0), parent, angle)
        
        ticks_delta = angle / (n_ticks - 1)
        start_ticks_angle = 1.5*pi - 0.5*angle
        for tick in range(n_ticks):            
            draw_knob_line_mark(radius, start_ticks_angle + ticks_delta*tick, 
                                tick_length, parent)        
            
            if rounding_level > 0:
                tick_text = str(round(start_num + float(tick) * (end_num - start_num) / n_ticks, rounding_level))
            else:
                tick_text = str(int(start_num + float(tick) * (end_num - start_num) / n_ticks))
            draw_text(tick_text,
                    radius + tick_length + text_spacing, 
                      start_ticks_angle + ticks_delta*tick, 
                      text_size,
                      parent)
            #draw_text(radius + tick_length, start_ticks_angle + ticks_delta*tick, parent)
            if tick == (n_ticks - 1):
                break
            
            subticks_delta = ticks_delta / (n_subticks + 1)
            subtick_start_angle = start_ticks_angle + ticks_delta*tick + subticks_delta            
            for subtick in range(n_subticks):
                draw_knob_line_mark(subtick_radius, subtick_start_angle + subticks_delta*subtick, 
                                    subtick_length, parent)
        
        
        
        
        

if __name__ == '__main__':
    e = Knob_Scale()
    e.affect()


# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
