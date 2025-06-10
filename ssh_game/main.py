import pygame
import sys
import os
from pygame.locals import *
from key_generator import KeyGenerator
from quiz import Quiz
from visualization import EncryptionVisualizer

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# Game states
MAIN_MENU = 0
LESSON_1 = 1
LESSON_2 = 2
LESSON_3 = 3
INTERACTIVE_1 = 4
QUIZ = 5
VISUALIZATION = 6
GAME_OVER = 7

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SSH Keys Educational Game")
clock = pygame.time.Clock()

# Font setup - уменьшим размер шрифтов для лучшей читаемости
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 24)
font_large = pygame.font.SysFont('Arial', 32)

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
        
        # Разобьем текст на части, если он слишком длинный
        if len(self.text) > 30:
            # Находим середину текста для разбиения
            mid_point = len(self.text) // 2
            # Ищем ближайший пробел к середине
            space_pos = self.text.rfind(' ', 0, mid_point)
            if space_pos == -1:  # если пробел не найден до середины
                space_pos = self.text.find(' ', mid_point)  # ищем после середины
            
            if space_pos != -1:  # если пробел найден
                text1 = self.text[:space_pos]
                text2 = self.text[space_pos+1:]
                
                text_surface1 = font_small.render(text1, True, BLACK)
                text_surface2 = font_small.render(text2, True, BLACK)
                
                text_rect1 = text_surface1.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
                text_rect2 = text_surface2.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
                
                surface.blit(text_surface1, text_rect1)
                surface.blit(text_surface2, text_rect2)
            else:
                # Если пробел не найден, отображаем весь текст
                text_surface = font_small.render(self.text, True, BLACK)
                text_rect = text_surface.get_rect(center=self.rect.center)
                surface.blit(text_surface, text_rect)
        else:
            # Для короткого текста отображаем как обычно
            text_surface = font_medium.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action is not None:
                return self.action
        return None

class Game:
    def __init__(self):
        self.state = MAIN_MENU
        self.key_generator = KeyGenerator(screen, font_small, font_medium, font_large)
        self.quiz = Quiz(screen, font_small, font_medium, font_large)
        self.visualizer = EncryptionVisualizer(screen, font_small, font_medium, font_large)
        
        # Create buttons for main menu - увеличим размер кнопок
        button_width = 320
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        self.buttons = {
            MAIN_MENU: [
                Button(button_x, 170, button_width, button_height, "Урок 1: Основы шифрования", GRAY, LIGHT_BLUE, LESSON_1),
                Button(button_x, 230, button_width, button_height, "Урок 2: Асимметричная криптография", GRAY, LIGHT_BLUE, LESSON_2),
                Button(button_x, 290, button_width, button_height, "Урок 3: SSH-ключи", GRAY, LIGHT_BLUE, LESSON_3),
                Button(button_x, 350, button_width, button_height, "Интерактив: Создание SSH-ключа", GRAY, LIGHT_BLUE, INTERACTIVE_1),
                Button(button_x, 410, button_width, button_height, "Тест знаний", GRAY, LIGHT_BLUE, QUIZ),
                Button(button_x, 470, button_width, button_height, "Визуализация шифрования", GRAY, LIGHT_BLUE, VISUALIZATION),
                Button(button_x, 530, button_width, button_height, "Выход", GRAY, LIGHT_BLUE, GAME_OVER)
            ],
            LESSON_1: [
                Button(button_x, 500, button_width, button_height, "Назад в меню", GRAY, LIGHT_BLUE, MAIN_MENU)
            ],
            LESSON_2: [
                Button(button_x, 500, button_width, button_height, "Назад в меню", GRAY, LIGHT_BLUE, MAIN_MENU)
            ],
            LESSON_3: [
                Button(button_x, 500, button_width, button_height, "Назад в меню", GRAY, LIGHT_BLUE, MAIN_MENU)
            ],
            VISUALIZATION: [
                Button(button_x, 550, button_width, button_height, "Назад в меню", GRAY, LIGHT_BLUE, MAIN_MENU)
            ]
        }
        
        # Lesson content
        self.lesson_content = {
            LESSON_1: [
                "Основы шифрования",
                "Шифрование - это процесс преобразования информации в код,",
                "который может быть прочитан только с помощью специального ключа.",
                "Существует два основных типа шифрования:",
                "симметричное и асимметричное.",
                "",
                "Симметричное шифрование использует один и тот же ключ для",
                "шифрования и дешифрования. Это быстро, но требует безопасного",
                "способа передачи ключа между участниками.",
                "",
                "Асимметричное шифрование использует пару ключей: публичный и",
                "приватный. Данные, зашифрованные одним ключом, могут быть",
                "расшифрованы только другим ключом из этой пары."
            ],
            LESSON_2: [
                "Асимметричная криптография",
                "Асимметричная криптография использует пару ключей:",
                "публичный (открытый) и приватный (закрытый).",
                "",
                "Публичный ключ можно свободно распространять.",
                "Приватный ключ должен храниться в секрете.",
                "",
                "Основные свойства асимметричного шифрования:",
                "1. Данные, зашифрованные публичным ключом, можно расшифровать",
                "   только соответствующим приватным ключом.",
                "2. Данные, зашифрованные приватным ключом, можно расшифровать",
                "   соответствующим публичным ключом (используется для цифровой подписи).",
                "",
                "Примеры алгоритмов: RSA, DSA, ECC, Ed25519."
            ],
            LESSON_3: [
                "SSH-ключи",
                "SSH (Secure Shell) - протокол для безопасного удаленного",
                "доступа к серверам и устройствам.",
                "",
                "SSH-ключи - это пары криптографических ключей, используемые",
                "для аутентификации в SSH вместо паролей.",
                "",
                "Преимущества SSH-ключей:",
                "1. Повышенная безопасность (нет передачи пароля по сети)",
                "2. Удобство использования (не нужно вводить пароль каждый раз)",
                "3. Возможность автоматизации подключений",
                "",
                "Типичное использование: доступ к серверам, Git-репозиториям,",
                "автоматизация развертывания, безопасные туннели."
            ]
        }
    
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Обновление состояния наведения для кнопок всех состояний
            if self.state in self.buttons:
                for button in self.buttons[self.state]:
                    button.check_hover(mouse_pos)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                # Handle key generator events if in interactive mode
                if self.state == INTERACTIVE_1:
                    result = self.key_generator.handle_event(event)
                    if result == "MAIN_MENU":
                        self.state = MAIN_MENU
                
                # Handle quiz events
                elif self.state == QUIZ:
                    result = self.quiz.handle_event(event)
                    if result == "MAIN_MENU":
                        self.state = MAIN_MENU
                
                # Handle visualization events
                elif self.state == VISUALIZATION:
                    result = self.visualizer.handle_event(event)
                    if result == "COMPLETE":
                        self.state = MAIN_MENU
                    
                    # Проверка кнопки "Назад в меню" для визуализации
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        for button in self.buttons[VISUALIZATION]:
                            if button.is_hovered:
                                self.state = MAIN_MENU
                
                # Handle button clicks for other states
                elif self.state in self.buttons:
                    for button in self.buttons[self.state]:
                        action = button.handle_event(event)
                        if action is not None:
                            if action == GAME_OVER:
                                running = False
                            else:
                                self.state = action
            
            # Update visualization
            if self.state == VISUALIZATION:
                self.visualizer.update()
            
            # Draw screen based on game state
            screen.fill(WHITE)
            
            if self.state == MAIN_MENU:
                title = font_large.render("SSH Keys Educational Game", True, BLACK)
                title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
                screen.blit(title, title_rect)
                
                subtitle = font_medium.render("Изучите основы криптографии и SSH-ключей", True, BLACK)
                subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 140))
                screen.blit(subtitle, subtitle_rect)
                
            elif self.state == INTERACTIVE_1:
                # Draw the key generator interface
                self.key_generator.draw()
                
            elif self.state == QUIZ:
                # Draw the quiz interface
                self.quiz.draw()
                
            elif self.state == VISUALIZATION:
                # Draw the visualization
                self.visualizer.draw()
                
                # Отрисовка кнопки "Назад в меню" для визуализации
                for button in self.buttons[VISUALIZATION]:
                    button.draw(screen)
                
            elif self.state in [LESSON_1, LESSON_2, LESSON_3]:
                title = font_large.render(self.lesson_content[self.state][0], True, BLACK)
                title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
                screen.blit(title, title_rect)
                
                # Используем меньший размер текста с ограниченной шириной для уроков
                max_width = SCREEN_WIDTH - 200  # Оставляем поля по бокам
                y_offset = 150
                for line in self.lesson_content[self.state][1:]:
                    if line == "":
                        y_offset += 15  # Add extra space for empty lines
                        continue
                    
                    # Если строка слишком длинная, разбиваем её
                    text = font_small.render(line, True, BLACK)
                    text_rect = text.get_rect(midleft=(100, y_offset))
                    
                    # Убедимся, что текст не выходит за пределы
                    if text_rect.width > max_width:
                        # Разбиваем строку на несколько
                        words = line.split()
                        current_line = words[0]
                        
                        for word in words[1:]:
                            test_line = current_line + " " + word
                            test_width = font_small.size(test_line)[0]
                            
                            if test_width <= max_width:
                                current_line = test_line
                            else:
                                # Отрисовка текущей строки и переход к новой
                                text = font_small.render(current_line, True, BLACK)
                                text_rect = text.get_rect(midleft=(100, y_offset))
                                screen.blit(text, text_rect)
                                y_offset += 20
                                current_line = word
                        
                        # Отрисовка последней строки
                        text = font_small.render(current_line, True, BLACK)
                        text_rect = text.get_rect(midleft=(100, y_offset))
                        screen.blit(text, text_rect)
                    else:
                        screen.blit(text, text_rect)
                    
                    y_offset += 20
                
                # Отрисовка кнопки "Назад в меню" для уроков
                for button in self.buttons[self.state]:
                    button.draw(screen)
            
            # Draw buttons for main menu
            if self.state == MAIN_MENU:
                for button in self.buttons[self.state]:
                    button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 