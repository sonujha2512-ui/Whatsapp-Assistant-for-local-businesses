# Whatsapp-Assistant-for-local-businesses
A WhatsApp chatbot for small businesses that handles orders, bookings and FAQs. Built with Python, Flask, SQLite and Twilio.

## Key Features
- **Order Management** - customers can place orders through whatsapp, check their order status anytime, and the admin can update order status (pending, confirmed, preparing, shipped etc) right from the chat
- **Appointment Booking** - customers can book appointments by picking a date and time slot (9am to 5pm, on the hour). The bot checks for conflicts so no double bookings happen
- **FAQ System** - reads questions and answers from a simple json file. Matches keywords from the users message to give the right answer. You can add/edit FAQs without touching any code, just edit faqs.json
- **Admin Controls** - one phone number (yours) gets admin access to update order statuses directly through whatsapp messages
- **Conversation State** - the bot remembers where each user is in the conversation (like if theyre halfway through placing an order) using sqlite, so it doesnt lose track even if the server restarts
- **Multi-user Support** - handles multiple users at the same time, each with their own session
---
## Prerequisites
Before you start, make sure you have these:
1. **Python 3.9 or higher** - check by running `python --version` in terminal
2. **A Twilio account** - sign up for free at https://www.twilio.com/try-twilio
3. **ngrok** - download from https://ngrok.com/download (free account works fine)
4. **pip** - usually comes with python. If not, google "install pip windows"
---
## Configuration
There are two files you need to edit before running:
### config.py
Open this file and change `ADMIN_PHONE` to your own whatsapp number. Use this format:
```
ADMIN_PHONE = "whatsapp:+91XXXXXXXXXX"
```
Replace the X's with your actual number. This is the number that will be able to run admin commands like updating order status.
### faqs.json
This file has all the FAQ answers. Each entry has keywords and an answer. Replace all the `EDIT ME` parts with your real business info:
```json
{
  "hours": {
    "keywords": ["hours", "open", "close", "timing"],
    "answer": "We are open Monday to Saturday, 10 AM to 8 PM."
  }
}
```
You can add new topics too, just follow the same format.
---
##How to Run
### Step 1 - Install dependencies
Open a terminal inside the project folder and run:
```
python -m pip install -r requirements.txt
```
This installs flask and twilio. On windows if `pip` doesnt work, use `python -m pip` instead.
## Step 2 - Start the flask server
```
python app.py
```
This starts the server on http://127.0.0.1:5000. Keep this terminal open.

## Step 3 - Expose it with ngrok
Open a second terminal. First time only, add your authtoken:
```
ngrok config add-authtoken YOUR_NGROK_TOKEN
```
You get this token from https://dashboard.ngrok.com after signing up.
Then start ngrok:
```
ngrok http 5000
```
It will show a url like `https://xxxx.ngrok-free.dev` - copy this url. Keep this terminal open.

## Step 4 - Setup Twilio WhatsApp Sandbox
1. Go to Twilio Console -> Messaging -> Try it out -> Send a WhatsApp message
2. From your whatsapp, send the join code they show to the sandbox number
3. Click on Sandbox settings tab
4. In the "When a message comes in" field, paste:
   ```
   https://YOUR-NGROK-URL/webhook
   ```
5. Make sure method is set to POST, then click Save

## Step 5 - Test
Send `hi` to the sandbox number from your whatsapp. You should get a menu with options
---
## Usage Instructions
### For Customers
When a customer sends a message, they get this menu:
```
Hi! How can I help you today?
1 - Place an order
2 - Check order status
3 - Book an appointment
4 - Frequently asked questions
Or just type your question directly.
```
| What to type | What it does |
|-------------|-------------|
| `1` | Starts the ordering flow - bot asks what item and quantity |
| `2` | Check order status by order number, or type `mine` to see all orders |
| `3` | Book an appointment - bot asks for name, date, and time |
| `4` | Shows FAQ topics, then customer can type their question |
| `hi` or `menu` | Resets the conversation and shows the menu again |
Customers can also skip the menu and directly type a question like "what are your hours?" and the bot will try to find an answer from faqs.json.
### For Admin
The admin (phone number set in config.py) can update order statuses by sending:
```
update <order_id> <status>
```
**Example:** `update 3 shipped`
Available statuses: `pending`, `confirmed`, `preparing`, `ready`, `shipped`, `delivered`, `cancelled`
---
## Project Structure
```
Whatsapp_assistant/
├── app.py             - flask server, entry point
├── chatbot.py         - conversation flow and state machine
├── orders.py          - order placement and status checking
├── booking.py         - appointment booking logic
├── faqs.py            - keyword matching for FAQs
├── faqs.json          - FAQ data (edit this for your business)
├── database.py        - sqlite database operations
├── config.py          - admin phone number
├── requirements.txt   - python dependencies
└── assistant.db       - created automatically when you first run the app

## Troubleshooting
| Problem | Fix |
|---------|-----|
| `pip is not recognized` | Use `python -m pip install ...` |
| `ngrok is not recognized` | Run ngrok from its folder, or add it to your PATH |
| `No module named database` | Make sure youre running `python app.py` from inside the project folder |
| Bot gives twilio default reply | Check that webhook url ends with `/webhook` and is saved properly |
| Webhook broke after restarting ngrok | ngrok gives a new url every time, update it in twilio sandbox settings |
| Admin commands dont work | Make sure ADMIN_PHONE in config.py matches your number exactly |
---
## Limitations
- Twilio sandbox is only for testing, not production. Users have to send a join code first
- ngrok url changes every time you restart it (paid plan gives you a fixed url)
- `debug=True` is for development only
- No payment integration, order status is updated manually by admin
- FAQ matching is keyword based, not AI powered
