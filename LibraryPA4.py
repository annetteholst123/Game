# Import the random package (needed to randomize the id of members)
import random
import datetime
    
class Book:
    all_books = []
    def __init__(self, Title=None, author=None):
        # User enters book title
        if Title is None:
            title = input("Enter the title of the book:")
        if author is None:
            author = input("Enter author of the book:")
        self.title = title
        self.author = author

    def Add_Book(self):
        # User enters amount of copies
        copies = int(input("Enter amount copies of the book:"))
        # Add book to the list of all books as many times as there are copies
        for copy in range(0, copies):
            Book.all_books.append([self.title, self.author])
        thanks = print("You've succesfully added the book to the library.")
        return thanks

    # View total of books
    # Source: https://stackoverflow.com/questions/46694430/extract-unique-list-from-nested-list-in-python 
    def Total_Books():
        # Return the amount of books in the library
        amount = len(Book.all_books)
        amount_books = print(f"There are {amount} books available.")
        unique_books = [list(y) for y in set([tuple(x) for x in Book.all_books])] 
        print_unique_books = print(f"The following books are in storage ('book title', 'author'): {unique_books}")
        return amount_books, print_unique_books
        
    def Number_Copies(self):
        # Since several books might have the same name, a specific book is identified by both booktitle and author
        # Go through all books and count the number of copies of the book that the user filled in
        counter = 0
        for book, author in Book.all_books:
            if book == self.title and author == self.author:
                counter += 1
        if counter == 0:
            number_copies = print(f"Sadly, {self.title} by {self.author} is not in this library.")
        else:
            number_copies = print(f"This book has {counter} amount of copies in store.")
        return number_copies

    def Search_Book(self):
        print("\nSearch Options:")
        print("1. Search by title")
        print("2. Search by author")
        print("3. Search by both title and author")
        choice = input("Choose an option (1-3): ")
    
        title = None
        author = None

        if choice == '1':
            title = input("Enter the book title to search: ").strip()
        elif choice == '2':
            author = input("Enter the author name to search: ").strip()
        elif choice == '3':
            title = input("Enter the book title to search: ").strip()
            author = input("Enter the author name to search: ").strip()
        else:
            print("Invalid choice. Returning to menu.")
            return

        matches = []
        for book in Book.all_books:
            match = True
            if title and book[0].lower() != title.lower():
                match = False
            if author and book[1].lower() != author.lower():
                match = False
            if match:
                matches.append(tuple(book))

        if matches:
            from collections import Counter
            count_books = Counter(matches)
            print("\nSearch Results:")
            for (title, author), count in count_books.items():
                print(f"'{title}' by {author} - {count} copy/copies")
        else:
            print("No matching books found.")
    

class Member:
    # List of members
    all_members = []
    
    def __init__(self):
        first_name = input("what is the first name?")
        self.first_name = first_name
        last_name = input("What is the last name?")
        self.last_name = last_name
        date_of_birth = input("What is the date of birth? (dd-mm-yyyy)")
        self.date_of_birth = date_of_birth
        # Set (string) of numbers that contains numbers allowed in id
        set_numbers = "0123456789"
        # Create an id that is randomized and exists out of 8 numbers
        id = ""
        for i in range(1,8):
         id += random.choice(set_numbers)
        self.id = id

    # Adding a member
    # Source: https://stackoverflow.com/questions/46694430/extract-unique-list-from-nested-list-in-python 
    def Add_Member(self):
        Member.all_members.append([self.first_name, self.last_name, self.date_of_birth, self.id])
        # Members are unique, thus can't appear twice (the chance of a person having the same first and last name and date of birth is almost impossible, thus unique identifier
        # Makes sure that members do not appear twice 
        Member.all_members = [list(y) for y in set([tuple(x) for x in Member.all_members])]
        print("Member succesfully added.")

    # Printing all existing members (last name, first name)
    def View_Members():
        try:
            i = 1
            for first_name, last_name, date_of_birth, id in Member.all_members:
                members = print(f"{i}. {last_name}, {first_name} ({id})")
                i += 1
            print("These are the existing members:")
            return members
        except UnboundLocalError:
            print("There are no members registered in the system yet.")
            
class Loan:
    all_loans = []
    loan_period_days = 14
    fine_per_day =  0.75
    borrowing_history = {}
    
    def __init__(self, member_id=None, book_title=None, book_author=None):
        self.member_id = member_id
        self.book_title = book_title
        self.book_author = book_author
        self.loan_date = datetime.date.today() if member_id else None
        self.return_date = None
        self.fine_paid = True

    def borrow_book(self):
        for loan in Loan.all_loans:
            if loan.member_id == self.member_id and loan.fine_paid is False:
                print(f"Borrowing blocked. Member {self.member_id} has unpaid fines.")
                Loan.view_fines(self.member_id)
                return

        if [self.book_title, self.book_author] in Book.all_books:
            Book.all_books.remove([self.book_title, self.book_author])
            Loan.all_loans.append(self)
            print(f"Book '{self.book_title}' successfully borrowed by member {self.member_id}.")
            Loan.log_action("borrow", self.member_id, self.book_title, self.book_author, "Book borrowed.")
        else:
            print(f"Sorry, '{self.book_title}' by {self.book_author} is not currently available.")
            
    def recommend_books(self, member_id):
        if member_id not in Loan.borrowing_history:
            print("No borrowing history found for this member.")
            return
        
        borrowed_books = Loan.borrowing_history[member_id]
        recommended = set()

        #Search all members that borrowed the same books
        for other_member, books in Loan.borrowing_history.items():
            if other_member == member_id:
                continue
            if any(book in books for book in borrowed_books):
                for book in books:
                    if book not in borrowed_books:
                        recommended.add(book)
        #book recommendation based on borrowing history 
        if recommended:
            print("\nRecommended books based on your borrowing history:")
            for title, author in recommended:
                print(f"- {title} by {author}")
        else:
            print("\nNo recommendations found based on your borrowing history.")
            
    # Loan history for recommendations: 
        if self.member_id in Loan.borrowing_history:
            Loan.borrowing_history[self.member_id].append((self.book_title, self.book_author))
        else:
            Loan.borrowing_history[self.member_id] = [(self.book_title, self.book_author)]

    def return_book(self):
        for loan in Loan.all_loans:
            if (loan.member_id == self.member_id and
                loan.book_title == self.book_title and
                loan.book_author == self.book_author and
                loan.return_date is None):
                loan.return_date = datetime.date.today()
                Book.all_books.append([self.book_title, self.book_author])
                print(f"Book '{self.book_title}' successfully returned by member {self.member_id}.")
                due_date = loan.loan_date + datetime.timedelta(days=Loan.loan_period_days)
                if loan.return_date > due_date:
                    late_days = (loan.return_date - due_date).days
                    fine = late_days * Loan.fine_per_day
                    loan.fine_paid = False
                    print(f"Returned too late, {late_days} days overdue.")
                    print(f"Fine: €{fine:.2f}")
                    Loan.log_action("return", self.member_id, self.book_title, self.book_author,
                                f"Returned late. Fine: €{fine:.2f}")
                else:
                    print("Returned on time. No fine.")
                    Loan.log_action("return", self.member_id, self.book_title, self.book_author,
                                "Returned on time.")
                return
        print("No matching active loan found.")

    def view_loans(self):
        if not Loan.all_loans:
            print("No loan records found.")
            return
        for loan in Loan.all_loans:
            status = "Returned" if loan.return_date else "Borrowed"
            print(f"{loan.member_id} - '{loan.book_title}' by {loan.book_author} | "
                  f"Loan Date: {loan.loan_date} | "
                  f"Return Date: {loan.return_date or 'Not Returned'} | Status: {status}")
            
    def view_fines(member_id):
        total_fine = 0.0
        print(f"\n Fine Summary for Member ID: {member_id}")
        for loan in Loan.all_loans:
            if loan.member_id == member_id and loan.return_date:
                due_date = loan.loan_date + datetime.timedelta(days=Loan.loan_period_days)
                if loan.return_date > due_date:
                    late_days = (loan.return_date - due_date).days
                    fine = late_days * Loan.fine_per_day
                    total_fine += fine
                    print(f"'{loan.book_title}' by {loan.book_author} — {late_days} days late. Fine: €{fine:.2f}")
        if total_fine > 0:
            print(f"\n Total Fine Due: €{total_fine:.2f}")
        else:
            print(" No outstanding fines.")
        
    def log_action(action_type, member_id, book_title, book_author, message):
        with open("log.txt", "a") as logfile:
            now = datetime.datetime.now().strftime("%Y-%m-%d")
            log_entry = f"[{now}] {action_type.upper()} | Member: {member_id} | Book: '{book_title}' by {book_author} | {message}\n"
            logfile.write(log_entry)