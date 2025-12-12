import turtle
import random

# Constants
COLORS = [
    (255, 50, 100),    # Hot pink
    (100, 200, 255),   # Sky blue
    (50, 255, 150),    # Mint green
    (255, 200, 50),    # Golden
    (200, 100, 255),   # Purple
    (255, 100, 100),   # Red
    (50, 255, 255),    # Cyan
    (255, 150, 50),    # Orange
]

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800


class AbstractArt:
    """Create abstract artwork using turtle graphics with fade effects"""
    
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.bgcolor("#0a0e27")
        self.screen.colormode(255)
        self.screen.title("Abstract Turtle Art - with Fades")
        
        self.turtle = turtle.Turtle()
        self.turtle.hideturtle()
        self.turtle.speed(0)
        self.screen.tracer(False)
    
    def random_pos(self):
        """Get random position on canvas"""
        x = random.randint(-SCREEN_WIDTH // 2 + 50, SCREEN_WIDTH // 2 - 50)
        y = random.randint(-SCREEN_HEIGHT // 2 + 50, SCREEN_HEIGHT // 2 - 50)
        return x, y
    
    def fade_color(self, base_color, fade_factor):
        """Create faded color by blending with background"""
        bg_color = (10, 14, 39)  # Background color
        r = int(base_color[0] * fade_factor + bg_color[0] * (1 - fade_factor))
        g = int(base_color[1] * fade_factor + bg_color[1] * (1 - fade_factor))
        b = int(base_color[2] * fade_factor + bg_color[2] * (1 - fade_factor))
        return (r, g, b)
    
    def setup_pen(self, size=2):
        """Setup turtle with random color"""
        self.turtle.penup()
        self.turtle.goto(*self.random_pos())
        self.turtle.pencolor(random.choice(COLORS))
        self.turtle.pensize(random.randint(1, size))
    
    def draw_spirals(self):
        """Draw spiral circles with fade effect"""
        for _ in range(8):
            self.setup_pen(size=8)
            base_color = random.choice(COLORS)
            for j in range(20):
                # Fade effect: circle gets fainter as it grows
                fade = 1.0 - (j / 20)
                faded_color = self.fade_color(base_color, fade)
                self.turtle.pencolor(faded_color)
                self.turtle.pendown()
                self.turtle.circle(j * 2)
                self.turtle.penup()
                self.turtle.right(18)
    
    def draw_polygons(self):
        """Draw geometric shapes with fade effect"""
        for _ in range(15):
            self.turtle.penup()
            self.turtle.goto(*self.random_pos())
            base_color = random.choice(COLORS)
            sides = random.choice([3, 4, 5, 6, 8])
            size = random.randint(30, 100)
            angle = 360 / sides
            
            # Fade effect: lines fade in
            for step in range(3):
                fade = (step + 1) / 3
                self.turtle.pencolor(self.fade_color(base_color, fade))
                self.turtle.pensize(random.randint(1, 6))
                
                self.turtle.pendown()
                for _ in range(sides):
                    self.turtle.forward(size * (0.7 + step * 0.15))
                    self.turtle.right(angle)
                self.turtle.penup()
    
    def draw_lines(self):
        """Draw random line patterns with fade effect"""
        for _ in range(25):
            self.turtle.penup()
            self.turtle.goto(*self.random_pos())
            base_color = random.choice(COLORS)
            self.turtle.setheading(random.randint(0, 359))
            
            # Fade effect: line thickness and opacity decrease
            steps = random.randint(5, 15)
            for step in range(steps):
                fade = 1.0 - (step / steps)
                self.turtle.pencolor(self.fade_color(base_color, fade))
                self.turtle.pensize(max(1, random.randint(1, 4) * fade))
                
                self.turtle.pendown()
                self.turtle.forward(random.randint(20, 100))
                self.turtle.penup()
                self.turtle.right(random.randint(30, 120))
    
    def draw_stars(self):
        """Draw star burst patterns with fade effect"""
        for _ in range(10):
            self.setup_pen(size=5)
            base_color = random.choice(COLORS)
            spikes = random.randint(8, 16)
            spike_length = random.randint(50, 150)
            
            for j in range(spikes):
                # Fade effect: spikes fade out
                fade = 1.0 - (j / spikes)
                self.turtle.pencolor(self.fade_color(base_color, fade))
                self.turtle.pensize(max(1, int(5 * fade)))
                
                self.turtle.pendown()
                self.turtle.forward(spike_length)
                self.turtle.backward(spike_length)
                self.turtle.penup()
                self.turtle.right(360 / spikes)
    
    def draw_waves(self):
        """Draw curved wave patterns with fade effect"""
        for i in range(6):
            self.turtle.penup()
            self.turtle.goto(-SCREEN_WIDTH // 2, -SCREEN_HEIGHT // 2 + i * 130)
            base_color = random.choice(COLORS)
            
            # Fade effect: wave becomes fainter as it progresses
            for step in range(60):
                fade = 1.0 - (step / 60)
                self.turtle.pencolor(self.fade_color(base_color, fade))
                self.turtle.pensize(max(1, random.randint(2, 6) * fade))
                
                self.turtle.pendown()
                self.turtle.forward(15)
                self.turtle.right(random.randint(5, 15))
            self.turtle.penup()
    
    def draw_concentric(self):
        """Draw concentric circles with fade effect"""
        for _ in range(5):
            self.turtle.penup()
            self.turtle.goto(*self.random_pos())
            base_color = random.choice(COLORS)
            
            for j in range(1, 8):
                # Fade effect: inner circles are brighter, outer are fainter
                fade = j / 8
                self.turtle.pencolor(self.fade_color(base_color, fade))
                self.turtle.pensize(j)
                self.turtle.pendown()
                self.turtle.circle(j * 15)
                self.turtle.penup()
    
    def draw_dots(self):
        """Draw decorative dots with fade effect"""
        for _ in range(100):
            self.turtle.penup()
            self.turtle.goto(*self.random_pos())
            base_color = random.choice(COLORS)
            
            # Fade effect: dot brightness varies
            fade = random.uniform(0.3, 1.0)
            self.turtle.pencolor(self.fade_color(base_color, fade))
            self.turtle.pensize(random.randint(3, 10))
            self.turtle.dot(random.randint(5, 20))
    
    def add_title(self):
        """Add title text"""
        self.turtle.penup()
        self.turtle.goto(0, SCREEN_HEIGHT // 2 - 40)
        self.turtle.pencolor(255, 255, 255)
        self.turtle.write("Abstract Turtle Art - with Fades", align="center", 
                         font=("Arial", 20, "bold"))
    
    def render(self):
        """Draw all elements and display"""
        self.draw_spirals()
        self.draw_polygons()
        self.draw_lines()
        self.draw_stars()
        self.draw_waves()
        self.draw_concentric()
        self.draw_dots()
        self.add_title()
        
        self.screen.tracer(True)
        self.screen.update()
        self.screen.mainloop()


if __name__ == "__main__":
    art = AbstractArt()
    art.render()
