todo_list = []

def menu():
    print("Welcome to To-Do List Manager\n")
    print("1. View Tasks")
    print("2. Add Task")
    print("3. Remove Task")
    print("4. Exit")
    
while True:
    
    menu()
    choice = input("Select an option: (1-4)")
    
    if choice == '1':
        print("\nYour Tasks: ")
        if not todo_list:
            print("Your list is empty")
        else:
            for index, task in enumerate(todo_list, start=1):
                print(f"{index}. {task}")
    
    elif choice == '2':
        new_task = input("Task to be added: ")
        todo_list.append(new_task)
        print("Task added!") 
        
    elif choice == '3':
        if not todo_list:
            print("Nothing to remove")
        else:
            try:
                task_num = int(input("Enter the task number to remove: "))
                removed = todo_list.pop(task_num-1)
                print(f"Removed: {removed}")
            except (ValueError, IndexError):
                print("Invalid number! Please look at the list and try again")
    
    elif choice == '4':
        print("Exiting ToDo list manager...")
        break
    
    else:
        print("Enter a valid option")