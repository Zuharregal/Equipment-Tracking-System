import cv2
import http.client
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import date
from pyzbar.pyzbar import decode
import json


def get_employee_id_from_qr():
    # Function to capture employee ID from QR code
    capture = cv2.VideoCapture(0)

    while True:
        ret, frame = capture.read()
        cv2.imshow("QR Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Decode QR code
        decoded_objects = decode(frame)
        if decoded_objects:
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                return data

    capture.release()
    cv2.destroyAllWindows()

    return None


def get_id_from_api(endpoint, booking_id):
    # Function to fetch data from API based on endpoint and booking ID
    try:
        conn = http.client.HTTPSConnection("apex.oracle.com")
        api_url = f"https://apex.oracle.com/pls/apex/ifs354_ind_assignment/test/{endpoint}?booking_id={booking_id}"
        print(f"Fetching {endpoint} with URL: {api_url}")  # Debugging print statement
        conn.request("GET", api_url)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        response_data = json.loads(data)
        if 'items' in response_data:
            for item in response_data['items']:
                if item['booking_id'] == booking_id:
                    return item
    except Exception as e:
        # Display error message if an exception occurs during API request
        messagebox.showerror("Error", f"An error occurred while fetching data from the API: {str(e)}")
        return None


def update_equipment_quantity(equipment_id):
    # Function to update equipment quantity in the database
    try:
        print("Updating equipment quantity for equipment ID:", equipment_id)

        # Fetch current equipment quantity
        conn = http.client.HTTPSConnection("apex.oracle.com")
        api_url = f"https://apex.oracle.com/pls/apex/ifs354_ind_assignment/test/equipment?pequipment_id={equipment_id}"
        conn.request("GET", api_url)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        equipment_data = json.loads(data)

        # Check if equipment data is retrieved successfully
        if 'items' in equipment_data:
            for item in equipment_data['items']:
                if item['equipment_id'] == equipment_id:
                    current_quantity = item['equipment_quantity']
                    break
        else:
            # Display error message if equipment data retrieval fails
            messagebox.showerror("Error", f"Failed to fetch current equipment quantity for equipment ID: {equipment_id}")
            return

        # Increment quantity by one
        updated_quantity = current_quantity + 1

        # Update equipment quantity
        api_url = "https://apex.oracle.com/pls/apex/ifs354_ind_assignment/test/equipment"
        payload = json.dumps({
            "pequipment_id": equipment_id,
            "pequipment_quantity": updated_quantity
        })
        headers = {
            'Content-Type': 'application/json'
        }
        conn.request("POST", api_url, payload, headers)

        # Get response from the update request
        res = conn.getresponse()
        if res.status == 200:
            # Display success message if equipment quantity is updated successfully
            messagebox.showinfo("Success", "Equipment quantity updated successfully!")
        else:
            # Display error message if equipment quantity update fails
            messagebox.showerror("Error", f"Failed to update equipment quantity with status code: {res.status}")
    except Exception as e:
        # Display error message if an exception occurs during equipment quantity update
        messagebox.showerror("Error", f"An error occurred while updating equipment quantity: {str(e)}")


def make_request():
    # Function to make API request based on user input
    booking_id = simpledialog.askinteger("Booking ID", "Enter Booking ID:")
    if booking_id is not None:
        employee_id = get_employee_id_from_qr()
        if employee_id is not None:
            print(f"Scanned employee ID: {employee_id}")
            employee_data = get_id_from_api("employee_id", booking_id)
            if employee_data is not None:
                employee_id_from_api = employee_data['employee_id']
                equipment_id_from_api = employee_data.get('equipment_id')
                print(f"Employee ID from API: {employee_id_from_api}")
                if int(employee_id) == int(employee_id_from_api):
                    today_date = date.today().strftime("%Y/%m/%d")
                    conn = http.client.HTTPSConnection("apex.oracle.com")
                    api_url = f"https://apex.oracle.com/pls/apex/ifs354_ind_assignment/test/checkin?pbooking_id={booking_id}&pdate_returned={today_date}"
                    conn.request("POST", api_url)
                    res = conn.getresponse()

                    if res.status == 200:
                        # Display success message if API request is successful
                        messagebox.showinfo("Success", "Check-In successful!")
                        if equipment_id_from_api is not None:
                            update_equipment_quantity(equipment_id_from_api)
                        else:
                            print(f"Failed to fetch equipment ID for booking ID: {booking_id}")
                    else:
                        # Display error message if API request fails
                        messagebox.showerror("Error", f"Request failed with status code: {res.status}")
                else:
                    # Display error message if employee ID does not match
                    messagebox.showerror("Error", "Invalid employee ID: Scanned employee ID does not match the employee ID from the API.")
            else:
                # Display error message if no employee data is found
                messagebox.showerror("Error", f"No employee data found for booking ID {booking_id}.")
        else:
            # Display error message if QR code scanning fails
            messagebox.showerror("Error", "Failed to scan QR code.")
    else:
        # Display error message if no booking ID is provided
        messagebox.showerror("Error", "No booking ID provided.")


# Create Tkinter window
root = tk.Tk()
root.title("Check-In Application")

# Create button to trigger API request
btn_checkin = tk.Button(root, text="Check-In", command=make_request)
btn_checkin.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
