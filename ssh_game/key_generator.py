import pygame
import sys
from pygame.locals import *
import rsa
import binascii
import random
import time

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
PURPLE = (128, 0, 128)

class KeyGenStage:
    INTRO = 0
    KEY_SIZE = 1
    GENERATING = 2
    GENERATION_STEPS = 3
    DISPLAY_KEYS = 4
    ENCRYPT_DECRYPT = 5
    COMPLETE = 6

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
        self.scroll_offset = 0  # Для прокрутки
        
        # Generation steps
        self.current_step = 0
        self.generation_steps = [
            {
                "title": "1. Выбор простых чисел",
                "description": "Выбираем два больших простых числа p и q",
                "progress": 0,
                "details": ""
            },
            {
                "title": "2. Вычисление модуля n",
                "description": "Вычисляем n = p × q (модуль для ключей)",
                "progress": 0,
                "details": ""
            },
            {
                "title": "3. Вычисление функции Эйлера",
                "description": "φ(n) = (p-1) × (q-1)",
                "progress": 0,
                "details": ""
            },
            {
                "title": "4. Выбор открытой экспоненты e",
                "description": "Выбираем e, взаимно простое с φ(n)",
                "progress": 0,
                "details": ""
            },
            {
                "title": "5. Вычисление секретной экспоненты d",
                "description": "Находим d, такое что e × d ≡ 1 mod φ(n)",
                "progress": 0,
                "details": ""
            },
            {
                "title": "6. Формирование ключей",
                "description": "Публичный ключ: (e, n)\nПриватный ключ: (d, n)",
                "progress": 0,
                "details": ""
            }
        ]
        
        # Create buttons
        button_width = 200
        button_height = 40
        self.buttons = {
            KeyGenStage.INTRO: [
                Button(300, 400, button_width, button_height, "Начать", GRAY, LIGHT_BLUE, self.start_key_size_selection)
            ],
            KeyGenStage.KEY_SIZE: [
                Button(200, 300, button_width, button_height, "1024 бит", GRAY, LIGHT_BLUE, lambda: self.set_key_size(1024)),
                Button(400, 300, button_width, button_height, "2048 бит", GRAY, LIGHT_BLUE, lambda: self.set_key_size(2048)),
                Button(300, 400, button_width, button_height, "Сгенерировать", GRAY, LIGHT_BLUE, self.generate_keys)
            ],
            KeyGenStage.GENERATING: [
                Button(300, 500, button_width, button_height, "Начать генерацию", GRAY, LIGHT_BLUE, 
                      lambda: setattr(self, 'stage', KeyGenStage.GENERATION_STEPS))
            ],
            KeyGenStage.GENERATION_STEPS: [
                Button(300, 500, button_width, button_height, "Продолжить", GRAY, LIGHT_BLUE, self.show_keys)
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
                "с использованием асимметричной криптографии RSA."
            ],
            KeyGenStage.KEY_SIZE: [
                "Выберите размер ключа:",
                "1024 бит - быстрее, но менее безопасный",
                "2048 бит - стандартный выбор, хороший баланс скорости и безопасности"
            ],
            KeyGenStage.GENERATING: [
                "Подготовка к генерации ключевой пары RSA...",
                "Процесс может занять некоторое время для больших ключей."
            ],
            KeyGenStage.DISPLAY_KEYS: [
                "Ваша ключевая пара RSA сгенерирована!",
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
                "создания и использования RSA-ключей.",
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
        self.current_step = 0
        self.scroll_offset = 0
        # Reset all steps
        for step in self.generation_steps:
            step["progress"] = 0
            step["details"] = ""
    
    def simulate_generation_step(self):
        if self.current_step < len(self.generation_steps):
            current = self.generation_steps[self.current_step]
            
            if current["progress"] < 100:
                current["progress"] += random.randint(5, 15)
                if current["progress"] > 100:
                    current["progress"] = 100
                
                # Add some details for each step when progress reaches certain points
                if current["title"] == "1. Выбор простых чисел" and current["progress"] == 50:
                    current["details"] = "Ищем подходящие простые числа..."
                elif current["title"] == "1. Выбор простых чисел" and current["progress"] == 100:
                    current["details"] = f"Найдены простые числа p и q длиной ~{self.key_size//2} бит"
                
                elif current["title"] == "2. Вычисление модуля n" and current["progress"] == 50:
                    current["details"] = "Умножаем p и q..."
                elif current["title"] == "2. Вычисление модуля n" and current["progress"] == 100:
                    current["details"] = "Модуль n вычислен"
                
                elif current["title"] == "3. Вычисление функции Эйлера" and current["progress"] == 100:
                    current["details"] = "φ(n) = (p-1)(q-1) вычислена"
                
                elif current["title"] == "4. Выбор открытой экспоненты e" and current["progress"] == 50:
                    current["details"] = "Проверяем взаимную простоту с φ(n)..."
                elif current["title"] == "4. Выбор открытой экспоненты e" and current["progress"] == 100:
                    current["details"] = "Обычно выбирают e=65537 (0x10001)"
                
                elif current["title"] == "5. Вычисление секретной экспоненты d" and current["progress"] == 50:
                    current["details"] = "Ищем обратный элемент с помощью алгоритма Евклида..."
                elif current["title"] == "5. Вычисление секретной экспоненты d" and current["progress"] == 100:
                    current["details"] = "Секретная экспонента d найдена"
                
                elif current["title"] == "6. Формирование ключей" and current["progress"] == 100:
                    current["details"] = "Ключи сформированы и готовы к использованию"
                
                return False
            else:
                self.current_step += 1
                return False
        else:
            # All steps completed, generate actual keys
            if not self.generation_complete:
                (self.public_key, self.private_key) = rsa.newkeys(self.key_size)
                self.generation_complete = True
                pygame.time.set_timer(pygame.USEREVENT, 1000)  # 1 second delay
            return True
    
    def show_keys(self):
        self.stage = KeyGenStage.DISPLAY_KEYS
    
    def handle_event(self, event):
        if event.type == USEREVENT:
            # Timer event for key generation completion
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
            self.stage = KeyGenStage.GENERATION_STEPS
        
        # Handle mouse wheel for scrolling
        if event.type == pygame.MOUSEWHEEL and self.stage == KeyGenStage.GENERATION_STEPS:
            self.scroll_offset -= event.y * 20  # Negative for natural scrolling
            # Calculate max scroll offset
            content_height = len(self.generation_steps) * 150 + 100
            visible_height = SCREEN_HEIGHT - 180
            max_offset = max(0, content_height - visible_height)
            self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
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
            try:
                # RSA encryption requires message to be encoded to bytes
                message_bytes = self.message.encode('utf-8')
                
                # Encrypt with public key
                self.encrypted = rsa.encrypt(message_bytes, self.public_key)
                
                # Decrypt with private key
                decrypted_bytes = rsa.decrypt(self.encrypted, self.private_key)
                self.decrypted = decrypted_bytes.decode('utf-8')
                
                self.stage = KeyGenStage.ENCRYPT_DECRYPT
            except Exception as e:
                print(f"Encryption error: {e}")
                # Fallback message if encryption fails
                self.encrypted = b"Error: Message too long for key size"
                self.decrypted = "Error: Could not decrypt"
                self.stage = KeyGenStage.ENCRYPT_DECRYPT
    
    def complete(self):
        self.stage = KeyGenStage.COMPLETE
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.font_large.render("Генератор RSA-ключей с объяснением", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 40))
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
            y_offset = 100
            
            # Title
            text = self.font_medium.render("Подготовка к генерации RSA ключей", True, PURPLE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50
            
            # Explanation
            explanation = [
                "RSA - это алгоритм асимметричного шифрования, основанный на",
                "вычислительной сложности факторизации больших чисел.",
                "Процесс генерации ключей включает несколько этапов:"
            ]
            
            for line in explanation:
                text = self.font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 30
            
            # List steps
            y_offset += 20
            for i, step in enumerate(self.generation_steps):
                color = LIGHT_BLUE if i == 0 else GRAY
                text = self.font_small.render(step["title"], True, color)
                text_rect = text.get_rect(midleft=(150, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 25
            
        elif self.stage == KeyGenStage.GENERATION_STEPS:
            # Simulate generation
            self.simulate_generation_step()
            
            # Create a surface for scrollable content
            content_height = len(self.generation_steps) * 150 + 100
            content_surface = pygame.Surface((SCREEN_WIDTH, content_height))
            content_surface.fill(WHITE)
            
            y_offset = 0
            
            # Title on content surface
            text = self.font_medium.render("Процесс генерации RSA ключей", True, PURPLE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset + 20))
            content_surface.blit(text, text_rect)
            y_offset += 50
            
            # Draw each step with scroll offset
            for i, step in enumerate(self.generation_steps):
                # Skip future steps
                if i > self.current_step and step["progress"] == 0:
                    continue
                
                # Step title
                color = BLUE if i == self.current_step else (GREEN if step["progress"] == 100 else BLACK)
                text = self.font_small.render(step["title"], True, color)
                text_rect = text.get_rect(midleft=(50, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 30
                
                # Step description
                text = self.font_small.render(step["description"], True, BLACK)
                text_rect = text.get_rect(midleft=(70, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 25
                
                # Step details if available
                if step["details"]:
                    text = self.font_small.render(step["details"], True, BLUE)
                    text_rect = text.get_rect(midleft=(70, y_offset + 20))
                    content_surface.blit(text, text_rect)
                    y_offset += 25
                
                # Progress bar
                if step["progress"] > 0:
                    bar_width = 600
                    bar_height = 15
                    bar_x = 70
                    
                    # Background
                    pygame.draw.rect(content_surface, GRAY, (bar_x, y_offset + 20, bar_width, bar_height))
                    # Filled
                    fill_width = int(bar_width * (step["progress"] / 100))
                    pygame.draw.rect(content_surface, GREEN, (bar_x, y_offset + 20, fill_width, bar_height))
                    # Border
                    pygame.draw.rect(content_surface, BLACK, (bar_x, y_offset + 20, bar_width, bar_height), 1)
                    # Percentage
                    text = self.font_small.render(f"{step['progress']}%", True, BLACK)
                    text_rect = text.get_rect(midleft=(bar_x + bar_width + 10, y_offset + 20 + bar_height//2))
                    content_surface.blit(text, text_rect)
                
                y_offset += 40
            
            # Add some educational explanation if all steps complete
            if self.current_step >= len(self.generation_steps):
                y_offset += 20
                text = self.font_small.render("Все этапы генерации ключей завершены!", True, GREEN)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 30
                
                text = self.font_small.render("Теперь у нас есть:", True, BLACK)
                text_rect = text.get_rect(midleft=(50, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 25
                
                text = self.font_small.render("- Публичный ключ (e, n) - можно свободно распространять", True, BLUE)
                text_rect = text.get_rect(midleft=(70, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 25
                
                text = self.font_small.render("- Приватный ключ (d, n) - должен храниться в секрете", True, RED)
                text_rect = text.get_rect(midleft=(70, y_offset + 20))
                content_surface.blit(text, text_rect)
                y_offset += 40
            
            # Draw the scrollable content with clipping
            visible_area = pygame.Rect(0, 80, SCREEN_WIDTH, SCREEN_HEIGHT - 180)
            self.screen.set_clip(visible_area)
            self.screen.blit(content_surface, (0, -self.scroll_offset + 80))
            self.screen.set_clip(None)
            
            # Draw scroll indicator if needed
            if content_height > visible_area.height:
                scroll_ratio = visible_area.height / content_height
                scroll_pos = (self.scroll_offset / content_height) * visible_area.height
                scroll_bar_height = scroll_ratio * visible_area.height
                pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 10, 80 + scroll_pos, 5, scroll_bar_height))
            
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
            private_key_str = f"n={hex(self.private_key.n)[:50]}...\nd={hex(self.private_key.d)[:50]}..."
            private_key_lines = private_key_str.split('\n')[:3]
            for line in private_key_lines:
                text = self.font_small.render(line, True, RED)
                text_rect = text.get_rect(midleft=(70, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 20
            
            y_offset += 30
            
            # Public key label
            text = self.font_small.render(self.stage_messages[self.stage][2], True, BLACK)
            text_rect = text.get_rect(midleft=(50, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
            # Public key display (first few lines)
            public_key_str = f"n={hex(self.public_key.n)[:50]}...\ne={hex(self.public_key.e)}"
            public_key_lines = public_key_str.split('\n')[:3]
            for line in public_key_lines:
                text = self.font_small.render(line, True, BLUE)
                text_rect = text.get_rect(midleft=(70, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 20
            
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
            if isinstance(self.encrypted, bytes):
                encrypted_hex = binascii.hexlify(self.encrypted).decode('utf-8')
            else:
                encrypted_hex = str(self.encrypted)
                
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
            
            # Add explanation
            y_offset += 50
            explanation = [
                "Как это работает:",
                "1. Публичный ключ (e,n) шифрует сообщение: c = m^e mod n",
                "2. Приватный ключ (d,n) расшифровывает: m = c^d mod n",
                "3. Без знания d расшифровать сообщение крайне сложно"
            ]
            
            for line in explanation:
                text = self.font_small.render(line, True, PURPLE)
                text_rect = text.get_rect(midleft=(50, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 25
            
        elif self.stage == KeyGenStage.COMPLETE:
            y_offset = 150
            for line in self.stage_messages[self.stage]:
                text = self.font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 35
        
        # Draw buttons for current stage (now drawn last)
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
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=5)
        
        font = pygame.font.SysFont('Arial', 16)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
