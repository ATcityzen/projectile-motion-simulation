# Physics Model – Projectile Motion with Drag

## Forces Acting on the Projectile

The projectile is affected by two forces:

### 1. Gravity

The gravitational force pulls the projectile downward.

F_g = m g

where
m = mass of the projectile
g = gravitational acceleration (9.81 m/s² downward)

### 2. Drag Force (Air Resistance)

Air resistance opposes the motion of the projectile.

F_drag = -k v

where
k = drag coefficient
v = velocity of the projectile

The negative sign means the drag force acts opposite the velocity.

## Total Force

The total force acting on the projectile is:

F_total = m g - k v

Using Newton's Second Law:

m dv/dt = m g - k v

## Acceleration

Dividing by mass:

a = g - (k/m)v

## Numerical Integration (Euler Method)

The simulation updates velocity and position using Euler integration.

Velocity update:

v = v + a * dt

Position update:

x = x + v * dt

where dt is a small time step.

This step-by-step process simulates the projectile's motion over time.
