import pygame
import numpy as np
import sys

pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Лабораторная работа 3: Множество Жюлиа («Дендрит»)")

# Параметры
MAX_ITER = 250
C_PARAM = complex(0.0, 1.0)

INIT_X_MIN, INIT_X_MAX = -2.0, 2.0
INIT_Y_MIN, INIT_Y_MAX = -2.0, 2.0

x_min, x_max = INIT_X_MIN, INIT_X_MAX
y_min, y_max = INIT_Y_MIN, INIT_Y_MAX

# Состояние для ввода итераций с клавиатуры
input_active = False
input_text = ""

try:
    font = pygame.font.SysFont("monospace", 18)
except:
    font = pygame.font.Font(None, 24)

def generate_fractal(xmin, xmax, ymin, ymax, width, height, c, max_iter):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    xx, yy = np.meshgrid(x, y)
    z = xx + 1j * yy
    
    output = np.zeros(z.shape, dtype=float)
    mask = np.ones(z.shape, dtype=bool)
    
    z_temp = np.copy(z)
    for i in range(max_iter):
        if not np.any(mask):
            break
        z_temp[mask] = z_temp[mask]**2 + c
        diverged = (np.abs(z_temp) > 2.0) & mask
        
        if np.any(diverged):
            log_zn = np.log(np.abs(z_temp[diverged])) / 2.0
            nu = np.log(log_zn / np.log(2.0)) / np.log(2.0)
            output[diverged] = i + 1 - nu
            
        mask[diverged] = False
        
    return output

def create_color_surface(data, max_iter):
    h, w = data.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    
    inside = (data == 0)
    norm = data / max_iter
    
    r = np.clip((0.5 + 0.5 * np.cos(np.pi * (norm * 3.0 + 0.0))) * 220, 0, 255).astype(np.float32)
    g = np.clip((0.5 + 0.5 * np.cos(np.pi * (norm * 3.0 + 0.4))) * 180, 0, 255).astype(np.float32)
    b = np.clip((0.5 + 0.5 * np.cos(np.pi * (norm * 3.0 + 0.8))) * 255, 0, 255).astype(np.float32)
    
    rgb[..., 0] = (r * 0.85).astype(np.uint8)
    rgb[..., 1] = (g * 0.70).astype(np.uint8)
    rgb[..., 2] = (b * 0.95).astype(np.uint8)
    
    rgb[inside] = [8, 8, 14]
    
    return pygame.surfarray.make_surface(rgb.swapaxes(0, 1))

clock = pygame.time.Clock()
running = True
needs_redraw = True
surface = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            center_x = (x_min + x_max) / 2
            y_span = y_max - y_min
            x_span = y_span * (WIDTH / HEIGHT)
            x_min = center_x - x_span / 2
            x_max = center_x + x_span / 2
            
            needs_redraw = True
            
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    try:
                        val = int(input_text)
                        if val > 0:
                            MAX_ITER = max(5, min(10000, val)) # Ограничим от 5 до 10000
                            needs_redraw = True
                    except ValueError:
                        pass
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    input_active = False
                else:
                    if event.unicode.isdigit():
                        input_text += event.unicode
            else:
                if event.key == pygame.K_r:
                    aspect = WIDTH / HEIGHT
                    x_min, x_max = -2.0 * aspect, 2.0 * aspect
                    y_min, y_max = -2.0, 2.0
                    needs_redraw = True
                
                elif event.key == pygame.K_i:
                    input_active = True
                    input_text = str(MAX_ITER)
                
                elif event.key == pygame.K_UP:
                    MAX_ITER = min(10000, MAX_ITER + 25)
                    needs_redraw = True
                elif event.key == pygame.K_DOWN:
                    MAX_ITER = max(5, MAX_ITER - 25)
                    needs_redraw = True
                
        elif event.type == pygame.MOUSEBUTTONDOWN and not input_active:
            mouse_x, mouse_y = event.pos
            c_x = x_min + (mouse_x / WIDTH) * (x_max - x_min)
            c_y = y_min + (mouse_y / HEIGHT) * (y_max - y_min)
            
            if event.button == 1:
                span_x = (x_max - x_min) * 0.5
                span_y = (y_max - y_min) * 0.5
                
                x_min = c_x - span_x / 2
                x_max = c_x + span_x / 2
                y_min = c_y - span_y / 2
                y_max = c_y + span_y / 2
                needs_redraw = True
                
            elif event.button == 3:
                span_x = (x_max - x_min) * 2.0
                span_y = (y_max - y_min) * 2.0
                
                x_min = c_x - span_x / 2
                x_max = c_x + span_x / 2
                y_min = c_y - span_y / 2
                y_max = c_y + span_y / 2
                needs_redraw = True

    if needs_redraw:
        raw_data = generate_fractal(x_min, x_max, y_min, y_max, WIDTH, HEIGHT, C_PARAM, MAX_ITER)
        surface = create_color_surface(raw_data, MAX_ITER)
        needs_redraw = False

    if surface:
        screen.blit(surface, (0, 0))

    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    zoom_level = 4.0 / (x_max - x_min)

    texts = [
        f"Фрактал: Дендрит (Михаил)",
        f"Разрешение: {WIDTH}x{HEIGHT}",
        f"Масштаб (Zoom): {zoom_level:.1f}x",
        f"Центр: ({center_x:.4f}, {center_y:.4f})",
        f"Итерации: {MAX_ITER} (↑/↓ или 'I' для ввода)",
        f"ЛКМ: Приблизить | ПКМ: Отдалить | R: Сброс"
    ]
    
    for idx, txt in enumerate(texts):
        shadow_surf = font.render(txt, True, (0, 0, 0))
        text_surf = font.render(txt, True, (230, 230, 240))
        screen.blit(shadow_surf, (12, 12 + idx * 22))
        screen.blit(text_surf, (10, 10 + idx * 22))

    # Отрисовка поля ввода поверх всего, если оно активно
    if input_active:
        box_width, box_height = 300, 50
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Полупрозрачная подложка
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Рамка ввода
        pygame.draw.rect(screen, (40, 40, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (100, 150, 255), (box_x, box_y, box_width, box_height), 2)
        
        prompt_txt = f"Введите итерации: {input_text}_"
        txt_surf = font.render(prompt_txt, True, (255, 255, 255))
        screen.blit(txt_surf, (box_x + 15, box_y + 15))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()