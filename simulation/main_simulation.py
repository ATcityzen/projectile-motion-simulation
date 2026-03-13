from vpython import *
launched = False

def launch(b):
    global launched
    launched = True

button(text="Launch 🚀", bind=launch)
scene.append_to_caption("\nInitial Speed: ")
speed_input = winput(text='20')

scene.append_to_caption("\nLaunch Angle: ")
angle_input = winput(text='45')

scene.append_to_caption("\nDrag Coefficient: ")
drag_input = winput(text='0.1')scene.width = 900
scene.height = 500
scene.background = vector(0.05,0.05,0.1)
scene.center = vector(20,5,0)
scene.range = 40
scene.title = "Projectile Motion Simulation"
# PARAMETERS
g = vector(0,-9.81,0)     # gravity
m = 1                     # mass
dt = 0.01                 # timestep

# INITIAL CONDITIONS

if mode == "2D":
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), 0)

elif mode == "3D":
    z_speed = 5
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), z_speed)

else:
    print("Invalid mode, defaulting to 2D")
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), 0)
# CREATE OBJECTS
sun = sphere(
    pos=vector(-80,80,-100),
    radius=20,
    color=color.yellow,
    emissive=True
)

local_light(pos=sun.pos, color=color.yellow)
ground = box(pos=vector(25,-0.5,0), size=vector(100,1,20), color=vector(0.2,0.8,0.2))
cannon_base = cylinder(
    pos=vector(0,0,0),
    axis=vector(2,0,0),
    radius=0.5,
    color=color.gray(0.6)
)
ball = sphere(
    pos=vector(0,0,0),
    radius=0.5,
    color=color.red,
    make_trail=True,
    trail_radius=0.1
)
info = label(
    pos=vector(10,15,0),
    text="",
    box=False,
    height=16,
    color=color.white
)
# SIMULATION LOOP
while ball.pos.y >= 0:

    rate(100)

    # camera follows the projectile
    scene.center = ball.pos
    scene.range = max(30, ball.pos.x*0.6 + 10)

    info.text = f"Position: {ball.pos}\nVelocity: {velocity}"

    acceleration = g - (k/m)*velocity

    velocity = velocity + acceleration*dt

    ball.pos = ball.pos + velocity*dt
