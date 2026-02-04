from app.database import SessionLocal
from app.models.session import DiscoverySession

db = SessionLocal()
session = db.query(DiscoverySession).first()
messages = session.all_messages or []

valid = []
last_role = None

for m in messages:
    role = m.get('role')
    content = m.get('content', '').strip()
    if not content or role not in ['user', 'assistant']:
        continue
    if role == last_role:
        continue
    valid.append({'role': role, 'content': content})
    last_role = role

print('After filtering:')
for i, m in enumerate(valid):
    print(f"{i}: {m['role']}")

if valid and valid[0]['role'] == 'assistant':
    valid.pop(0)
    print('Removed first assistant')
    if valid:
        print('Now starts with:', valid[0]['role'])
    else:
        print('List is now empty!')

from app.services.discovery import _get_client

# After the filtering above, let's try sending to Claude
client = _get_client()

# Remove first assistant message
if valid and valid[0]['role'] == 'assistant':
    valid.pop(0)

print(f"\nSending {len(valid)} messages to Claude...")
print(f"First message role: {valid[0]['role'] if valid else 'none'}")

try:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system="You are a helpful assistant. The user has returned to continue a conversation.",
        messages=valid,
    )
    print(f"\nResponse content length: {len(response.content)}")
    if response.content:
        print(f"Response: {response.content[0].text[:200]}...")
    else:
        print("Response content is empty!")
        print(f"Full response: {response}")
except Exception as e:
    import traceback
    traceback.print_exc()