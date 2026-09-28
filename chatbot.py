import json
import database
import orders
import booking
import faqs
import config

menu_text = """Hi! How can I help you today?
1 - Place an order
2 - Check order status
3 - Book an appointment
4 - Frequently asked questions

Or just type your question directly."""


def get_response(phone, message):
    msg = message.strip()
    msg_lower = msg.lower()

    # admin commands - check first
    if phone == config.ADMIN_PHONE:
        parts = msg.split()
        if len(parts) >= 3 and parts[0].lower() == 'update':
            result = orders.admin_update_status(parts[1], parts[2])
            if result is not None:
                return result

    # get where the user is in the conversation
    session = database.get_session(phone)
    state = session['state']
    temp = session['temp_data']
    if temp is None or temp == '':
        temp = '{}'
    data = json.loads(temp)

    # if they say hi or menu, start over
    if msg_lower in ('hi', 'hello', 'menu', 'start'):
        database.reset_session(phone)
        return menu_text

    # idle - show menu options
    if state == 'idle':
        if msg == '1':
            database.update_session(phone, 'order_item', '{}')
            return "What would you like to order? (describe the item)"

        elif msg == '2':
            database.update_session(phone, 'order_status_lookup', '{}')
            return "What's your order number? (or type 'mine' to see all your orders)"

        elif msg == '3':
            database.update_session(phone, 'booking_name', '{}')
            return "Great — what's your name?"

        elif msg == '4':
            topics = faqs.list_topics()
            return "Ask me about: " + topics + "\n\nJust type your question, e.g. 'what are your hours?'"

        else:
            # maybe they typed a question directly
            ans = faqs.find_answer(msg)
            if ans is not None:
                return ans
            return "I didn't quite get that.\n\n" + menu_text

    # ordering - step 1: what item
    elif state == 'order_item':
        data['item'] = msg
        database.update_session(phone, 'order_quantity', json.dumps(data))
        return "How many would you like?"

    # ordering - step 2: how many
    elif state == 'order_quantity':
        ok, reply = orders.place_order(phone, data.get('item', ''), msg)
        if not ok:
            return reply   # let them try again
        database.reset_session(phone)
        return reply + "\n\nReply 'menu' for more options."

    # checking order status
    elif state == 'order_status_lookup':
        database.reset_session(phone)
        if msg_lower == 'mine':
            return orders.list_my_orders(phone) + "\n\nReply 'menu' for more options."
        return orders.check_status(msg) + "\n\nReply 'menu' for more options."

    # booking - step 1: name
    elif state == 'booking_name':
        data['name'] = msg
        database.update_session(phone, 'booking_date', json.dumps(data))
        return "What date would you like? (YYYY-MM-DD)"

    # booking - step 2: date
    elif state == 'booking_date':
        data['date'] = msg
        database.update_session(phone, 'booking_time', json.dumps(data))
        return "What time? (e.g. 14:00 or 2:00PM)"

    # booking - step 3: time
    elif state == 'booking_time':
        ok, reply = booking.create_booking(phone, data.get('name', 'Unknown'), data.get('date', ''), msg)
        database.reset_session(phone)
        if ok:
            return reply + "\n\nReply 'menu' for more options."
        else:
            return reply + "\n\nReply 'menu' to start over."

    # something went wrong, just reset
    else:
        database.reset_session(phone)
        return menu_text