def format_mail(name, domain):
    clean_name = name.lower().replace(" ", ".")
    return f"{clean_name}@{domain}.com"

print(format_mail("John", "company"))