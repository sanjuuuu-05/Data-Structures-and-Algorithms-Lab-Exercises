class PatientNode:
    def __init__(self,token,name,age,department):
        self.token = token
        self.name = name
        self.age = age
        self.department = department
        self.next = None
class PatientQueue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.count = 0
        self.next_token = 101
    def is_empty(self):
        return self.front is None
    pass

    def enqueue(self,name,age,department):
        if age <= 0 or name is None or name.strip() == "": 
            print("Error")
            return
        new_patient = PatientNode(self.next_token, name, age, department)
        issued_token = self.next_token
        self.next_token+=1
        if self.is_empty():
            self.front=new_patient
            self.rear=new_patient
        else:
            self.rear.next = new_patient
            self.rear = new_patient
        self.count+=1
        print(f"Token {issued_token} issue")
    
    def dequeue(self):
        if self.is_empty():
            print("No patients waiting")
            return
        called_patient = self.front
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self.count -= 1
        print(f"Token {called_patient.token} - {called_patient.name} to {called_patient.department}")
    
    def peek(self):
        if self.is_empty():
            print("No patient")
        else:
            print(f"Token {self.front.token} - {self.front.name}")
    
    def display(self):
        if self.is_empty():
            print("No patient")
            return
        curr = self.front
        while curr is not None:
            print(f"Token {curr.token} - {curr.name} ({curr.department})")
            curr = curr.next
patient_queue = PatientQueue()

while True:
    print("\n1. Register Patient (Enqueue)")
    print("2. Call Next Patient (Dequeue)")
    print("3. Peek Next Patient")
    print("4. Display Waiting List")
    print("5. Show Count")
    print("6. Exit")
    
    choice = input("Enter choice: ")
    
    if choice == "1":
        name = input("Patient name: ")
        age = input("Age: ")
        department = input("Department: ")
        patient_queue.enqueue(name, int(age), department)
    elif choice == "2":
        patient_queue.dequeue()
    elif choice == "3":
        patient_queue.peek()
    elif choice == "4":
        patient_queue.display()
    elif choice == "5":
        print("Patients waiting:", patient_queue.count)
    elif choice == "6":
        print("Exiting...")
        break
    else:
        print("Invalid choice")