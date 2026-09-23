import tkinter as tk
import math, random

class FractalTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal tree")
 
        self.max_depth = 20
        self.current_depth = 0
        self.start_length = 150
        self.angle_spread = 30
        self.length_ratio = 0.75

        self.colorfull = ["red", "orange", "yellow", "green", "blue", "purple", "cyan", "pink"]
        
        width, height = 900, 700
        

        self.canvas = tk.Canvas(root, width=width, height=height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
  
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
   
        btn_back = tk.Button(
            control_frame, 
            text="< Prev", 
            command=self.prev_step,
            font=("Arial", 11),
            bg="#f0f0f0"
        )
        btn_back.pack(side=tk.LEFT, padx=8)
        
   
        btn_forward = tk.Button(
            control_frame, 
            text="Next >", 
            command=self.next_step,
            font=("Arial", 11),
            bg="#e0ffe0"
        )
        btn_forward.pack(side=tk.LEFT, padx=8)
        
        jump_frame = tk.Frame(control_frame)
        jump_frame.pack(side=tk.LEFT, padx=20)
        
        lbl = tk.Label(jump_frame, text="Level:", font=("Arial", 11))
        lbl.pack(side=tk.LEFT)
        
        self.depth_entry = tk.Entry(jump_frame, width=4, font=("Arial", 11))
        self.depth_entry.pack(side=tk.LEFT, padx=5)

        self.depth_entry.insert(0, "0")
        
        btn_jump = tk.Button(
            jump_frame, 
            text="Go!", 
            command=self.jump_to_level,
            font=("Arial", 11)
        )
        btn_jump.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            root, 
            text=f"Current Level is {self.current_depth} out {self.max_depth}", 
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        self.draw_tree()

    def draw_branch(self, x, y, length, angle, depth, target_depth):
        if depth > target_depth or length < 2:
            return

        end_x = x + math.sin(math.radians(angle)) * length
        end_y = y - math.cos(math.radians(angle)) * length 

        width = max(1, int((target_depth - depth + 1) / 2))

        self.canvas.create_line(x, y, end_x, end_y, fill=random.choice(self.colorfull), width=width)

        new_length = length * self.length_ratio
        self.draw_branch(end_x, end_y, new_length, angle - self.angle_spread, depth + 1, target_depth)
        self.draw_branch(end_x, end_y, new_length, angle + self.angle_spread, depth + 1, target_depth)

    def draw_tree(self):
        self.canvas.delete("all")
        
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        
        start_x = w // 2
        start_y = h - 5
        
        if self.current_depth > 0:
            self.draw_branch(start_x, start_y, self.start_length, 0, 1, self.current_depth)
        
        self.status_label.config(text=f"Current level is {self.current_depth} out {self.max_depth}")

    def next_step(self):
        if self.current_depth < self.max_depth:
            self.current_depth += 1
            self.draw_tree()
   
            self._update_entry_value()

    def prev_step(self):
        if self.current_depth > 0:
            self.current_depth -= 1
            self.draw_tree()
            self._update_entry_value()

    def jump_to_level(self):
        text = self.depth_entry.get().strip()

        if not text:
            return
        
        try:
            target = int(text)
        except ValueError:
            return

        target = max(0, min(target, self.max_depth))
        
        self.current_depth = target
        self.draw_tree()
        self._update_entry_value()

    def _update_entry_value(self):
        self.depth_entry.delete(0, tk.END)
        self.depth_entry.insert(0, str(self.current_depth))

def main():
    root = tk.Tk()
    app = FractalTreeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
