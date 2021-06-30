import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import pyrr
import numpy as np
from moves import train, punch, move, spec, comp
from PIL import Image

vertex_shader = """
# version 330

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 v_color;

void main()
{   
    gl_Position = projection * view * model * vec4(position, 1.0f);
    v_color = color;
}
"""

fragment_shader = """
# version 330

in vec3 v_color;
out vec4 out_color;

void main()
{
    out_color = vec4(v_color, 1.0f);
}
"""


def initialize():
    if not glfw.init():
        raise Exception("glfw can not be initialized!")

    display = (1280, 720)  
    window = glfw.create_window(display[0], display[1], "OpenGL window", None, None)

    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

    glfw.make_context_current(window)

    vertices = np.array([np.array(train, dtype=np.float32),
                         np.array(punch, dtype=np.float32),
                         np.array(move,  dtype=np.float32),
                         np.array(spec,  dtype=np.float32),
                         np.array(comp,  dtype=np.float32)], dtype=object)

    all_indices = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10,  # legs
                   13, 12, 12, 11, 11, 5,  # torso + head
                   12, 14, 14, 15, 15, 16, 16, 17, 12, 18, 18, 19, 19, 20, 20, 21]  # arms

    indices = np.array(all_indices, dtype=np.uint32)

    '''
    MAIN VAO, VBO and EBO
    '''

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices[0].nbytes, vertices[0], GL_DYNAMIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)  # position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices[0].itemsize * 6, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)  # color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertices[0].itemsize * 6, ctypes.c_void_p(3 * 4))

    glBindVertexArray(0)

    '''
    SHADER LOGIC
    '''

    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    glUseProgram(shader)

    projection_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")
    model_loc = glGetUniformLocation(shader, "model")

    '''
    VIEWPORT AND CAMERA
    '''

    projection = pyrr.matrix44.create_perspective_projection_matrix(60, (display[0] / display[1]), 0.1, 2000)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)

    view = pyrr.matrix44.create_look_at([0, 0, 800], [0, 350, 0], [0, 1, 0])
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    '''
    SETUP
    '''

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.2, 0.2, 0.3, 0.25)
    glLineWidth(2.5)
    anim_index = 0
    frame_index = 0
    counter = 0
    completed = False
    frame_count = 0
    capture_count = 0

    '''
    MAIN LOOP
    '''

    while not glfw.window_should_close(window):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Render Here

        translate = pyrr.Matrix44.from_translation([0, 0, 0])
        model = translate

        glBindVertexArray(vao)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glDrawElements(GL_LINES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        if frame_count % 50 == 0:

            if frame_index < len(vertices[anim_index]) - 1 and not completed:
                frame_index += 1
            elif not completed:
                frame_index = 0
                if anim_index < len(vertices) - 1:
                    anim_index += 1
                else:
                    completed = True
                    anim_index = 0

        frame_count += 1

        glfw.set_window_title(window, 'anim: ' + str(anim_index) + ' - frame: ' + str(frame_index))
        glBufferData(GL_ARRAY_BUFFER, vertices[anim_index].nbytes, vertices[anim_index][frame_index], GL_DYNAMIC_DRAW)

        view = pyrr.matrix44.create_look_at([800 * np.cos(counter), 800, 800 * np.sin(counter)], [0, 350, 0],
                                            [0, 1, 0])
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        counter += 0.0007

        '''if not completed:
            image_buffer = glReadPixels(0, 0, display[0], display[1], GL_RGBA, GL_UNSIGNED_BYTE)
            image_out = np.frombuffer(image_buffer, dtype=np.uint8)
            image_out = image_out.reshape(display[1], display[0], 4)
            img = Image.fromarray(image_out, 'RGBA')
            img_flip = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_flip.save(r"frames/image_out" + str(capture_count) + ".png")
            capture_count += 1'''

        glfw.swap_buffers(window)

        glfw.poll_events()

    glDeleteProgram(shader)
    glfw.terminate()


initialize()
