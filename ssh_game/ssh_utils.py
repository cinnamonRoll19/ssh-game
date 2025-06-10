from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os

def generate_rsa_key_pair(key_size=2048):
    """
    Generate an RSA key pair with the specified key size.
    
    Args:
        key_size (int): Size of the key in bits. Default is 2048.
        
    Returns:
        tuple: (private_key, public_key) as PEM-encoded strings
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

def save_key_pair(private_key, public_key, private_path, public_path):
    """
    Save the key pair to files.
    
    Args:
        private_key (str): PEM-encoded private key
        public_key (str): PEM-encoded public key
        private_path (str): Path to save the private key
        public_path (str): Path to save the public key
    """
    with open(private_path, 'w') as f:
        f.write(private_key)
    
    with open(public_path, 'w') as f:
        f.write(public_key)
    
    # Set appropriate permissions for private key (Unix-like systems)
    if os.name == 'posix':
        os.chmod(private_path, 0o600)

def encrypt_message(message, public_key_pem):
    """
    Encrypt a message using the public key (simplified demonstration).
    Note: This is a simplified example for educational purposes only.
    In practice, you would use hybrid encryption with RSA for key exchange and
    symmetric encryption for the actual message.
    
    Args:
        message (str): The message to encrypt
        public_key_pem (str): PEM-encoded public key
        
    Returns:
        bytes: The encrypted message
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    
    # Load the public key
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )
    
    # Encrypt the message
    encrypted = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted

def decrypt_message(encrypted_message, private_key_pem):
    """
    Decrypt a message using the private key.
    
    Args:
        encrypted_message (bytes): The encrypted message
        private_key_pem (str): PEM-encoded private key
        
    Returns:
        str: The decrypted message
    """
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes
    
    # Load the private key
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    
    # Decrypt the message
    decrypted = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return decrypted.decode('utf-8')

def format_key_for_display(key_pem, max_chars_per_line=50):
    """
    Format a key for display in the game by adding line breaks.
    
    Args:
        key_pem (str): PEM-encoded key
        max_chars_per_line (int): Maximum characters per line
        
    Returns:
        list: List of lines for display
    """
    lines = key_pem.split('\n')
    formatted_lines = []
    
    for line in lines:
        if len(line) <= max_chars_per_line:
            formatted_lines.append(line)
        else:
            # Split long lines
            for i in range(0, len(line), max_chars_per_line):
                formatted_lines.append(line[i:i+max_chars_per_line])
    
    return formatted_lines 