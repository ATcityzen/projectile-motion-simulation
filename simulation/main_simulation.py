Web VPython 3.2

# ════════════════════════════════════════════════════════════════════
#  Projectile Motion Simulator + Physics Calculator  (Full 3D)
#  Axes: X = forward, Y = up, Z = sideways
#  Elevation angle θ  (angle_slider)  →  vertical launch angle
#  Azimuth   angle φ  (azim_slider)   →  horizontal direction (Z)
#  vx = v0·cos(θ)·cos(φ)
#  vy = v0·sin(θ)
#  vz = v0·cos(θ)·sin(φ)
# ════════════════════════════════════════════════════════════════════

scene.title = "Projectile Motion Simulator + Physics Calculator (3D)"
scene.width  = 960
scene.height = 360
scene.background = color.black
scene.userspin = False

G  = 9.81
DT = 0.01

velocity   = vector(0, 0, 0)
launched      = False
paused        = False
_launch_flash = 0          # countdown frames for Launch button animation
_peak_range   = 25         # scene.range captured at the trajectory peak
t          = 0
speed_mult = 3
mode3D     = False

# ── Scene objects ────────────────────────────────────────────────────
ground = box(pos=vector(60, -0.5, 0), size=vector(200, 1, 80),
             color=color.green, opacity=0.55)

# X / Y / Z axis arrows (shown in 3D mode)
ax_x = arrow(pos=vector(0,0,0), axis=vector(12,0,0), shaftwidth=0.3,
              color=color.red,   opacity=0)
ax_y = arrow(pos=vector(0,0,0), axis=vector(0,12,0), shaftwidth=0.3,
              color=color.green, opacity=0)
ax_z = arrow(pos=vector(0,0,0), axis=vector(0,0,12), shaftwidth=0.3,
              color=color.cyan,  opacity=0)
lbl_x = label(pos=vector(13,0,0),  text="X", box=False, height=12, color=color.red,   opacity=0)
lbl_y = label(pos=vector(0,13,0),  text="Y", box=False, height=12, color=color.green, opacity=0)
lbl_z = label(pos=vector(0,0,13),  text="Z", box=False, height=12, color=color.cyan,  opacity=0)

cannon = cylinder(pos=vector(0,0,0), axis=vector(3,0,0), radius=0.5, color=color.orange)
ball   = sphere(pos=vector(0,0,0), radius=0.6, color=color.red, make_trail=True)

# Live data label — pixel-pinned, draggable (origin = canvas centre)
lbl_px, lbl_py = 330, 140          # current pixel position
_drag_active   = False             # is the user dragging the panel?
_drag_origin   = vector(0, 0, 0)   # mouse pixel pos when drag started
_drag_lbl0     = vector(0, 0, 0)   # label pixel pos when drag started

data_label = label(pixel_pos=True, pos=vector(lbl_px, lbl_py, 0),
                   text="", box=True, border=6, height=12,
                   color=color.cyan, background=color.black,
                   opacity=0.75, align="left")

def _world_to_pixel(world_pos):
    """Convert a 3-D mouse position to canvas pixel coords (origin = centre)."""
    scale = scene.width / (2.0 * scene.range)
    return vector((world_pos.x - scene.center.x) * scale,
                  (world_pos.y - scene.center.y) * scale, 0)

def _on_mousedown(evt):
    global _drag_active, _drag_origin, _drag_lbl0, lbl_px, lbl_py
    mp = _world_to_pixel(evt.pos)
    # Hit-test: click must be within ~90 x 35 px of the label centre
    if abs(mp.x - lbl_px) < 90 and abs(mp.y - lbl_py) < 35:
        _drag_active = True
        _drag_origin = mp
        _drag_lbl0   = vector(lbl_px, lbl_py, 0)

def _on_mousemove(evt):
    global lbl_px, lbl_py
    if _drag_active:
        mp     = _world_to_pixel(evt.pos)
        delta  = mp - _drag_origin
        lbl_px = _drag_lbl0.x + delta.x
        lbl_py = _drag_lbl0.y + delta.y
        data_label.pos = vector(lbl_px, lbl_py, 0)

def _on_mouseup(evt):
    global _drag_active
    _drag_active = False

scene.bind('mousedown', _on_mousedown)
scene.bind('mousemove', _on_mousemove)
scene.bind('mouseup',   _on_mouseup)

# ── Extra visual objects ──────────────────────────────────────────────
shadow = sphere(pos=vector(0,0.08,0), radius=0.55, color=color.black, opacity=0.35)

vel_arrow = arrow(pos=vector(0,0,0), axis=vector(0,0.01,0),
                  shaftwidth=0.3, headwidth=0.6, headlength=0.6,
                  color=color.yellow, opacity=0)

# Acceleration arrow (magenta) — shown during flight
accel_arrow = arrow(pos=vector(0,0,0), axis=vector(0,-0.01,0),
                    shaftwidth=0.25, headwidth=0.5, headlength=0.5,
                    color=color.magenta, opacity=0)

peak_marker = sphere(pos=vector(0,0,0), radius=0.55,
                     color=color.yellow, opacity=0, emissive=True)
peak_label  = label(pos=vector(0,0,0), text="", box=True,
                    height=12, color=color.yellow, opacity=0,
                    background=color.black, border=4)
ideal_trail = curve(color=color.cyan, opacity=0, radius=0.15)

peak_highest = 0.0
peak_vec     = vector(0, 0, 0)

# ════════════════════════════════════════════════════════════════════
#  ROW 1 — Buttons
# ════════════════════════════════════════════════════════════════════
scene.append_to_caption("\n")

def do_launch(b):
    global velocity, launched, t, ideal_trail, peak_highest, peak_vec, _launch_flash
    _launch_flash = 130                          # start countdown
    b.text       = "🚀 Liftoff!"
    b.background = vector(0.0, 0.78, 0.22)       # bright green burst
    b.color      = color.white
    t = 0
    spd  = speed_slider.value
    elev = angle_slider.value * pi / 180
    azim = azim_slider.value  * pi / 180
    velocity = vector(spd * cos(elev) * cos(azim),
                      spd * sin(elev),
                      spd * cos(elev) * sin(azim))
    ball.pos = vector(0, 0, 0)
    ball.clear_trail()
    height_curve.delete()
    velocity_curve.delete()
    accel_curve.delete()
    launched = True

    # Reset peak tracking
    peak_highest = 0.0
    peak_vec     = vector(0, 0, 0)
    peak_marker.opacity  = 0
    peak_label.opacity   = 0
    vel_arrow.opacity    = 1
    accel_arrow.opacity  = 1

    # Draw ideal (no-drag) ghost trail
    ideal_trail.visible = False
    ideal_trail = curve(color=color.cyan, opacity=0.3, radius=0.15)
    gv0x = spd * cos(elev) * cos(azim)
    gv0y = spd * sin(elev)
    gv0z = spd * cos(elev) * sin(azim)
    g_tof = 2 * gv0y / G
    n_pts = 60
    for gi in range(n_pts + 1):
        gtt = gi * g_tof / n_pts
        gx  = gv0x * gtt
        gy  = gv0y * gtt - 0.5 * G * gtt * gtt
        gz  = gv0z * gtt
        ideal_trail.append(vector(gx, max(gy, 0), gz))

def do_pause(b):
    global paused
    paused = not paused
    if paused:
        b.text       = "▶ Resume"
        b.background = vector(0.65, 0.30, 0.02)   # amber  → paused
        b.color      = color.white
    else:
        b.text       = "⏸ Pause"
        b.background = vector(0.85, 0.85, 0.85)   # reset to normal
        b.color      = color.black

def do_toggle_dim(b):
    global mode3D
    mode3D = not mode3D
    if mode3D:
        scene.forward  = vector(-1, -0.4, -0.8)
        scene.userspin = True
        b.text       = "● 2D View"
        b.background = vector(0.07, 0.45, 0.18)   # green → active
        b.color      = color.white
        ax_x.opacity = 1;  ax_y.opacity = 1;  ax_z.opacity = 1
        lbl_x.opacity = 1; lbl_y.opacity = 1; lbl_z.opacity = 1
    else:
        scene.forward  = vector(0, 0, -1)
        scene.userspin = False
        b.text       = "3D View"
        b.background = vector(0.85, 0.85, 0.85)   # reset to normal
        b.color      = color.black
        ax_x.opacity = 0;  ax_y.opacity = 0;  ax_z.opacity = 0
        lbl_x.opacity = 0; lbl_y.opacity = 0; lbl_z.opacity = 0

def do_slow(b):
    global speed_mult
    speed_mult = 1
    _speed_select(btn_slow)

def do_normal(b):
    global speed_mult
    speed_mult = 3
    _speed_select(btn_normal)

def do_fast(b):
    global speed_mult
    speed_mult = 9
    _speed_select(btn_fast)

# ── helper: highlight the active speed button ────────────────────────
_ACTIVE_BG  = vector(0.07, 0.45, 0.18)   # green → selected
_RESET_BG   = vector(0.85, 0.85, 0.85)   # light gray → normal browser look

def _speed_select(active):
    for btn, lbl in ((btn_slow, "0.3x"), (btn_normal, "1x"), (btn_fast, "3x")):
        if btn is active:
            btn.background = _ACTIVE_BG
            btn.color      = color.white
            btn.text       = "● " + lbl
        else:
            btn.background = _RESET_BG
            btn.color      = color.black
            btn.text       = lbl

btn_launch = button(text="Launch 🚀", bind=do_launch)
btn_pause  = button(text="⏸ Pause",  bind=do_pause)
btn_dim    = button(text="3D View",   bind=do_toggle_dim)
scene.append_to_caption("&nbsp;&nbsp;<b>Speed:</b>&nbsp;")
btn_slow   = button(text="0.3x", bind=do_slow)
btn_normal = button(text="● 1x", bind=do_normal)
btn_fast   = button(text="3x",   bind=do_fast)

# Mark 1x as active on startup
btn_normal.background = _ACTIVE_BG
btn_normal.color      = color.white

# ════════════════════════════════════════════════════════════════════
#  ROW 2 — Sliders  (v₀ · θ elevation · φ azimuth · k drag)
# ════════════════════════════════════════════════════════════════════
scene.append_to_caption("\n<b>v&#8320;:</b>&nbsp;")
speed_slider = slider(min=5, max=80, value=20, step=1, length=140, bind=update_calc)
scene.append_to_caption("&nbsp;")
speed_wt = wtext(text="20 m/s")

scene.append_to_caption("&nbsp;&nbsp;<b>&theta; (elev):</b>&nbsp;")
angle_slider = slider(min=1, max=89, value=45, step=1, length=130, bind=update_calc)
scene.append_to_caption("&nbsp;")
angle_wt = wtext(text="45 deg")

scene.append_to_caption("&nbsp;&nbsp;<b>&phi; (azim):</b>&nbsp;")
azim_slider = slider(min=0, max=90, value=0, step=1, length=120, bind=update_calc)
scene.append_to_caption("&nbsp;")
azim_wt = wtext(text="0 deg")

scene.append_to_caption("&nbsp;&nbsp;<b>k:</b>&nbsp;")
drag_slider = slider(min=0, max=0.5, value=0.1, step=0.01, length=110, bind=update_calc)
scene.append_to_caption("&nbsp;")
drag_wt = wtext(text="0.10")

# ════════════════════════════════════════════════════════════════════
#  CALCULATOR RESULTS — compact inline rows
# ════════════════════════════════════════════════════════════════════
scene.append_to_caption("""
<hr style="margin:5px 0;border-color:#334155;">
<span style="color:#38bdf8;font-weight:bold;">&#9632; Ideal (XY-plane)</span>&nbsp;
<span style="color:#555">ToF=</span>""")
r_tof_i = wtext(text="--")
scene.append_to_caption("""s&nbsp;
<span style="color:#555">H=</span>""")
r_maxh_i = wtext(text="--")
scene.append_to_caption("""m&nbsp;
<span style="color:#555">R&#8339;=</span>""")
r_rng_i = wtext(text="--")
scene.append_to_caption("""m&nbsp;
<span style="color:#555">tPeak=</span>""")
r_peak_i = wtext(text="--")
scene.append_to_caption("""s&nbsp;
<span style="color:#555">v&#8320;x=</span>""")
r_v0x = wtext(text="--")
scene.append_to_caption("""m/s&nbsp;
<span style="color:#555">v&#8320;y=</span>""")
r_v0y = wtext(text="--")
scene.append_to_caption("""m/s&nbsp;
<span style="color:#555">v&#8320;z=</span>""")
r_v0z = wtext(text="--")
scene.append_to_caption("m/s")

scene.append_to_caption("""
<br><span style="color:#facc15;font-weight:bold;">&#9632; Drag</span>&nbsp;
<span style="color:#555">ToF=</span>""")
r_tof_d = wtext(text="--")
scene.append_to_caption("""s&nbsp;
<span style="color:#555">H=</span>""")
r_maxh_d = wtext(text="--")
scene.append_to_caption("""m&nbsp;
<span style="color:#555">R&#8339;=</span>""")
r_rng_d = wtext(text="--")
scene.append_to_caption("""m&nbsp;
<span style="color:#555">tPeak=</span>""")
r_peak_d = wtext(text="--")
scene.append_to_caption("s")

scene.append_to_caption("""
<br><span style="color:#a78bfa;font-weight:bold;">&#9632; At t=</span>&nbsp;""")
t_slider = slider(min=0, max=15, value=1, step=0.1, length=110, bind=update_calc)
scene.append_to_caption("&nbsp;")
t_wt = wtext(text="1.0 s")
scene.append_to_caption("""&nbsp;&nbsp;
<span style="color:#38bdf8">Ideal:</span> x=<b>""")
q_xi = wtext(text="--")
scene.append_to_caption("</b> y=<b>")
q_yi = wtext(text="--")
scene.append_to_caption("</b> z=<b>")
q_zi = wtext(text="--")
scene.append_to_caption("</b> v=<b>")
q_vi = wtext(text="--")
scene.append_to_caption("""</b>m/s&nbsp;&nbsp;
<span style="color:#facc15">Drag:</span> x=<b>""")
q_xd = wtext(text="--")
scene.append_to_caption("</b> y=<b>")
q_yd = wtext(text="--")
scene.append_to_caption("</b> z=<b>")
q_zd = wtext(text="--")
scene.append_to_caption("</b> v=<b>")
q_vd = wtext(text="--")
scene.append_to_caption("</b>m/s")

# ── Acceleration row ────────────────────────────────────────────────
scene.append_to_caption("""
<br><span style="color:#c084fc;font-weight:bold;">&#9632; Acceleration at t</span>&nbsp;&nbsp;
<span style="color:#38bdf8">Ideal:</span>
&nbsp;ax=<b>""")
q_axi = wtext(text="--")
scene.append_to_caption("</b> ay=<b>")
q_ayi = wtext(text="--")
scene.append_to_caption("</b> az=<b>")
q_azi = wtext(text="--")
scene.append_to_caption("""</b> m/s&#178;&nbsp;
<span style="color:#c084fc">|a|=<b>""")
q_ai = wtext(text="--")
scene.append_to_caption("""</b> m/s&#178;</span>&nbsp;&nbsp;&nbsp;
<span style="color:#facc15">Drag:</span>
&nbsp;ax=<b>""")
q_axd = wtext(text="--")
scene.append_to_caption("</b> ay=<b>")
q_ayd = wtext(text="--")
scene.append_to_caption("</b> az=<b>")
q_azd = wtext(text="--")
scene.append_to_caption("""</b> m/s&#178;&nbsp;
<span style="color:#c084fc">|a|=<b>""")
q_ad = wtext(text="--")
scene.append_to_caption("</b> m/s&#178;</span>")

scene.append_to_caption("""
<hr style="margin:5px 0;border-color:#334155;">
""")

# ════════════════════════════════════════════════════════════════════
#  GRAPHS
# ════════════════════════════════════════════════════════════════════
graph1 = graph(title="Height vs Time", xtitle="t (s)", ytitle="y (m)",
               align="left", width=460, height=160)
height_curve = gcurve(color=color.cyan)

graph2 = graph(title="Speed vs Time", xtitle="t (s)", ytitle="v (m/s)",
               align="left", width=460, height=160)
velocity_curve = gcurve(color=color.yellow)

graph3 = graph(title="Acceleration Magnitude vs Time", xtitle="t (s)", ytitle="|a| (m/s²)",
               align="left", width=460, height=160)
accel_curve = gcurve(color=color.magenta)

# ════════════════════════════════════════════════════════════════════
#  Physics helpers
# ════════════════════════════════════════════════════════════════════

def r2(x):
    return str(round(x, 2))

def r1(x):
    return str(round(x, 1))

def calc_ideal(spd, elev, azim):
    e = elev * pi / 180
    a = azim * pi / 180
    v0x = spd * cos(e) * cos(a)
    v0y = spd * sin(e)
    v0z = spd * cos(e) * sin(a)
    tof  = 2 * v0y / G
    maxh = v0y * v0y / (2 * G)
    rng  = sqrt(v0x*v0x + v0z*v0z) * tof
    return tof, maxh, rng, tof / 2, v0x, v0y, v0z

def sim_drag_3d(spd, elev, azim, k):
    e = elev * pi / 180
    a = azim * pi / 180
    vx = spd * cos(e) * cos(a)
    vy = spd * sin(e)
    vz = spd * cos(e) * sin(a)
    x, y, z, ts = 0.0, 0.0, 0.0, 0.0
    maxh, peak_t = 0.0, 0.0
    while True:
        vx = vx + (-k * vx) * DT
        vy = vy + (-G - k * vy) * DT
        vz = vz + (-k * vz) * DT
        x  = x + vx * DT
        y  = y + vy * DT
        z  = z + vz * DT
        ts = ts + DT
        if y > maxh:
            maxh   = y
            peak_t = ts
        if y < 0 or ts > 400:
            break
    rng = sqrt(x*x + z*z)
    return ts, maxh, rng, peak_t

def at_time_ideal_3d(spd, elev, azim, qt):
    e   = elev * pi / 180
    a   = azim * pi / 180
    v0x = spd * cos(e) * cos(a)
    v0y = spd * sin(e)
    v0z = spd * cos(e) * sin(a)
    xi  = v0x * qt
    yi  = v0y * qt - 0.5 * G * qt * qt
    zi  = v0z * qt
    vyi = v0y - G * qt
    vi  = sqrt(v0x*v0x + vyi*vyi + v0z*v0z)
    if yi < 0:
        yi = 0
    # Ideal acceleration: only gravity acts (no drag)
    axi = 0.0
    ayi = -G
    azi = 0.0
    ai  = G
    return round(xi,2), round(yi,2), round(zi,2), round(vi,2), round(axi,2), round(ayi,2), round(azi,2), round(ai,2)

def at_time_drag_3d(spd, elev, azim, k, qt):
    e  = elev * pi / 180
    a  = azim * pi / 180
    vx = spd * cos(e) * cos(a)
    vy = spd * sin(e)
    vz = spd * cos(e) * sin(a)
    xd, yd, zd, ts = 0.0, 0.0, 0.0, 0.0
    while ts < qt:
        vx = vx + (-k * vx) * DT
        vy = vy + (-G - k * vy) * DT
        vz = vz + (-k * vz) * DT
        xd = xd + vx * DT
        yd = yd + vy * DT
        zd = zd + vz * DT
        ts = ts + DT
        if yd < 0:
            break
    vd  = sqrt(vx*vx + vy*vy + vz*vz)
    # Drag acceleration components at this moment
    axd = -k * vx
    ayd = -G - k * vy
    azd = -k * vz
    ad  = sqrt(axd*axd + ayd*ayd + azd*azd)
    if yd < 0:
        yd = 0
    return round(xd,2), round(yd,2), round(zd,2), round(vd,2), round(axd,2), round(ayd,2), round(azd,2), round(ad,2)

def update_calc(evt):
    spd  = speed_slider.value
    elev = angle_slider.value
    azim = azim_slider.value
    k    = drag_slider.value
    qt   = t_slider.value

    speed_wt.text = r1(spd) + " m/s"
    angle_wt.text = r1(elev) + " deg"
    azim_wt.text  = r1(azim) + " deg"
    drag_wt.text  = r2(k)
    t_wt.text     = r1(qt) + " s"

    tof, maxh, rng, peak, v0x, v0y, v0z = calc_ideal(spd, elev, azim)
    r_tof_i.text  = r2(tof)
    r_maxh_i.text = r2(maxh)
    r_rng_i.text  = r2(rng)
    r_peak_i.text = r2(peak)
    r_v0x.text    = r2(v0x)
    r_v0y.text    = r2(v0y)
    r_v0z.text    = r2(v0z)

    dtof, dmaxh, drng, dpeak = sim_drag_3d(spd, elev, azim, k)
    r_tof_d.text  = r2(dtof)
    r_maxh_d.text = r2(dmaxh)
    r_rng_d.text  = r2(drng)
    r_peak_d.text = r2(dpeak)

    xi, yi, zi, vi, axi, ayi, azi, ai = at_time_ideal_3d(spd, elev, azim, qt)
    q_xi.text  = str(xi)
    q_yi.text  = str(yi)
    q_zi.text  = str(zi)
    q_vi.text  = str(vi)
    q_axi.text = str(axi)
    q_ayi.text = str(ayi)
    q_azi.text = str(azi)
    q_ai.text  = str(ai)

    xd, yd, zd, vd, axd, ayd, azd, ad = at_time_drag_3d(spd, elev, azim, k, qt)
    q_xd.text  = str(xd)
    q_yd.text  = str(yd)
    q_zd.text  = str(zd)
    q_vd.text  = str(vd)
    q_axd.text = str(axd)
    q_ayd.text = str(ayd)
    q_azd.text = str(azd)
    q_ad.text  = str(ad)

    e = elev * pi / 180
    a = azim * pi / 180
    cannon.axis = 3 * vector(cos(e)*cos(a), sin(e), cos(e)*sin(a))

update_calc(0)

# ════════════════════════════════════════════════════════════════════
#  Simulation loop
# ════════════════════════════════════════════════════════════════════
while True:
    rate(100)

    # ── Launch button flash animation ─────────────────────────────────
    if _launch_flash > 0:
        _launch_flash -= 1
        if _launch_flash == 90:                      # mid-flash: soften
            btn_launch.text       = "✔ Launched!"
            btn_launch.background = vector(0.04, 0.55, 0.15)
        elif _launch_flash == 0:                     # done: reset to normal
            btn_launch.text       = "Launch 🚀"
            btn_launch.background = vector(0.85, 0.85, 0.85)
            btn_launch.color      = color.black

    if launched and not paused:
        k = drag_slider.value

        for i in range(speed_mult):
            ax_accel = -k * velocity.x
            ay_accel = -G - k * velocity.y
            az_accel = -k * velocity.z
            accel_vec = vector(ax_accel, ay_accel, az_accel)
            accel_mag = mag(accel_vec)

            velocity = velocity + accel_vec * DT
            ball.pos = ball.pos + velocity * DT
            t = t + DT

            scene.center = ball.pos
            horiz = sqrt(ball.pos.x*ball.pos.x + ball.pos.z*ball.pos.z)
            if velocity.y >= 0:
                # Ascending — zoom out as usual; record the current range
                scene.range = max(25, horiz * 0.4 + 10)
                _peak_range = scene.range
            else:
                # Descending — zoom back in proportional to remaining height
                height_frac = max(0.0, ball.pos.y / peak_highest) if peak_highest > 0 else 0.0
                scene.range = 25 + (_peak_range - 25) * height_frac

            if horiz > ground.size.x / 2 - 10:
                ground.size.x = ground.size.x * 1.5
                ground.pos.x  = ground.size.x / 4

            if abs(ball.pos.z) > ground.size.z / 2 - 8:
                ground.size.z = ground.size.z * 1.5

            height_curve.plot(t, ball.pos.y)
            velocity_curve.plot(t, mag(velocity))
            accel_curve.plot(t, accel_mag)

            # Shadow tracks ball on ground plane
            shadow.pos = vector(ball.pos.x, 0.08, ball.pos.z)

            # Velocity arrow (yellow) follows ball
            vel_arrow.pos  = ball.pos
            vel_arrow.axis = velocity * 0.6

            # Acceleration arrow (magenta) follows ball
            accel_arrow.pos  = ball.pos
            accel_arrow.axis = accel_vec * 0.6

            # Track peak height
            if ball.pos.y > peak_highest:
                peak_highest = ball.pos.y
                peak_vec     = vector(ball.pos.x, ball.pos.y, ball.pos.z)

            data_label.text = (
                "t=" + str(round(t, 2)) + "s"
                + "  x=" + str(round(ball.pos.x, 1))
                + "  y=" + str(round(ball.pos.y, 1))
                + "  z=" + str(round(ball.pos.z, 1))
                + "\nv=" + str(round(mag(velocity), 1)) + " m/s"
                + "  |a|=" + str(round(accel_mag, 2)) + " m/s\u00b2"
                + "\nax=" + str(round(ax_accel, 2))
                + "  ay=" + str(round(ay_accel, 2))
                + "  az=" + str(round(az_accel, 2)) + " m/s\u00b2"
            )

            if ball.pos.y < 0:
                launched = False
                # Place peak marker at apex
                peak_marker.pos     = peak_vec
                peak_marker.opacity = 0.9
                peak_label.pos      = peak_vec + vector(0, 4, 0)
                peak_label.text     = "Peak: " + str(round(peak_highest, 1)) + " m"
                peak_label.opacity  = 1
                vel_arrow.opacity   = 0
                accel_arrow.opacity = 0
                break
