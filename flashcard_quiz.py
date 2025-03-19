import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

from kivy.uix.widget import Widget
import random
import sqlite3

class FlashcardApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = sqlite3.connect("leaderboard.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                               (name TEXT, score INTEGER)''')
        self.create_database()
        
        self.quizzes = {}
        self.current_quiz_name = ""
        self.current_questions = []
        self.num_questions = 0
        self.current_frame = BoxLayout()

    def build(self):
        self.root = BoxLayout(orientation="vertical", padding=10)
        self.main_menu()
        return self.root
    
        btn_start_quiz = Button(text="Start Random Quiz")
        btn_start_quiz.bind(on_press=self.start_random_quiz)
        return btn_start_quiz
    
    def start_random_quiz(self, instance=None):
        print("Starting Random Quiz...")
        sample_questions = [
        ("What is the capital of France?", "Paris"),
        ("What is 5 + 7?", "12"),
        ("Which planet is known as the Red Planet?", "Mars"),
        ("Who wrote 'Hamlet'?", "Shakespeare"),
        ("What is the square root of 64?", "8")
        ]

        self.random_questions = random.sample(sample_questions, min(5, len(sample_questions)))
        print("Random questions selected:", self.random_questions)  # Debugging print
        self.user_answers = [""] * len(self.random_questions)
        self.current_question_index = 0
        self.show_random_question()

    def navigate_question(self, direction):
        self.current_question_index += direction

        if self.current_question_index >= len(self.random_questions):
            self.show_random_quiz_score()
        else:
            self.show_random_question()
    
    def show_random_quiz_score(self):
        score_layout = BoxLayout(orientation='vertical', spacing=10)

        # Calculate the score
        self.random_quiz_score = sum(1 for i in range(len(self.random_questions)) if self.user_answers[i].lower() == self.random_questions[i][1].lower())

        # Display score
        score_label = Label(text=f"Your Score: {self.random_quiz_score}/{len(self.random_questions)}", font_size=24)
        score_layout.add_widget(score_label)

        # Name input section
        name_label = Label(text="Enter your name for the leaderboard:", font_size=14)
        score_layout.add_widget(name_label)

        name_input = TextInput(font_size=14, size_hint=(1, None), height=30)
        score_layout.add_widget(name_input)

        # Submit button functionality
        def submit_score(instance):
            user_name = name_input.text.strip()
            if user_name:
                self.save_random_quiz_score(user_name)
            else:
                # Show error popup
                error_popup = Popup(title="Error", content=Label(text="Please enter a name."), size_hint=(0.5, 0.5))
                error_popup.open()

        submit_button = Button(text="Submit", on_press=submit_score, size_hint=(1, None), height=40)
        score_layout.add_widget(submit_button)

        self.root.clear_widgets()  # Clear any existing widgets
        self.root.add_widget(score_layout)

    def save_random_quiz_score(self, name):
        """Save the random quiz score to the leaderboard."""
        try:
            self.cursor.execute("INSERT INTO leaderboard (name, score) VALUES (?, ?)", (name, self.random_quiz_score))
            self.conn.commit()
            print("Score saved successfully.")
            self.show_leaderboard()
        except Exception as e:
            print(f"Error saving score: {e}")

    def show_leaderboard(self):
        """Display the leaderboard."""
        self.cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10")
        leaderboard = self.cursor.fetchall()
        print("Leaderboard:")
        for entry in leaderboard:
            print(f"{entry[0]}: {entry[1]}")

    def show_random_question(self):
     self.clear_root()
    
     question, _ = self.random_questions[self.current_question_index]

     quiz_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

     quiz_layout.add_widget(Label(text=f"Question {self.current_question_index + 1}/5", font_size=24))
     quiz_layout.add_widget(Label(text=question, font_size=18))
    
     self.answer_entry = TextInput(font_size=16, text=self.user_answers[self.current_question_index])
     quiz_layout.add_widget(self.answer_entry)
    
     button_layout = BoxLayout(orientation="horizontal", spacing=10)
    
     btn_back = Button(text="Back", size_hint=(0.5, 0.2))
     btn_back.bind(on_press=lambda instance: self.random_quiz_menu())
     button_layout.add_widget(btn_back)
    
     btn_next = Button(text="Next", size_hint=(0.5, 0.2))
     btn_next.bind(on_press=lambda instance: self.save_answer_and_next())
     button_layout.add_widget(btn_next)
    
     quiz_layout.add_widget(button_layout)
    
     self.root.add_widget(quiz_layout)

    def save_answer_and_next(self):
     self.user_answers[self.current_question_index] = self.answer_entry.text.strip()
     self.navigate_question(1)

    def create_database(self):
        # Create quizzes table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS quizzes (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                quiz_name TEXT)''')

        # Create quiz_questions table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_questions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                quiz_id INTEGER,
                                question TEXT,
                                answer TEXT,
                                FOREIGN KEY (quiz_id) REFERENCES quizzes (id))''')

        self.conn.commit()

    def main_menu(self, instance=None):
        self.clear_root()
        menu_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Flashcard Quiz (Alpha)", font_size=24, size_hint=(1, 0.1))
        menu_layout.add_widget(label)

        btn_random_quiz = Button(text="Random Quiz", size_hint=(1, 0.1))
        btn_random_quiz.bind(on_press=self.random_quiz_menu)
        menu_layout.add_widget(btn_random_quiz)

        btn_self_quiz = Button(text="Self Quiz", size_hint=(1, 0.1))
        btn_self_quiz.bind(on_press=self.self_quiz_menu)
        menu_layout.add_widget(btn_self_quiz)

        btn_about = Button(text="About", size_hint=(1, 0.1))
        btn_about.bind(on_press=self.show_about)
        menu_layout.add_widget(btn_about)

        btn_report_bug = Button(text="Report Bug", size_hint=(1, 0.1))
        btn_report_bug.bind(on_press=self.report_bug)
        menu_layout.add_widget(btn_report_bug)

        btn_exit = Button(text="Exit", size_hint=(1, 0.1), background_color=(1, 0, 0, 1))
        btn_exit.bind(on_press=self.stop)
        menu_layout.add_widget(btn_exit)

        self.root.add_widget(menu_layout)

    def random_quiz_menu(self, instance=None):
        self.clear_root()
        quiz_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Random Quiz", font_size=24, size_hint=(1, 0.1))
        quiz_layout.add_widget(label)

        description = Label(text="This is a random quiz with 5 easy-to-medium questions.", font_size=14, size_hint=(1, 0.1))
        quiz_layout.add_widget(description)

        btn_start_quiz = Button(text="Start Quiz", size_hint=(1, 0.1))
        btn_start_quiz.bind(on_press=self.start_random_quiz)
        quiz_layout.add_widget(btn_start_quiz)

        btn_leaderboard = Button(text="Leaderboard", size_hint=(1, 0.1))
        btn_leaderboard.bind(on_press=self.show_leaderboard)
        quiz_layout.add_widget(btn_leaderboard)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.main_menu)
        quiz_layout.add_widget(btn_back)

        self.root.add_widget(quiz_layout)

    def self_quiz_menu(self, instance=None):
        self.clear_root()
        quiz_menu_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Self Quiz Menu", font_size=24, size_hint=(1, 0.1))
        quiz_menu_layout.add_widget(label)

        btn_create_quiz = Button(text="Create Quiz", size_hint=(1, 0.1))
        btn_create_quiz.bind(on_press=self.create_quiz_name)
        quiz_menu_layout.add_widget(btn_create_quiz)

        btn_load_quiz = Button(text="Load Quiz", size_hint=(1, 0.1))
        btn_load_quiz.bind(on_press=self.load_quiz)
        quiz_menu_layout.add_widget(btn_load_quiz)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.main_menu)
        quiz_menu_layout.add_widget(btn_back)

        self.root.add_widget(quiz_menu_layout)

    def load_quiz(self, instance=None):
        self.clear_root()
        quiz_list_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Select a Quiz to Load", font_size=24, size_hint=(1, 0.1))
        quiz_list_layout.add_widget(label)

        self.cursor.execute("SELECT id, quiz_name FROM quizzes")
        quizzes = self.cursor.fetchall()

        if quizzes:
         for quiz in quizzes:
            quiz_id, quiz_name = quiz
            btn_quiz = Button(text=quiz_name, size_hint=(1, 0.1))
            btn_quiz.bind(on_press=lambda instance, q_id=quiz_id: self.display_quiz(q_id))
            quiz_list_layout.add_widget(btn_quiz)
        else:
             quiz_list_layout.add_widget(Label(text="No quizzes available.", font_size=14))

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.self_quiz_menu)
        quiz_list_layout.add_widget(btn_back)

        self.root.add_widget(quiz_list_layout)

    def display_quiz(self, quiz_id):
        self.clear_root()
        quiz_display_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.cursor.execute("SELECT question, answer FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = self.cursor.fetchall()

        if questions:
            for i, (question, answer) in enumerate(questions):
                quiz_display_layout.add_widget(Label(text=f"{i+1}. {question}", font_size=14))
                quiz_display_layout.add_widget(Label(text=f"Answer: {answer}", font_size=12, color=(0, 1, 0, 1)))

        else:
            quiz_display_layout.add_widget(Label(text="No questions found in this quiz.", font_size=14))

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.load_quiz)
        quiz_display_layout.add_widget(btn_back)

        self.root.add_widget(quiz_display_layout)

    def create_quiz_name(self, instance=None):
        self.clear_root()
        quiz_name_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Enter Quiz Name", font_size=24, size_hint=(1, 0.1))
        quiz_name_layout.add_widget(label)

        self.quiz_name_input = TextInput(font_size=14, size_hint=(1, 0.1))
        quiz_name_layout.add_widget(self.quiz_name_input)

        btn_save_quiz = Button(text="Save Quiz Name", size_hint=(1, 0.1))
        btn_save_quiz.bind(on_press=self.save_quiz_name)
        quiz_name_layout.add_widget(btn_save_quiz)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.self_quiz_menu)
        quiz_name_layout.add_widget(btn_back)

        self.root.add_widget(quiz_name_layout)

    def save_quiz_name(self, instance=None):
        quiz_name = self.quiz_name_input.text.strip()
        if quiz_name:
            self.current_quiz_name = quiz_name
            self.current_questions = []
            self.ask_number_of_questions()
        else:
            self.show_popup("Error", "Please enter a quiz name.")

    def ask_number_of_questions(self):
        self.clear_root()
        number_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Enter Number of Questions", font_size=24, size_hint=(1, 0.1))
        number_layout.add_widget(label)

        self.num_questions_input = TextInput(font_size=14, size_hint=(1, 0.1))
        number_layout.add_widget(self.num_questions_input)

        btn_save_number = Button(text="Save Number", size_hint=(1, 0.1))
        btn_save_number.bind(on_press=self.save_number_of_questions)
        number_layout.add_widget(btn_save_number)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.self_quiz_menu)
        number_layout.add_widget(btn_back)

        self.root.add_widget(number_layout)

    def save_number_of_questions(self, instance):
        try:
            num_questions = int(self.num_questions_input.text.strip())
            if num_questions > 0:
                self.num_questions = num_questions
                self.create_quiz_questions(0)
            else:
                self.show_popup("Error", "Please enter a valid number of questions.")
        except ValueError:
            self.show_popup("Error", "Please enter a valid number.")

    def create_quiz_questions(self, question_count):
        if question_count < self.num_questions:
            self.clear_root()
            question_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

            label = Label(text=f"Question {question_count + 1}", font_size=24, size_hint=(1, 0.1))
            question_layout.add_widget(label)

            self.question_input = TextInput(font_size=14, size_hint=(1, 0.1))
            question_layout.add_widget(self.question_input)

            self.answer_input = TextInput(font_size=14, size_hint=(1, 0.1))
            question_layout.add_widget(self.answer_input)

            btn_save_question = Button(text="Save Question", size_hint=(1, 0.1))
            btn_save_question.bind(on_press=self.save_question)
            question_layout.add_widget(btn_save_question)

            btn_back = Button(text="Back", size_hint=(1, 0.1))
            btn_back.bind(on_press=self.self_quiz_menu)
            question_layout.add_widget(btn_back)

            self.root.add_widget(question_layout)

        else:
            self.show_popup("Success", "Quiz Created Successfully!")
            self.main_menu()

    def save_question(self, instance):
        question_text = self.question_input.text.strip()
        answer_text = self.answer_input.text.strip()
        if question_text and answer_text:
            self.current_questions.append((question_text, answer_text))
            if len(self.current_questions) < self.num_questions:
                self.create_quiz_questions(len(self.current_questions))
            else:
                self.save_quiz()
        else:
            self.show_popup("Error", "Both question and answer must be provided.")

    def save_quiz(self):
        if self.current_quiz_name and self.current_questions:
            try:
                self.cursor.execute("INSERT INTO quizzes (quiz_name) VALUES (?)", (self.current_quiz_name,))
                self.conn.commit()

                self.cursor.execute("SELECT last_insert_rowid()")
                quiz_id = self.cursor.fetchone()[0]

                for question, answer in self.current_questions:
                    self.cursor.execute("INSERT INTO quiz_questions (quiz_id, question, answer) VALUES (?, ?, ?)", 
                                        (quiz_id, question, answer))
                self.conn.commit()

                self.show_popup("Success", "Quiz saved successfully!")
                self.main_menu()

            except Exception as e:
                self.show_popup("Error", f"An error occurred while saving the quiz: {e}")
        else:
            self.show_popup("Error", "Quiz name or questions are missing.")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_about(self, instance):
        self.clear_root()
        about_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="About", font_size=24, size_hint=(1, 0.1))
        about_layout.add_widget(label)

        about_text = Label(
            text="Flashcard Quiz App\n\nThis is a demo flashcard quiz application where you can create quizzes, "
                 "test your knowledge, and review your performance.",
            font_size=14, size_hint=(1, 0.1), halign="center", valign="middle"
        )
        about_layout.add_widget(about_text)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.main_menu)
        about_layout.add_widget(btn_back)

        self.root.add_widget(about_layout)

    def report_bug(self, instance):
        self.clear_root()
        report_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Report Bug", font_size=24, size_hint=(1, 0.1))
        report_layout.add_widget(label)

        report_text = Label(
            text="If you encounter any bugs, please report them to the developer:\n\ndiego.gounden@gmail.com",
            font_size=14, size_hint=(1, 0.1), halign="center", valign="middle"
        )
        report_layout.add_widget(report_text)

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.main_menu)
        report_layout.add_widget(btn_back)

        self.root.add_widget(report_layout)

    def show_leaderboard(self, instance=None):
        self.clear_root()
        leaderboard_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        label = Label(text="Leaderboard", font_size=24, size_hint=(1, 0.1))
        leaderboard_layout.add_widget(label)

        self.cursor.execute("SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10")
        rows = self.cursor.fetchall()

        if not rows:
            leaderboard_layout.add_widget(Label(text="No leaderboard data available.", font_size=14))

        else:
            for row in rows:
                name, score = row
                leaderboard_layout.add_widget(Label(text=f"{name}: {score}", font_size=14))

        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.main_menu)
        leaderboard_layout.add_widget(btn_back)

        self.root.add_widget(leaderboard_layout)

    def clear_root(self):
        self.root.clear_widgets()

if __name__ == "__main__":
    FlashcardApp().run()
