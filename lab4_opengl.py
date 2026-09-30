import sys
import math
from array import array
import glfw
import moderngl as mgl
import glm
from PIL import Image

VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_texcoord;
layout (location = 2) in vec3 in_normal;

out vec2 v_texcoord;
out vec3 v_normal;
out vec3 v_frag_pos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    vec4 world_pos = model * vec4(in_position, 1.0);
    v_frag_pos = world_pos.xyz;
    v_texcoord = in_texcoord;
    
    // Преобразование нормалей с учетом матрицы модели
    v_normal = mat3(transpose(inverse(model))) * in_normal;
    
    gl_Position = projection * view * world_pos;
}
"""

FRAGMENT_SHADER = """
#version 330 core

in vec2 v_texcoord;
in vec3 v_normal;
in vec3 v_frag_pos;

out vec4 fragColor;

uniform sampler2D u_texture;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;

void main() {
    // 1. Ambient (Фоновое освещение)
    float ambientStrength = 0.3;
    vec3 ambient = ambientStrength * lightColor;
    
    // 2. Diffuse (Диффузное / Рассеянное освещение)
    vec3 norm = normalize(v_normal);
    vec3 lightDir = normalize(lightPos - v_frag_pos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // 3. Specular (Блик)
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - v_frag_pos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    // Итоговый цвет с учетом текстуры
    vec4 texColor = texture(u_texture, v_texcoord);
    vec3 result = (ambient + diffuse + specular) * texColor.rgb;
    
    fragColor = vec4(result, texColor.a);
}
"""

def get_house_mesh():
    vertices = []

    cube_data = [
        # Задняя грань
        -0.8, -1.0, -0.8,  0.0, 0.0,   0.0,  0.0, -1.0,
         0.8, -1.0, -0.8,  1.0, 0.0,   0.0,  0.0, -1.0,
         0.8,  0.0, -0.8,  1.0, 1.0,   0.0,  0.0, -1.0,
         0.8,  0.0, -0.8,  1.0, 1.0,   0.0,  0.0, -1.0,
        -0.8,  0.0, -0.8,  0.0, 1.0,   0.0,  0.0, -1.0,
        -0.8, -1.0, -0.8,  0.0, 0.0,   0.0,  0.0, -1.0,

        # Передняя грань
        -0.8, -1.0,  0.8,  0.0, 0.0,   0.0,  0.0,  1.0,
         0.8, -1.0,  0.8,  1.0, 0.0,   0.0,  0.0,  1.0,
         0.8,  0.0,  0.8,  1.0, 1.0,   0.0,  0.0,  1.0,
         0.8,  0.0,  0.8,  1.0, 1.0,   0.0,  0.0,  1.0,
        -0.8,  0.0,  0.8,  0.0, 1.0,   0.0,  0.0,  1.0,
        -0.8, -1.0,  0.8,  0.0, 0.0,   0.0,  0.0,  1.0,

        # Левая грань
        -0.8,  0.0,  0.8,  1.0, 1.0,  -1.0,  0.0,  0.0,
        -0.8,  0.0, -0.8,  0.0, 1.0,  -1.0,  0.0,  0.0,
        -0.8, -1.0, -0.8,  0.0, 0.0,  -1.0,  0.0,  0.0,
        -0.8, -1.0, -0.8,  0.0, 0.0,  -1.0,  0.0,  0.0,
        -0.8, -1.0,  0.8,  1.0, 0.0,  -1.0,  0.0,  0.0,
        -0.8,  0.0,  0.8,  1.0, 1.0,  -1.0,  0.0,  0.0,

        # Правая грань
         0.8,  0.0,  0.8,  1.0, 1.0,   1.0,  0.0,  0.0,
         0.8,  0.0, -0.8,  0.0, 1.0,   1.0,  0.0,  0.0,
         0.8, -1.0, -0.8,  0.0, 0.0,   1.0,  0.0,  0.0,
         0.8, -1.0, -0.8,  0.0, 0.0,   1.0,  0.0,  0.0,
         0.8, -1.0,  0.8,  1.0, 0.0,   1.0,  0.0,  0.0,
         0.8,  0.0,  0.8,  1.0, 1.0,   1.0,  0.0,  0.0,

        # Нижняя грань
        -0.8, -1.0, -0.8,  0.0, 1.0,   0.0, -1.0,  0.0,
         0.8, -1.0, -0.8,  1.0, 1.0,   0.0, -1.0,  0.0,
         0.8, -1.0,  0.8,  1.0, 0.0,   0.0, -1.0,  0.0,
         0.8, -1.0,  0.8,  1.0, 0.0,   0.0, -1.0,  0.0,
        -0.8, -1.0,  0.8,  0.0, 0.0,   0.0, -1.0,  0.0,
        -0.8, -1.0, -0.8,  0.0, 1.0,   0.0, -1.0,  0.0,
    ]
    vertices.extend(cube_data)

    n_front = glm.normalize(glm.vec3(0.0, 0.8, 0.9))
    n_back  = glm.normalize(glm.vec3(0.0, 0.8, -0.9))
    n_left  = glm.normalize(glm.vec3(-0.9, 0.8, 0.0))
    n_right = glm.normalize(glm.vec3(0.9, 0.8, 0.0))

    pyramid_data = [
        # Передняя грань
        -0.8, 0.0,  0.8,  0.0, 0.0,  n_front.x, n_front.y, n_front.z,
         0.8, 0.0,  0.8,  1.0, 0.0,  n_front.x, n_front.y, n_front.z,
         0.0, 0.9,  0.0,  0.5, 1.0,  n_front.x, n_front.y, n_front.z,

        # Правая грань
         0.8, 0.0,  0.8,  0.0, 0.0,  n_right.x, n_right.y, n_right.z,
         0.8, 0.0, -0.8,  1.0, 0.0,  n_right.x, n_right.y, n_right.z,
         0.0, 0.9,  0.0,  0.5, 1.0,  n_right.x, n_right.y, n_right.z,

        # Задняя грань
         0.8, 0.0, -0.8,  0.0, 0.0,  n_back.x,  n_back.y,  n_back.z,
        -0.8, 0.0, -0.8,  1.0, 0.0,  n_back.x,  n_back.y,  n_back.z,
         0.0, 0.9,  0.0,  0.5, 1.0,  n_back.x,  n_back.y,  n_back.z,

        # Левая грань
        -0.8, 0.0, -0.8,  0.0, 0.0,  n_left.x,  n_left.y,  n_left.z,
        -0.8, 0.0,  0.8,  1.0, 0.0,  n_left.x,  n_left.y,  n_left.z,
         0.0, 0.9,  0.0,  0.5, 1.0,  n_left.x,  n_left.y,  n_left.z,
    ]
    vertices.extend(pyramid_data)

    return array('f', vertices)

class App:
    def __init__(self):
        if not glfw.init():
            raise RuntimeError("Не удалось инициализировать GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.width, self.height = 1024, 768
        self.window = glfw.create_window(self.width, self.height, "Лабораторная работа 4 - 3D OpenGL", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Не удалось создать окно GLFW")

        glfw.make_context_current(self.window)
        
        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.DEPTH_TEST)

        self.camera_dist = 5.0
        self.rot_x = 20.0
        self.rot_y = -30.0
        self.auto_rotate = True
        
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_mouse_pressed = False

        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_key_callback(self.window, self.key_callback)

        self.init_gl()

    def load_texture(self, filename="texture.png"):
        """Загрузка текстуры из файла или генерация шахматного узора."""
        try:
            img = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')
        except FileNotFoundError:
            img = Image.new('RGBA', (128, 128), (255, 255, 255, 255))
            pixels = img.load()
            for i in range(128):
                for j in range(128):
                    if (i // 16 + j // 16) % 2 == 0:
                        pixels[i, j] = (200, 50, 50, 255)
                    else:
                        pixels[i, j] = (230, 230, 230, 255)
                        
        texture = self.ctx.texture(img.size, 4, img.tobytes())
        texture.build_mipmaps()
        texture.filter = (mgl.NEAREST, mgl.NEAREST)
        return texture

    def init_gl(self):
        self.prog = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER
        )

        vertex_data = get_house_mesh()
        self.vbo = self.ctx.buffer(vertex_data)
        
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '3f 2f 3f', 'in_position', 'in_texcoord', 'in_normal')
            ]
        )

        self.texture = self.load_texture("bim.png")
        # self.texture = self.load_texture("bumbo.png")
        self.texture.use(location=0)
        self.prog['u_texture'].value = 0

        self.prog['lightPos'].value = (3.0, 4.0, 3.0)
        self.prog['lightColor'].value = (1.0, 1.0, 1.0)

    def mouse_button_callback(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.is_mouse_pressed = True
                self.last_mouse_x, self.last_mouse_y = glfw.get_cursor_pos(window)
            elif action == glfw.RELEASE:
                self.is_mouse_pressed = False

    def mouse_callback(self, window, xpos, ypos):
        if self.is_mouse_pressed:
            dx = xpos - self.last_mouse_x
            dy = ypos - self.last_mouse_y
            
            self.rot_y += dx * 0.4
            self.rot_x += dy * 0.4
            
            self.rot_x = max(-89.0, min(89.0, self.rot_x))
            
            self.last_mouse_x = xpos
            self.last_mouse_y = ypos

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key in (glfw.KEY_W, glfw.KEY_EQUAL): # W или +
                self.camera_dist = max(1.5, self.camera_dist - 0.3)
            elif key in (glfw.KEY_S, glfw.KEY_MINUS): # S или -
                self.camera_dist = min(15.0, self.camera_dist + 0.3)
                
            elif key == glfw.KEY_LEFT:
                self.rot_y -= 5.0
            elif key == glfw.KEY_RIGHT:
                self.rot_y += 5.0
            elif key == glfw.KEY_UP:
                self.rot_x = max(-89.0, self.rot_x - 5.0)
            elif key == glfw.KEY_DOWN:
                self.rot_x = min(89.0, self.rot_x + 5.0)
                
            elif key == glfw.KEY_SPACE and action == glfw.PRESS:
                self.auto_rotate = not self.auto_rotate

    def run(self):
        last_time = glfw.get_time()

        while not glfw.window_should_close(self.window):
            current_time = glfw.get_time()
            delta_time = current_time - last_time
            last_time = current_time

            if self.auto_rotate:
                self.rot_y += 20.0 * delta_time

            self.ctx.clear(0.52, 0.52, 0.55, 1.0, depth=1.0)

            self.width, self.height = glfw.get_framebuffer_size(self.window)
            aspect = self.width / max(1, self.height)
            projection = glm.perspective(glm.radians(45.0), aspect, 0.1, 100.0)

            cam_x = self.camera_dist * math.sin(glm.radians(self.rot_y)) * math.cos(glm.radians(self.rot_x))
            cam_y = self.camera_dist * math.sin(glm.radians(self.rot_x))
            cam_z = self.camera_dist * math.cos(glm.radians(self.rot_y)) * math.cos(glm.radians(self.rot_x))
            
            camera_pos = glm.vec3(cam_x, cam_y, cam_z)
            view = glm.lookAt(camera_pos, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))

            model = glm.mat4(1.0)

            self.prog['projection'].write(projection)
            self.prog['view'].write(view)
            self.prog['model'].write(model)
            self.prog['viewPos'].value = tuple(camera_pos)

            self.vao.render(mgl.TRIANGLES)

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        glfw.terminate()

if __name__ == "__main__":
    app = App()
    app.run()