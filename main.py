import pygame
import random
import math
from pygame.math import Vector2
import asyncio
import platform

# --- Constants ---
WIDTH, HEIGHT = 1400, 900
BG_COLOR = (10, 10, 25)
FONT_COLOR = (200, 200, 200)
FPS = 60
SIM_SPEED = 1.0
MAX_BOIDS = 1000
MAX_PREDATORS = 20

# Initial Population
NUM_BOIDS = 300
NUM_PREDATORS = 5
NUM_FOOD = 40
NUM_WATER_SOURCES = 6
NUM_OBSTACLES = 10

# Grid for Spatial Partitioning
GRID_CELL_SIZE = 80
GRID_COLS = math.ceil(WIDTH / GRID_CELL_SIZE)
GRID_ROWS = math.ceil(HEIGHT / GRID_CELL_SIZE)

# --- Boid Parameters ---
BOID_COLOR = (100, 180, 255)
MAX_BOID_SPEED = 2.0
MAX_BOID_FORCE = 0.2
BOID_PERCEPTION_RADIUS = 60
BOID_SEPARATION_RADIUS = 20
BOID_SIZE = 4
BOID_START_ENERGY = 150
BOID_ENERGY_DECAY = 0.08 * SIM_SPEED
BOID_MAX_ENERGY = 300
BOID_START_HEALTH = 100
BOID_HEALTH_DECAY = 0.005 * SIM_SPEED
BOID_MAX_HEALTH = 100
BOID_START_THIRST = 100
BOID_THIRST_DECAY = 0.06 * SIM_SPEED
BOID_MAX_THIRST = 100
BOID_MIN_REPRODUCTION_AGE = 400
BOID_REPRODUCTION_ENERGY_COST = 100
BOID_REPRODUCTION_THIRST_COST = 30
BOID_REPRODUCTION_HEALTH_COST = 10
BOID_REPRODUCTION_COOLDOWN = 600
BOID_MAX_AGE = 3000
BOID_AGED_SPEED_PENALTY_FACTOR = 0.5
BOID_AGED_HEALTH_PENALTY_FACTOR = 0.02

# --- Predator Parameters ---
PREDATOR_COLOR = (255, 80, 80)
MAX_PREDATOR_SPEED = 2.8
MAX_PREDATOR_FORCE = 0.3
PREDATOR_PERCEPTION_RADIUS = 100
PREDATOR_SEPARATION_RADIUS = 30
PREDATOR_SIZE = 7
PREDATOR_START_ENERGY = 200
PREDATOR_ENERGY_DECAY = 0.12 * SIM_SPEED
PREDATOR_MAX_ENERGY = 400
PREDATOR_START_HEALTH = 150
PREDATOR_HEALTH_DECAY = 0.01 * SIM_SPEED
PREDATOR_MAX_HEALTH = 150
PREDATOR_START_THIRST = 80
PREDATOR_THIRST_DECAY = 0.08 * SIM_SPEED
PREDATOR_MAX_THIRST = 80
PREDATOR_BOIDS_EATEN_FOR_REPRODUCTION = 3
PREDATOR_REPRODUCTION_COOLDOWN = 900
PREDATOR_MAX_AGE = 4000
PREDATOR_AGED_SPEED_PENALTY_FACTOR = 0.6
PREDATOR_AGED_HEALTH_PENALTY_FACTOR = 0.03
PREDATOR_BOID_ENERGY = 100

# --- Food Parameters ---
FOOD_COLOR = (80, 255, 80)
FOOD_SIZE = 4
FOOD_ENERGY_VALUE = 70
FOOD_SPAWN_INTERVAL = 240
FOOD_MAX_COUNT = 80
FOOD_DECAY_START_AGE = 600
FOOD_DECAY_RATE = 0.005

# --- Water Parameters ---
WATER_COLOR = (80, 80, 255)
WATER_SIZE = 30
WATER_THIRST_GAIN_RATE = 1.5 * SIM_SPEED
WATER_REPLENISH_RATE = 0.01 * SIM_SPEED
WATER_START_LEVEL = 100.0
WATER_MAX_LEVEL = 100.0

# --- Obstacle Parameters ---
OBSTACLE_COLOR = (150, 150, 150)
OBSTACLE_SIZE = 25

# --- Sickness Parameters ---
SICKNESS_TRANSMISSION_RADIUS = 15
SICKNESS_CHANCE_PER_FRAME_NEAR_SICK = 0.008 * SIM_SPEED
SICKNESS_HEALTH_IMPACT = 0.05 * SIM_SPEED
SICKNESS_SPEED_PENALTY_FACTOR = 0.7
SICKNESS_DURATION_MIN = 300
SICKNESS_DURATION_MAX = 800
SICKNESS_ENERGY_GAIN_PENALTY_FACTOR = 0.5

# --- Rule Weights ---
BOID_SEPARATION_WEIGHT = 1.5
BOID_ALIGNMENT_WEIGHT = 1.0
BOID_COHESION_WEIGHT = 1.0
BOID_FLEE_PREDATOR_WEIGHT = 5.5
BOID_SEEK_FOOD_WEIGHT = 2.2
BOID_AVOID_OBSTACLE_WEIGHT = 5.0
BOID_SEEK_WATER_WEIGHT = 2.0
BOID_DISTRESS_AMPLIFICATION = 2.0

PREDATOR_SEEK_BOID_WEIGHT = 3.0
PREDATOR_SEPARATION_WEIGHT = 0.6
PREDATOR_AVOID_OBSTACLE_WEIGHT = 3.0
PREDATOR_SEEK_WATER_WEIGHT = 1.8
PREDATOR_FLOCKING_WEIGHT = 0.8

# --- Dialogue System ---
DIALOGUE_DURATION = 90
BOID_DIALOGUES = [
    "Hey!", "Nice flock!", "Where's food?", "Predator!", "Lost?",
    "Follow!", "So fast!", "Tasty!", "This way!", "Let's go!",
    "Sunny!", "Thirsty...", "Sick...", "Old...", "Run!", "Water!",
    "Meteor scars...", "New hope!", "Survive!", "Together!"
]
PREDATOR_DIALOGUES = [
    "Hungry...", "Target!", "Soon...", "Gotcha!", "Mine!",
    "Faster!", "Need more!", "Too slow!", "Run, run!", "Pathetic.",
    "Easy meal.", "Blood!", "Thirsty...", "Sick...", "Old...",
    "We hunt!", "Pack rules!", "No escape!"
]
DIALOGUE_CHANCE_BASE = 0.0001
DIALOGUE_CHANCE_STATUS = 0.004
DIALOGUE_CHANCE_EVENT = 0.03

# --- Natural Events Parameters ---
EVENT_INTERVAL_MIN = 900 * (1/SIM_SPEED)
EVENT_INTERVAL_MAX = 2400 * (1/SIM_SPEED)
EVENT_TYPES = ["storm", "sickness_outbreak", "food_bloom", "predator_influx", "heatwave", "acid_rain", "obstacle_spawn", "calm"]

# --- Particle System ---
PARTICLE_DECAY = 7 * SIM_SPEED
PARTICLE_SIZE = 2
PARTICLE_SPEED = 1.0

# --- Story Parameters ---
STORY_EVENTS = [
    (0, "A meteor struck, shattering the ecosystem. Survivors struggle to rebuild."),
    (1000, "Boids discover new food patches, sparking hope."),
    (2000, "Predators grow bolder, forming hunting packs."),
    (3000, "A strange sickness spreads, challenging survival."),
    (4000, "The ecosystem stabilizes, but storms loom.")
]

class Camera:
    def __init__(self):
        self.position = Vector2(WIDTH / 2, HEIGHT / 2)
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.dragging = False
        self.last_mouse_pos = Vector2(0, 0)

    def apply(self, position):
        offset = position - self.position
        scaled = offset * self.zoom
        return Vector2(scaled.x + WIDTH / 2, scaled.y + HEIGHT / 2)

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = Vector2(event.pos)
                elif event.button == 4:
                    self.zoom = min(self.max_zoom, self.zoom * 1.1)
                elif event.button == 5:
                    self.zoom = max(self.min_zoom, self.zoom / 1.1)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                current_pos = Vector2(event.pos)
                delta = (current_pos - self.last_mouse_pos) / self.zoom
                self.position -= delta
                self.last_mouse_pos = current_pos

class Particle:
    def __init__(self, pos, color, velocity):
        self.position = Vector2(pos)
        self.color = color
        self.velocity = Vector2(velocity) * random.uniform(0.5, 1.0) * SIM_SPEED
        self.alpha = 255
        self.size = PARTICLE_SIZE
        self.is_alive = True

    def update(self):
        self.position += self.velocity
        self.alpha -= PARTICLE_DECAY
        if self.alpha <= 0:
            self.is_alive = False

    def draw(self, screen, camera):
        if self.is_alive:
            pos = camera.apply(self.position)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = self.color[:3] + (max(0, int(self.alpha)),)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(s, (pos.x - self.size, pos.y - self.size))

def get_grid_cell(position):
    col = int(position.x / GRID_CELL_SIZE)
    row = int(position.y / GRID_CELL_SIZE)
    col = max(0, min(col, GRID_COLS - 1))
    row = max(0, min(row, GRID_ROWS - 1))
    return (col, row)

def get_neighbors_from_grid(position, perception_radius, grid, entity_type=None):
    cell = get_grid_cell(position)
    neighbors = []
    cell_check_radius = math.ceil(perception_radius / GRID_CELL_SIZE)
    for i in range(max(0, cell[0] - cell_check_radius), min(GRID_COLS, cell[0] + cell_check_radius + 1)):
        for j in range(max(0, cell[1] - cell_check_radius), min(GRID_ROWS, cell[1] + cell_check_radius + 1)):
            if (i, j) in grid:
                for entity in grid[(i, j)]:
                    if entity.position.distance_to(position) < perception_radius:
                        if entity_type is None or isinstance(entity, entity_type):
                            neighbors.append(entity)
    return neighbors

class Entity:
    def __init__(self, x, y, color, max_speed, max_force, size,
                 start_energy, energy_decay, max_energy,
                 start_health, health_decay, max_health,
                 start_thirst, thirst_decay, max_thirst, max_age,
                 aged_speed_penalty_factor, aged_health_penalty_factor):
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(max_speed / 2, max_speed)
        self.acceleration = Vector2(0, 0)
        self.color = color
        self.max_speed = max_speed
        self.max_force = max_force
        self.size = size
        self.energy = start_energy
        self.energy_decay_rate = energy_decay
        self.max_energy = max_energy
        self.health = start_health
        self.health_decay_rate = health_decay
        self.max_health = max_health
        self.thirst = start_thirst
        self.thirst_decay_rate = thirst_decay
        self.max_thirst = max_thirst
        self.age = 0
        self.max_age = max_age
        self.aged_speed_penalty_factor = aged_speed_penalty_factor
        self.aged_health_penalty_factor = aged_health_penalty_factor
        self.is_alive = True
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.is_sick = False
        self.sickness_duration = 0

    def update(self, all_entities, grid, particles):
        if not self.is_alive:
            return
        self.velocity += self.acceleration * SIM_SPEED
        current_max_speed = self.max_speed * self.get_speed_multiplier()
        if self.velocity.length() > current_max_speed:
            self.velocity.scale_to_length(current_max_speed)
        self.position += self.velocity * SIM_SPEED
        self.acceleration *= 0
        self.handle_boundaries()
        self.age += SIM_SPEED
        self.energy = max(0, self.energy - self.energy_decay_rate * SIM_SPEED)
        self.thirst = max(0, self.thirst - self.thirst_decay_rate * SIM_SPEED)
        self.health = max(0, self.health - self.health_decay_rate * SIM_SPEED)
        if self.age > self.max_age * 0.7:
            age_factor = (self.age - self.max_age * 0.7) / (self.max_age * 0.3)
            self.health -= self.aged_health_penalty_factor * age_factor * SIM_SPEED
        if self.is_sick:
            self.sickness_duration -= SIM_SPEED
            self.health -= SICKNESS_HEALTH_IMPACT * SIM_SPEED
            neighbors = get_neighbors_from_grid(self.position, SICKNESS_TRANSMISSION_RADIUS, grid)
            for entity in neighbors:
                if entity is not self and entity.is_alive and not entity.is_sick and isinstance(entity, (Boid, Predator)):
                    if random.random() < SICKNESS_CHANCE_PER_FRAME_NEAR_SICK:
                        entity.contract_sickness()
            if self.sickness_duration <= 0:
                self.is_sick = False
        if self.energy <= 0 or self.health <= 0 or self.thirst <= 0 or self.age >= self.max_age:
            self.is_alive = False
        if self.dialogue_timer > 0:
            self.dialogue_timer -= SIM_SPEED
            if self.dialogue_timer <= 0:
                self.current_dialogue = ""
        else:
            base_chance = DIALOGUE_CHANCE_BASE * SIM_SPEED
            status_chance = 0
            if self.is_sick:
                status_chance = DIALOGUE_CHANCE_STATUS * SIM_SPEED
            elif self.energy < self.max_energy * 0.4:
                status_chance = DIALOGUE_CHANCE_STATUS * SIM_SPEED
            elif self.health < self.max_health * 0.4:
                status_chance = DIALOGUE_CHANCE_STATUS * SIM_SPEED
            elif self.thirst < self.max_thirst * 0.4:
                status_chance = DIALOGUE_CHANCE_STATUS * SIM_SPEED
            elif self.age > self.max_age * 0.8:
                status_chance = DIALOGUE_CHANCE_STATUS * SIM_SPEED
            if random.random() < base_chance + status_chance:
                self.start_dialogue()

    def get_speed_multiplier(self):
        age_penalty_mult = 1.0
        if self.age > self.max_age * 0.7:
            age_factor = (self.age - self.max_age * 0.7) / (self.max_age * 0.3)
            age_penalty_mult = 1.0 - (age_factor * (1.0 - self.aged_speed_penalty_factor))
        sickness_penalty_mult = SICKNESS_SPEED_PENALTY_FACTOR if self.is_sick else 1.0
        return age_penalty_mult * sickness_penalty_mult

    def contract_sickness(self):
        if not self.is_sick:
            self.is_sick = True
            self.sickness_duration = random.uniform(SICKNESS_DURATION_MIN, SICKNESS_DURATION_MAX)
            if self.dialogue_timer <= 0:
                self.start_dialogue(status="sick")

    def apply_force(self, force):
        self.acceleration += force

    def seek(self, target_pos):
        desired = target_pos - self.position
        if desired.length() == 0:
            return Vector2(0, 0)
        desired = desired.normalize() * self.max_speed * self.get_speed_multiplier()
        steer = desired - self.velocity
        if steer.length() > self.max_force:
            steer.scale_to_length(self.max_force)
        return steer

    def avoid(self, target_pos, avoidance_radius):
        steer = Vector2(0, 0)
        distance = self.position.distance_to(target_pos)
        if distance > 0 and distance < avoidance_radius:
            desired = self.position - target_pos
            desired = desired.normalize() * self.max_speed * self.get_speed_multiplier()
            steer = desired - self.velocity
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
        return steer

    def handle_boundaries(self):
        if self.position.x < 0:
            self.position.x = WIDTH
        elif self.position.x > WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = HEIGHT
        elif self.position.y > HEIGHT:
            self.position.y = 0

    def start_dialogue(self, status=None):
        self.dialogue_timer = DIALOGUE_DURATION
        dialogues = BOID_DIALOGUES if isinstance(self, Boid) else PREDATOR_DIALOGUES
        if status == "sick" and "Sick..." in dialogues:
            self.current_dialogue = "Sick..."
        elif status == "predator" and "Predator!" in dialogues:
            self.current_dialogue = "Predator!"
        elif status == "food" and ("Tasty!" in dialogues or "Hungry..." in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Tasty" in d or "Hungry" in d])
        elif status == "water" and ("Water!" in dialogues or "Thirsty..." in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Water" in d or "Thirsty" in d])
        elif status == "target" and ("Target!" in dialogues or "Hungry..." in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Target" in d or "Hungry" in d])
        elif status == "story" and ("Meteor scars..." in dialogues or "We hunt!" in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Meteor" in d or "hope" in d or "Survive" in d or "hunt" in d])
        elif self.energy < self.max_energy * 0.3 and ("Hungry..." in dialogues or "Tasty!" in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Hungry" in d or "Tasty" in d] or dialogues)
        elif self.thirst < self.max_thirst * 0.3 and "Thirsty..." in dialogues:
            self.current_dialogue = "Thirsty..."
        elif self.age > self.max_age * 0.7 and ("Old..." in dialogues or "tired" in dialogues):
            self.current_dialogue = random.choice([d for d in dialogues if "Old" in d or "tired" in d] or dialogues)
        else:
            self.current_dialogue = random.choice(dialogues)

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            if self.dialogue_timer > 0 and self.current_dialogue:
                text_surface = font.render(self.current_dialogue, True, FONT_COLOR)
                text_rect = text_surface.get_rect(center=(pos.x, pos.y - self.size - 15))
                screen.blit(text_surface, text_rect)

class Boid(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, BOID_COLOR, MAX_BOID_SPEED, MAX_BOID_FORCE, BOID_SIZE,
                         BOID_START_ENERGY, BOID_ENERGY_DECAY, BOID_MAX_ENERGY,
                         BOID_START_HEALTH, BOID_HEALTH_DECAY, BOID_MAX_HEALTH,
                         BOID_START_THIRST, BOID_THIRST_DECAY, BOID_MAX_THIRST, BOID_MAX_AGE,
                         BOID_AGED_SPEED_PENALTY_FACTOR, BOID_AGED_HEALTH_PENALTY_FACTOR)
        self.last_reproduction_time = 0
        self.state = "foraging"  # foraging, resting, fleeing
        self.memory = {"last_food": None, "last_water": None}
        self.state_timer = random.uniform(100, 300)

    def update(self, all_entities_list, grid, particles):
        if not self.is_alive:
            self.spawn_particles(particles, self.color)
            return None
        new_boid = None
        self.update_state(all_entities_list, grid)
        self.flock(all_entities_list, grid)
        super().update(all_entities_list, grid, particles)
        if self.is_sick:
            self.energy -= self.energy_decay_rate * (1.0 - SICKNESS_ENERGY_GAIN_PENALTY_FACTOR) * SIM_SPEED
        if len([b for b in all_entities_list if isinstance(b, Boid) and b.is_alive]) < MAX_BOIDS and \
           not self.is_sick and \
           self.age >= BOID_MIN_REPRODUCTION_AGE and \
           self.energy >= BOID_REPRODUCTION_ENERGY_COST and \
           self.thirst >= BOID_MAX_THIRST * 0.5 and \
           self.health >= BOID_MAX_HEALTH * 0.7 and \
           (pygame.time.get_ticks() - self.last_reproduction_time) / (1000 / FPS) >= BOID_REPRODUCTION_COOLDOWN * (1/SIM_SPEED):
            nearby_boids = get_neighbors_from_grid(self.position, self.size * 5, grid, Boid)
            has_nearby_mate = any(other_boid.is_alive and other_boid is not self for other_boid in nearby_boids)
            if has_nearby_mate or random.random() < 0.002 * SIM_SPEED:
                new_boid = Boid(self.position.x + random.uniform(-self.size*2, self.size*2), self.position.y + random.uniform(-self.size*2, self.size*2))
                self.energy -= BOID_REPRODUCTION_ENERGY_COST
                self.thirst -= BOID_REPRODUCTION_THIRST_COST
                self.health -= BOID_REPRODUCTION_HEALTH_COST
                self.last_reproduction_time = pygame.time.get_ticks()
        return new_boid

    def update_state(self, all_entities_list, grid):
        self.state_timer -= SIM_SPEED
        if self.state_timer <= 0:
            predators_near = get_neighbors_from_grid(self.position, BOID_PERCEPTION_RADIUS * 1.2, grid, Predator)
            if predators_near:
                self.state = "fleeing"
            elif self.energy > self.max_energy * 0.8 and self.thirst > self.max_thirst * 0.8:
                self.state = "resting"
            else:
                self.state = "foraging"
            self.state_timer = random.uniform(100, 300)

    def flock(self, all_entities_list, grid):
        sep = Vector2(0, 0)
        ali = Vector2(0, 0)
        coh = Vector2(0, 0)
        flee_predator = Vector2(0, 0)
        seek_food = Vector2(0, 0)
        seek_water = Vector2(0, 0)
        avoid_obstacle = Vector2(0, 0)
        total_nearby_boids = 0
        avg_position_boids = Vector2(0, 0)
        avg_velocity_boids = Vector2(0, 0)
        fleeing_neighbors_flee_force = Vector2(0, 0)
        closest_food = None
        min_food_dist = float('inf')
        closest_water = None
        min_water_dist = float('inf')
        neighbors = get_neighbors_from_grid(self.position, max(BOID_PERCEPTION_RADIUS, SICKNESS_TRANSMISSION_RADIUS), grid)
        for entity in neighbors:
            if entity is self or not entity.is_alive:
                continue
            distance = self.position.distance_to(entity.position)
            if isinstance(entity, Boid) and distance < BOID_PERCEPTION_RADIUS:
                total_nearby_boids += 1
                avg_velocity_boids += entity.velocity
                avg_position_boids += entity.position
                if distance < BOID_SEPARATION_RADIUS:
                    diff = self.position - entity.position
                    if distance > 0:
                        diff = diff.normalize() / distance
                    sep += diff
                predators_near_neighbor = get_neighbors_from_grid(entity.position, PREDATOR_PERCEPTION_RADIUS * 0.8, grid, Predator)
                if predators_near_neighbor:
                    fleeing_neighbors_flee_force += (self.position - entity.position).normalize()
            elif isinstance(entity, Predator):
                flee_vector = self.avoid(entity.position, BOID_PERCEPTION_RADIUS * 1.2)
                flee_predator += flee_vector
                if distance < BOID_PERCEPTION_RADIUS * 0.8 and self.dialogue_timer <= 0:
                    self.start_dialogue(status="predator")
            elif isinstance(entity, Food):
                if distance < min_food_dist:
                    min_food_dist = distance
                    closest_food = entity
                    self.memory["last_food"] = entity.position
                if distance < self.size + entity.size / 2:
                    if entity.is_alive:
                        entity.is_alive = False
                        self.energy = min(self.max_energy, self.energy + entity.energy_value)
                        if self.dialogue_timer <= 0:
                            self.start_dialogue(status="food")
            elif isinstance(entity, WaterSource):
                if distance < min_water_dist:
                    min_water_dist = distance
                    closest_water = entity
                    self.memory["last_water"] = entity.position
                if distance < entity.size:
                    if entity.water_level > 0:
                        thirst_gained = min(self.max_thirst - self.thirst, WATER_THIRST_GAIN_RATE * SIM_SPEED, entity.water_level)
                        self.thirst += thirst_gained
                        entity.water_level -= thirst_gained
                        if self.dialogue_timer <= 0:
                            self.start_dialogue(status="water")
            elif isinstance(entity, Obstacle):
                avoid_vector = self.avoid(entity.position, entity.size + self.size)
                avoid_obstacle += avoid_vector
        if total_nearby_boids > 0:
            avg_velocity_boids /= total_nearby_boids
            ali = avg_velocity_boids.normalize() * self.max_speed
            ali = ali - self.velocity
            if ali.length() > self.max_force:
                ali.scale_to_length(self.max_force)
            avg_position_boids /= total_nearby_boids
            coh = avg_position_boids - self.position
            coh = coh.normalize() * self.max_speed
            coh = coh - self.velocity
            if coh.length() > self.max_force:
                coh.scale_to_length(self.max_force)
        if sep.length() > 0:
            sep = sep.normalize() * self.max_speed
            sep = sep - self.velocity
            if sep.length() > self.max_force:
                sep.scale_to_length(self.max_force)
        if self.state == "fleeing":
            seek_food *= 0.1
            seek_water *= 0.1
        elif self.state == "resting":
            sep *= 0.5
            ali *= 0.5
            coh *= 0.5
            seek_food *= 0.2
            seek_water *= 0.2
        elif self.state == "foraging":
            if self.thirst < self.max_thirst * 0.7:
                if closest_water and closest_water.water_level > 0:
                    seek_water = self.seek(closest_water.position)
                elif self.memory["last_water"]:
                    seek_water = self.seek(self.memory["last_water"]) * 0.5
                if self.thirst < self.max_thirst * 0.3:
                    seek_food *= 0.2
            elif self.energy < self.max_energy * 0.7:
                if closest_food:
                    seek_food = self.seek(closest_food.position)
                elif self.memory["last_food"]:
                    seek_food = self.seek(self.memory["last_food"]) * 0.5
                if self.energy < self.max_energy * 0.3:
                    seek_water *= 0.2
        final_force = sep * BOID_SEPARATION_WEIGHT + \
                      ali * BOID_ALIGNMENT_WEIGHT + \
                      coh * BOID_COHESION_WEIGHT + \
                      avoid_obstacle * BOID_AVOID_OBSTACLE_WEIGHT
        effective_flee_predator = flee_predator
        if fleeing_neighbors_flee_force.length() > 0:
            effective_flee_predator += fleeing_neighbors_flee_force.normalize() * BOID_DISTRESS_AMPLIFICATION * self.max_force
        final_force += effective_flee_predator * BOID_FLEE_PREDATOR_WEIGHT
        final_force += seek_food * BOID_SEEK_FOOD_WEIGHT
        final_force += seek_water * BOID_SEEK_WATER_WEIGHT
        self.apply_force(final_force)

    def spawn_particles(self, particles, color):
        for _ in range(5):
            particles.append(Particle(self.position, color, Vector2(random.uniform(-1, 1), random.uniform(-1, 1))))

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            if self.velocity.length() > 0:
                direction_vector = self.velocity.normalize()
            else:
                direction_vector = Vector2(0, -1)
            angle = math.atan2(direction_vector.y, direction_vector.x)
            angle_degrees = math.degrees(angle) - 90
            size = self.size * camera.zoom
            points = [Vector2(0, -size * 1.5), Vector2(-size, size), Vector2(size, size)]
            rotated_points = [(pos + p.rotate(angle_degrees)) for p in points]
            pygame.draw.polygon(screen, self.color, rotated_points)
            if camera.zoom > 0.8:
                bar_width = self.size * 2.5 * camera.zoom
                bar_height = 2 * camera.zoom
                bar_y_offset = self.size + 5 * camera.zoom
                bar_x = pos.x - bar_width / 2
                energy_fill = (self.energy / self.max_energy) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 200, 0), (bar_x, pos.y - bar_y_offset, energy_fill, bar_height))
                health_fill = (self.health / self.max_health) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset + bar_height + 1, bar_width, bar_height))
                pygame.draw.rect(screen, (200, 0, 0), (bar_x, pos.y - bar_y_offset + bar_height + 1, health_fill, bar_height))
                thirst_fill = (self.thirst / self.max_thirst) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset + (bar_height + 1) * 2, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 0, 200), (bar_x, pos.y - bar_y_offset + (bar_height + 1) * 2, thirst_fill, bar_height))
                if self.is_sick:
                    pygame.draw.circle(screen, (100, 255, 100), (int(pos.x), int(pos.y)), self.size + 3 * camera.zoom, 1)
        super().draw(screen, font, camera)

class Predator(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PREDATOR_COLOR, MAX_PREDATOR_SPEED, MAX_PREDATOR_FORCE, PREDATOR_SIZE,
                         PREDATOR_START_ENERGY, PREDATOR_ENERGY_DECAY, PREDATOR_MAX_ENERGY,
                         PREDATOR_START_HEALTH, PREDATOR_HEALTH_DECAY, PREDATOR_MAX_HEALTH,
                         PREDATOR_START_THIRST, PREDATOR_THIRST_DECAY, PREDATOR_MAX_THIRST, PREDATOR_MAX_AGE,
                         PREDATOR_AGED_SPEED_PENALTY_FACTOR, PREDATOR_AGED_HEALTH_PENALTY_FACTOR)
        self.boids_eaten_for_reproduction = 0
        self.last_reproduction_time = 0
        self.state = "hunting"  # hunting, stalking, resting
        self.state_timer = random.uniform(100, 300)
        self.target_boid = None

    def update(self, all_entities_list, grid, particles):
        if not self.is_alive:
            self.spawn_particles(particles, self.color)
            return None
        new_predator = None
        self.update_state(all_entities_list, grid)
        self.hunt(all_entities_list, grid, particles)
        super().update(all_entities_list, grid, particles)
        if self.is_sick:
            self.energy -= self.energy_decay_rate * (1.0 - SICKNESS_ENERGY_GAIN_PENALTY_FACTOR) * SIM_SPEED
        if len([p for p in all_entities_list if isinstance(p, Predator) and p.is_alive]) < MAX_PREDATORS and \
           not self.is_sick and \
           self.boids_eaten_for_reproduction >= PREDATOR_BOIDS_EATEN_FOR_REPRODUCTION and \
           self.energy >= PREDATOR_START_ENERGY * 0.8 and \
           self.thirst >= PREDATOR_MAX_THIRST * 0.6 and \
           self.health >= PREDATOR_MAX_HEALTH * 0.8 and \
           (pygame.time.get_ticks() - self.last_reproduction_time) / (1000 / FPS) >= PREDATOR_REPRODUCTION_COOLDOWN * (1/SIM_SPEED):
            new_predator = Predator(self.position.x + random.uniform(-self.size*3, self.size*3), self.position.y + random.uniform(-self.size*3, self.size*3))
            self.boids_eaten_for_reproduction = 0
            self.energy -= PREDATOR_START_ENERGY * 0.5
            self.thirst -= PREDATOR_MAX_THIRST * 0.2
            self.health -= PREDATOR_MAX_HEALTH * 0.1
            self.last_reproduction_time = pygame.time.get_ticks()
        return new_predator

    def update_state(self, all_entities_list, grid):
        self.state_timer -= SIM_SPEED
        if self.state_timer <= 0:
            boids_near = get_neighbors_from_grid(self.position, PREDATOR_PERCEPTION_RADIUS, grid, Boid)
            if boids_near and self.energy < self.max_energy * 0.9:
                min_dist = float('inf')
                for boid in boids_near:
                    dist = self.position.distance_to(boid.position)
                    if dist < min_dist:
                        min_dist = dist
                        self.target_boid = boid
                if min_dist > PREDATOR_PERCEPTION_RADIUS * 0.5:
                    self.state = "stalking"
                else:
                    self.state = "hunting"
            else:
                self.state = "resting"
                self.target_boid = None
            self.state_timer = random.uniform(100, 300)

    def hunt(self, all_entities_list, grid, particles):
        seek_force = Vector2(0, 0)
        avoid_obstacle = Vector2(0, 0)
        sep_predator = Vector2(0, 0)
        ali_predator = Vector2(0, 0)
        coh_predator = Vector2(0, 0)
        seek_water = Vector2(0, 0)
        target_boid = self.target_boid
        min_boid_dist = float('inf')
        nearby_predators_count = 0
        avg_velocity_predators = Vector2(0, 0)
        avg_position_predators = Vector2(0, 0)
        neighbors = get_neighbors_from_grid(self.position, max(PREDATOR_PERCEPTION_RADIUS, SICKNESS_TRANSMISSION_RADIUS), grid)
        for entity in neighbors:
            if entity is self or not entity.is_alive:
                continue
            distance = self.position.distance_to(entity.position)
            if isinstance(entity, Boid) and distance < PREDATOR_PERCEPTION_RADIUS:
                if distance < min_boid_dist:
                    min_boid_dist = distance
                    target_boid = entity
                    if distance < PREDATOR_PERCEPTION_RADIUS * 0.6 and self.dialogue_timer <= 0:
                        self.start_dialogue(status="target")
            elif isinstance(entity, Predator) and distance < PREDATOR_PERCEPTION_RADIUS:
                nearby_predators_count += 1
                avg_velocity_predators += entity.velocity
                avg_position_predators += entity.position
                if distance < PREDATOR_SEPARATION_RADIUS:
                    diff = self.position - entity.position
                    if distance > 0:
                        diff = diff.normalize() / distance
                    sep_predator += diff
            elif isinstance(entity, WaterSource):
                if distance < entity.size and entity.water_level > 0:
                    thirst_gained = min(self.max_thirst - self.thirst, WATER_THIRST_GAIN_RATE * SIM_SPEED, entity.water_level)
                    self.thirst += thirst_gained
                    entity.water_level -= thirst_gained
                    if self.dialogue_timer <= 0:
                        self.start_dialogue(status="water")
            elif isinstance(entity, Obstacle):
                avoid_vector = self.avoid(entity.position, entity.size + self.size)
                avoid_obstacle += avoid_vector
        if target_boid and target_boid.is_alive:
            self.target_boid = target_boid
            speed_factor = 0.6 if self.state == "stalking" else 1.0
            seek_force = self.seek(target_boid.position) * speed_factor
            if min_boid_dist < self.size + target_boid.size / 2:
                target_boid.is_alive = False
                self.energy = min(self.max_energy, self.energy + PREDATOR_BOID_ENERGY)
                self.boids_eaten_for_reproduction += 1
                self.spawn_particles(particles, target_boid.color)
                self.state = "resting"
                self.state_timer = random.uniform(50, 150)
        if self.thirst < self.max_thirst * 0.5 and not (target_boid and min_boid_dist < PREDATOR_PERCEPTION_RADIUS * 0.8):
            closest_water_predator = None
            min_water_dist_predator = float('inf')
            water_sources = get_neighbors_from_grid(self.position, PREDATOR_PERCEPTION_RADIUS * 1.5, grid, WaterSource)
            for water in water_sources:
                if water.water_level > 0:
                    dist = self.position.distance_to(water.position)
                    if dist < min_water_dist_predator:
                        min_water_dist_predator = dist
                        closest_water_predator = water
            if closest_water_predator:
                seek_water = self.seek(closest_water_predator.position)
                if min_water_dist_predator < PREDATOR_PERCEPTION_RADIUS * 0.5 and self.dialogue_timer <= 0:
                    self.start_dialogue(status="water")
        if self.state == "resting":
            seek_force *= 0.2
            seek_water *= 0.5
        final_force = avoid_obstacle * PREDATOR_AVOID_OBSTACLE_WEIGHT + \
                      sep_predator * PREDATOR_SEPARATION_WEIGHT + \
                      seek_force * PREDATOR_SEEK_BOID_WEIGHT + \
                      seek_water * PREDATOR_SEEK_WATER_WEIGHT
        if nearby_predators_count > 0 and self.state == "hunting":
            avg_velocity_predators /= nearby_predators_count
            avg_position_predators /= nearby_predators_count
            ali_predator = avg_velocity_predators.normalize() * self.max_speed - self.velocity if avg_velocity_predators.length() > 0 else Vector2(0, 0)
            coh_predator = avg_position_predators - self.position
            coh_predator = coh_predator.normalize() * self.max_speed - self.velocity if coh_predator.length() > 0 else Vector2(0, 0)
            if ali_predator.length() > self.max_force:
                ali_predator.scale_to_length(self.max_force)
            if coh_predator.length() > self.max_force:
                coh_predator.scale_to_length(self.max_force)
            final_force += ali_predator * PREDATOR_FLOCKING_WEIGHT
            final_force += coh_predator * PREDATOR_FLOCKING_WEIGHT
        self.apply_force(final_force)

    def spawn_particles(self, particles, color):
        for _ in range(7):
            particles.append(Particle(self.position, color, Vector2(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))))

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            if self.velocity.length() > 0:
                direction_vector = self.velocity.normalize()
            else:
                direction_vector = Vector2(0, -1)
            angle = math.atan2(direction_vector.y, direction_vector.x)
            angle_degrees = math.degrees(angle) - 90
            size = self.size * camera.zoom
            points = [Vector2(0, -size * 1.5), Vector2(-size, size), Vector2(size, size)]
            rotated_points = [(pos + p.rotate(angle_degrees)) for p in points]
            pygame.draw.polygon(screen, self.color, rotated_points)
            if camera.zoom > 0.8:
                bar_width = self.size * 2.5 * camera.zoom
                bar_height = 2 * camera.zoom
                bar_y_offset = self.size + 5 * camera.zoom
                bar_x = pos.x - bar_width / 2
                energy_fill = (self.energy / self.max_energy) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 200, 0), (bar_x, pos.y - bar_y_offset, energy_fill, bar_height))
                health_fill = (self.health / self.max_health) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset + bar_height + 1, bar_width, bar_height))
                pygame.draw.rect(screen, (200, 0, 0), (bar_x, pos.y - bar_y_offset + bar_height + 1, health_fill, bar_height))
                thirst_fill = (self.thirst / self.max_thirst) * bar_width
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, pos.y - bar_y_offset + (bar_height + 1) * 2, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 0, 200), (bar_x, pos.y - bar_y_offset + (bar_height + 1) * 2, thirst_fill, bar_height))
                if self.is_sick:
                    pygame.draw.circle(screen, (100, 255, 100), (int(pos.x), int(pos.y)), self.size + 3 * camera.zoom, 1)
        super().draw(screen, font, camera)

class Food(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, FOOD_COLOR, 0, 0, FOOD_SIZE, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.energy_value = FOOD_ENERGY_VALUE
        self.age = 0

    def update(self, all_entities_list, grid, particles):
        if not self.is_alive:
            return
        self.age += SIM_SPEED
        if self.age >= FOOD_DECAY_START_AGE:
            self.health -= FOOD_DECAY_RATE * SIM_SPEED
            if self.health <= 0:
                self.is_alive = False

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.size * camera.zoom)

class WaterSource(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, WATER_COLOR, 0, 0, WATER_SIZE, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.water_level = WATER_START_LEVEL
        self.replenish_timer = random.uniform(0, 300)

    def update(self, all_entities_list, grid, particles):
        if not self.is_alive:
            return
        if self.water_level < WATER_MAX_LEVEL:
            self.replenish_timer += SIM_SPEED
            if self.replenish_timer >= 60:
                self.water_level = min(WATER_MAX_LEVEL, self.water_level + WATER_MAX_LEVEL * WATER_REPLENISH_RATE * self.replenish_timer/60)
                self.replenish_timer = 0

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.size * camera.zoom, 1)
            inner_size = self.size * (self.water_level / WATER_MAX_LEVEL) * camera.zoom
            if inner_size > 0:
                pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), int(inner_size))

class Obstacle(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, OBSTACLE_COLOR, 0, 0, OBSTACLE_SIZE, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

    def update(self, all_entities_list, grid, particles):
        if not self.is_alive:
            return

    def draw(self, screen, font, camera):
        if not self.is_alive:
            return
        pos = camera.apply(self.position)
        if 0 <= pos.x <= WIDTH and 0 <= pos.y <= HEIGHT:
            pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.size * camera.zoom)

event_timer = random.randint(int(EVENT_INTERVAL_MIN), int(EVENT_INTERVAL_MAX))
current_event = None
event_duration = 0
event_timer_countdown = 0
story_index = 0
story_message = STORY_EVENTS[0][1]
story_timer = 300

def trigger_random_event(entities_dict, food_items, predators, obstacles, water_sources):
    global current_event, event_duration, event_timer_countdown, event_timer
    available_events = EVENT_TYPES[:]
    if not entities_dict["boids"] and "sickness_outbreak" in available_events:
        available_events.remove("sickness_outbreak")
    if not entities_dict["boids"] and "predator_influx" in available_events:
        available_events.remove("predator_influx")
    if not food_items and "food_bloom" in available_events:
        available_events.remove("food_bloom")
    if not obstacles and "obstacle_spawn" in available_events:
        available_events.remove("obstacle_spawn")
    if current_event == "calm" and "calm" in available_events and len(available_events) > 1:
        available_events.remove("calm")
    if not available_events:
        return
    current_event = random.choice(available_events)
    print(f"\n--- Event Triggered: {current_event.replace('_', ' ').title()} ---")
    event_duration = random.randint(300, 800) * (1/SIM_SPEED)
    event_timer_countdown = event_duration
    if current_event == "sickness_outbreak":
        all_living_entities = [e for e in entities_dict["boids"] + entities_dict["predators"] if e.is_alive]
        num_to_infect = max(1, int(len(all_living_entities) * 0.08))
        for _ in range(num_to_infect):
            if all_living_entities:
                entity_to_infect = random.choice(all_living_entities)
                entity_to_infect.contract_sickness()
                all_living_entities.remove(entity_to_infect)
        for entity in random.sample(all_living_entities, min(5, len(all_living_entities))):
            if entity.dialogue_timer <= 0:
                entity.start_dialogue(status="story")
    elif current_event == "obstacle_spawn":
        for _ in range(random.randint(2, 5)):
            obstacles.append(Obstacle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
    elif current_event == "food_bloom":
        for entity in random.sample(entities_dict["boids"], min(5, len(entities_dict["boids"]))):
            if entity.dialogue_timer <= 0:
                entity.start_dialogue(status="story")
    elif current_event == "predator_influx":
        for entity in random.sample(entities_dict["predators"], min(5, len(entities_dict["predators"]))):
            if entity.dialogue_timer <= 0:
                entity.start_dialogue(status="story")

def handle_active_event(entities_dict, food_items, predators, obstacles, water_sources):
    global event_timer_countdown, current_event, event_timer
    if current_event is None:
        return (255, 255, 255)
    event_color = (255, 255, 255)
    if current_event == "food_bloom":
        if len(food_items) < FOOD_MAX_COUNT * 1.5 and random.random() < 0.03 * SIM_SPEED:
            food_items.append(Food(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
    elif current_event == "predator_influx":
        if len(predators) < MAX_PREDATORS and random.random() < 0.004 * SIM_SPEED:
            predators.append(Predator(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
    elif current_event == "heatwave":
        event_color = (255, 200, 200)
        for entity in entities_dict["boids"] + entities_dict["predators"]:
            if entity.is_alive:
                entity.thirst -= entity.thirst_decay_rate * 0.8 * SIM_SPEED
                if random.random() < DIALOGUE_CHANCE_EVENT * SIM_SPEED and entity.dialogue_timer <= 0:
                    entity.start_dialogue(status="story")
    elif current_event == "acid_rain":
        event_color = (200, 255, 200)
        for entity in entities_dict["boids"] + entities_dict["predators"]:
            if entity.is_alive:
                entity.health -= entity.max_health * 0.0015 * SIM_SPEED
                if random.random() < DIALOGUE_CHANCE_EVENT * SIM_SPEED and entity.dialogue_timer <= 0:
                    entity.start_dialogue(status="story")
    elif current_event == "storm":
        event_color = (200, 200, 255)
        for entity in entities_dict["boids"] + entities_dict["predators"]:
            if entity.is_alive:
                entity.apply_force(Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)))
                if random.random() < DIALOGUE_CHANCE_EVENT * SIM_SPEED and entity.dialogue_timer <= 0:
                    entity.start_dialogue(status="story")
    elif current_event == "obstacle_spawn":
        if random.random() < 0.0008 * SIM_SPEED and len(obstacles) < NUM_OBSTACLES + 15:
            obstacles.append(Obstacle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
    event_timer_countdown -= SIM_SPEED
    if event_timer_countdown <= 0:
        print(f"--- Event {current_event.replace('_', ' ').title()} Ended ---")
        current_event = None
        event_timer = random.randint(int(EVENT_INTERVAL_MIN), int(EVENT_INTERVAL_MAX))
    return event_color

class SimulationStats:
    def __init__(self):
        self.boid_births = 0
        self.predator_births = 0
        self.boid_deaths_energy = 0
        self.boid_deaths_health = 0
        self.boid_deaths_thirst = 0
        self.boid_deaths_age = 0
        self.boid_deaths_predator = 0
        self.predator_deaths_energy = 0
        self.predator_deaths_health = 0
        self.predator_deaths_thirst = 0
        self.predator_deaths_age = 0
        self._boid_age_sum = 0
        self._predator_age_sum = 0
        self._boid_count_history = []
        self._predator_count_history = []

    def update(self, boids, predators):
        if boids:
            self._boid_age_sum = sum(b.age for b in boids)
            self._boid_count_history.append(len(boids))
        else:
            self._boid_age_sum = 0
            self._boid_count_history.append(0)
        if predators:
            self._predator_age_sum = sum(p.age for p in predators)
            self._predator_count_history.append(len(predators))
        else:
            self._predator_age_sum = 0
            self._predator_count_history.append(0)

    def get_average_age(self, entity_type):
        if entity_type == 'boid' and self._boid_count_history and self._boid_age_sum > 0:
            return self._boid_age_sum / self._boid_count_history[-1] if self._boid_count_history[-1] > 0 else 0
        elif entity_type == 'predator' and self._predator_count_history and self._predator_age_sum > 0:
            return self._predator_age_sum / self._predator_count_history[-1] if self._predator_count_history[-1] > 0 else 0
        return 0

async def run_simulation():
    global event_timer, current_event, event_duration, event_timer_countdown, frame_count, story_index, story_message, story_timer
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ecosystem Reborn: A Struggle for Survival")
    try:
        font = pygame.font.SysFont("Arial", 14)
        story_font = pygame.font.SysFont("Arial", 20)
    except pygame.error:
        font = pygame.font.Font(None, 14)
        story_font = pygame.font.Font(None, 20)
    clock = pygame.time.Clock()
    frame_count = 0
    boids = [Boid(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUM_BOIDS)]
    predators = [Predator(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUM_PREDATORS)]
    food_items = [Food(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUM_FOOD)]
    water_sources = [WaterSource(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUM_WATER_SOURCES)]
    obstacles = [Obstacle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUM_OBSTACLES)]
    particles = []
    food_spawn_timer = FOOD_SPAWN_INTERVAL
    stats = SimulationStats()
    camera = Camera()
    running = True
    paused = False
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    camera.position = Vector2(WIDTH / 2, HEIGHT / 2)
                    camera.zoom = 1.0
        if paused:
            await asyncio.sleep(1.0 / FPS)
            continue
        camera.update(events)
        grid = {}
        all_entities_list = boids + predators + food_items + water_sources + obstacles
        for entity in all_entities_list:
            if entity.is_alive or isinstance(entity, (Food, WaterSource, Obstacle)):
                cell = get_grid_cell(entity.position)
                if cell not in grid:
                    grid[cell] = []
                grid[cell].append(entity)
        new_boids = []
        new_predators = []
        dead_entities = []
        for boid in boids:
            result = boid.update(all_entities_list, grid, particles)
            if result is None:
                dead_entities.append(boid)
            elif isinstance(result, Boid):
                new_boids.append(result)
        for predator in predators:
            result = predator.update(all_entities_list, grid, particles)
            if result is None:
                dead_entities.append(predator)
            elif isinstance(result, Predator):
                new_predators.append(result)
        for item in food_items + water_sources + obstacles:
            result = item.update(all_entities_list, grid, particles)
            if result is None and item.is_alive is False:
                dead_entities.append(item)
        stats.boid_births += len(new_boids)
        boids.extend(new_boids)
        stats.predator_births += len(new_predators)
        predators.extend(new_predators)
        for entity in dead_entities:
            if isinstance(entity, Boid):
                if entity.energy <= 0 and entity.age < entity.max_age * 0.9:
                    stats.boid_deaths_energy += 1
                elif entity.health <= 0 and entity.age < entity.max_age * 0.9:
                    stats.boid_deaths_health += 1
                elif entity.thirst <= 0 and entity.age < entity.max_age * 0.9:
                    stats.boid_deaths_thirst += 1
                elif entity.age >= entity.max_age * 0.9:
                    stats.boid_deaths_age += 1
                else:
                    stats.boid_deaths_predator += 1
            elif isinstance(entity, Predator):
                if entity.energy <= 0 and entity.age < entity.max_age * 0.9:
                    stats.predator_deaths_energy += 1
                elif entity.health <= 0 and entity.age < entity.max_age * 0.9:
                    stats.predator_deaths_health += 1
                elif entity.thirst <= 0 and entity.age < entity.max_age * 0.9:
                    stats.predator_deaths_thirst += 1
                elif entity.age >= entity.max_age * 0.9:
                    stats.predator_deaths_age += 1
        boids = [boid for boid in boids if boid.is_alive]
        predators = [predator for predator in predators if predator.is_alive]
        food_items = [food for food in food_items if food.is_alive]
        for particle in particles:
            particle.update()
        particles = [particle for particle in particles if particle.is_alive]
        stats.update(boids, predators)
        food_spawn_timer -= SIM_SPEED
        if food_spawn_timer <= 0 and len(food_items) < FOOD_MAX_COUNT:
            food_items.append(Food(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))
            food_spawn_timer = FOOD_SPAWN_INTERVAL
        if current_event is None:
            event_timer -= SIM_SPEED
            if event_timer <= 0:
                trigger_random_event({"boids": boids, "predators": predators}, food_items, predators, obstacles, water_sources)
        event_color = handle_active_event({"boids": boids, "predators": predators}, food_items, predators, obstacles, water_sources)
        story_timer -= SIM_SPEED
        if story_index < len(STORY_EVENTS) - 1 and frame_count >= STORY_EVENTS[story_index + 1][0]:
            story_index += 1
            story_message = STORY_EVENTS[story_index][1]
            story_timer = 300
            for entity in random.sample(boids + predators, min(5, len(boids + predators))):
                if entity.dialogue_timer <= 0:
                    entity.start_dialogue(status="story")
        screen.fill(tuple(c * (event_color[c] / 255) for c in range(3)))
        for obstacle in obstacles:
            obstacle.draw(screen, font, camera)
        for water in water_sources:
            water.draw(screen, font, camera)
        for food in food_items:
            food.draw(screen, font, camera)
        for predator in predators:
            predator.draw(screen, font, camera)
        for boid in boids:
            boid.draw(screen, font, camera)
        for particle in particles:
            particle.draw(screen, camera)
        stats_lines = [
            f"Frame: {int(frame_count)} FPS: {int(clock.get_fps())}",
            f"Boids: {len(boids)} (Born: {stats.boid_births} | Dead: {stats.boid_deaths_energy+stats.boid_deaths_health+stats.boid_deaths_thirst+stats.boid_deaths_age+stats.boid_deaths_predator}) AvgAge: {stats.get_average_age('boid'):.1f}",
            f"Predators: {len(predators)} (Born: {stats.predator_births} | Dead: {stats.predator_deaths_energy+stats.predator_deaths_health+stats.predator_deaths_thirst+stats.predator_deaths_age}) AvgAge: {stats.get_average_age('predator'):.1f}",
            f"Food: {len(food_items)} | Water: {len(water_sources)} | Obstacles: {len(obstacles)}",
            f"Particles: {len(particles)}",
            "Controls: Drag to pan, Scroll to zoom, Space to pause, R to reset camera"
        ]
        for i, line in enumerate(stats_lines):
            stats_surface = font.render(line, True, (180, 180, 180))
            screen.blit(stats_surface, (10, 10 + i * 20))
        if current_event:
            event_text = f"Event: {current_event.replace('_', ' ').title()} ({int(event_timer_countdown / (1/SIM_SPEED))}s left)"
            event_surface = font.render(event_text, True, (255, 220, 0))
            screen.blit(event_surface, (WIDTH - event_surface.get_width() - 10, 10))
        if story_timer > 0:
            story_surface = story_font.render(story_message, True, (255, 255, 200))
            story_rect = story_surface.get_rect(center=(WIDTH / 2, HEIGHT - 50))
            screen.blit(story_surface, story_rect)
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += SIM_SPEED
        await asyncio.sleep(1.0 / FPS)
    pygame.quit()

async def main():
    await run_simulation()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
