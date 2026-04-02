"""
Step-by-step Python tutorial with OOP and function examples.

Run:
    python oop_tutorial.py
"""

from abc import ABC, abstractmethod
from functools import partial, reduce
from pathlib import Path


class Person:
    """Basic class used to explain class, object, constructor, and methods."""

    school_name = "Python Learning Academy"  # class variable

    def __init__(self, name, age):
        # Constructor: runs automatically when an object is created.
        self.name = name  # public instance variable
        self.age = age
        self._nickname = "No nickname yet"  # protected by convention
        self.__pin = "1234"  # private by name mangling

    def introduce(self):
        """Instance method: works with data stored in the object."""
        return f"My name is {self.name} and I am {self.age} years old."

    def set_nickname(self, nickname):
        """Encapsulation: controlled access to internal data."""
        self._nickname = nickname

    def get_nickname(self):
        return self._nickname

    def set_pin(self, new_pin):
        if len(str(new_pin)) != 4:
            raise ValueError("PIN must be exactly 4 digits.")
        self.__pin = str(new_pin)

    def show_private_pin_inside_class(self):
        return self.__pin

    @classmethod
    def change_school(cls, new_school_name):
        """Class method: works with class-level data shared by all objects."""
        cls.school_name = new_school_name

    @staticmethod
    def is_adult(age):
        """Static method: utility logic not tied to one object or the class state."""
        return age >= 18


class Student(Person):
    """Inheritance: Student gets features from Person."""

    def __init__(self, name, age, student_id, course):
        super().__init__(name, age)
        self.student_id = student_id
        self.course = course

    def introduce(self):
        """Polymorphism: same method name, different behavior."""
        return (
            f"I am student {self.name}, age {self.age}, "
            f"ID {self.student_id}, studying {self.course}."
        )

    def study(self):
        return f"{self.name} is studying {self.course}."


class Teacher(Person):
    """Another child class showing polymorphism."""

    def __init__(self, name, age, subject):
        super().__init__(name, age)
        self.subject = subject

    def introduce(self):
        return f"I am teacher {self.name} and I teach {self.subject}."


class Shape(ABC):
    """Abstraction: defines a rule that child classes must follow."""

    @abstractmethod
    def area(self):
        pass


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


def print_introduction(person_obj):
    """Works with any object that provides introduce(): polymorphism in action."""
    print(person_obj.introduce())


def add_numbers(a, b):
    """Pure function: same inputs always give same output."""
    return a + b


counter = 0


def impure_add_and_update_counter(value):
    """Impure function: depends on and changes outside state."""
    global counter
    counter += 1
    return value + counter


def apply_operation(a, b, operation):
    """Higher-order function: receives another function as an argument."""
    return operation(a, b)


def multiply(a, b):
    return a * b


def make_multiplier(factor):
    """Closure: inner function remembers the outer variable."""

    def multiplier(number):
        return number * factor

    return multiplier


def compose(f, g):
    """Function composition: combine functions into one new function."""

    def composed(x):
        return f(g(x))

    return composed


def square(number):
    return number * number


def increment(number):
    return number + 1


def execute_callback(value, callback):
    """Callback function example."""
    return callback(value)


def recursive_factorial(n):
    """Recursive function: a function calling itself."""
    if n == 0 or n == 1:
        return 1
    return n * recursive_factorial(n - 1)


def file_handling_demo():
    """Create, write, read, and append to a small file."""
    file_path = Path(__file__).with_name("learning_notes.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Python File Handling Example\n")
        file.write("Line 1: File created successfully.\n")

    with open(file_path, "a", encoding="utf-8") as file:
        file.write("Line 2: New text appended.\n")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    return file_path, content


def exception_handling_demo():
    """Show try, except, else, and finally."""
    try:
        result = 10 / 2
    except ZeroDivisionError:
        return "Cannot divide by zero."
    else:
        return f"Division worked. Result = {result}"
    finally:
        print("Exception demo finished.")


def main():
    print("\n1. CLASS AND OBJECT")
    person1 = Person("Alice", 25)
    print(f"Object created: {person1}")
    print(person1.introduce())

    print("\n2. CONSTRUCTOR")
    print("The constructor __init__ gave values to name and age automatically.")
    print(f"Name: {person1.name}")
    print(f"Age: {person1.age}")

    print("\n3. INSTANCE METHOD")
    print(person1.introduce())

    print("\n4. CLASS VARIABLE AND CLASS METHOD")
    print(f"School before change: {Person.school_name}")
    Person.change_school("Advanced Python Institute")
    print(f"School after change: {Person.school_name}")
    student1 = Student("Bob", 20, "S101", "Computer Science")
    print(f"Student also sees same school: {student1.school_name}")

    print("\n5. STATIC METHOD")
    print(f"Is 16 adult? {Person.is_adult(16)}")
    print(f"Is 22 adult? {Person.is_adult(22)}")

    print("\n6. INHERITANCE")
    print(student1.introduce())
    print(student1.study())

    print("\n7. POLYMORPHISM")
    teacher1 = Teacher("Mr. John", 40, "Mathematics")
    print_introduction(person1)
    print_introduction(student1)
    print_introduction(teacher1)

    print("\n8. ENCAPSULATION")
    person1.set_nickname("Ally")
    print(f"Nickname through getter: {person1.get_nickname()}")
    person1.set_pin("5678")
    print("Private PIN was updated safely through a setter method.")
    print(f"Private PIN accessed inside class method: {person1.show_private_pin_inside_class()}")

    print("\n9. ACCESS SPECIFIER CONVENTIONS IN PYTHON")
    print(f"Public variable: {person1.name}")
    print(f"Protected variable by convention: {person1._nickname}")
    print("Private variables use double underscore and should not be accessed directly.")

    print("\n10. ABSTRACTION")
    rectangle1 = Rectangle(5, 4)
    print(f"Rectangle area: {rectangle1.area()}")

    print("\n11. SUMMARY")
    print("Person, Student, Teacher, Shape, and Rectangle together show the main OOP ideas.")

    print("\n12. FILE HANDLING")
    file_path, content = file_handling_demo()
    print(f"File created at: {file_path}")
    print("File content:")
    print(content)

    print("\n13. EXCEPTION HANDLING")
    print(exception_handling_demo())
    try:
        value = int("hello")
        print(value)
    except ValueError as error:
        print(f"Caught ValueError: {error}")

    print("\n14. HIGHER-ORDER FUNCTION")
    result = apply_operation(4, 5, multiply)
    print(f"apply_operation(4, 5, multiply) = {result}")

    print("\n15. PURE VS IMPURE FUNCTIONS")
    print(f"Pure function add_numbers(2, 3) = {add_numbers(2, 3)}")
    print(f"Pure function add_numbers(2, 3) again = {add_numbers(2, 3)}")
    print(f"Impure function first call = {impure_add_and_update_counter(10)}")
    print(f"Impure function second call = {impure_add_and_update_counter(10)}")

    print("\n16. LAMBDA FUNCTION")
    double = lambda x: x * 2
    print(f"Lambda double(6) = {double(6)}")

    print("\n17. MAP FUNCTION")
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = list(map(lambda x: x * x, numbers))
    print(f"Original numbers: {numbers}")
    print(f"Squared with map: {squared_numbers}")

    print("\n18. FILTER FUNCTION")
    even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"Even numbers with filter: {even_numbers}")

    print("\n19. REDUCE FUNCTION")
    total = reduce(lambda x, y: x + y, numbers)
    print(f"Sum with reduce: {total}")

    print("\n20. CLOSURE FUNCTION")
    times_three = make_multiplier(3)
    print(f"Closure times_three(7) = {times_three(7)}")

    print("\n21. PARTIAL FUNCTION")
    double_with_partial = partial(multiply, 2)
    print(f"Partial function double_with_partial(9) = {double_with_partial(9)}")

    print("\n22. FUNCTION COMPOSITION")
    increment_then_square = compose(square, increment)
    print(f"compose(square, increment)(4) = {increment_then_square(4)}")

    print("\n23. CALLBACK FUNCTION")
    callback_result = execute_callback("python", lambda text: text.upper())
    print(f"Callback result = {callback_result}")

    print("\n24. RECURSIVE FUNCTION")
    print(f"Factorial of 5 = {recursive_factorial(5)}")


if __name__ == "__main__":
    main()
