# Software-Engineering-Budget-Project
Jaxen Politowicz Software Engineering Project

This Budget project is a simple desktop application that helps users track expenses, set category-based budget limits, and visualize spending with automatically updating pie charts. It uses a JSON file for persistent storage and a Tkinter interface for ease of use.
--------------------------------------------------------------------------------------------------------------------------------------------------
Features:

-Add expenses with category selection via dropdown menu

-Create new custom categories anytime

-Set and edit per-category budget limits

-Two live-updating pie charts:

  -Spending Distribution
  
  -Budget Allocation
  
-Persistent data stored in budget_data.json

-Automatically updates visualizations when expenses or categories change

-------------------------------------------------------------------------------------------------------------------------------------------------
Requirements:

-Python 3.10+

-Installed libraries:

  -tkinter (usually included with Python)
  
  -matplotlib
  
  -json (built-in)
  

To run:

-simply run main.py with the above libraries installed

-the .json file will automacially be created if one does not already exist

------------------------------------------------------------------------------------------------------------------------------------------------
Usage Example:

-Add an Expense

-Select a category from the dropdown

-Enter a description

-Enter an amount

-Click Add Expense

→ The category totals update instantly

→ Pie charts redraw immediately


Add a New Category

-Click Category Manager

-Enter name & budget limit

-Click Add Category

→ Category appears in dropdown

→ Budget limit visible in budget distribution chart


Modify a Category Limit

-Open Category Manager

-Select an existing category

-Enter new limit

-Click Update Limit

