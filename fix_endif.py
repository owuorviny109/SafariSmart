with open('templates/payments/sponsorship.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add endif after the card button
content = content.replace(
    '                            </button>\n                        </div>\n                    </div>\n\n                    <!-- Processing State -->',
    '                            </button>\n                            {% endif %}\n                        </div>\n                    </div>\n\n                    <!-- Processing State -->'
)

with open('templates/payments/sponsorship.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Added endif tag!')
