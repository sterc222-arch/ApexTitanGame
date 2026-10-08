import pygame
import math
import sys
import random
import array

# --- SIGURAN HAPTIČKI SUSTAV ZA ANDROID ---
vibrate_fn = None
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    Context = autoclass('android.content.Context')
    vibrator_service = activity.getSystemService(Context.VIBRATOR_SERVICE)
    Build_VERSION = autoclass('android.os.Build$VERSION')
    sdk_int = Build_VERSION.SDK_INT
    VibrationEffect = autoclass('android.os.VibrationEffect') if sdk_int >= 26 else None

    def trigger_vibe(ms, strength=255):
        try:
            if vibrator_service and vibrator_service.hasVibrator():
                if VibrationEffect and sdk_int >= 26:
                    eff = VibrationEffect.createOneShot(int(ms), min(255, max(1, int(strength))))
                    vibrator_service.vibrate(eff)
                else:
                    vibrator_service.vibrate(int(ms))
        except Exception:
            pass
    vibrate_fn = trigger_vibe
except Exception:
    vibrate_fn = lambda ms, strength=255: None

def haptic(ms, strength=255):
    if vibrate_fn:
        try:
            vibrate_fn(ms, strength)
        except Exception:
            pass

# --- ZVUKOVI ---
audio_enabled = False
snd_step = None
snd_catch = None
snd_tear = None
snd_chew = None
snd_sting = None
snd_evolve = None
snd_burrow = None
snd_breath = None
snd_slam = None
snd_door = None
snd_charge = None

try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    pygame.mixer.init()

    def synthesize_sound(sample_fn, duration_sec, volume=0.7):
        sr = 22050
        n_samples = int(sr * duration_sec)
        buf = array.array('h')
        for i in range(n_samples):
            t = i / sr
            s = sample_fn(t, duration_sec)
            s = max(-1.0, min(1.0, s)) * volume
            buf.append(int(s * 32767))
        return pygame.mixer.Sound(buffer=buf)

    snd_step = synthesize_sound(lambda t, dur: (math.sin(2 * math.pi * (140 - t * 2000) * t) * 0.6 + random.uniform(-0.3, 0.3)) * (1.0 - t / dur) ** 2, 0.05, 0.45)
    snd_catch = synthesize_sound(lambda t, dur: (random.uniform(-0.9, 0.9) if t < 0.015 else math.sin(2 * math.pi * 320 * t) * (1.0 - t / dur)), 0.08, 0.75)
    snd_tear = synthesize_sound(lambda t, dur: (random.uniform(-0.7, 0.7) * math.sin(2 * math.pi * 60 * t)) * (1.0 - (t / dur) ** 0.5), 0.14, 0.8)
    snd_chew = synthesize_sound(lambda t, dur: math.sin(2 * math.pi * (260 - t * 800) * t) * (1.0 - t / dur) + random.uniform(-0.25, 0.25) * (1.0 - t / dur), 0.09, 0.65)
    snd_sting = synthesize_sound(lambda t, dur: (math.sin(2 * math.pi * (180 + t * 900) * t) * 0.7 + (random.uniform(-0.8, 0.8) if t > 0.1 else 0)) * (1.0 - t / dur), 0.22, 0.95)
    snd_evolve = synthesize_sound(lambda t, dur: math.sin(2 * math.pi * (110 + t * 650) * t) * math.sin(2 * math.pi * 12 * t) * (1.0 - (t / dur) ** 2), 0.45, 0.9)
    snd_burrow = synthesize_sound(lambda t, dur: (random.uniform(-0.8, 0.8) * math.sin(2 * math.pi * 45 * t)) * (1.0 - t / dur), 0.25, 0.75)
    snd_breath = synthesize_sound(lambda t, dur: (random.uniform(-0.4, 0.4) * (1.0 - math.cos(2 * math.pi * t / dur))) * 0.5, 0.40, 0.35)
    snd_slam = synthesize_sound(lambda t, dur: (math.sin(2 * math.pi * (80 - t * 250) * t) * 0.8 + random.uniform(-0.5, 0.5)) * (1.0 - t / dur), 0.30, 1.0)
    snd_door = synthesize_sound(lambda t, dur: (math.sin(2 * math.pi * 90 * t) + random.uniform(-0.3, 0.3)) * (1.0 - math.cos(2 * math.pi * t / dur)), 0.50, 0.7)
    snd_charge = synthesize_sound(lambda t, dur: math.sin(2 * math.pi * (70 + t * 400) * t) * (1.0 - t / dur), 0.35, 0.9)
    audio_enabled = True
except Exception:
    pygame.init()

def play_snd(snd):
    if audio_enabled and snd:
        try:
            snd.play()
        except Exception:
            pass

# --- POSTAVKE EKRANA I ARENE ---
info = pygame.display.Info()
WIDTH = info.current_w if info.current_w > 0 else 1080
HEIGHT = info.current_h if info.current_h > 0 else 1920

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if hasattr(pygame, 'FULLSCREEN') else 0)
actual_w, actual_h = screen.get_size()
WIDTH, HEIGHT = actual_w, actual_h

pygame.display.set_caption("Apex Titan Arachnid - Bio-Evolucija")
clock = pygame.time.Clock()

HUD_BAR_HEIGHT = max(115, int(HEIGHT * 0.095))
SAFE_PAD_X = max(35, int(WIDTH * 0.045))
SAFE_PAD_BOTTOM = max(40, int(HEIGHT * 0.035))

MIN_X = SAFE_PAD_X
MAX_X = WIDTH - SAFE_PAD_X
MIN_Y = HUD_BAR_HEIGHT + 20
MAX_Y = HEIGHT - SAFE_PAD_BOTTOM

def clamp_x(val, extra=0):
    return max(MIN_X + extra, min(MAX_X - extra, val))

def clamp_y(val, extra=0):
    return max(MIN_Y + extra, min(MAX_Y - extra, val))

# --- PALETA BOJA S 5 SLOJEVA 3D SJENČANJA ---
C_GROUND_SHADOW = (10, 6, 12)

# Normalan mod (Duboki opsidijan/hitin s rožnatim bridovima)
NORM_PAL = {
    'dark': (18, 12, 19),
    'mid': (48, 34, 46),
    'light': (85, 65, 80),
    'spec': (195, 180, 190),
    'edge': (225, 235, 250),
    'neon': (255, 20, 60)
}

# Ledeni mod (Besprijekorno definiran polarni kristalni hitin)
CRYO_PAL = {
    'dark': (8, 22, 36),
    'mid': (22, 58, 86),
    'light': (60, 135, 185),
    'spec': (220, 248, 255),
    'edge': (0, 235, 255),
    'neon': (130, 245, 255)
}

# Overdrive mod (Vulkanska magma i usijani hitin)
OD_PAL = {
    'dark': (45, 8, 12),
    'mid': (95, 16, 26),
    'light': (175, 40, 55),
    'spec': (255, 190, 120),
    'edge': (255, 115, 30),
    'neon': (255, 225, 40)
}

# --- SUSTAV TEKUĆE KRVI I EFEKATA ---
class BloodFluid:
    def __init__(self, x, y, vx, vy, color, size=4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.life = random.randint(18, 28)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.88
        self.vy *= 0.88
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), max(1, int(self.size * (self.life / 25.0))))

class BloodPuddle:
    def __init__(self, x, y, max_r, color):
        self.x = clamp_x(x)
        self.y = clamp_y(y)
        self.r = 2.0
        self.max_r = max_r
        self.color = color
        self.life = 350
        self.max_life = 350

    def update(self):
        if self.r < self.max_r:
            self.r += 0.45
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        fade = self.life / float(self.max_life)
        c = (max(0, int(self.color[0] * fade)),
             max(0, int(self.color[1] * fade)),
             max(0, int(self.color[2] * fade)))
        pygame.draw.ellipse(surf, c, (int(self.x - self.r), int(self.y - self.r * 0.65), int(self.r * 2), int(self.r * 1.3)))

particles = []
blood_drops = []
blood_puddles = []
footprints = []
ground_cracks = []
shockwaves = []
boss_projectiles = []

screen_shake = 0
flash_alpha = 0
flash_color = (255, 255, 255)

combo_count = 0
combo_timer = 0
cryo_mode = False

last_click_time = 0
DOUBLE_CLICK_THRESH = 280

active_boss = None
next_boss_level = 25
boss_cycle_index = 0

last_mutation_name = "NEMA"

def add_shake(amount):
    global screen_shake
    screen_shake = max(screen_shake, amount)

def spill_blood(x, y, color, count=16, spread=5.5):
    if len(blood_puddles) < 55:
        blood_puddles.append(BloodPuddle(x, y, random.uniform(8, 22), color))
    for _ in range(count):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(1.8, spread)
        blood_drops.append(BloodFluid(x, y, math.cos(ang) * spd, math.sin(ang) * spd, color, random.randint(2, 5)))

def emit_particles(x, y, color, count=14, speed_mult=1.0):
    for _ in range(count):
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(2.0, 6.0) * speed_mult
        life = random.randint(12, 24)
        particles.append([clamp_x(x), clamp_y(y), math.cos(ang) * spd, math.sin(ang) * spd, life, life, color])

def draw_floor_glow(surf, x, y, radius, color, max_alpha=40):
    for r_step in range(3, 0, -1):
        r = int(radius * (r_step / 3.0))
        dim = max_alpha * (1.0 - (r_step - 1) / 3.0)
        c = (min(255, int(color[0] * dim / 255)),
             min(255, int(color[1] * dim / 255)),
             min(255, int(color[2] * dim / 255)))
        pygame.draw.circle(surf, c, (int(x), int(y)), max(1, r))

# --- PUKOTINE TLA ---
class GroundCrackEffect:
    def __init__(self, x, y, max_radius=135):
        self.x = clamp_x(x, 15)
        self.y = clamp_y(y, 15)
        self.duration = 160
        self.timer = 160
        self.max_radius = max_radius
        self.branches = []

        num_main = random.randint(5, 7)
        for i in range(num_main):
            base_ang = (i * (2 * math.pi / num_main)) + random.uniform(-0.35, 0.35)
            branch_len = max_radius * random.uniform(0.65, 1.1)
            cur_x, cur_y = self.x, self.y
            steps = random.randint(4, 6)
            step_len = branch_len / steps

            for s in range(steps):
                ang = base_ang + random.uniform(-0.40, 0.40)
                nx = clamp_x(cur_x + math.cos(ang) * step_len, 4)
                ny = clamp_y(cur_y + math.sin(ang) * step_len, 4)
                thick = max(1, 4 - s // 2)
                self.branches.append((cur_x, cur_y, nx, ny, thick))
                cur_x, cur_y = nx, ny

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self, surf):
        fade = self.timer / float(self.duration)
        alpha_mult = min(1.0, fade * 1.4)
        col_outer = (int(50 * alpha_mult), int(12 * alpha_mult), int(18 * alpha_mult))
        col_hot = (int(255 * alpha_mult), int(190 * alpha_mult), int(75 * alpha_mult))

        for x1, y1, x2, y2, thick in self.branches:
            pygame.draw.line(surf, col_outer, (x1, y1), (x2, y2), thick + 2)
            pygame.draw.line(surf, col_hot, (x1, y1), (x2, y2), max(1, thick))

# --- MRAVI (PRAVI PLIJEN S 6 NOGU, GLAVOM I ABDOMENOM) ---
class Ant:
    def __init__(self, force_gold=False):
        self.force_gold = force_gold
        self.paralyzed_timer = 0
        self.march_phase = 0.0
        self.respawn()

    def respawn(self):
        self.x = random.randint(MIN_X + 40, MAX_X - 40)
        self.y = random.randint(MIN_Y + 40, MAX_Y - 40)
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-2.0, 2.0)
        self.angle = 0.0

        if self.force_gold or random.random() < 0.12:
            self.type_name = "Zlatna Kraljica Mrava"
            self.color = (255, 215, 0)
            self.blood_col = (255, 240, 140)
            self.max_spd = 4.3
            self.size = 10
            self.is_gold = True
        else:
            types = [
                {"name": "Crni Mrav Radilica", "color": (32, 28, 35), "blood": (140, 130, 145), "speed": 3.6, "size": 6},
                {"name": "Crveni Vatreni Mrav", "color": (195, 35, 45), "blood": (180, 20, 30), "speed": 3.9, "size": 7},
                {"name": "Kiselinski Šumski Mrav", "color": (45, 210, 75), "blood": (35, 255, 80), "speed": 3.0, "size": 7},
                {"name": "Fantomski Mrav Dubina", "color": (160, 40, 230), "blood": (190, 60, 255), "speed": 3.4, "size": 7}
            ]
            chosen = random.choice(types)
            self.type_name = chosen["name"]
            self.color = chosen["color"]
            self.blood_col = chosen["blood"]
            self.max_spd = chosen["speed"]
            self.size = chosen["size"]
            self.is_gold = False

    def update(self, pred_x, pred_y, is_pred_burrowed):
        self.march_phase += 0.35
        if self.paralyzed_timer > 0:
            self.paralyzed_timer -= 1
            return

        dx = self.x - pred_x
        dy = self.y - pred_y
        dist = math.hypot(dx, dy)
        flee_dist = 0 if is_pred_burrowed else 185

        if 0 < dist < flee_dist:
            flee_x = (dx / dist) * self.max_spd * 1.35
            flee_y = (dy / dist) * self.max_spd * 1.35
            self.vx += (flee_x - self.vx) * 0.18
            self.vy += (flee_y - self.vy) * 0.18
        else:
            self.vx += random.uniform(-0.4, 0.4)
            self.vy += random.uniform(-0.4, 0.4)
            spd = math.hypot(self.vx, self.vy)
            if spd > self.max_spd:
                self.vx = (self.vx / spd) * self.max_spd
                self.vy = (self.vy / spd) * self.max_spd

        if math.hypot(self.vx, self.vy) > 0.2:
            self.angle = math.atan2(self.vy, self.vx)

        self.x = clamp_x(self.x + self.vx, 10)
        self.y = clamp_y(self.y + self.vy, 10)

    def draw(self, surf):
        perp = self.angle + math.pi / 2
        fwd = self.angle
        s = self.size

        # 6 Nogu koje marširaju
        for i, leg_offset in enumerate([-s * 0.6, 0, s * 0.6]):
            leg_wave = math.sin(self.march_phase + i * 1.4) * (s * 0.8)
            for side in [-1, 1]:
                base_x = self.x + math.cos(fwd) * leg_offset
                base_y = self.y + math.sin(fwd) * leg_offset
                tip_x = base_x + math.cos(perp * side) * (s * 1.6) + math.cos(fwd) * leg_wave
                tip_y = base_y + math.sin(perp * side) * (s * 1.6) + math.sin(fwd) * leg_wave
                pygame.draw.line(surf, (40, 35, 45) if not self.is_gold else (180, 150, 20), (base_x, base_y), (tip_x, tip_y), 2)

        # Abdomen (Gaster)
        gast_x = self.x - math.cos(fwd) * (s * 1.2)
        gast_y = self.y - math.sin(fwd) * (s * 1.2)
        pygame.draw.ellipse(surf, self.color, (int(gast_x - s * 0.9), int(gast_y - s * 0.7), int(s * 1.8), int(s * 1.4)))
        pygame.draw.circle(surf, (255, 255, 255) if self.is_gold else (80, 70, 85), (int(gast_x), int(gast_y)), max(1, s // 3))

        # Torzo
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), max(2, int(s * 0.65)))

        # Glava s ticalima
        head_x = self.x + math.cos(fwd) * (s * 1.1)
        head_y = self.y + math.sin(fwd) * (s * 1.1)
        pygame.draw.circle(surf, self.color, (int(head_x), int(head_y)), max(2, int(s * 0.75)))

        for side in [-1, 1]:
            ant_tip_x = head_x + math.cos(fwd + 0.5 * side) * (s * 1.5)
            ant_tip_y = head_y + math.sin(fwd + 0.5 * side) * (s * 1.5)
            pygame.draw.line(surf, (220, 220, 220) if not self.is_gold else (255, 255, 180), (head_x, head_y), (ant_tip_x, ant_tip_y), 1)

# --- BJEŽEĆI CRV S BLAGOM (PRIMAL GENE WORM - RIJEDAK SPON) ---
class TreasureWorm:
    MUTATIONS_POOL = [
        "TITANSKI OKLOP (+25% Redukcija)",
        "OŠTRE KANDŽE (+30% DMG)",
        "KAUSTIČNI OTROV (+Rep DoT)",
        "HIPER-BRZINA (+20% Spd)",
        "DUBOKI ŽELUDAC (+500 Max Glad)",
        "KRISTALNI ŽALAC (+Domet Repa)",
        "BIOLUMINISCENCIJA (+Sjaj Auri)"
    ]

    def __init__(self):
        self.active = False
        self.segments = []
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.speed = 4.8
        self.angle = 0
        self.wave = 0.0

    def spawn(self):
        self.active = True
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': self.x, self.y = random.randint(MIN_X+50, MAX_X-50), MIN_Y + 15
        elif side == 'bottom': self.x, self.y = random.randint(MIN_X+50, MAX_X-50), MAX_Y - 15
        elif side == 'left': self.x, self.y = MIN_X + 15, random.randint(MIN_Y+50, MAX_Y-50)
        else: self.x, self.y = MAX_X - 15, random.randint(MIN_Y+50, MAX_Y-50)

        # Bježi na suprotnu stranu
        self.target_x = WIDTH - self.x
        self.target_y = HEIGHT - self.y
        self.segments = [[self.x, self.y] for _ in range(9)]

    def update(self, pred_x, pred_y):
        if not self.active:
            return

        self.wave += 0.4
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        # Ako je predator blizu, bježi još brže
        d_pred = math.hypot(pred_x - self.x, pred_y - self.y)
        if d_pred < 170:
            dx = self.x - pred_x
            dy = self.y - pred_y

        self.angle = math.atan2(dy, dx)
        self.x += math.cos(self.angle) * self.speed + math.sin(self.wave) * 2.2
        self.y += math.sin(self.angle) * self.speed + math.cos(self.wave) * 2.2

        self.segments[0] = [self.x, self.y]
        for k in range(1, len(self.segments)):
            prev = self.segments[k-1]
            curr = self.segments[k]
            ang = math.atan2(curr[1] - prev[1], curr[0] - prev[0])
            curr[0] = prev[0] + math.cos(ang) * 9
            curr[1] = prev[1] + math.sin(ang) * 9

        # Ako pobjegne van arene
        if self.x <= MIN_X or self.x >= MAX_X or self.y <= MIN_Y or self.y >= MAX_Y:
            if dist < 40 or random.random() < 0.02:
                self.active = False

    def draw(self, surf):
        if not self.active:
            return

        draw_floor_glow(surf, self.x, self.y, 35, (255, 230, 80), 60)
        for i in reversed(range(len(self.segments))):
            sx, sy = self.segments[i]
            r = max(3, 8 - i // 2)
            pygame.draw.circle(surf, (255, 215, 0) if i % 2 == 0 else (255, 90, 160), (int(sx), int(sy)), r)
            pygame.draw.circle(surf, (255, 255, 255), (int(sx), int(sy)), max(1, r - 3))

def solve_ik(p0_x, p0_y, p2_x, p2_y, l1, l2, flip=1):
    dx = p2_x - p0_x
    dy = p2_y - p0_y
    dist = math.hypot(dx, dy)
    d = min(max(dist, 1e-4), l1 + l2 - 0.001)

    base_angle = math.atan2(dy, dx)
    cos_a = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    cos_a = max(-1.0, min(1.0, cos_a))
    angle_a = math.acos(cos_a)

    joint_angle = base_angle + angle_a * flip
    jx = p0_x + math.cos(joint_angle) * l1
    jy = p0_y + math.sin(joint_angle) * l1
    return jx, jy

class Segment:
    def __init__(self, x, y, length, radius, angle=0.0):
        self.x = clamp_x(x)
        self.y = clamp_y(y)
        self.length = length
        self.radius = radius
        self.angle = angle

    def follow(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        self.angle = math.atan2(dy, dx)
        self.x = tx - math.cos(self.angle) * self.length
        self.y = ty - math.sin(self.angle) * self.length
        self.x = clamp_x(self.x, self.radius * 0.4)
        self.y = clamp_y(self.y, self.radius * 0.4)

class Limb:
    def __init__(self, creature, seg_idx, side, l1, l2, reach, is_heavy=False, is_overdrive_leg=False):
        self.creature = creature
        self.seg_idx = seg_idx
        self.side = side
        self.l1 = l1
        self.l2 = l2
        self.reach = reach
        self.is_heavy = is_heavy
        self.is_overdrive_leg = is_overdrive_leg

        self.foot_x = 0.0
        self.foot_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.step_start_x = 0.0
        self.step_start_y = 0.0
        self.step_progress = 1.0

        hx, hy, ang = self.get_hip()
        init_ang = ang + ((math.pi / 3.0) if is_heavy else (math.pi / 2.2)) * side
        self.foot_x = clamp_x(hx + math.cos(init_ang) * reach)
        self.foot_y = clamp_y(hy + math.sin(init_ang) * reach)

    def get_hip(self):
        seg = self.creature.segments[min(self.seg_idx, len(self.creature.segments) - 1)]
        perp = seg.angle + (math.pi / 2) * self.side
        hip_dist = seg.radius * (1.30 if self.is_heavy else 1.05)
        hx = clamp_x(seg.x + math.cos(perp) * hip_dist)
        hy = clamp_y(seg.y + math.sin(perp) * hip_dist)
        return hx, hy, seg.angle

    def update(self):
        if self.is_overdrive_leg and not self.creature.is_overdrive:
            return

        hx, hy, ang = self.get_hip()

        if self.creature.is_burrowed and not self.is_heavy:
            return

        if self.is_heavy and self.creature.is_burrowed:
            t = pygame.time.get_ticks() * 0.003
            spread_ang = ang + (0.55 + math.sin(t + self.side) * 0.14) * self.side
            reach_pulse = self.reach * (0.65 + math.cos(t * 1.5) * 0.08)
            self.foot_x = clamp_x(hx + math.cos(spread_ang) * reach_pulse)
            self.foot_y = clamp_y(hy + math.sin(spread_ang) * reach_pulse)
            return

        if self.is_heavy and self.creature.slam_timer > 0:
            slam_t = (25 - self.creature.slam_timer) / 25.0
            slam_reach = self.reach * (0.8 + math.sin(slam_t * math.pi) * 0.4)
            slam_ang = ang + (0.35 * self.side)
            self.foot_x = clamp_x(hx + math.cos(slam_ang) * slam_reach)
            self.foot_y = clamp_y(hy + math.sin(slam_ang) * slam_reach)
            return

        if (self.is_heavy or self.is_overdrive_leg) and self.creature.is_feasting:
            prey = self.creature.feast_target
            tear_rip = math.sin(pygame.time.get_ticks() * 0.035 + self.side * math.pi) * 16
            self.foot_x = clamp_x(prey[0] + self.side * 18 + tear_rip)
            self.foot_y = clamp_y(prey[1] + math.cos(pygame.time.get_ticks() * 0.025) * 8)
            return

        wall_thresh = 95
        if hx < MIN_X + wall_thresh and self.side == -1:
            self.foot_x = MIN_X + 2
            self.foot_y = clamp_y(hy + math.sin(pygame.time.get_ticks() * 0.003) * 15)
            return
        elif hx > MAX_X - wall_thresh and self.side == 1:
            self.foot_x = MAX_X - 2
            self.foot_y = clamp_y(hy + math.sin(pygame.time.get_ticks() * 0.003) * 15)
            return

        if self.is_heavy and self.creature.is_idle:
            t = pygame.time.get_ticks() * 0.003
            spread_ang = ang + (math.pi / 2.6 + math.sin(t + self.side) * 0.28) * self.side
            reach_pulse = self.reach * (1.1 + math.cos(t * 1.5) * 0.15)
            self.foot_x = clamp_x(hx + math.cos(spread_ang) * reach_pulse)
            self.foot_y = clamp_y(hy + math.sin(spread_ang) * reach_pulse)
            return

        rest_ang = ang + ((math.pi / 3.2) if self.is_heavy else ((math.pi / 2.8) if self.is_overdrive_leg else (math.pi / 2.25))) * self.side
        ideal_x = clamp_x(hx + math.cos(rest_ang) * self.reach)
        ideal_y = clamp_y(hy + math.sin(rest_ang) * self.reach)

        dist = math.hypot(self.foot_x - ideal_x, self.foot_y - ideal_y)
        threshold = self.reach * (0.75 if self.is_heavy else 0.85)

        if dist > threshold and self.step_progress >= 1.0:
            self.step_start_x = self.foot_x
            self.step_start_y = self.foot_y
            stride = 28 if self.is_heavy else 20
            self.target_x = clamp_x(ideal_x + math.cos(ang) * stride)
            self.target_y = clamp_y(ideal_y + math.sin(ang) * stride)
            self.step_progress = 0.0

        if self.step_progress < 1.0:
            speed = 0.30 if (self.creature.is_overdrive or self.is_heavy) else 0.24
            self.step_progress += speed
            t = min(1.0, self.step_progress)
            self.foot_x = clamp_x(self.step_start_x + (self.target_x - self.step_start_x) * t)
            self.foot_y = clamp_y(self.step_start_y + (self.target_y - self.step_start_y) * t)

            if self.step_progress >= 1.0 and not self.creature.is_burrowed:
                if len(footprints) < 40:
                    footprints.append([self.foot_x, self.foot_y, 4 if self.is_heavy else 2, 100])
                if self.is_heavy:
                    play_snd(snd_step)
                    haptic(14, 70)

    def draw(self, surf, pal):
        if self.is_overdrive_leg and not self.creature.is_overdrive:
            return
        if self.creature.is_burrowed and not self.is_heavy:
            return

        hx, hy, _ = self.get_hip()
        jx, jy = solve_ik(hx, hy, self.foot_x, self.foot_y, self.l1, self.l2, self.side)
        evo = self.creature.evo_level

        pygame.draw.ellipse(surf, C_GROUND_SHADOW, (int(self.foot_x - 12), int(self.foot_y - 6), 24, 12))

        if self.is_heavy:
            v1_dx = jx - hx; v1_dy = jy - hy
            v1_len = max(1e-4, math.hypot(v1_dx, v1_dy))
            n1_x = -v1_dy / v1_len * (9.5 + min(16, evo * 0.20))
            n1_y = v1_dx / v1_len * (9.5 + min(16, evo * 0.20))

            p_femur = [
                (hx - n1_x * 0.6, hy - n1_y * 0.6),
                (hx + n1_x * 1.4, hy + n1_y * 1.4),
                (jx + n1_x * 0.9, jy + n1_y * 0.9),
                (jx - n1_x * 0.4, jy - n1_y * 0.4)
            ]
            pygame.draw.polygon(surf, pal['dark'], p_femur)
            pygame.draw.polygon(surf, pal['mid'], [
                (hx + n1_x * 0.1, hy + n1_y * 0.1),
                (hx + n1_x * 1.1, hy + n1_y * 1.1),
                (jx + n1_x * 0.6, jy + n1_y * 0.6),
                (jx, jy)
            ])
            pygame.draw.line(surf, pal['spec'], (hx + n1_x * 1.3, hy + n1_y * 1.3), (jx + n1_x * 0.8, jy + n1_y * 0.8), 2)
            pygame.draw.lines(surf, pal['edge'], True, p_femur, 2)
            pygame.draw.line(surf, pal['neon'], (hx, hy), (jx, jy), 3)

            v2_dx = self.foot_x - jx; v2_dy = self.foot_y - jy
            v2_len = max(1e-4, math.hypot(v2_dx, v2_dy))
            n2_x = -v2_dy / v2_len * (8.5 + min(14, evo * 0.18))
            n2_y = v2_dx / v2_len * (8.5 + min(14, evo * 0.18))

            p_shin = [
                (jx - n2_x * self.side * 0.4, jy - n2_y * self.side * 0.4),
                (jx + n2_x * self.side * 1.5, jy + n2_y * self.side * 1.5),
                (self.foot_x + n2_x * self.side * 0.9, self.foot_y + n2_y * self.side * 0.9),
                (self.foot_x, self.foot_y)
            ]
            pygame.draw.polygon(surf, pal['dark'], p_shin)
            pygame.draw.lines(surf, pal['edge'], True, p_shin, 2)

            pygame.draw.circle(surf, pal['mid'], (int(jx), int(jy)), 10 + min(8, evo // 12))
            pygame.draw.circle(surf, pal['spec'], (int(jx - 2), int(jy - 2)), 4)
            pygame.draw.circle(surf, pal['neon'], (int(jx), int(jy)), 6)
            pygame.draw.circle(surf, (255, 255, 255), (int(jx), int(jy)), 2)

            c_ang = math.atan2(self.foot_y - jy, self.foot_x - jx)
            tip_len = 26 + min(36, evo * 0.45)

            out_ang = c_ang + (0.15 * self.side)
            tip1_x = clamp_x(self.foot_x + math.cos(out_ang) * tip_len)
            tip1_y = clamp_y(self.foot_y + math.sin(out_ang) * tip_len)

            in_ang = c_ang - (0.35 * self.side)
            tip2_x = clamp_x(self.foot_x + math.cos(in_ang) * (tip_len * 0.65))
            tip2_y = clamp_y(self.foot_y + math.sin(in_ang) * (tip_len * 0.65))

            claw_poly = [
                (self.foot_x - n2_x * self.side * 0.5, self.foot_y - n2_y * self.side * 0.5),
                (tip1_x, tip1_y),
                (self.foot_x + math.cos(c_ang) * 6, self.foot_y + math.sin(c_ang) * 6),
                (tip2_x, tip2_y)
            ]
            pygame.draw.polygon(surf, pal['dark'], claw_poly)
            pygame.draw.polygon(surf, pal['mid'], [
                (self.foot_x, self.foot_y),
                (tip1_x, tip1_y),
                (self.foot_x + math.cos(c_ang) * 5, self.foot_y + math.sin(c_ang) * 5)
            ])
            pygame.draw.lines(surf, pal['edge'], True, claw_poly, 2)
            pygame.draw.line(surf, pal['spec'], (self.foot_x, self.foot_y), (tip1_x, tip1_y), 2)
            pygame.draw.circle(surf, pal['neon'], (int(self.foot_x), int(self.foot_y)), 5)

            for z_step in (0.35, 0.65):
                zx = self.foot_x + (tip1_x - self.foot_x) * z_step
                zy = self.foot_y + (tip1_y - self.foot_y) * z_step
                pygame.draw.circle(surf, (255, 255, 255), (int(zx), int(zy)), 2)
        else:
            p_leg = [(hx, hy), (jx, jy), (self.foot_x, self.foot_y)]
            pygame.draw.lines(surf, pal['dark'], False, p_leg, 4)
            pygame.draw.lines(surf, pal['edge'], False, p_leg, 2)
            pygame.draw.circle(surf, pal['neon'], (int(jx), int(jy)), 5)
            pygame.draw.circle(surf, (255, 255, 255), (int(jx), int(jy)), 2)

            c_ang = math.atan2(self.foot_y - jy, self.foot_x - jx)
            c_tip_x = clamp_x(self.foot_x + math.cos(c_ang) * (11 + min(12, evo * 0.15)))
            c_tip_y = clamp_y(self.foot_y + math.sin(c_ang) * (11 + min(12, evo * 0.15)))
            pygame.draw.line(surf, pal['spec'], (self.foot_x, self.foot_y), (c_tip_x, c_tip_y), 2)
            pygame.draw.circle(surf, (255, 255, 255), (int(self.foot_x), int(self.foot_y)), 2)

class Scorpion:
    def __init__(self, x, y):
        self.evo_level = 1
        self.bugs_eaten = 0
        self.pulse_phase = 0.0

        self.max_hunger = 1800.0
        self.hunger = 1800.0
        self.auto_hunting = False
        self.ambush_timer = 0

        self.is_idle = False
        self.is_burrowed = False
        self.is_overdrive = False

        self.is_feasting = False
        self.feast_timer = 0
        self.feast_target = (0, 0)
        self.feast_bug_color = (255, 255, 255)
        self.feasting_gold = False
        self.feasting_boss = None

        self.is_stinging = False
        self.sting_progress = 0.0
        self.sting_target = (0, 0)
        self.ambush_target = None
        self.ambush_cooldown = 0

        self.slam_timer = 0
        self.breath_clock = 0.0

        self.vx = 0.0
        self.vy = 0.0

        self.tail2_growth = 0.0
        self.segments = []
        self.segments_tail_left = []
        self.segments_tail_right = []
        self.limbs = []
        self.rebuild_skeleton(x, y)

    def rebuild_skeleton(self, x, y):
        new_num_segments = 32 + min(14, int(self.evo_level * 0.14))
        self.seg_len = 11 + min(7, int(self.evo_level * 0.07))

        old_segs = getattr(self, 'segments', [])
        new_segments = []

        for i in range(new_num_segments):
            base_r = 18 + min(26, self.evo_level * 0.28)
            if i < 17:
                r = math.sin((i / 17.0) * math.pi) * base_r + 9
            else:
                r = max(4.5, base_r - (i - 17) * 0.60)

            if i < len(old_segs):
                seg = Segment(old_segs[i].x, old_segs[i].y, self.seg_len, r, old_segs[i].angle)
            elif len(new_segments) > 0:
                prev = new_segments[-1]
                nx = prev.x - math.cos(prev.angle) * self.seg_len
                ny = prev.y - math.sin(prev.angle) * self.seg_len
                seg = Segment(nx, ny, self.seg_len, r, prev.angle)
            else:
                seg = Segment(x, y, self.seg_len, r, 0.0)

            new_segments.append(seg)

        self.num_segments = new_num_segments
        self.segments = new_segments

        f_l1 = 58 + min(44, self.evo_level * 0.45)
        f_l2 = 62 + min(48, self.evo_level * 0.50)
        f_reach = 92 + min(65, self.evo_level * 0.65)

        # 1. Glavne prednje masivne grabežljive noge / kliješta
        self.limbs = [
            Limb(self, 1, -1, f_l1, f_l2, f_reach, is_heavy=True),
            Limb(self, 1, 1, f_l1, f_l2, f_reach, is_heavy=True)
        ]

        # 2. DODATNI SET NOGU ZA HODANJE IZA GLAVNIH U OVERDRIVE MODU
        od_front_l1 = 44 + min(24, self.evo_level * 0.26)
        od_front_l2 = 48 + min(26, self.evo_level * 0.28)
        od_front_reach = 76 + min(36, self.evo_level * 0.38)
        self.limbs.append(Limb(self, 2, -1, od_front_l1, od_front_l2, od_front_reach, is_heavy=False, is_overdrive_leg=True))
        self.limbs.append(Limb(self, 2, 1, od_front_l1, od_front_l2, od_front_reach, is_heavy=False, is_overdrive_leg=True))

        # 3. Dodatne Overdrive noge na 4. segmentu
        od_l1 = 40 + min(22, self.evo_level * 0.25)
        od_l2 = 44 + min(24, self.evo_level * 0.28)
        od_reach = 68 + min(32, self.evo_level * 0.35)
        self.limbs.append(Limb(self, 4, -1, od_l1, od_l2, od_reach, is_heavy=False, is_overdrive_leg=True))
        self.limbs.append(Limb(self, 4, 1, od_l1, od_l2, od_reach, is_heavy=False, is_overdrive_leg=True))

        # 4. Standardne noge za kretanje (4 para)
        b_l1 = 36 + min(22, self.evo_level * 0.25)
        b_l2 = 40 + min(24, self.evo_level * 0.28)
        b_reach = 62 + min(32, self.evo_level * 0.35)

        for s_idx in [6, 9, 12, 15]:
            self.limbs.append(Limb(self, s_idx, -1, b_l1, b_l2, b_reach, is_heavy=False))
            self.limbs.append(Limb(self, s_idx, 1, b_l1, b_l2, b_reach, is_heavy=False))

    def trigger_slam(self, bugs_list):
        self.slam_timer = 25
        play_snd(snd_slam)
        haptic(220)
        add_shake(20)
        head = self.segments[0]

        impact_reach = 65
        impact_x = clamp_x(head.x + math.cos(head.angle) * impact_reach)
        impact_y = clamp_y(head.y + math.sin(head.angle) * impact_reach)

        if len(ground_cracks) < 8:
            ground_cracks.append(GroundCrackEffect(impact_x, impact_y, max_radius=145))

        slam_pull_radius = 240
        for b in bugs_list:
            dist = math.hypot(b.x - impact_x, b.y - impact_y)
            if dist < slam_pull_radius:
                b.paralyzed_timer = 180
                pull_ang = math.atan2(impact_y - b.y, impact_x - b.x)
                pull_strength = (1.0 - dist / slam_pull_radius) * 15.0
                b.vx += math.cos(pull_ang) * pull_strength
                b.vy += math.sin(pull_ang) * pull_strength

        global active_boss
        if active_boss and active_boss.state == "active":
            d_boss = math.hypot(active_boss.x - impact_x, active_boss.y - impact_y)
            if d_boss < 240:
                active_boss.take_slam_hit()

    def trigger_feast(self, bug_x, bug_y, bug_color, is_gold=False):
        global combo_count, combo_timer, cryo_mode
        if self.is_feasting:
            return

        if self.is_burrowed:
            self.unburrow()

        self.is_feasting = True
        self.feasting_boss = None
        self.feast_timer = 45
        self.feast_target = (clamp_x(bug_x), clamp_y(bug_y))
        self.feast_bug_color = bug_color
        self.feasting_gold = is_gold

        if combo_timer > 0:
            combo_count += 1
        else:
            combo_count = 1
        combo_timer = 300

        if combo_count >= 15:
            cryo_mode = True

        play_snd(snd_catch)
        haptic(50, 180)
        spill_blood(bug_x, bug_y, bug_color, count=14, spread=5.0)

    def trigger_boss_feast(self, boss):
        global combo_count, combo_timer, cryo_mode
        if self.is_burrowed:
            self.unburrow()

        self.is_feasting = True
        self.feasting_boss = boss
        self.feast_timer = 150
        self.feast_target = (clamp_x(boss.x), clamp_y(boss.y))
        self.feast_bug_color = boss.color_neon
        self.feasting_gold = False

        combo_count += 5
        combo_timer = 400
        if combo_count >= 15:
            cryo_mode = True

        play_snd(snd_catch)
        add_shake(18)
        haptic(250)
        spill_blood(boss.x, boss.y, boss.color_neon, count=24, spread=7.0)

    def trigger_sting(self, tx, ty):
        self.is_stinging = True
        self.sting_progress = 0.0
        self.sting_target = (clamp_x(tx), clamp_y(ty))

    def unburrow(self):
        if self.is_burrowed:
            self.is_burrowed = False
            head = self.segments[0]
            play_snd(snd_burrow)
            emit_particles(head.x, head.y, (120, 100, 80), count=25, speed_mult=1.5)
            add_shake(12)
            haptic(100, 200)

    def evolve_now(self):
        if self.evo_level < 100:
            self.evo_level += 1
            head = self.segments[0]
            self.rebuild_skeleton(head.x, head.y)

            global flash_alpha, flash_color
            flash_alpha = 200
            flash_color = (255, 215, 0) if self.feasting_gold else (255, 255, 255)
            shockwaves.append([head.x, head.y, 0, 190 + min(300, self.evo_level * 5), (255, 215, 0) if self.feasting_gold else (255, 35, 75)])
            add_shake(26)
            play_snd(snd_evolve)
            haptic(350, 255)

    def update(self, tx, ty, user_touching, bugs_list):
        global combo_count, combo_timer, cryo_mode, active_boss
        self.pulse_phase = (self.pulse_phase + 0.42) % (self.num_segments + 8)
        head = self.segments[0]
        tip = self.segments[-1]

        if cryo_mode:
            self.tail2_growth = min(1.0, self.tail2_growth + 0.04)
        else:
            self.tail2_growth = max(0.0, self.tail2_growth - 0.05)

        self.breath_clock += 0.025
        if int(self.breath_clock) % 240 == 0 and not self.is_feasting:
            play_snd(snd_breath)

        if combo_timer > 0:
            combo_timer -= 1
        else:
            combo_count = 0
            cryo_mode = False

        tx = clamp_x(tx, 35)
        ty = clamp_y(ty, 35)

        self.hunger = max(0.0, self.hunger - 1.0)
        hunger_ratio = self.hunger / self.max_hunger
        self.is_overdrive = hunger_ratio < 0.50

        if hunger_ratio <= 0.05:
            self.auto_hunting = True
        elif hunger_ratio >= 0.40:
            self.auto_hunting = False

        if user_touching:
            self.ambush_timer = 0
        elif self.ambush_timer > 0:
            self.ambush_timer -= 1

        dist_to_target = math.hypot(tx - head.x, ty - head.y)
        self.is_idle = ((dist_to_target < 25 or (self.ambush_timer > 0 and not user_touching))
                        and not self.is_feasting and not self.auto_hunting)

        if self.slam_timer > 0:
            self.slam_timer -= 1

        if self.is_idle and not user_touching and hunger_ratio > 0.45:
            if not self.is_burrowed and random.random() < 0.012:
                self.is_burrowed = True
                play_snd(snd_burrow)
                emit_particles(head.x, head.y, (100, 85, 70), count=18)
                haptic(60, 120)
        elif user_touching or hunger_ratio <= 0.45 or self.auto_hunting:
            if self.is_burrowed and not self.is_stinging:
                self.unburrow()

        if self.is_burrowed and not self.is_stinging and not self.is_feasting:
            self.ambush_cooldown += 1
            if self.ambush_cooldown >= 20:
                self.ambush_cooldown = 0
                tail_reach = 210.0
                candidates = [b for b in bugs_list if math.hypot(b.x - tip.x, b.y - tip.y) < tail_reach]
                if active_boss and active_boss.state == "active" and math.hypot(active_boss.x - tip.x, active_boss.y - tip.y) < tail_reach:
                    candidates.append(active_boss)

                if candidates and random.random() < 0.06:
                    target = random.choice(candidates)
                    self.trigger_sting(target.x, target.y)
                    self.ambush_target = target

        if self.is_feasting:
            self.feast_timer -= 1
            head.x += (self.feast_target[0] - head.x) * 0.25 + random.uniform(-2, 2)
            head.y += (self.feast_target[1] - head.y) * 0.25 + random.uniform(-2, 2)

            f_dx = self.feast_target[0] - head.x
            f_dy = self.feast_target[1] - head.y
            if math.hypot(f_dx, f_dy) > 1.0:
                target_ang = math.atan2(f_dy, f_dx)
                diff = (target_ang - head.angle + math.pi) % (2 * math.pi) - math.pi
                head.angle += diff * 0.35

            if self.feasting_boss:
                if self.feast_timer == 115:
                    self.feasting_boss.parts_torn = 1
                    play_snd(snd_tear)
                    add_shake(12); haptic(150)
                    spill_blood(self.feast_target[0], self.feast_target[1], self.feasting_boss.color_neon, count=16)
                elif self.feast_timer == 70:
                    self.feasting_boss.parts_torn = 2
                    play_snd(snd_tear)
                    add_shake(15); haptic(180)
                    spill_blood(self.feast_target[0], self.feast_target[1], self.feasting_boss.color_armor, count=20)
                elif self.feast_timer == 25:
                    self.feasting_boss.parts_torn = 3
                    play_snd(snd_chew)
                    add_shake(18); haptic(220)
                    spill_blood(self.feast_target[0], self.feast_target[1], (255, 215, 0), count=25)

                if self.feast_timer <= 0:
                    self.is_feasting = False
                    self.feasting_boss = None
                    active_boss = None
                    self.hunger = self.max_hunger
                    for _ in range(5):
                        self.evolve_now()
                    self.ambush_timer = 0 if user_touching else 180
            else:
                if self.feast_timer in [35, 20]:
                    play_snd(snd_tear); haptic(35, 140)
                    spill_blood(self.feast_target[0], self.feast_target[1], self.feast_bug_color, count=6)
                elif self.feast_timer in [30, 15]:
                    play_snd(snd_chew); haptic(25, 100)

                if self.feast_timer <= 0:
                    self.is_feasting = False
                    extra_dna = max(0, combo_count - 1)
                    self.bugs_eaten += 1 + extra_dna

                    if self.feasting_gold:
                        self.hunger = self.max_hunger
                        self.evolve_now()
                    else:
                        self.hunger = min(self.max_hunger, self.hunger + (self.max_hunger / 3.0))
                        if self.bugs_eaten % 5 == 0:
                            self.evolve_now()

                    self.ambush_timer = 0 if user_touching else 180
                    self.pulse_phase = 0.0
                    self.feasting_gold = False
        else:
            if not self.is_idle and not self.is_burrowed:
                move_dx = 0.0
                move_dy = 0.0

                if cryo_mode:
                    ax = (tx - head.x) * 0.03
                    ay = (ty - head.y) * 0.03
                    self.vx = (self.vx + ax) * 0.92
                    self.vy = (self.vy + ay) * 0.92
                    head.x += self.vx
                    head.y += self.vy
                    move_dx, move_dy = self.vx, self.vy
                elif self.is_overdrive:
                    speed = 0.40 if (dist_to_target < 120 and not user_touching) else 0.24
                    move_dx = (tx - head.x) * speed + math.sin(pygame.time.get_ticks() * 0.06) * 1.5
                    move_dy = (ty - head.y) * speed
                    head.x += move_dx
                    head.y += move_dy
                else:
                    speed = 0.35 if (dist_to_target < 120 and not user_touching) else 0.18
                    move_dx = (tx - head.x) * speed
                    move_dy = (ty - head.y) * speed
                    head.x += move_dx
                    head.y += move_dy

                if math.hypot(move_dx, move_dy) > 0.4:
                    target_ang = math.atan2(move_dy, move_dx)
                    ang_diff = (target_ang - head.angle + math.pi) % (2 * math.pi) - math.pi
                    turn_speed = 0.14 if cryo_mode else (0.35 if self.is_overdrive else 0.24)
                    head.angle += ang_diff * turn_speed

        head.x = clamp_x(head.x, 25)
        head.y = clamp_y(head.y, 25)

        if self.is_stinging:
            if self.sting_progress == 0.0:
                play_snd(snd_sting)
            self.sting_progress += 0.07
            if 0.44 <= self.sting_progress <= 0.52:
                add_shake(10)
                haptic(160, 255)
                emit_particles(self.sting_target[0], self.sting_target[1], (0, 220, 255) if cryo_mode else (255, 20, 60), count=16)

                if self.ambush_target:
                    play_snd(snd_tear)
                    combo_count += 1
                    combo_timer = 300
                    if combo_count >= 15:
                        cryo_mode = True

                    if self.ambush_target == active_boss:
                        active_boss.take_stinger_hit(head.x, head.y)
                    elif hasattr(self.ambush_target, 'blood_col'):
                        spill_blood(self.ambush_target.x, self.ambush_target.y, self.ambush_target.blood_col, count=18)
                        self.bugs_eaten += 1
                        if self.ambush_target.is_gold:
                            self.hunger = self.max_hunger
                            self.evolve_now()
                        else:
                            self.hunger = min(self.max_hunger, self.hunger + 350.0)
                            if self.bugs_eaten % 5 == 0:
                                self.evolve_now()
                        self.ambush_target.respawn()

                    self.ambush_target = None

            if self.sting_progress >= 1.0:
                self.is_stinging = False
                self.sting_progress = 0.0

        tail_root_idx = 14
        for i in range(1, len(self.segments)):
            self.segments[i].follow(self.segments[i - 1].x, self.segments[i - 1].y)

        # STABILNO SIMETRIČNO V-GRANANJE CRYO DVOSTRUKOG REPA
        if cryo_mode or self.tail2_growth > 0.01:
            total_tail_segs = len(self.segments) - tail_root_idx
            root_seg = self.segments[tail_root_idx]

            while len(self.segments_tail_left) < total_tail_segs:
                self.segments_tail_left.append(Segment(root_seg.x, root_seg.y, self.seg_len, 6.0, root_seg.angle))
                self.segments_tail_right.append(Segment(root_seg.x, root_seg.y, self.seg_len, 6.0, root_seg.angle))
            while len(self.segments_tail_left) > total_tail_segs:
                self.segments_tail_left.pop()
                self.segments_tail_right.pop()

            for idx in range(total_tail_segs):
                s_center = self.segments[tail_root_idx + idx]
                s_l = self.segments_tail_left[idx]
                s_r = self.segments_tail_right[idx]

                s_l.radius = s_center.radius
                s_r.radius = s_center.radius
                s_l.angle = s_center.angle
                s_r.angle = s_center.angle

                t_prog = (idx + 1) / float(total_tail_segs)
                flare_offset = (16.0 + t_prog * 48.0) * self.tail2_growth
                perp_ang = s_center.angle + math.pi / 2

                s_l.x = clamp_x(s_center.x - math.cos(perp_ang) * flare_offset)
                s_l.y = clamp_y(s_center.y - math.sin(perp_ang) * flare_offset)
                s_r.x = clamp_x(s_center.x + math.cos(perp_ang) * flare_offset)
                s_r.y = clamp_y(s_center.y + math.sin(perp_ang) * flare_offset)
        else:
            self.segments_tail_left.clear()
            self.segments_tail_right.clear()

        if self.is_stinging:
            sp = self.sting_progress
            strike_weight = math.sin(sp * math.pi)
            total_tail_segs = len(self.segments) - tail_root_idx
            tx_st = self.sting_target[0]
            ty_st = self.sting_target[1]
            root_seg = self.segments[tail_root_idx]

            for idx in range(tail_root_idx, len(self.segments)):
                t_rel = (idx - tail_root_idx) / float(total_tail_segs)
                cur_seg = self.segments[idx]
                arc_h = math.sin(t_rel * math.pi) * 110 * strike_weight
                curve_x = (1 - t_rel) * root_seg.x + t_rel * tx_st
                curve_y = (1 - t_rel) * root_seg.y + t_rel * ty_st - arc_h
                cur_seg.x += (curve_x - cur_seg.x) * (0.65 * strike_weight)
                cur_seg.y += (curve_y - cur_seg.y) * (0.65 * strike_weight)

        for limb in self.limbs:
            limb.update()

    def draw_tail_chain(self, surf, seg_list, pal):
        tip = seg_list[-1]
        for i in range(len(seg_list) - 1, -1, -1):
            seg = seg_list[i]
            rot = seg.angle + math.pi / 2
            cos_r = math.cos(rot); sin_r = math.sin(rot)
            a = seg.radius * 0.75; b = seg.length * 0.95

            pts = []
            for step in range(6):
                th = 2 * math.pi * step / 6
                pts.append((clamp_x(seg.x + (a * math.cos(th)) * cos_r - (b * math.sin(th)) * sin_r),
                            clamp_y(seg.y + (a * math.cos(th)) * sin_r + (b * math.sin(th)) * cos_r)))

            pygame.draw.polygon(surf, pal['dark'], pts)
            pygame.draw.lines(surf, pal['edge'], True, pts, 2)
            pygame.draw.line(surf, pal['spec'], (seg.x, seg.y), (pts[0][0], pts[0][1]), 1)

            if i % 2 == 0:
                spk_len = a + 8
                back_ang = seg.angle + math.pi
                for s_sign in [-1, 1]:
                    spk_x = clamp_x(seg.x + cos_r * spk_len * s_sign + math.cos(back_ang) * 4)
                    spk_y = clamp_y(seg.y + sin_r * spk_len * s_sign + math.sin(back_ang) * 4)
                    pygame.draw.line(surf, pal['edge'], (seg.x, seg.y), (spk_x, spk_y), 2)

            pygame.draw.circle(surf, pal['neon'], (int(seg.x), int(seg.y)), 3)

        st_ang = tip.angle + math.pi
        st_x = clamp_x(tip.x + math.cos(st_ang) * 16)
        st_y = clamp_y(tip.y + math.sin(st_ang) * 16)
        pygame.draw.line(surf, (255, 255, 255), (tip.x, tip.y), (st_x, st_y), 3)
        pygame.draw.circle(surf, pal['neon'], (int(st_x), int(st_y)), 3)

    def draw(self, surf):
        head = self.segments[0]
        tip = self.segments[-1]
        tail_root_idx = 14

        pal = CRYO_PAL if cryo_mode else (OD_PAL if self.is_overdrive else NORM_PAL)

        if not self.is_burrowed:
            for idx in range(1, 16, 2):
                s = self.segments[idx]
                pygame.draw.ellipse(surf, C_GROUND_SHADOW, (int(s.x - s.radius * 1.1), int(s.y - s.radius * 0.7), int(s.radius * 2.2), int(s.radius * 1.4)))

            for idx in range(0, len(self.segments), 5):
                seg = self.segments[idx]
                dist_p = abs(idx - self.pulse_phase)
                if dist_p < 3.0:
                    draw_floor_glow(surf, seg.x, seg.y, seg.radius * 2.2, pal['neon'], 35)

        if self.is_burrowed:
            pygame.draw.ellipse(surf, (24, 18, 14), (head.x - 35, head.y - 25, 70, 50))
            pygame.draw.ellipse(surf, (38, 28, 20), (head.x - 25, head.y - 18, 50, 36), 2)

        for limb in self.limbs:
            limb.draw(surf, pal)

        # Čeljusti
        perp = head.angle + math.pi / 2
        fwd_ang = head.angle
        jaw_len = 16 + min(16, self.evo_level * 0.18)
        jaw_pinch = math.sin(pygame.time.get_ticks() * 0.05 if self.is_feasting else self.breath_clock * 3) * 0.22

        for side in [-1, 1]:
            j_base_x = head.x + math.cos(fwd_ang) * (head.radius * 0.8) + math.cos(perp) * (side * 7)
            j_base_y = head.y + math.sin(fwd_ang) * (head.radius * 0.8) + math.sin(perp) * (side * 7)

            jaw_ang = fwd_ang + (0.35 + jaw_pinch) * side
            j_mid_x = j_base_x + math.cos(jaw_ang) * (jaw_len * 0.6)
            j_mid_y = j_base_y + math.sin(jaw_ang) * (jaw_len * 0.6)

            j_tip_ang = jaw_ang - (0.55 * side)
            j_tip_x = j_mid_x + math.cos(j_tip_ang) * (jaw_len * 0.55)
            j_tip_y = j_mid_y + math.sin(j_tip_ang) * (jaw_len * 0.55)

            jaw_poly = [(j_base_x, j_base_y), (j_mid_x, j_mid_y), (j_tip_x, j_tip_y)]
            pygame.draw.lines(surf, (255, 235, 20), False, jaw_poly, 3)
            pygame.draw.circle(surf, (255, 255, 255), (int(j_tip_x), int(j_tip_y)), 2)

        breath_expand = math.sin(self.breath_clock) * 1.5
        stop_idx = (tail_root_idx - 1) if (cryo_mode and not self.is_burrowed) else -1

        # TRUP - DEFINIRANI RELJEF OKLOPA
        for i in range(len(self.segments) - 1, stop_idx, -1):
            if self.is_burrowed and i < len(self.segments) - 2:
                continue

            seg = self.segments[i]
            rot = seg.angle + math.pi / 2
            cos_r = math.cos(rot); sin_r = math.sin(rot)
            a = seg.radius + (breath_expand if i < 17 else 0)
            b = seg.length * 1.05

            if self.is_overdrive and not self.is_burrowed:
                a *= 1.15

            dist_to_pulse = abs(i - self.pulse_phase)
            energy_factor = max(0.0, 1.0 - (dist_to_pulse / 3.0)) if dist_to_pulse < 3.0 else 0.0

            pts = []
            steps = 10
            for step in range(steps):
                th = 2 * math.pi * step / steps
                pts.append((clamp_x(seg.x + (a * math.cos(th)) * cos_r - (b * math.sin(th)) * sin_r),
                            clamp_y(seg.y + (a * math.cos(th)) * sin_r + (b * math.sin(th)) * cos_r)))

            pygame.draw.polygon(surf, pal['dark'], pts)

            if a > 6:
                inner_pts = []
                for step in range(steps):
                    th = 2 * math.pi * step / steps
                    inner_pts.append((clamp_x(seg.x + ((a * 0.65) * math.cos(th)) * cos_r - ((b * 0.65) * math.sin(th)) * sin_r),
                                      clamp_y(seg.y + ((a * 0.65) * math.cos(th)) * sin_r + ((b * 0.65) * math.sin(th)) * cos_r)))
                pygame.draw.polygon(surf, pal['mid'], inner_pts)

                back_x = seg.x - math.cos(seg.angle) * (b * 0.45)
                back_y = seg.y - math.sin(seg.angle) * (b * 0.45)
                fwd_x = seg.x + math.cos(seg.angle) * (b * 0.45)
                fwd_y = seg.y + math.sin(seg.angle) * (b * 0.45)
                pygame.draw.line(surf, pal['spec'], (back_x, back_y), (fwd_x, fwd_y), 2)

            # OŠTRI VANJSKI BRID TRUPA
            pygame.draw.lines(surf, pal['edge'], True, pts, 2)

            if not self.is_burrowed and 2 <= i <= 16:
                back_ang = seg.angle + math.pi
                sp_len = a + (11 if energy_factor > 0.3 else 7) + min(22, self.evo_level * 0.40)
                w_base = 5.0
                for s_sign in [-1, 1]:
                    base_cx = seg.x + cos_r * (a * 0.85) * s_sign
                    base_cy = seg.y + sin_r * (a * 0.85) * s_sign
                    spk_tip_x = clamp_x(seg.x + cos_r * sp_len * s_sign + math.cos(back_ang) * 6)
                    spk_tip_y = clamp_y(seg.y + sin_r * sp_len * s_sign + math.sin(back_ang) * 6)

                    tri = [
                        (base_cx - math.cos(back_ang) * w_base, base_cy - math.sin(back_ang) * w_base),
                        (base_cx + math.cos(back_ang) * w_base, base_cy + math.sin(back_ang) * w_base),
                        (spk_tip_x, spk_tip_y)
                    ]
                    pygame.draw.polygon(surf, pal['dark'], tri)
                    pygame.draw.lines(surf, pal['neon'] if energy_factor > 0.3 else pal['edge'], True, tri, 2)
                    pygame.draw.line(surf, pal['spec'], (base_cx, base_cy), (spk_tip_x, spk_tip_y), 1)

            pygame.draw.circle(surf, pal['neon'], (int(seg.x), int(seg.y)), 4 if energy_factor > 0.3 else 3)
            if energy_factor > 0.5:
                pygame.draw.circle(surf, (255, 255, 255), (int(seg.x), int(seg.y)), 2)

        # DVA REPA U CRYO MODU
        if cryo_mode and not self.is_burrowed and len(self.segments_tail_left) > 0:
            self.draw_tail_chain(surf, self.segments_tail_left, pal)
            self.draw_tail_chain(surf, self.segments_tail_right, pal)

        # Glava
        if not self.is_burrowed:
            h_rad = head.radius + 2
            head_pts = [
                (head.x + math.cos(fwd_ang) * (h_rad * 1.3), head.y + math.sin(fwd_ang) * (h_rad * 1.3)),
                (head.x + math.cos(perp) * h_rad, head.y + math.sin(perp) * h_rad),
                (head.x - math.cos(fwd_ang) * (h_rad * 0.8), head.y - math.sin(fwd_ang) * (h_rad * 0.8)),
                (head.x - math.cos(perp) * h_rad, head.y - math.sin(perp) * h_rad),
            ]
            pygame.draw.polygon(surf, pal['dark'], head_pts)
            pygame.draw.lines(surf, pal['edge'], True, head_pts, 2)

            horn_len = 12 + min(16, self.evo_level * 0.20)
            for s in [-1, 1]:
                h_bx = head.x + math.cos(perp) * (s * 8)
                h_by = head.y + math.sin(perp) * (s * 8)
                h_tx = h_bx + math.cos(fwd_ang + s * 0.25) * horn_len
                h_ty = h_by + math.sin(fwd_ang + s * 0.25) * horn_len
                pygame.draw.line(surf, pal['spec'], (h_bx, h_by), (h_tx, h_ty), 3)

            num_eyes = 4 + min(12, self.evo_level // 8 * 2)
            for e_idx in range(num_eyes // 2):
                fwd = 9 - e_idx * 3
                lat = 6 + e_idx * 4
                for s in [-1, 1]:
                    ex = clamp_x(head.x + math.cos(fwd_ang) * fwd + math.cos(perp) * (lat * s))
                    ey = clamp_y(head.y + math.sin(fwd_ang) * fwd + math.sin(perp) * (lat * s))
                    pygame.draw.circle(surf, pal['neon'], (int(ex), int(ey)), 2)

        # Običan žalac
        if not cryo_mode or self.is_burrowed:
            if self.is_stinging:
                pygame.draw.circle(surf, pal['neon'], (int(tip.x), int(tip.y)), 10)
                pygame.draw.circle(surf, (255, 255, 255), (int(tip.x), int(tip.y)), 4)
                s_ang = tip.angle
                b1_x = tip.x + math.cos(s_ang - 0.7) * 16
                b1_y = tip.y + math.sin(s_ang - 0.7) * 16
                b2_x = tip.x + math.cos(s_ang + 0.7) * 16
                b2_y = tip.y + math.sin(s_ang + 0.7) * 16
                pygame.draw.line(surf, pal['spec'], (tip.x, tip.y), (b1_x, b1_y), 3)
                pygame.draw.line(surf, pal['spec'], (tip.x, tip.y), (b2_x, b2_y), 3)
            else:
                st_ang = tip.angle + math.pi
                st_x = clamp_x(tip.x + math.cos(st_ang) * 16)
                st_y = clamp_y(tip.y + math.sin(st_ang) * 16)
                pygame.draw.line(surf, pal['edge'], (tip.x, tip.y), (st_x, st_y), 3)
                pygame.draw.circle(surf, (255, 255, 255), (int(st_x), int(st_y)), 3)

# --- 5 KOMPLEKSNIH 3D BOSSOVA ---
class BossTitan:
    def __init__(self, x, y, boss_type="IRON_HORN", tier=1):
        self.x = float(x)
        self.y = float(y)
        self.boss_type = boss_type
        self.tier = tier
        self.angle = math.pi / 2
        self.state = "entering"
        self.target_y = MIN_Y + 110
        self.timer = 0
        self.stun_timer = 0
        self.parts_torn = 0
        self.wing_anim = 0.0

        if self.boss_type == "IRON_HORN":
            self.max_hp = 22 + (tier - 1) * 12
            self.hp = self.max_hp
            self.color_armor = (42, 22, 28)
            self.color_neon = (255, 45, 60)
            self.charge_vx = 0.0; self.charge_vy = 0.0

        elif self.boss_type == "TOXIC_QUEEN":
            self.max_hp = 15 + (tier - 1) * 8
            self.hp = self.max_hp
            self.color_armor = (18, 48, 28)
            self.color_neon = (45, 255, 95)
            self.shoot_cooldown = 80
            self.patrol_angle = 0.0

        elif self.boss_type == "SHADOW_STALKER":
            self.max_hp = 18 + (tier - 1) * 9
            self.hp = self.max_hp
            self.color_armor = (28, 14, 40)
            self.color_neon = (190, 45, 255)
            self.is_stealthed = False
            self.stealth_timer = 0
            self.segments = [[self.x, self.y - i * 14, 0.0, max(8, 26 - i)] for i in range(16)]

        elif self.boss_type == "PLASMA_GOLIATH":
            self.max_hp = 28 + (tier - 1) * 14
            self.hp = self.max_hp
            self.color_armor = (38, 30, 14)
            self.color_neon = (255, 170, 20)
            self.pulse_timer = 0

        else: # VOID_DREADNOUGHT
            self.max_hp = 24 + (tier - 1) * 11
            self.hp = self.max_hp
            self.color_armor = (14, 28, 48)
            self.color_neon = (0, 240, 255)
            self.warp_timer = 0

    def update(self, player_x, player_y):
        self.wing_anim += 0.35
        if self.state in ["entering", "captured"]:
            if self.state == "entering":
                self.y += 2.4
                if self.y >= self.target_y:
                    self.state = "active"
                    add_shake(18); haptic(200); play_snd(snd_slam)
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            return

        if self.boss_type == "IRON_HORN":
            self.timer += 1
            if self.state == "active":
                dx = player_x - self.x; dy = player_y - self.y
                target_ang = math.atan2(dy, dx)
                self.angle += ((target_ang - self.angle + math.pi) % (2 * math.pi) - math.pi) * 0.05
                self.x += math.cos(self.angle) * 1.6
                self.y += math.sin(self.angle) * 1.6
                if self.timer >= 180 and math.hypot(dx, dy) > 140:
                    self.state = "windup"; self.timer = 0; play_snd(snd_charge)
            elif self.state == "windup":
                self.angle = math.atan2(player_y - self.y, player_x - self.x)
                if self.timer >= 50:
                    self.state = "charging"; self.timer = 0
                    self.charge_vx = math.cos(self.angle) * 11.5
                    self.charge_vy = math.sin(self.angle) * 11.5
                    add_shake(16)
            elif self.state == "charging":
                self.x += self.charge_vx
                self.y += self.charge_vy
                emit_particles(self.x, self.y, self.color_neon, count=4, speed_mult=0.6)
                if self.x <= MIN_X + 25 or self.x >= MAX_X - 25 or self.y <= MIN_Y + 25 or self.y >= MAX_Y - 25:
                    self.state = "active"; self.stun_timer = 120
                    add_shake(24); haptic(350); play_snd(snd_slam)
                    if len(ground_cracks) < 8:
                        ground_cracks.append(GroundCrackEffect(self.x, self.y, max_radius=120))

        elif self.boss_type == "TOXIC_QUEEN":
            self.patrol_angle += 0.03
            target_px = (MIN_X + MAX_X) * 0.5 + math.cos(self.patrol_angle) * ((MAX_X - MIN_X) * 0.35)
            target_py = MIN_Y + 120 + math.sin(self.patrol_angle * 1.5) * 50
            self.x += (target_px - self.x) * 0.05
            self.y += (target_py - self.y) * 0.05
            self.angle = math.atan2(player_y - self.y, player_x - self.x)

            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = 100
                p_ang = self.angle
                boss_projectiles.append([self.x, self.y, math.cos(p_ang) * 6.0, math.sin(p_ang) * 6.0, 120])
                emit_particles(self.x, self.y, (45, 255, 80), count=12)

        elif self.boss_type == "SHADOW_STALKER":
            self.stealth_timer += 1
            if self.stealth_timer >= 220:
                self.stealth_timer = 0
                self.is_stealthed = not self.is_stealthed
                emit_particles(self.x, self.y, self.color_neon, count=20)

            spd = 3.6 if self.is_stealthed else 1.8
            dx = player_x - self.x; dy = player_y - self.y
            if math.hypot(dx, dy) > 60:
                target_ang = math.atan2(dy, dx)
                self.angle += ((target_ang - self.angle + math.pi) % (2 * math.pi) - math.pi) * 0.08
                self.x += math.cos(self.angle) * spd
                self.y += math.sin(self.angle) * spd

            self.segments[0][0] = self.x; self.segments[0][1] = self.y; self.segments[0][2] = self.angle
            for k in range(1, len(self.segments)):
                prev = self.segments[k - 1]; curr = self.segments[k]
                p_dx = prev[0] - curr[0]; p_dy = prev[1] - curr[1]
                curr[2] = math.atan2(p_dy, p_dx)
                curr[0] = prev[0] - math.cos(curr[2]) * 13
                curr[1] = prev[1] - math.sin(curr[2]) * 13

        elif self.boss_type == "PLASMA_GOLIATH":
            dx = player_x - self.x; dy = player_y - self.y
            target_ang = math.atan2(dy, dx)
            self.angle += ((target_ang - self.angle + math.pi) % (2 * math.pi) - math.pi) * 0.04
            self.x += math.cos(self.angle) * 1.3
            self.y += math.sin(self.angle) * 1.3

            self.pulse_timer += 1
            if self.pulse_timer >= 160:
                self.pulse_timer = 0
                shockwaves.append([self.x, self.y, 0, 180, self.color_neon])
                add_shake(15); haptic(150)

        elif self.boss_type == "VOID_DREADNOUGHT":
            self.warp_timer += 1
            self.angle = math.atan2(player_y - self.y, player_x - self.x)
            if self.warp_timer >= 180:
                self.warp_timer = 0
                emit_particles(self.x, self.y, self.color_neon, count=25)
                self.x = clamp_x(player_x - math.cos(self.angle) * 170)
                self.y = clamp_y(player_y - math.sin(self.angle) * 170)
                emit_particles(self.x, self.y, self.color_neon, count=25)
                add_shake(12)
            else:
                self.x += math.cos(self.angle) * 2.2
                self.y += math.sin(self.angle) * 2.2

        self.x = clamp_x(self.x, 25)
        self.y = clamp_y(self.y, 25)

    def take_stinger_hit(self, hit_from_x, hit_from_y):
        if self.state == "captured":
            return
        if self.boss_type == "IRON_HORN" and self.stun_timer <= 0:
            diff = abs((math.atan2(hit_from_y - self.y, hit_from_x - self.x) - self.angle + math.pi) % (2 * math.pi) - math.pi)
            if diff < math.pi / 2.2:
                emit_particles(self.x, self.y, (255, 255, 255), count=12); add_shake(6)
                return

        self.hp -= 2
        add_shake(15); haptic(140)
        spill_blood(self.x, self.y, self.color_neon, count=16)
        if self.hp <= 0:
            self.state = "captured"
            scorpion.trigger_boss_feast(self)

    def take_slam_hit(self):
        if self.state == "captured":
            return
        self.hp -= (3 if self.boss_type == "IRON_HORN" and self.stun_timer > 0 else 2)
        add_shake(16); haptic(160)
        spill_blood(self.x, self.y, self.color_neon, count=18)
        if self.hp <= 0:
            self.state = "captured"
            scorpion.trigger_boss_feast(self)

    def draw(self, surf):
        # 1. IRON HORN (Buba Nosorog s oklopom i masivnim rogom)
        if self.boss_type == "IRON_HORN":
            perp = self.angle + math.pi / 2
            ab_x = self.x - math.cos(self.angle) * 22
            ab_y = self.y - math.sin(self.angle) * 22
            pygame.draw.circle(surf, self.color_armor, (int(ab_x), int(ab_y)), 34)
            pygame.draw.circle(surf, self.color_neon, (int(ab_x), int(ab_y)), 34, 2)
            pygame.draw.circle(surf, (65, 30, 40), (int(self.x), int(self.y)), 28)

            h_len = 58
            h_tip_x = self.x + math.cos(self.angle) * h_len
            h_tip_y = self.y + math.sin(self.angle) * h_len
            h_poly = [(self.x + math.cos(perp)*12, self.y + math.sin(perp)*12),
                      (self.x - math.cos(perp)*12, self.y - math.sin(perp)*12),
                      (h_tip_x, h_tip_y)]
            pygame.draw.polygon(surf, (220, 230, 240), h_poly)
            pygame.draw.lines(surf, self.color_neon, True, h_poly, 2)

        # 2. TOXIC QUEEN (Osa s lepršavim krilima i prugama)
        elif self.boss_type == "TOXIC_QUEEN":
            perp = self.angle + math.pi / 2
            for step in range(4):
                ax = self.x - math.cos(self.angle) * (18 + step * 9)
                ay = self.y - math.sin(self.angle) * (18 + step * 9)
                col = self.color_neon if step % 2 == 0 else (10, 32, 15)
                pygame.draw.circle(surf, col, (int(ax), int(ay)), max(4, 22 - step * 4))

            pygame.draw.circle(surf, self.color_armor, (int(self.x), int(self.y)), 24)
            w_flap = math.sin(self.wing_anim) * 25
            for side in [-1, 1]:
                w_tip_x = self.x + math.cos(perp * side) * 50
                w_tip_y = self.y + math.sin(perp * side) * 50 + w_flap
                pygame.draw.polygon(surf, (180, 255, 210), [(self.x, self.y), (w_tip_x, w_tip_y), (self.x - 16, self.y + w_flap)])

        # 3. SHADOW STALKER (Oklopljena stonoga)
        elif self.boss_type == "SHADOW_STALKER":
            if not (self.is_stealthed and (pygame.time.get_ticks() // 80) % 2 == 0):
                for k in range(len(self.segments) - 1, 0, -1):
                    sc = self.segments[k]; sp = self.segments[k - 1]
                    perp = sc[2] + math.pi / 2
                    for s_side in [-1, 1]:
                        lx = sc[0] + math.cos(perp * s_side) * 22
                        ly = sc[1] + math.sin(perp * s_side) * 22
                        pygame.draw.line(surf, self.color_neon, (sc[0], sc[1]), (lx, ly), 2)
                    pygame.draw.circle(surf, self.color_armor, (int(sc[0]), int(sc[1])), int(sc[3]))
                    pygame.draw.circle(surf, self.color_neon, (int(sc[0]), int(sc[1])), int(sc[3]), 2)

        # 4. PLASMA GOLIATH (Kolos s energetskim kristalima)
        elif self.boss_type == "PLASMA_GOLIATH":
            pygame.draw.circle(surf, self.color_armor, (int(self.x), int(self.y)), 38)
            pygame.draw.circle(surf, self.color_neon, (int(self.x), int(self.y)), 22)
            pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y)), 10)
            for s_ang in [0.7, -0.7, 2.3, -2.3]:
                lx = self.x + math.cos(self.angle + s_ang) * 46
                ly = self.y + math.sin(self.angle + s_ang) * 46
                pygame.draw.line(surf, (80, 60, 25), (self.x, self.y), (lx, ly), 8)
                pygame.draw.circle(surf, self.color_neon, (int(lx), int(ly)), 7)

        # 5. VOID DREADNOUGHT (Vanzemaljski geometrijski titan)
        elif self.boss_type == "VOID_DREADNOUGHT":
            rot = pygame.time.get_ticks() * 0.003
            for r_step in range(4):
                c_ang = rot + r_step * (math.pi / 2)
                cx = self.x + math.cos(c_ang) * 40
                cy = self.y + math.sin(c_ang) * 40
                pygame.draw.circle(surf, self.color_neon, (int(cx), int(cy)), 8)
                pygame.draw.line(surf, (255, 255, 255), (self.x, self.y), (cx, cy), 2)
            pygame.draw.circle(surf, self.color_armor, (int(self.x), int(self.y)), 30)
            pygame.draw.circle(surf, (0, 240, 255), (int(self.x), int(self.y)), 15, 3)

        if self.state != "captured":
            bar_w = 120
            bar_x = self.x - bar_w // 2
            bar_y = self.y - 48
            pygame.draw.rect(surf, (30, 10, 15), (bar_x, bar_y, bar_w, 8), border_radius=3)
            hp_ratio = max(0.0, self.hp / float(self.max_hp))
            pygame.draw.rect(surf, self.color_neon, (bar_x, bar_y, int(bar_w * hp_ratio), 8), border_radius=3)
            pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, bar_w, 8), 1, border_radius=3)

# 100 RAZINA EVOLUCIJSKIH TITULA
EVO_TITLES = [
    "STALKER", "PROWLER", "RAVAGER", "HUNTER", "DREADNOUGHT", "GOLIATH", "BEHEMOTH", "COLOSSUS", "HARBINGER", "NIGHTFALL",
    "TWIN-TAIL BEAST", "DOMINATOR", "TYRANT", "SOVEREIGN", "VOID WALKER", "APEX ECLIPSE", "ARCHON", "PRIMORDIAL", "SHADOWFANG", "NETHERLORD",
    "TWIN-TAIL APEX", "WARBRINGER", "DEATHSTALKER", "BLOODHOUND", "CATACLYSM", "DOOMWEAVER", "HELLSPAWN", "OBLIVION", "DREADLORD", "ABYSSAL KING",
    "NIGHTSTALKER", "TERRORTITAN", "CHRONOS", "VALKYRIE", "APEX PREDATOR", "SINGULARITY", "IMMORTAL", "GOD-TITAN", "SOLAR ECLIPSE", "HYPERION",
    "DARK MATRIC", "ZENITH REAPER", "ASTRAL COLOSSUS", "VOID EMPEROR", "LEVIATHAN", "PLANET EATER", "ETERNAL OVERLORD", "STAR SHREDDER", "COSMIC HORROR", "GENESIS PRIME",
    "INFINITY STRIDER", "OMEGA PREDATOR", "CHRONO DESTROYER", "APEX DIVINITY", "GOD-TITAN APOCALYPSE", "NEBULA STRIKER", "CHAOS WEAVER", "ECLIPSE DRAGON", "TITAN OMEGA", "SOLARIS PRIME",
    "DARK STAR", "VOID ANNIHILATOR", "CHRONO TITAN", "ASTRAL EMPEROR", "GALAXY CRUSHER", "NEO APEX", "DIMENSION STRIDER", "SUPERNOVA", "ABYSS LORD", "ETERNAL COLOSSUS",
    "INFINITY GOD", "ZENITH APEX", "NIGHT HYDRA", "STELLAR SHREDDER", "WAR BRINGER PRIME", "DEATH EMPEROR", "HELL TITAN", "VOID GOD", "OMEGA TITAN", "APEX INFINITY",
    "ALPHA PRIME", "COSMIC LEVIATHAN", "TITAN ARCHON", "BLACK HOLE STRIDER", "GENESIS GOD", "IMMORTAL TITAN", "OMEGA SOVEREIGN", "STAR EATER", "CHRONO GOD", "APEX OVERLORD",
    "HYPER TITAN", "VOID SINGULARITY", "ASTRAL OMEGA", "INFINITY LORD", "NEBULA GOD", "CHAOS EMPEROR", "DEATH GOD TITAN", "COSMIC APEX", "ETERNAL DIVINITY", "ULTIMATE APEX TITAN"
]

target_x, target_y = WIDTH // 2, HEIGHT // 2
scorpion = Scorpion(target_x, target_y)
ants = [Ant(force_gold=True)] + [Ant(force_gold=False) for _ in range(4)]
treasure_worm = TreasureWorm()
worm_spawn_timer = 0

is_user_touching = False
door_open_progress = 0.0

font_title = pygame.font.SysFont(None, 28, bold=True)
font_hud = pygame.font.SysFont(None, 22)
font_combo = pygame.font.SysFont(None, 36, bold=True)

flash_surf = pygame.Surface((WIDTH, HEIGHT))
running = True

while running:
    current_time_ms = pygame.time.get_ticks()
    cycle_val = math.sin(current_time_ms * 0.00015)
    day_blend = 0.5 + 0.5 * cycle_val

    is_night = day_blend < 0.35
    is_twilight = 0.35 <= day_blend <= 0.65
    stealth_active = is_night or is_twilight

    current_bg = (int(3 + day_blend * 12), int(3 + day_blend * 14), int(6 + day_blend * 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_user_touching = True
            scorpion.ambush_timer = 0
            if scorpion.is_burrowed:
                scorpion.unburrow()

            if current_time_ms - last_click_time < DOUBLE_CLICK_THRESH:
                scorpion.trigger_slam(ants)

            last_click_time = current_time_ms
            target_x = clamp_x(event.pos[0])
            target_y = clamp_y(event.pos[1])

        elif event.type == pygame.MOUSEMOTION:
            if is_user_touching:
                target_x = clamp_x(event.pos[0])
                target_y = clamp_y(event.pos[1])
                scorpion.ambush_timer = 0
        elif event.type == pygame.MOUSEBUTTONUP:
            is_user_touching = False

    if is_user_touching:
        m_pos = pygame.mouse.get_pos()
        target_x = clamp_x(m_pos[0])
        target_y = clamp_y(m_pos[1])
        scorpion.ambush_timer = 0

    head = scorpion.segments[0]

    # Spawn crva s blagom svakih ~1500 frameova
    worm_spawn_timer += 1
    if worm_spawn_timer >= 1200 and not treasure_worm.active:
        worm_spawn_timer = 0
        treasure_worm.spawn()

    if treasure_worm.active:
        treasure_worm.update(head.x, head.y)
        d_worm = math.hypot(head.x - treasure_worm.x, head.y - treasure_worm.y)
        if d_worm < 42 and not scorpion.is_feasting:
            last_mutation_name = random.choice(TreasureWorm.MUTATIONS_POOL)
            treasure_worm.active = False
            play_snd(snd_catch); haptic(250)
            spill_blood(head.x, head.y, (255, 230, 80), count=25, spread=7.0)
            add_shake(15)
            scorpion.hunger = scorpion.max_hunger
            for _ in range(2): scorpion.evolve_now()

    # Boss pojava
    if scorpion.evo_level >= next_boss_level and not active_boss:
        door_open_progress = 1.0
        play_snd(snd_door)
        door_center_x = (MIN_X + MAX_X) // 2

        boss_types = ["IRON_HORN", "TOXIC_QUEEN", "SHADOW_STALKER", "PLASMA_GOLIATH", "VOID_DREADNOUGHT"]
        chosen_type = boss_types[boss_cycle_index % len(boss_types)]
        boss_tier = (boss_cycle_index // len(boss_types)) + 1
        active_boss = BossTitan(door_center_x, MIN_Y - 45, chosen_type, boss_tier)

        boss_cycle_index += 1
        next_boss_level += 5

    if door_open_progress > 0:
        door_open_progress = max(0.0, door_open_progress - 0.015)

    extra_cryo_ants = min(3, max(0, 1 + (combo_count - 15) // 10)) if (cryo_mode and combo_count >= 15) else 0
    desired_ant_count = min(8, 5 + extra_cryo_ants)
    while len(ants) < desired_ant_count:
        ants.append(Ant(force_gold=False))

    should_hunt = scorpion.auto_hunting and (scorpion.ambush_timer <= 0) and not scorpion.is_burrowed

    if not is_user_touching and not scorpion.is_feasting:
        if active_boss and active_boss.state == "active" and should_hunt:
            target_x, target_y = active_boss.x, active_boss.y
        elif should_hunt and ants:
            closest_ant = min(ants, key=lambda b: math.hypot(head.x - b.x, head.y - b.y))
            target_x, target_y = closest_ant.x, closest_ant.y
        elif not is_user_touching:
            target_x, target_y = head.x, head.y

    if active_boss:
        active_boss.update(head.x, head.y)
        d_boss_head = math.hypot(head.x - active_boss.x, head.y - active_boss.y)
        if d_boss_head < 50 and not scorpion.is_feasting and active_boss.state == "active":
            active_boss.take_stinger_hit(head.x, head.y)

    surv_proj = []
    for pr in boss_projectiles:
        pr[0] += pr[2]; pr[1] += pr[3]; pr[4] -= 1
        d_p = math.hypot(head.x - pr[0], head.y - pr[1])
        if d_p < 30:
            scorpion.hunger = max(0.0, scorpion.hunger - 150.0)
            add_shake(10); haptic(100)
            spill_blood(pr[0], pr[1], (45, 255, 80), count=8)
            continue
        if pr[4] > 0 and (MIN_X < pr[0] < MAX_X) and (MIN_Y < pr[1] < MAX_Y):
            surv_proj.append(pr)
    boss_projectiles = surv_proj

    for ant in list(ants):
        ant.update(head.x, head.y, scorpion.is_burrowed)
        dist = math.hypot(head.x - ant.x, head.y - ant.y)
        can_eat = is_user_touching or scorpion.auto_hunting
        if dist < 42 and not scorpion.is_feasting and can_eat and not scorpion.is_burrowed:
            scorpion.trigger_feast(ant.x, ant.y, ant.blood_col, ant.is_gold)
            ant.respawn()

    scorpion.update(target_x, target_y, is_user_touching, ants)

    # ==================== ISCRTAVANJE ====================
    screen.fill(current_bg)

    # 1. GRANICE ARENE
    border_col = (int(50 + day_blend * 30), 20, int(30 + day_blend * 20))
    pygame.draw.rect(screen, border_col, (MIN_X, MIN_Y, MAX_X - MIN_X, MAX_Y - MIN_Y), 2, border_radius=8)

    # Vrata
    door_w = 170
    door_x = (MIN_X + MAX_X) // 2 - door_w // 2
    door_shift = int((door_w // 2) * door_open_progress)
    pygame.draw.line(screen, (0, 240, 255), (door_x, MIN_Y), (door_x + door_w // 2 - door_shift, MIN_Y), 5)
    pygame.draw.line(screen, (0, 240, 255), (door_x + door_w // 2 + door_shift, MIN_Y), (door_x + door_w, MIN_Y), 5)

    # Pukotine tla
    surv_gc = []
    for gc in ground_cracks:
        if gc.update():
            gc.draw(screen)
            surv_gc.append(gc)
    ground_cracks = surv_gc

    # Lokve tekuće krvi na podu
    surv_puddles = []
    for bp in blood_puddles:
        if bp.update():
            bp.draw(screen)
            surv_puddles.append(bp)
    blood_puddles = surv_puddles

    # Kapljice krvi u letu
    surv_b = []
    for b in blood_drops:
        if b.update():
            b.draw(screen)
            surv_b.append(b)
    blood_drops = surv_b

    surv_fp = []
    for fp in footprints:
        fp[3] -= 1
        if fp[3] > 0:
            fade = fp[3] / 100.0
            col = (int(160 * fade), int(20 * fade), int(45 * fade))
            pygame.draw.circle(screen, col, (int(fp[0]), int(fp[1])), fp[2])
            surv_fp.append(fp)
    footprints = surv_fp

    surv_waves = []
    for w in shockwaves:
        w[2] += 5
        if w[2] < w[3]:
            pygame.draw.circle(screen, w[4], (int(w[0]), int(w[1])), int(w[2]), 3)
            surv_waves.append(w)
    shockwaves = surv_waves

    # Crtanje plijena
    treasure_worm.draw(screen)
    for ant in ants:
        ant.draw(screen)

    for pr in boss_projectiles:
        pygame.draw.circle(screen, (45, 255, 80), (int(pr[0]), int(pr[1])), 6)

    if active_boss:
        active_boss.draw(screen)

    # Crtanje škorpiona
    scorpion.draw(screen)

    surv_p = []
    for p in particles:
        p[0] += p[2]; p[1] += p[3]
        p[2] *= 0.90; p[3] *= 0.90
        p[4] -= 1
        if p[4] > 0:
            sz = max(1, int(3.5 * (p[4] / p[5])))
            px = clamp_x(p[0])
            py = clamp_y(p[1])
            pygame.draw.circle(screen, p[6], (int(px), int(py)), sz)
            surv_p.append(p)
    particles = surv_p[-60:]

    if flash_alpha > 0:
        flash_surf.fill(flash_color)
        flash_surf.set_alpha(int(flash_alpha))
        screen.blit(flash_surf, (0, 0))
        flash_alpha = max(0, flash_alpha - 12)

    # ==================== HUD TRAKA (STROGO IZNAD ARENE) ====================
    pygame.draw.rect(screen, (8, 6, 12), (0, 0, WIDTH, HUD_BAR_HEIGHT))
    pygame.draw.line(screen, (50, 40, 52), (0, HUD_BAR_HEIGHT), (WIDTH, HUD_BAR_HEIGHT), 2)

    title_idx = min(len(EVO_TITLES) - 1, scorpion.evo_level - 1)
    hud_title = EVO_TITLES[title_idx]
    dna_progress = scorpion.bugs_eaten % 5

    lvl_col = (0, 220, 255) if cryo_mode else ((255, 10, 50) if scorpion.is_overdrive else (255, 255, 255))
    prefix = "CRYO" if cryo_mode else ("OVERDRIVE" if scorpion.is_overdrive else "EVO")
    title_surf = font_title.render(f"{prefix} [LVL {scorpion.evo_level}/100] : {hud_title}", True, lvl_col)
    screen.blit(title_surf, (SAFE_PAD_X, 8))

    # Health / Hunger bar
    bar_x, bar_y = SAFE_PAD_X, 38
    bar_w, bar_h = 240, 16
    hunger_pct = scorpion.hunger / scorpion.max_hunger

    pygame.draw.rect(screen, (35, 15, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    curr_bar_w = int(bar_w * hunger_pct)
    if curr_bar_w > 0:
        bar_col = (0, 220, 255) if cryo_mode else ((255, 10, 50) if scorpion.is_overdrive else (255, 45, 75))
        pygame.draw.rect(screen, bar_col, (bar_x, bar_y, curr_bar_w, bar_h), border_radius=4)
    pygame.draw.rect(screen, (140, 140, 160), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    status_txt = "UKOPAN" if scorpion.is_burrowed else ("HUNT" if scorpion.auto_hunting else ("OD" if scorpion.is_overdrive else "AKTIVAN"))
    hunger_info = font_hud.render(f"{int(hunger_pct * 100)}% [{status_txt}]", True, (220, 225, 240))
    screen.blit(hunger_info, (bar_x + bar_w + 12, bar_y))

    # ZADNJA POKUPLJENA MODIFIKACIJA OD CRVA
    mod_txt = font_hud.render(f"MODIFIKACIJA: {last_mutation_name}", True, (255, 230, 80))
    screen.blit(mod_txt, (SAFE_PAD_X, 64))

    # DNA status
    dna_label = font_hud.render(f"DNA: {dna_progress}/5", True, (255, 215, 0))
    dna_x = WIDTH - SAFE_PAD_X - dna_label.get_width()
    screen.blit(dna_label, (dna_x, 8))

    dot_start_x = dna_x - 70
    for d_i in range(5):
        d_pos = (dot_start_x + d_i * 12, 16)
        is_filled = d_i < dna_progress
        pygame.draw.circle(screen, (255, 215, 0) if is_filled else (60, 50, 20), d_pos, 4)
        if is_filled:
            pygame.draw.circle(screen, (255, 255, 255), d_pos, 2)

    phase_name = "NOĆ" if is_night else ("DAN" if day_blend > 0.65 else "SUMRAK")
    cycle_col = (140, 200, 255) if is_night else ((255, 220, 80) if day_blend > 0.65 else (255, 140, 180))
    cycle_surf = font_hud.render(f"CIKLUS: {phase_name}", True, cycle_col)
    screen.blit(cycle_surf, (WIDTH - SAFE_PAD_X - cycle_surf.get_width(), 38))

    if combo_count >= 2 and combo_timer > 0:
        combo_txt = f"COMBO x{combo_count}!"
        c_surf = font_combo.render(combo_txt, True, (255, 215, 0) if combo_count >= 3 else (255, 80, 100))
        screen.blit(c_surf, (WIDTH - SAFE_PAD_X - c_surf.get_width(), 64))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
