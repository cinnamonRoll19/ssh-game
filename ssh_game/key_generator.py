import pygame
import sys
from pygame.locals import *
import ssh_utils

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)

class KeyGenStage:
    INTRO = 0
    KEY_SIZE = 1
    GENERATING = 2
    DISPLAY_KEYS = 3
    ENCRYPT_DECRYPT = 4
    COMPLETE = 5

class KeyGenerator:
    def __init__(self, screen, font_small, font_medium, font_large):
        self.screen = screen
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        self.stage = KeyGenStage.INTRO
        self.key_size = 2048
        self.private_key = None
        self.public_key = None
        self.message = "Секретное сообщение"
        self.encrypted = None
        self.decrypted = None
        self.completion_percentage = 0
        self.generation_complete = False
        
        # Create buttons
        button_width = 200
        button_height = 50
        self.buttons = {
            KeyGenStage.INTRO: [
                Button(300, 400, button_width, button_height, "Начать", GRAY, LIGHT_BLUE, self.start_key_size_selection)
            ],
            KeyGenStage.KEY_SIZE: [
                Button(200, 300, button_width, button_height, "1024 бит", GRAY, LIGHT_BLUE, lambda: self.set_key_size(1024)),
                Button(400, 300, button_width, button_height, "2048 бит", GRAY, LIGHT_BLUE, lambda: self.set_key_size(2048)),
                Button(300, 400, button_width, button_height, "Сгенерировать", GRAY, LIGHT_BLUE, self.generate_keys)
            ],
            KeyGenStage.DISPLAY_KEYS: [
                Button(300, 500, button_width, button_height, "Продолжить", GRAY, LIGHT_BLUE, self.show_encryption)
            ],
            KeyGenStage.ENCRYPT_DECRYPT: [
                Button(300, 500, button_width, button_height, "Завершить", GRAY, LIGHT_BLUE, self.complete)
            ],
            KeyGenStage.COMPLETE: [
                Button(300, 500, button_width, button_height, "В главное меню", GRAY, LIGHT_BLUE, None)
            ]
        }
        
        # Messages for each stage
        self.stage_messages = {
            KeyGenStage.INTRO: [
                "Добро пожаловать в интерактивный генератор SSH-ключей!",
                "Здесь вы узнаете, как создаются и работают SSH-ключи",
                "с использованием асимметричной криптографии."
            ],
            KeyGenStage.KEY_SIZE: [
                "Выберите размер ключа:",
                "1024 бит - быстрее, но менее безопасный",
                "2048 бит - стандартный выбор, хороший баланс скорости и безопасности"
            ],
            KeyGenStage.GENERATING: [
                "Генерация ключевой пары...",
                "Это может занять некоторое время."
            ],
            KeyGenStage.DISPLAY_KEYS: [
                "Ваша ключевая пара SSH сгенерирована!",
                "Приватный ключ (держите в секрете):",
                "Публичный ключ (можно свободно распространять):"
            ],
            KeyGenStage.ENCRYPT_DECRYPT: [
                "Давайте проверим, как работает шифрование с нашими ключами:",
                "Сообщение для шифрования:",
                "Зашифрованное сообщение (с публичным ключом):",
                "Расшифрованное сообщение (с приватным ключом):"
            ],
            KeyGenStage.COMPLETE: [
                "Поздравляем! Вы успешно прошли интерактивную демонстрацию",
                "создания и использования SSH-ключей.",
                "Теперь вы понимаете основной принцип работы асимметричной криптографии."
            ]
        }
    
    def start_key_size_selection(self):
        self.stage = KeyGenStage.KEY_SIZE
    
    def set_key_size(self, size):
        self.key_size = size
    
    def generate_keys(self):
        self.stage = KeyGenStage.GENERATING
        self.generation_complete = False
        self.completion_percentage = 0
    
    def update_key_generation(self):
        if self.completion_percentage < 100:
            # Simulate key generation progress
            self.completion_percentage += 1
        else:
            if not self.generation_complete:
                # Generate the actual keys when progress bar is full
                self.private_key, self.public_key = ssh_utils.generate_rsa_key_pair(self.key_size)
                self.generation_complete = True
                # Move to next stage after a short delay
                pygame.time.set_timer(pygame.USEREVENT, 500)  # 500ms delay
    
    def handle_event(self, event):
        if event.type == USEREVENT:
            # Timer event for key generation completion
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
            self.stage = KeyGenStage.DISPLAY_KEYS
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle button clicks
        if self.stage in self.buttons:
            for button in self.buttons[self.stage]:
                button.check_hover(mouse_pos)
                if event.type == MOUSEBUTTONDOWN and event.button == 1 and button.is_hovered:
                    if button.action:
                        button.action()
                    elif self.stage == KeyGenStage.COMPLETE:
                        return "MAIN_MENU"  # Signal to return to main menu
    
    def show_encryption(self):
        # Encrypt and decrypt a sample message
        if self.private_key and self.public_key:
            self.encrypted = ssh_utils.encrypt_message(self.message, self.public_key)
            self.decrypted = ssh_utils.decrypt_message(self.encrypted, self.private_key)
            self.stage = KeyGenStage.ENCRYPT_DECRYPT
    
    def complete(self):
        self.stage = KeyGenStage.COMPLETE
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.font_large.render("Интерактивный генератор SSH-ключей", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw stage-specific content
        if self.stage == KeyGenStage.INTRO:
            y_offset = 150
            for line in self.stage_messages[self.stage]:
                text = self.font_medium.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40
                
        elif self.stage == KeyGenStage.KEY_SIZE:
            y_offset = 150
            for line in self.stage_messages[self.stage]:
                text = self.font_medium.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40
            
            # Highlight selected key size
            for button in self.buttons[self.stage]:
                if "1024" in button.text and self.key_size == 1024:
                    button.color = LIGHT_BLUE
                elif "2048" in button.text and self.key_size == 2048:
                    button.color = LIGHT_BLUE
                else:
                    button.color = GRAY
                
        elif self.stage == KeyGenStage.GENERATING:
            y_offset = 150
            for line in self.stage_messages[self.stage]:
                text = self.font_medium.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40
            
            # Draw progress bar
            bar_width = 500
            bar_height = 30
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = 300
            
            # Background of the bar
            pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Filled portion of the bar
            fill_width = int(bar_width * (self.completion_percentage / 100))
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Percentage text
            percentage_text = self.font_medium.render(f"{self.completion_percentage}%", True, BLACK)
            percentage_rect = percentage_text.get_rect(center=(SCREEN_WIDTH//2, bar_y + bar_height + 30))
            self.screen.blit(percentage_text, percentage_rect)
            
            # Update the key generation progress
            self.update_key_generation()
            
        elif self.stage == KeyGenStage.DISPLAY_KEYS:
            y_offset = 120
            
            # Title and instructions
            text = self.font_medium.render(self.stage_messages[self.stage][0], True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
            
            # Private key label
            text = self.font_small.render(self.stage_messages[self.stage][1], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            # Private key display (first few lines)
            private_key_lines = self.private_key.split('\n')[:3]
            for line in private_key_lines:
                if len(line) > 50:
                    line = line[:47] + "..."
                text = self.font_small.render(line, True, RED)
                text_rect = text.get_rect(midleft=(70, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 20
            
            text = self.font_small.render("...", True, RED)
            text_rect = text.get_rect(midleft=(70, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
            
            # Public key label
            text = self.font_small.render(self.stage_messages[self.stage][2], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            # Public key display (first few lines)
            public_key_lines = self.public_key.split('\n')[:3]
            for line in public_key_lines:
                if len(line) > 50:
                    line = line[:47] + "..."
                text = self.font_small.render(line, True, BLUE)
                text_rect = text.get_rect(midleft=(70, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 20
            
            text = self.font_small.render("...", True, BLUE)
            text_rect = text.get_rect(midleft=(70, y_offset))
            self.screen.blit(text, text_rect)
            
        elif self.stage == KeyGenStage.ENCRYPT_DECRYPT:
            y_offset = 120
            
            # Title
            text = self.font_medium.render(self.stage_messages[self.stage][0], True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
            
            # Original message
            text = self.font_small.render(self.stage_messages[self.stage][1], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            text = self.font_small.render(self.message, True, BLACK)
            text_rect = text.get_rect(midleft=(70, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
            
            # Encrypted message
            text = self.font_small.render(self.stage_messages[self.stage][2], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            # Display part of the encrypted message as hex
            encrypted_hex = self.encrypted.hex()
            text = self.font_small.render(encrypted_hex[:50] + "...", True, BLUE)
            text_rect = text.get_rect(midleft=(70, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
            
            # Decrypted message
            text = self.font_small.render(self.stage_messages[self.stage][3], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            text = self.font_small.render(self.decrypted, True, GREEN)
            text_rect = text.get_rect(midleft=(70, y_offset))
            self.screen.blit(text, text_rect)
            
        elif self.stage == KeyGenStage.COMPLETE:
            y_offset = 150
            # Используем шрифт меньшего размера для основного текста
            for line in self.stage_messages[self.stage]:
                text = self.font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 35  # Увеличим немного интервал для лучшей читаемости
        
        # Draw buttons for current stage
        if self.stage in self.buttons:
            for button in self.buttons[self.stage]:
                button.draw(self.screen)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont('Arial', 20)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered 