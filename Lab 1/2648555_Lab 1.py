class Node:
    def __init__(self,data):
        self.data = data
        self.next = None
class BrowserHistoryStack:
    def __init__(self):
        self.top = None
    def push(self,page):
        new_page = Node(page)
        new_page.next = self.top
        self.top = new_page
        pass
    def pop(self):
        if(self.top==None):
            print("Underflow")
            return
        temp = self.top.data
        self.top = self.top.next
        return temp
    def peek(self):
        if(self.top==None):
            print("Empty")
        else:
            return(self.top.data)
    def display(self):
        if(self.top == None):
            print("Empty")
        else:
            temp = self.top
            while(temp!=None):
                print(temp.data)
                temp = temp.next   
history = BrowserHistoryStack()
while True:
    print("\n1. Visit a Page (Push)")
    print("2. Go Back (Pop)")
    print("3. Current Page (Peek)")
    print("4. Display History")
    print("5. Exit")
    choice = input("Enter Choice: ")
    if choice == '1':
        page = input("Enter the page name: ")
        history.push(page)
    elif choice == '2':
        print(history.pop())
    elif choice == '3':
        print(history.peek())
    elif choice == '4':
        history.display()
    elif choice == '5':
        break
    else:
        print("Invalid Choice")
    