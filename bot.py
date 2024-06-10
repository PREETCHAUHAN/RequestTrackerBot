# Importing External Packages
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from pyrogram.errors.exceptions import (
    PeerIdInvalid,
    UserNotParticipant,
    ChannelPrivate,
    ChatIdInvalid,
    ChannelInvalid
)
from pymongo import MongoClient

# Importing Credentials & Required Data
try:
    from testexp.config import *
except ModuleNotFoundError:
    from config import *

# Importing built-in module
from re import match, search


"""Connecting to Bot"""
app = Client(
    "RequestTrackerBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
)


'''Connecting To Database'''
mongo_client = MongoClient(Config.MONGO_STR)
db_bot = mongo_client['RequestTrackerBot']
collection_ID = db_bot['channelGroupID']


# Regular Expression for #request
requestRegex = "#[rR][eE][qQ][uU][eE][sS][tT] "


"""Handlers"""

# Start & Help Handler
@app.on_message(filters.private & filters.command(["start", "help"]))
async def start_handler(_, msg: Message):
    bot_info = await app.get_me()
    await msg.reply_text(
        "<b>Hi, I am Request Tracker Bot🤖.\nIf you hadn't added me in your Group & Channel then ➕add me now.\n\nHow to Use me?</b>\n\t1. Add me to your Group & CHannel.\n\t2. Make me admin in both Channel & Group.\n\t3. Give permission to Post , Edit & Delete Messages.\n\t4. Now send Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.\nNow Bot is ready to be used.\n\n<b>😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕Add me to your Group.",
                        url=f"https://telegram.me/{bot_info.username}?startgroup=true"
                    )
                ]
            ]
        )
    )


# return group id when bot is added to group
@app.on_message(filters.new_chat_members)
async def chat_handler(_, msg: Message):
    if msg.new_chat_members[0].is_self:  # If bot is added
        await msg.reply_text(
            f"<b>Hey😁, Your Group ID is <code>{msg.chat.id}</code></b>",
        )


# return channel id when message/post from channel is forwarded
@app.on_message(filters.forwarded & filters.private)
async def forwarded_handler(_, msg: Message):
     if msg.forward_from_chat.type == "channel":   # If message forwarded from channe
        await msg.reply_text(
            f"<b>Hey😁, Your Channel ID is <code>{forward_info.id}</code>\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
        )


# /add handler to add group id & channel id with database
@app.on_message(filters.private & filters.command("add"))
async def group_channel_id_handler(_, msg: Message):
    message = msg.text.split(" ")
    if len(message) == 3:  # If command is valid
        _, group_id, channel_id = message
        try:
            int(group_id)
            int(channel_id)
        except ValueError:  # If Ids are not integer type
            await msg.reply_text(
                "<b>Group ID & Channel ID should be integer type😒.</b>",
            )
        else:  # If Ids are integer type
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[group_id]
                except KeyError:
                    pass
                else:  # If group id found in database
                    await msg.reply_text(
                        "<b>Your Group ID already Added.</b>",
                    )
                    break
                for record in document:
                    if record == "_id":
                        continue
                    else:
                        if document[record][0] == channel_id:  # If channel id found in database
                            await msg.reply_text(
                                "<b>Your Channel ID already Added.</b>",
                            )
                            break
            else:  # If group id & channel not found in db
                try:
                    bot_self_group = await app.get_chat_member(int(group_id), 'me')
                except (PeerIdInvalid, ValueError):  # If given group id is invalid
                    await msg.reply_text(
                        "<b>😒Group ID is wrong.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                    )
                except UserNotParticipant:  # If bot is not in group
                    await msg.reply_text(
                        "<b>😁Add me in group and make me admin, then use /add.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                    )
                else:
                    if bot_self_group.status != "administrator":  # If bot is not admin in group
                        await msg.reply_text(
                            "<b>🥲Make me admin in Group, Then add use /add.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                        )
                    else:  # If bot is admin in group
                        try:
                            bot_self_channel = await app.get_chat_member(int(channel_id), 'me')
                        except (UserNotParticipant, ChannelPrivate):  # If bot not in channel
                            await msg.reply_text(
                                "<b>😁Add me in Channel and make me admin, then use /add.</b>",
                            )
                        except (ChatIdInvalid, ChannelInvalid):  # If given channel id is invalid
                            await msg.reply_text(
                                "<b>😒Channel ID is wrong.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                            )
                        else:
                            if not (bot_self_channel.can_post_messages and bot_self_channel.can_edit_messages and bot_self_channel.can_delete_messages):  # If bot has not enough permissions
                                await msg.reply_text(
                                    "<b>🥲Make sure to give Permissions like Post Messages, Edit Messages & Delete Messages.</b>",
                                )
                            else:  # Adding Group ID, Channel ID & User ID in group
                                collection_ID.insert_one(
                                    {
                                        group_id: [channel_id, msg.chat.id]
                                    }
                                )
                                await msg.reply_text(
                                    "<b>Your Group and Channel has now been added SuccessFully🥳.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                                )
    else:  # If command is invalid
        await msg.reply_text(
            "<b>Invalid Format😒\nSend Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
        )


# /remove handler to remove group id & channel id from database
@app.on_message(filters.private & filters.command("remove"))
async def channel_group_remover(_, msg: Message):
    message = msg.text.split(" ")
    if len(message) == 2:  # If command is valid
        _, group_id = message
        try:
            int(group_id)
        except ValueError:  # If group id not integer type
            await msg.reply_text(
                "<b>Group ID should be integer type😒.</b>",
            )
        else:  # If group id is integer type
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[group_id]
                except KeyError:
                    continue
                else:  # If group id found in database
                    if document[group_id][1] == msg.chat.id:  # If group id, channel id is removing by one who added
                        collection_ID.delete_one(document)
                        await msg.reply_text(
                            "<b>Your Channel ID & Group ID has now been Deleted😢 from our Database.\nYou can add them again by using <code>/add GroupID ChannelID</code>.</b>",
                        )
                    else:  # If group id, channel id is not removing by one who added
                        await msg.reply_text(
                            "<b>😒You are not the one who added this Channel ID & Group ID.</b>",
                        )
                    break
            else:  # If group id not found in database
                await msg.reply_text(
                    "<b>Given Group ID is not found in our Database🤔.\n\n😊Join @PreetModzNetworkz & @MrBot02 for getting more awesome 🤖bots like this.</b>",
                )
    else:  # If command is invalid
        await msg.reply_text(
            "<b>Invalid Command😒\nUse <code>/remove GroupID</code></b>.",
        )


# #request handler
@app.on_message(filters.group & filters.regex(requestRegex + "(.*)"))
async def request_handler(_, msg: Message):
    group_id = str(msg.chat.id)

    documents = collection_ID.find()
    for document in documents:
        try:
            document[group_id]
        except KeyError:
            continue
        else:  # If group id found in database
            channel_id = document[group_id][0]
            from_user = msg.from_user
            mention_user = f"<a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>"
            request_text = f"<b>Request by {mention_user}\n\n{msg.text}</b>"
            original_msg = msg.text
            find_regex_str = match(requestRegex, original_msg)
            request_string = find_regex_str.group()
            content_requested = original_msg.split(request_string)[1]

            try:
                group_id_pro = group_id.removeprefix(str(-100))
                channel_id_pro = channel_id.removeprefix(str(-100))
            except AttributeError:
                group_id_pro = group_id[4:]
                channel_id_pro = channel_id[4:]

            # Sending request in channel
            request_msg = await app.send_message(
                int(channel_id),
                request_text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Requested Message",
                                url=f"https://t.me/c/{group_id_pro}/{msg.message_id}"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🚫Reject",
                                "reject"
                            ),
                            InlineKeyboardButton(
                                "Done✅",
                                "done"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "⚠️Unavailable⚠️",
                                "unavailable"
                            )
                        ]
                    ]
                )
            )

            reply_text = f"<b>👋 Hello {mention_user} !!\n\n📍 Your Request for {content_requested} has been submitted to the admins.\n\n🚀 Your Request Will Be Uploaded soon.\n📌 Please Note that Admins might be busy. So, this may take more time.\n\n👇 See Your Request Status Here 👇</b>"

            # Sending message for user in group
            await msg.reply_text(
                reply_text,
                parse_mode="html",
                reply_to_message_id=msg.message_id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⏳Request Status⏳",
                                url=f"https://t.me/c/{channel_id_pro}/{request_msg.message_id}"
                            )
                        ]
                    ]
                )
            )
            break


# callback buttons handler
@app.on_callback_query()
async def callback_button(_, callback_query: CallbackQuery):
    channel_id = str(callback_query.message.chat.id)

    documents = collection_ID.find()
    for document in documents:
        for key in document:
            if key == "_id":
                continue
            else:
                if document[key][0] != channel_id:
                    continue
                else:  # If channel id found in database
                    group_id = key

                    data = callback_query.data  # Callback Data
                    if data == "rejected":
                        return await callback_query.answer(
                            "This request is rejected💔...\nAsk admins in group for more info💔",
                            show_alert=True
                        )
                    elif data == "completed":
                        return await callback_query.answer(
                            "This request Is Completed🥳...\nCheckout in Channel😊",
                            show_alert=True
                        )
                    user = await app.get_chat_member(int(channel_id), callback_query.from_user.id)
                    if user.status not in ("administrator", "creator"):  # If accepting, rejecting request tried to be done by neither admin nor owner
                        await callback_query.answer(
                            "Who the hell are you?\nYour are not Admin😒.",
                            show_alert=True
                        )
                    else:  # If accepting, rejecting request tried to be done by either admin or owner
                        if data == "reject":
                            result = "REJECTED"
                            group_result = "has been Rejected💔."
                            button = InlineKeyboardButton("Request Rejected🚫", "rejected")
                        elif data == "done":
                            result = "COMPLETED"
                            group_result = "is Completed🥳."
                            button = InlineKeyboardButton("Request Completed✅", "completed")
                        elif data == "unavailable":
                            result = "UNAVAILABLE"
                            group_result = "has been rejected💔 due to Unavailablity🥲."
                            button = InlineKeyboardButton("Request Rejected🚫", "rejected")

                        msg = callback_query.message
                        user_id = 12345678
                        for m in msg.entities:
                            if m.type == "text_mention":
                                user_id = m.user.id
                        original_msg = msg.text
                        find_regex_str = search(requestRegex, original_msg)
                        request_string = find_regex_str.group()
                        content_requested = original_msg.split(request_string)[1]
                        requested_by = original_msg.removeprefix("Request by ").split('\n\n')[0]
                        mention_user = f"<a href='tg://user?id={user_id}'>{requested_by}</a>"
                        original_msg_mod = original_msg.replace(requested_by, mention_user)
                        original_msg_mod = f"<s>{original_msg_mod}</s>"

                        new_msg = f"<b>{result}</b>\n\n{original_msg_mod}"

                        # Editing request message in channel
                        await callback_query.edit_message_text(
                            new_msg,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        button
                                    ]
                                ]
                            )
                        )

                        # Result of request sent to group
                        reply_text = f"<b>Dear {mention_user}🧑\nYour request for {content_requested} {group_result}\n👍Thanks for requesting!</b>"
                        await app.send_message(
                            int(group_id),
                            reply_text,
                        )
                    return
    return


"""Bot is Started"""
print("Bot has been Started!!!")
app.run()
