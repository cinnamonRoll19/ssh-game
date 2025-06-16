import pygame
import sys
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
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
LIGHT_RED = (255, 182, 193)

class Quiz:
    def __init__(self, screen, font_small, font_medium, font_large):
        self.screen = screen
        self.font_small = font_small
        self.font_medium = font_medium
        self.font_large = font_large
        self.current_question = 0
        self.score = 0
        self.selected_answer = None
        self.answer_submitted = False
        self.quiz_completed = False
        
        # Quiz questions
        self.questions = [
            {
                "question": "Что такое SSH?",
                "options": [
                    "Протокол для безопасного удаленного доступа к серверам",
                    "Тип шифрования данных на жестком диске",
                    "Программа для создания резервных копий",
                    "Метод аутентификации на веб-сайтах"
                ],
                "correct": 0
            },
            {
                "question": "Какой тип шифрования используется в SSH-ключах?",
                "options": [
                    "Симметричное шифрование",
                    "Асимметричное шифрование",
                    "Шифрование Цезаря",
                    "Блочное шифрование"
                ],
                "correct": 1
            },
            {
                "question": "Какой ключ можно безопасно передавать другим?",
                "options": [
                    "Приватный ключ",
                    "Симметричный ключ",
                    "Публичный ключ",
                    "Мастер-ключ"
                ],
                "correct": 2
            },
            {
                "question": "Какой алгоритм часто используется для создания SSH-ключей?",
                "options": [
                    "AES",
                    "RSA",
                    "MD5",
                    "HTTP"
                ],
                "correct": 1
            },
            {
                "question": "Что НЕ является преимуществом использования SSH-ключей?",
                "options": [
                    "Повышенная безопасность",
                    "Удобство использования",
                    "Возможность автоматизации",
                    "Шифрование жесткого диска"
                ],
                "correct": 3
            }
        ]
        
        # Initialize buttons
        button_width = 500
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        self.option_buttons = []
        
        for i in range(4):
            button_y = 250 + i * 70
            self.option_buttons.append(
                Button(button_x, button_y, button_width, button_height, "", GRAY, LIGHT_BLUE, i)
            )
        
        self.next_button = Button(SCREEN_WIDTH//2 - 100, 520, 200, 50, "Далее", GRAY, LIGHT_BLUE, self.next_question)
        self.finish_button = Button(SCREEN_WIDTH//2 - 100, 520, 200, 50, "Завершить", GRAY, LIGHT_BLUE, None)
        
        # Update button text for first question
        self.update_button_text()
    
    def update_button_text(self):
        if not self.quiz_completed:
            for i, button in enumerate(self.option_buttons):
                button.text = self.questions[self.current_question]["options"][i]
    
    def select_answer(self, option_index):
        if not self.answer_submitted:
            self.selected_answer = option_index
    
    def submit_answer(self):
        if self.selected_answer is not None and not self.answer_submitted:
            correct_answer = self.questions[self.current_question]["correct"]
            if self.selected_answer == correct_answer:
                self.score += 1
            self.answer_submitted = True
            
            # Если это последний вопрос, сразу завершаем тест
            if self.current_question == len(self.questions) - 1:
                self.quiz_completed = True
            
            return True
        return False
    
    def next_question(self):
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.selected_answer = None
            self.answer_submitted = False
            self.update_button_text()
        else:
            self.quiz_completed = True
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle option button clicks
        if not self.answer_submitted and not self.quiz_completed:
            for button in self.option_buttons:
                button.check_hover(mouse_pos)
                if event.type == MOUSEBUTTONDOWN and event.button == 1 and button.is_hovered:
                    self.select_answer(button.action)
                    self.submit_answer()
        
        # Handle next/finish button
        if self.answer_submitted and not self.quiz_completed:
            self.next_button.check_hover(mouse_pos)
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.next_button.is_hovered:
                self.next_question()
        
        # Handle finish button in quiz completed state
        if self.quiz_completed:
            self.finish_button.check_hover(mouse_pos)
            if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.finish_button.is_hovered:
                return "MAIN_MENU"
        
        return None
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw title
        title = self.font_large.render("Тест на знание SSH и криптографии", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        if not self.quiz_completed:
            # Draw question number
            question_num = self.font_medium.render(f"Вопрос {self.current_question + 1}/{len(self.questions)}", True, BLACK)
            question_num_rect = question_num.get_rect(center=(SCREEN_WIDTH//2, 100))
            self.screen.blit(question_num, question_num_rect)
            
            # Draw question
            question_text = self.font_medium.render(self.questions[self.current_question]["question"], True, BLACK)
            question_rect = question_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(question_text, question_rect)
            
            # Draw options
            for i, button in enumerate(self.option_buttons):
                # Change button color based on selection and submission
                if self.answer_submitted:
                    correct_answer = self.questions[self.current_question]["correct"]
                    if i == correct_answer:
                        button.color = LIGHT_GREEN
                    elif i == self.selected_answer and i != correct_answer:
                        button.color = LIGHT_RED
                    else:
                        button.color = GRAY
                else:
                    button.color = LIGHT_BLUE if self.selected_answer == i else GRAY
                
                button.draw(self.screen)
            
            # Draw next button after answer is submitted
            if self.answer_submitted:
                self.next_button.draw(self.screen)
        else:
            # Draw quiz completion message
            completion_text = self.font_large.render("Тест завершен!", True, BLACK)
            completion_rect = completion_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(completion_text, completion_rect)
            
            # Draw score
            score_text = self.font_large.render(f"Ваш результат: {self.score}/{len(self.questions)}", True, BLACK)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(score_text, score_rect)
            
            # Draw feedback based on score
            feedback = ""
            if self.score == len(self.questions):
                feedback = "Отлично! Вы превосходно разбираетесь в SSH и криптографии!"
            elif self.score >= len(self.questions) * 0.7:
                feedback = "Хороший результат! Вы хорошо понимаете основы."
            else:
                feedback = "Рекомендуем повторить материал и пройти тест снова."
            
            feedback_text = self.font_medium.render(feedback, True, BLACK)
            feedback_rect = feedback_text.get_rect(center=(SCREEN_WIDTH//2, 350))
            self.screen.blit(feedback_text, feedback_rect)
            
            # Draw finish button
            self.finish_button.draw(self.screen)

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
