from werkzeug.security import generate_password_hash

# Prompt user for password
password = input("Enter password to hash: ").strip()

# Generate hash
hash_value = generate_password_hash(password)

print("\nGenerated Hash:")
print(hash_value)
print("\n✅ Copy this hash and paste it into docker/mysql-init/init.sql")
