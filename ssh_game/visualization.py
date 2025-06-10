import pygame
import math
import random
from pygame.locals import *

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class Particle:
    def __init__(self, x, y, color, size=3, speed=2):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = speed
        self.target_x = x
        self.target_y = y
        self.angle = 0
        self.distance = 0
        self.is_moving = False
        self.reached_target = True
    
    def set_target(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        self.angle = math.atan2(dy, dx)
        self.distance = math.sqrt(dx**2 + dy**2)
        self.is_moving = True
        self.reached_target = False
    
    def update(self):
        if self.is_moving and not self.reached_target:
            # Move towards target
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
            
            # Check if reached target (within threshold)
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            remaining_distance = math.sqrt(dx**2 + dy**2)
            
            if remaining_distance < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.reached_target = True
                self.is_moving = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class EncryptionVisualizer:
    def __init__(self, screen, font_small, font_medium, font_large):
        self.screen = screen
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        self.current_stage = 0
        self.max_stages = 3
        self.particles = []
        self.timer = 0
        self.animation_done = False
        self.show_explanation = True
        
        # Define the positions
        self.sender_pos = (150, 300)
        self.receiver_pos = (650, 300)
        self.key_pos = (400, 200)
        self.encryption_box_pos = (400, 300)
        
        # Create message particles
        self.message_particles = []
        self.generate_message_particles()
        
        # Create encryption box particles
        self.encryption_box_points = []
        self.generate_encryption_box()
        
        # Create key particles
        self.key_particles = []
        self.generate_key_particles()
        
        # Encrypted message particles
        self.encrypted_particles = []
        
        # Define explanations for each stage
        self.explanations = [
            ["Отправитель хочет отправить конфиденциальное сообщение получателю.",
             "Для этого необходим безопасный способ шифрования."],
            ["Используется пара ключей: публичный (для шифрования)",
             "и приватный (для дешифрования)."],
            ["Сообщение шифруется публичным ключом и может быть",
             "расшифровано только соответствующим приватным ключом."],
            ["Преимущества: даже если сообщение перехвачено,",
             "его невозможно прочитать без приватного ключа."]
        ]
    
    def generate_message_particles(self):
        # Create particles representing the original message
        message_width = 80
        message_height = 40
        num_particles = 30
        
        for _ in range(num_particles):
            x = self.sender_pos[0] - message_width/2 + random.uniform(0, message_width)
            y = self.sender_pos[1] - message_height/2 + random.uniform(0, message_height)
            particle = Particle(x, y, GREEN, random.randint(2, 4), random.uniform(1, 3))
            self.message_particles.append(particle)
    
    def generate_encryption_box(self):
        # Create points for the encryption box
        box_width = 100
        box_height = 60
        center_x = self.encryption_box_pos[0]
        center_y = self.encryption_box_pos[1]
        
        top_left = (center_x - box_width/2, center_y - box_height/2)
        top_right = (center_x + box_width/2, center_y - box_height/2)
        bottom_right = (center_x + box_width/2, center_y + box_height/2)
        bottom_left = (center_x - box_width/2, center_y + box_height/2)
        
        self.encryption_box_points = [top_left, top_right, bottom_right, bottom_left]
    
    def generate_key_particles(self):
        # Create particles representing the key
        key_width = 60
        key_height = 30
        num_particles = 15
        
        for _ in range(num_particles):
            x = self.key_pos[0] - key_width/2 + random.uniform(0, key_width)
            y = self.key_pos[1] - key_height/2 + random.uniform(0, key_height)
            particle = Particle(x, y, YELLOW, random.randint(2, 4), random.uniform(1, 3))
            self.key_particles.append(particle)
    
    def next_stage(self):
        if self.current_stage < self.max_stages:
            self.current_stage += 1
            self.animation_done = False
            self.timer = 0
            
            if self.current_stage == 1:
                # Move message to encryption box
                for particle in self.message_particles:
                    target_x = self.encryption_box_pos[0] - 20 + random.uniform(0, 40)
                    target_y = self.encryption_box_pos[1] - 15 + random.uniform(0, 30)
                    particle.set_target(target_x, target_y)
                
                # Move key to encryption box
                for particle in self.key_particles:
                    target_x = self.encryption_box_pos[0] - 15 + random.uniform(0, 30)
                    target_y = self.encryption_box_pos[1] - 10 + random.uniform(0, 20)
                    particle.set_target(target_x, target_y)
            
            elif self.current_stage == 2:
                # Create encrypted particles
                for _ in range(len(self.message_particles)):
                    x = self.encryption_box_pos[0] - 20 + random.uniform(0, 40)
                    y = self.encryption_box_pos[1] - 15 + random.uniform(0, 30)
                    particle = Particle(x, y, PURPLE, random.randint(2, 4), random.uniform(1, 3))
                    target_x = self.receiver_pos[0] - 40 + random.uniform(0, 80)
                    target_y = self.receiver_pos[1] - 20 + random.uniform(0, 40)
                    particle.set_target(target_x, target_y)
                    self.encrypted_particles.append(particle)
            
            elif self.current_stage == 3:
                # Final stage - just show explanation
                pass
    
    def update(self):
        self.timer += 1
        
        # Update all particles
        for particle in self.message_particles:
            particle.update()
        
        for particle in self.key_particles:
            particle.update()
        
        for particle in self.encrypted_particles:
            particle.update()
        
        # Check if current stage animation is done
        if self.current_stage == 0:
            # Initial stage - just showing the setup
            if self.timer > 100:
                self.animation_done = True
        
        elif self.current_stage == 1:
            # Check if all particles reached target
            all_reached = True
            for particle in self.message_particles + self.key_particles:
                if not particle.reached_target:
                    all_reached = False
                    break
            
            if all_reached and self.timer > 100:
                self.animation_done = True
        
        elif self.current_stage == 2:
            # Check if all encrypted particles reached target
            all_reached = True
            for particle in self.encrypted_particles:
                if not particle.reached_target:
                    all_reached = False
                    break
            
            if all_reached and self.timer > 100:
                self.animation_done = True
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.animation_done:
                if self.current_stage < self.max_stages:
                    self.next_stage()
                else:
                    # На финальной стадии возвращаем COMPLETE при клике
                    # Это позволит main.py определить, что визуализация завершена
                    return "COMPLETE"
        
        return None
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.font_large.render("Визуализация асимметричного шифрования", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw sender and receiver
        pygame.draw.circle(self.screen, BLUE, self.sender_pos, 30)
        sender_label = self.font_small.render("Отправитель", True, BLACK)
        sender_rect = sender_label.get_rect(center=(self.sender_pos[0], self.sender_pos[1] + 50))
        self.screen.blit(sender_label, sender_rect)
        
        pygame.draw.circle(self.screen, RED, self.receiver_pos, 30)
        receiver_label = self.font_small.render("Получатель", True, BLACK)
        receiver_rect = receiver_label.get_rect(center=(self.receiver_pos[0], self.receiver_pos[1] + 50))
        self.screen.blit(receiver_label, receiver_rect)
        
        # Draw encryption box
        pygame.draw.polygon(self.screen, GRAY, self.encryption_box_points)
        pygame.draw.polygon(self.screen, BLACK, self.encryption_box_points, 2)
        
        # Draw key label
        key_label = self.font_small.render("Публичный ключ", True, BLACK)
        key_rect = key_label.get_rect(center=(self.key_pos[0], self.key_pos[1] - 25))
        self.screen.blit(key_label, key_rect)
        
        # Draw encryption box label
        box_label = self.font_small.render("Шифрование", True, BLACK)
        box_rect = box_label.get_rect(center=(self.encryption_box_pos[0], self.encryption_box_pos[1] + 45))
        self.screen.blit(box_label, box_rect)
        
        # Draw particles
        for particle in self.message_particles:
            particle.draw(self.screen)
        
        for particle in self.key_particles:
            particle.draw(self.screen)
        
        for particle in self.encrypted_particles:
            particle.draw(self.screen)
        
        # Draw explanation
        if self.show_explanation:
            explanation_box = pygame.Rect(150, 400, 500, 150)
            pygame.draw.rect(self.screen, LIGHT_BLUE, explanation_box, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, explanation_box, 2, border_radius=10)
            
            # Draw stage number
            stage_text = self.font_medium.render(f"Этап {self.current_stage + 1}/{self.max_stages + 1}", True, BLACK)
            stage_rect = stage_text.get_rect(midtop=(SCREEN_WIDTH//2, 410))
            self.screen.blit(stage_text, stage_rect)
            
            # Draw explanation text
            y_offset = 450
            for line in self.explanations[self.current_stage]:
                text = self.font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 30
            
            # Draw "click to continue" if animation is done
            if self.animation_done:
                continue_text = self.font_small.render("Нажмите, чтобы продолжить", True, BLACK)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, 520))
                self.screen.blit(continue_text, continue_rect) 