import pickle
import socket

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

def calculate_alphanumeric_ratio(payload):
    alphanumeric_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    alphanumeric_count = sum(1 for char in payload if char in alphanumeric_characters)
    payload_length = len(payload)
    input_length = max(payload_length, 1)  # Avoid division by zero if payload_length is 0
    alphanumeric_ratio = (alphanumeric_count / input_length) * 100
    print(alphanumeric_ratio)
    return alphanumeric_ratio

def calculate_input_length(payload):
    input_length = len(payload)
    return input_length

def calculate_special_character_ratio(payload):
    alphanumeric_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    special_count = sum(1 for char in payload if char not in alphanumeric_characters)
    payload_length = len(payload)
    input_length = max(payload_length, 1)  # Avoid division by zero if payload_length is 0
    special_ratio = (special_count / input_length) * 100
    return special_ratio

def parse_http_payload(payload):
    # Load the pre-trained CountVectorizer model
    count_vectorizer_model = joblib.load('CountVectorizer.sav')  # Adjust the filename as needed
    # Example text data

    # Transform the new text data using the pre-trained model
    payload_vectorized = count_vectorizer_model.transform([payload])

    return payload_vectorized


def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    server_socket.bind(('127.0.0.1', 1234))

    # Listen for incoming connections
    server_socket.listen(1)

    print("Server is listening...")

    try:
        while True:
            # Accept a new connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Receive the HTTP message
            payload = client_socket.recv(1024).decode('utf-8')
            print("Received HTTP message:")
            print(payload)

            # Parse payload using CountVectorizer
            payload_vectorized = parse_http_payload(payload)
            # print("Payload vectorized:")
            # print(payload_vectorized.toarray())

            # create a dataframe from payload_vectorized
            df = pd.DataFrame(payload_vectorized.toarray())

            # Calculate features
            input_length = calculate_input_length(payload)
            alphanumeric_ratio = calculate_alphanumeric_ratio(payload)
            special_character_ratio = calculate_special_character_ratio(payload)

            # print the features
            # print("Features:")
            # print(f"Input length: {input_length}")
            # print(f"Alphanumeric ratio: {alphanumeric_ratio}")
            # print(f"Special character ratio: {special_character_ratio}")


            # append the features to the dataframe
            # Append the features to the dataframe
            extra_features = np.array([[input_length, alphanumeric_ratio, special_character_ratio]])
            df_with_features = np.concatenate((df, extra_features), axis=1)

            # payload vector with features
            # print("Payload vector with features:")
            # print(df_with_features)
            # print(len(df_with_features[0]))

            # load the ensemble model with pickle
            with open('Ensemble_Model.sav', 'rb') as f:
                ensemble_model = pickle.load(f)

            # Use the pre-trained ensemble model to predict the payload
            prediction = ensemble_model.predict(df_with_features)

            if prediction[0] == 0:
                print("The payload is not an attack.")
                # return 0 to the client
                client_socket.send("0".encode('utf-8'))
            else:
                # return 1 to the client
                print("The payload is an attack.")
                client_socket.send("1".encode('utf-8'))

            # Close the connection
            client_socket.close()
    except KeyboardInterrupt:
        print("Server stopped.")


# Example usage:
if __name__ == "__main__":
    start_server()
