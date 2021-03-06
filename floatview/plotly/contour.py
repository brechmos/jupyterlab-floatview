from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
import numpy as np
from ipywidgets import IntText

class GlueContourPlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], self.dimensions[1])
        self.DefaultLayoutScales("linear","linear");
        self.options['line_width'] = IntText(description = 'Lines width:', value = 1)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = IntText(description = 'Markers size:', value = 3)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new'],'selected.marker.size':v['new'],'unselected.marker.size':v['new']}), names='value')        
        self.options['ncontours'] = IntText(description = '# Contours:', value = 1)
        self.options['ncontours'].observe(lambda v:self.UpdateTraces({'ncontours':v['new']}), names='value')        
        self.options['nbins'] = IntText(description = 'Number of Bins', value = 40)
        self.options['nbins'].observe(lambda v:self.updateRender(), names='value')        
        
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id):
        heatmap, xedges, yedges = np.histogram2d(self.data[x_id].flatten().astype('float'), self.data[y_id].flatten().astype('float'), bins=self.options['nbins'].value)
        mod_heatmap = np.zeros(( self.options['nbins'].value+2, self.options['nbins'].value+2))
        mod_heatmap[1:-1,1:-1] = heatmap.T
        #d_val = self.data[x_id]
        #if hasattr(self.data[x_id].flatten(), 'codes'):
        #    d_val = self.data[x_id].flatten().codes
        
        traces = []
        trace = {
            'type': "contour",
            'colorscale':[[0, 'rgb(255,255,255)'], [1, 'rgb(0,0,0)']],'showlegend':False,
            'autocontour':False,'ncontours':self.options['ncontours'].value,
            'contours':{'coloring':'heatmap'},
            'x0': xedges[0]-(xedges[1]-xedges[0])/2,
            'dx': xedges[1]-xedges[0],
            'y0': yedges[0]-(yedges[1]-yedges[0])/2,
            'dy': yedges[1]-yedges[0],
            'z':mod_heatmap
        }
        if self.only_subsets == False:
            traces.append(trace)
        trace = {
            'type': "scattergl", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.options['marker_size'].value, 'color': 'rgba(0, 0, 0, 0.4)',
                'line' : { 'width' : self.options['line_width'].value, 'color' : 'rgba(0, 0, 0, 0.3)' }
            }),
            'x': self.data[x_id].flatten(),
            'y': self.data[y_id].flatten(),
        }
        if self.only_subsets == False:    
            traces.append(trace)
        for sset in self.data.subsets:
            color = sset.style.color
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': sset.label,
                'marker': dict({
                    'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                    'line' : { 'width' : self.options['line_width'].value, 'color' : '#000000'}      
                }),
                'selected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},
                'unselected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},                 
                'x': sset[x_id].flatten(),
                'y': sset[y_id].flatten(),
            }
            traces.append(trace)

        layout = {
            'title' : self.options['title'].value,
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value, 
                'type' : self.options['xscale'].value 
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'type' : self.options['yscale'].value
            },
            'showlegend': True,
        }        
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], self.dimensions[1])    
        if self.only_subsets == False:
            self.plotly_fig.data[1].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        self.plotly_fig.data[1].update(
            selectedpoints=ids,
            selected={'marker':{'color':'rgba(0, 0, 0, 0.4)', 'size': self.options['marker_size'].value}},
            unselected={'marker':{'color':'rgba(0, 0, 0, 0.1)', 'size': self.options['marker_size'].value}}
        )
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.x_scale_type = type
        if (axis ==  'yaxis'):
            self.y_scale_type = type
        self.plotly_fig.layout[axis].type = type

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)