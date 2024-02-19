def preprocess_datasets(dataset_file):
    # Load your dataset
    df = pd.read_csv(f'{dataset_file}_shuffled.csv')
    # Apply the feature calculation across all rows
    df[['payload_len', 'alpha', 'non_alpha', 'attack_feature']] = df.apply(calculate_features, axis=1)
    # Split and save preprocessed datasets
    train_df, test_df = train_test_split(df, test_size=test_percentage)
    train_df.to_csv(f'{dataset_file}_train.csv', index=False)
    test_df.to_csv(f'{dataset_file}_test.csv', index=False)

def calculate_features(row):
    # Assuming 'payload' is the column with the data to analyze. Adjust as necessary.
    payload = str(row['payloads'])  # Adjust if your dataframe has a different column name
    alphanumeric_ratio = calculate_alphanumeric_ratio(payload)
    input_length = calculate_input_length(payload)
    special_character_ratio = calculate_special_character_ratio(payload)
    # Here, you need to define how you calculate the attack weight based on your dataset
    # For the sake of example, let's assume a simple check for common SQL injection patterns
    attack_weight = calculate_url_weight(payload, ['select', 'union', 'insert', 'delete', 'update'])
    return pd.Series([input_length, alphanumeric_ratio, special_character_ratio, attack_weight])
    
def calculate_alphanumeric_ratio(payload):
    alphanumeric_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    alphanumeric_count = sum(1 for char in payload if char in alphanumeric_characters)
    payload_length = len(payload)
    input_length = max(payload_length, 1)  # Avoid division by zero if payload_length is 0
    alphanumeric_ratio = (alphanumeric_count / input_length) * 10
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


def calculate_url_weight(url, discovered_malicious):
    # Define weights for discovered malicious
    malicious_weights = {
        "special_character": 10,
        "attack_word": 50,
        "unauthorized_resource_access": 200
    }
    # Initialize URL weight
    url_weight = 0
    # Check if any discovered malicious is present in the URL
    for malicious in discovered_malicious:
        if malicious in url:
            url_weight += malicious_weights.get(malicious, 0)

    return url_weight

def calculate_attack_weight(row):
    # Example of weights, these should be determined based on your analysis
    url_weight = row['url_weight']
    payload_weight = row['payload_weight']
    manipulation = row['manipulation']  # Number of attack words
    alphanumeric_ratio = row['alpha'] / (row['alpha'] + row['non_alpha']) if row['alpha'] + row['non_alpha'] > 0 else 0
    files_weight = row['files_weight']  # This should be calculated based on your context
    attack_weight = url_weight + payload_weight + manipulation + alphanumeric_ratio + files_weight
    return attack_weight
