import http.client
import json
import tkinter as tk
from tkinter import simpledialog, ttk, messagebox


def fetch_data(api_url):
    # Function to fetch data from the specified API URL
    try:
        # Establishing connection to the API
        conn = http.client.HTTPSConnection("apex.oracle.com")
        conn.request("GET", api_url)
        response = conn.getresponse()

        # Checking if the request was successful
        if response.status == 200:
            data = response.read()
            return json.loads(data.decode('utf-8'))
        else:
            # Displaying error message if request failed
            messagebox.showerror("Error", f"Failed to fetch data from API. Status: {response.status}")
            return None
    except http.client.HTTPException as http_err:
        # Handling HTTP exceptions
        messagebox.showerror("HTTP Error", f"HTTP Error occurred: {http_err}")
        return None
    except json.JSONDecodeError as json_err:
        # Handling JSON decoding errors
        messagebox.showerror("JSON Decode Error", f"JSON Decode Error occurred: {json_err}")
        return None
    except Exception as e:
        # Handling other exceptions
        messagebox.showerror("Error", f"An error occurred while fetching data: {e}")
        return None


def retrieve_employee_bookings(employee_id):
    # Function to retrieve and display booking data for a given employee ID
    try:
        # Constructing the API URL to retrieve bookings associated with the employee ID
        employee_booking_api = f"https://apex.oracle.com/pls/apex/ifs354_ind_assignment/test/employee_id?EMPLOYEE_ID={employee_id}"

        # Fetching booking data for the employee
        employee_booking_data = fetch_data(employee_booking_api)

        # Handling different scenarios based on the retrieved data
        if employee_booking_data is not None:
            if "items" in employee_booking_data:
                if employee_booking_data["items"]:
                    # Create a new window for displaying the booking data
                    popup = tk.Tk()
                    popup.title("Bookings")

                    # Create a Treeview widget to display the data in a table
                    tree = ttk.Treeview(popup)
                    tree["columns"] = ("Equipment ID", "Date Booked", "Date Returned")
                    tree.heading("#0", text="Booking ID")
                    tree.heading("Equipment ID", text="Equipment ID")
                    tree.heading("Date Booked", text="Date Booked")
                    tree.heading("Date Returned", text="Date Returned")

                    # Insert data into the tree
                    for booking in employee_booking_data["items"]:
                        if booking.get("employee_id") == int(employee_id):
                            booking_id = booking.get("booking_id")
                            equipment_id = booking.get("equipment_id")
                            date_booked = booking.get("date_booked")
                            date_returned = booking.get("date_returned")
                            tree.insert("", "end", text=booking_id, values=(equipment_id, date_booked, date_returned))

                    tree.pack(expand=True, fill=tk.BOTH)

                    # Run the main loop of the popup window
                    popup.mainloop()
                else:
                    messagebox.showinfo("Information", f"No bookings found for Employee ID: {employee_id}")
            else:
                messagebox.showerror("Error", "Error fetching booking data.")
        else:
            messagebox.showerror("Error", f"Failed to retrieve data for Employee ID: {employee_id}")
    except Exception as e:
        # Handling other exceptions
        messagebox.showerror("Error", f"An error occurred: {e}")


def employee_functionality():
    # Function to initiate the employee functionality by prompting for employee ID and displaying bookings
    try:
        # Fetching employee ID from user input
        employee_id = simpledialog.askstring("Employee ID", "Enter your Employee ID:")

        if employee_id:
            # Fetching and displaying bookings for the employee
            retrieve_employee_bookings(employee_id)
        else:
            messagebox.showerror("Error", "Please enter your Employee ID.")
    except Exception as e:
        # Handling other exceptions
        messagebox.showerror("Error", f"An error occurred: {e}")


# Call the function to start the employee functionality
employee_functionality()
