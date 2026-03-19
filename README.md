### physics project   **Grade 11 Physics: 3D Kinematics Simulation**
**St. John's Baptist De La Salle Catholic School**
The projectile motion is modeled using Newton's Second Law.

The projectile experiences two forces:

1. Gravitational force
2. Air resistance (drag) force

### Gravitational force

Gravity acts downward only:

F_g = mg

where g = (0, -9.81, 0)

### Drag Force

Drag acts opposite to the velocity vector:

F_drag = -kv

where
k = drag coefficient
v = velocity vector

### The total Force

The total force acting on the projectile is:

F_total = mg - k v

Using Newton's Second Law:

m dv/dt = mg - k v

### Numerical Integration

The simulation uses Euler integration to update the motion step-by-step.

Velocity update:

v = v + a dt

Position update:

x = x + v dt
