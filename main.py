from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import BindTexture, RenderContext
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.effectwidget import shader_header
from kivy.clock import Clock
from kivy.core.window import Window
from time import gmtime

shader_header += '''
uniform vec3 iResolution;
uniform float iGlobalTime;
uniform float iChannelTime[4];
uniform vec3 iChannelResolution0;
uniform vec3 iChannelResolution1;
uniform vec3 iChannelResolution2;
uniform vec3 iChannelResolution3;

uniform vec4 iMouse;
uniform vec4 iDate;
uniform float iSampleRate;

'''

shader_base = '''\
void mainImage(out vec4 fragColor, in vec2 fragCoord){
    fragColor = vec4(.5, .5, .5, 1.0);
    fragColor *= texture2D(iChannel0, fragCoord);
}
'''

definition_template = '''
uniform %s iChannel0;
uniform %s iChannel1;
uniform %s iChannel2;
uniform %s iChannel3;

'''

shader_footer = '''
void main(void){
    mainImage(gl_FragColor, tex_coord0);
}
'''


class TextureChoice(BoxLayout):
    source = StringProperty('')


class ShaderWidget(Widget):
    shader_source = StringProperty(shader_base)
    iChannel0_source = StringProperty()
    iChannel1_source = StringProperty()
    iChannel2_source = StringProperty()
    iChannel3_source = StringProperty()
    iChannel0 = ObjectProperty()
    iChannel1 = ObjectProperty()
    iChannel2 = ObjectProperty()
    iChannel3 = ObjectProperty()
    ichannels_definition = StringProperty('')
    iGlobalTime = NumericProperty(0)
    iMouse = ListProperty([0, 0])

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        super(ShaderWidget, self).__init__(**kwargs)
        self.bind(iChannel0_source=self.update_definitions,
                  iChannel1_source=self.update_definitions,
                  iChannel2_source=self.update_definitions,
                  iChannel3_source=self.update_definitions,
                  ichannels_definition=self.update_definitions)

    def on_shader_source(self, *args):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = (
            shader_header +
            self.ichannels_definition +
            self.shader_source +
            shader_footer)

        if not shader.success:
            shader.fs = old_value
            app.warn('fs error')

    def update_definitions(self, *args):
        self.ichannels_definition = definition_template % (
            'samplerCube' if 'cube' in self.iChannel0_source else 'sampler2D',
            'samplerCube' if 'cube' in self.iChannel1_source else 'sampler2D',
            'samplerCube' if 'cube' in self.iChannel2_source else 'sampler2D',
            'samplerCube' if 'cube' in self.iChannel3_source else 'sampler2D')

    def update_glsl(self, dt):
        t = gmtime()
        self.iGlobalTime += dt
        self.canvas['iGlobalTime'] = self.iGlobalTime
        self.canvas['iResolution'] = self.size[0], self.size[1], 1.0
        self.canvas['iChannelTime'] = 0
        self.canvas['iDate'] = [t.tm_year, t.tm_mon, t.tm_mday, t.tm_sec]
        self.canvas['iSampleRate'] = 44100
        self.canvas['iMouse'] = 0.0, 0.0, 0.0, 0.0
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.iMouse = touch.pos
        else:
            return super(ShaderWidget, self).on_touch_move(touch)

    def on_iChannel0(self, *args):
        with self.canvas:
            BindTexture(texture=self.iChannel0, index=1)
        self.canvas['iChannel0'] = 1

    def on_iChannel1(self, *args):
        with self.canvas:
            BindTexture(texture=self.iChannel1, index=2)
        self.canvas['iChannel1'] = 2

    def on_iChannel2(self, *args):
        with self.canvas:
            BindTexture(texture=self.iChannel2, index=3)
        self.canvas['iChannel2'] = 3

    def on_iChannel3(self, *args):
        with self.canvas:
            BindTexture(texture=self.iChannel3, index=4)
        self.canvas['iChannel3'] = 4


class ShaderApp(App):
    def build(self):
        super(ShaderApp, self).build()
        Clock.schedule_interval(self.root.ids.shader.update_glsl, 0)

    def warn(self, message):
        print(message)

if __name__ == '__main__':
    app = ShaderApp()
    app.run()
