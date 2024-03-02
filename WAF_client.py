import socket
import tkinter as tk
from tkinter import messagebox


def craft_and_send_http_packet(payload, dest_ip, dest_port):
    # Create a TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # setsockopt
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    response = ""

    try:
        # Connect to the destination IP and port
        tcp_socket.connect((dest_ip, dest_port))
        # Send the packet
        tcp_socket.sendall(payload.encode('utf-8'))
        # Wait for the response
        response = tcp_socket.recv(1024).decode('utf-8')
    except Exception as e:
        response = f"Failed to send HTTP packet: {e}"
    finally:
        # Close the socket
        tcp_socket.close()
    return response


def send_request():
    payload = request_entry.get()
    if not payload:
        messagebox.showerror("Error", "Please enter a request.")
        return
    response = craft_and_send_http_packet(payload, dest_ip, dest_port)
    if response == "0":
        response = "Benign"
    else:
        response = "Malicious- INTRUDER!!!!!!"
    response_label.config(text=f"Prediction: {response}")


# UI setup
root = tk.Tk()
root.title("URL Classification Model")

request_entry = tk.Entry(root, width=50)
request_entry.pack()

send_button = tk.Button(root, text="Make Classification", command=send_request)
send_button.pack()

response_label = tk.Label(root, text="Prediction:")
response_label.pack()

# Example server details
dest_ip = "127.0.0.1"
dest_port = 1234

root.mainloop()
