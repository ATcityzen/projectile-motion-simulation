from vpython import *
mode = input("Choose simulation mode (2D or 3D): ")
# PARAMETERS
g = vector(0,-9.81,0)     # gravity
k = 0.1                   # drag coefficient
m = 1                     # mass
dt = 0.01                 # timestep

# INITIAL CONDITIONS
initial_speed = float(input("Enter initial speed: "))
angle = float(input("Enter launch angle (degrees): "))*pi/180

if mode == "2D":
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), 0)

elif mode == "3D":
    z_speed = 5
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), z_speed)

else:
    print("Invalid mode, defaulting to 2D")
    velocity = vector(initial_speed*cos(angle), initial_speed*sin(angle), 0)
# CREATE OBJECTS
ground = box(pos=vector(0,-0.5,0), size=vector(50,1,10), color=color.green)

ball = sphere(pos=vector(0,0,0), radius=0.3, color=color.red, make_trail=True)

# SIMULATION LOOP
while ball.pos.y >= 0:
    
    rate(100)

    acceleration = g - (k/m)*velocity

    velocity = velocity + acceleration*dt

    ball.pos = ball.pos + velocity*dt
