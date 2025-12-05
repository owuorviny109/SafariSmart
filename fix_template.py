with open('templates/payments/sponsorship.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # Add {% if %} before card button
    if 'id="pay-card-btn"' in line and i > 0:
        indent = ' ' * 28
        new_lines.insert(-1, indent + '{% if enable_flutterwave %}\n')
    # Add {% endif %} after card button closes
    if 'Pay with Card (Global)' in line and '</button>' in line:
        indent = ' ' * 28
        new_lines.append(indent + '{% endif %}\n')

with open('templates/payments/sponsorship.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Template fixed!')
