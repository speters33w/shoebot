import cairo
import pango
import pangocairo
from shoebot.data import Grob, BezierPath, TransformMixin, ColorMixin, _copy_attrs
from shoebot.util import RecordingSurfaceA8

class Text(Grob, TransformMixin, ColorMixin):

    def __init__(self, canvas, text, x=0, y=0, width=None, height=None, outline=False, ctx=None, **kwargs):
        Grob.__init__(self, canvas)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, canvas, **kwargs)

        self.ctx = ctx
        self.pang_ctx = None

        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._fontfile = kwargs.get('font', canvas.fontfile)
        self._fontsize = kwargs.get('fontsize', canvas.fontsize)
        self._lineheight = kwargs.get('lineheight', canvas.lineheight)
        self._align = kwargs.get('align', canvas.align)

        # here we start to do the magic with pango, first we set typeface    
        self._fontface = pango.FontDescription()
        self._fontface.set_family(self._fontfile)

        # then the font weight
        self._weight = pango.WEIGHT_NORMAL
        if kwargs.has_key("weight"):
            if kwargs["weight"]=="ultralight":
                self._weight = pango.WEIGHT_ULTRALIGHT
            if kwargs["weight"]=="light":
                self._weight = pango.WEIGHT_LIGHT
            if kwargs["weight"]=="bold":
                self._weight = pango.WEIGHT_BOLD
            if kwargs["weight"]=="ultrabold":
                self._weight = pango.WEIGHT_ULTRABOLD
            if kwargs["weight"]=="heavy":
                self._weight = pango.WEIGHT_HEAVY                                                
        self._fontface.set_weight(self._weight)

        # the variant
        self._variant = pango.VARIANT_NORMAL
        if kwargs.has_key("variant"):
            if kwargs["variant"]=="small-caps" or kwargs["variant"]=="smallcaps":
                self._variant = pango.VARIANT_SMALL_CAPS
        self._fontface.set_variant(self._variant)

        # the style        
        self._style = pango.STYLE_NORMAL
        if kwargs.has_key("style"):
            if kwargs["style"]=="italic" or kwargs["style"]=="oblique":
                self._style = pango.STYLE_ITALIC
        self._fontface.set_style(self._style)       
        # the stretch
        self._stretch = pango.STRETCH_NORMAL
        if kwargs.has_key("stretch"):
            if kwargs["stretch"]=="ultracondensed" or kwargs["stretch"]=="ultra-condensed":
                self._stretch = pango.STRETCH_ULTRA_CONDENSED
            if kwargs["stretch"]=="condensed":
                self._stretch = pango.STRETCH_CONDENSED
            if kwargs["stretch"]=="expanded":
                self._stretch = pango.STRETCH_EXPANDED            
            if kwargs["stretch"]=="ultraexpanded" or kwargs["stretch"]=="ultra-expanded":
                self._stretch = pango.STRETCH_ULTRA_EXPANDED
        self._fontface.set_stretch(self._stretch)                                              
        # then we set fontsize (multiplied by pango.SCALE)
        if kwargs.has_key("fontsize"):
            self._fontsize = kwargs["fontsize"] 
        self._fontface.set_absolute_size(self._fontsize*pango.SCALE)
        if kwargs.has_key("lineheight"):
            self._lineheight = kwargs["lineheight"]           
        if kwargs.has_key("align"):
            self._align= kwargs["align"]

        
        if bool(ctx):
            self._render(self.ctx)
        else:
            # Normal rendering, can be deferred
            self._canvas.drawqueue.append(self._render)

    def _get_context(self):
        self.ctx = self.ctx or cairo.Context(RecordingSurfaceA8(0, 0))
        return self.ctx

    def _render(self, ctx = None):
        ctx = ctx or self._get_context()
        ctx.move_to(self.x,self.y)
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout
        self.pang_ctx = pangocairo.CairoContext(ctx)
        self.layout = self.pang_ctx.create_layout()
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        self.layout.set_spacing(((self._lineheight-1)*self._fontsize)*pango.SCALE)
        # we pass pango font description and the text to the pango layout
        self.layout.set_font_description(self._fontface)
        self.layout.set_text(self.text)
        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self.layout.set_width(self.width*pango.SCALE)
            if kwargs.has_key("indent"):
                self.layout.set_indent(kwargs["indent"]*pango.SCALE)                
        # set text alignment    
        if self._align == "right":
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        elif self._align == "center":
            self.layout.set_alignment(pango.ALIGN_CENTER)
        elif self._align == "justify":
            self.layout.set_alignment(pango.ALIGN_LEFT)
            self.layout.set_justify(True)
        else:
            self.layout.set_alignment(pango.ALIGN_LEFT)

        ctx.set_source_rgba(*self._strokecolor)
        self.pang_ctx.show_layout(self.layout)
        self.pang_ctx.update_layout(self.layout)
        


    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    #def _get_baseline(self):
        #self.iter = self.layout.get_iter()
        #baseline_y = self.iter.get_baseline()
        #baseline_delta = baseline_y/pango.SCALE
        #return (baseline_delta)
    #baseline = property(_get_baseline)

    def _get_baseline(self):
        # retrieves first line of text block
        first_line = self.layout.get_line(0)
        # get the logical extents rectangle of first line
        first_line_extent = first_line.get_extents()[1]
        # get the descent value, in order to calculate baseline position
        first_line_descent = pango.DESCENT(first_line.get_extents()[1])
        # gets the baseline offset from the top of thext block
        baseline_delta = (first_line_extent[3]-first_line_descent)/pango.SCALE
        return (baseline_delta)
    baseline = property(_get_baseline)

    
    def _get_metrics(self):
        w,h = self.layout.get_pixel_size()
        return (w,h)
    metrics = property(_get_metrics)

    def _get_path(self):
        if not self.pang_ctx:
            self._render()
        # add pango layout to current cairo path in temporary context
        self.pang_ctx.layout_path(self.layout)
        # retrieve current path from current context
        pathdata = self._get_context().copy_path()
        # creates a BezierPath instance for storing new shoebot path
        p = BezierPath(self._canvas)
        # parsing of cairo path to build a shoebot path
        for item in pathdata:
            cmd = item[0]
            args = item[1]
            if cmd == 0: # moveto
                p.moveto(*args)
            elif cmd == 1: # lineto
                p.lineto(*args)
            elif cmd == 2: # curveto
                p.curveto(*args)
            elif cmd == 3: # close
                p.closepath()
        return p
        # cairo function for freeing path memory
        pathdata.path_destroy()
    path = property(_get_path)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        w,h = self.layout.get_pixel_size()
        x = (self.x+w/2)
        y = (self.y+h/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
            ('x', 'y', 'width', 'height', '_transform', '_transformmode',
            '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new

