1. System Overview

SmartBudget is a personal budgeting application that separates data logic from user interface logic. The system loads and saves budget data to a JSON file, manages categories and expenses, and displays two live-updating pie charts in a Tkinter GUI.

The BudgetManager class handles all data operations such as adding expenses, tracking totals, enforcing category uniqueness, and managing per-category budget limits.

The GUI (implemented using Tkinter) provides interactive components including dropdown menus, input fields, category management windows, and dynamically updating matplotlib charts.

This architecture keeps business logic clean and testable while allowing the user interface to remain flexible.

2. Class Structure
BudgetManager (Singleton)

The BudgetManager class acts as the central source of truth for the entire system.

Responsibilities

Loading and saving data to budget_data.json

Storing category limits and expense history

Ensuring categories are unique

Providing computed totals for charts and summaries

Serving all components through a single shared instance

Key Methods

add_category(name, limit)

update_limit(name, new_limit)

add_expense(category, amount)

get_totals()

save()

GUI Components
MainApp

Main window of the application

Contains expense input fields, category dropdown menu, and chart area

Updates charts and summaries whenever the data changes

CategoryManagerWindow

Separate window for creating new categories or editing limits

Prevents category duplication

Updates the main interface instantly after changes

ChartRenderer

Draws pie charts using matplotlib

Consumes summary data from BudgetManager

Redraws charts each time the dataset updates

3. Design Patterns Used
Singleton Pattern

The BudgetManager uses the Singleton design pattern to ensure that:

Only one instance manages the application’s budget data

All GUI components share the same state

Data remains consistent across windows and updates

This pattern simplifies synchronization while avoiding global variables.

5. Iterative Development Reflections

The project evolved through multiple development iterations:

Early Prototype

A simple text-based system was implemented first to validate:

Category structure

Storage logic

Total calculations

Transition to GUI

Introducing the Tkinter interface required:

Decoupling logic from presentation

Designing event-driven update flows

Handling user-triggered actions cleanly

Persistence and Data Loading

JSON storage was added and refined to:

Auto-create missing files

Validate structure

Immediately save on every modification

Visual Feedback

Pie charts required a restructuring of update logic so that:

Every data change triggers a redraw

Both charts remain consistent with each other

Improved Category Management

Originally, category limits were fixed at creation.
Iterations added the ability to:

Modify limits

Update totals instantly

Maintain clean category structure

Lessons Learned

Separating logic from UI leads to cleaner, more maintainable code.

GUIs require strong central state management.

Visual components reveal weaknesses in architecture early.

Future Improvements

Monthly or time-based budget tracking

Line graphs for spending over time

Income tracking and surplus calculations

CSV export

Searchable expense history
