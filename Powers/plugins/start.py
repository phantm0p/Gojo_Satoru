from pyrogram import filters
from pyrogram.errors import MessageNotModified, QueryIdInvalid, UserIsBlocked
from pyrogram.types import CallbackQuery, Message

from Powers import HELP_COMMANDS, LOGGER
from Powers.bot_class import Gojo
from Powers.utils.custom_filters import command
from Powers.utils.kbhelpers import ikb
from Powers.utils.start_utils import (
    gen_cmds_kb,
    gen_start_kb,
    get_help_msg,
    get_private_note,
    get_private_rules,
)
from Powers.vars import Config


@Gojo.on_message(
    command("donate") & (filters.group | filters.private),
)
async def donate(_, m: Message):
    LOGGER.info(f"{m.from_user.id} fetched donation text in {m.chat.id}")
    await m.reply_text(text="""Hey Thanks for your thought of donating me!
      When you donate, all the fund goes towards my development which makes on fast and responsive.
      Your donation might also me get me a new feature or two, which I wasn't able to get due to server limitations.

      All the fund would be put into my services such as database, storage and hosting!

      You can donate by contacting my owner: @iamgojoof6eyes""")
    return


@Gojo.on_callback_query(filters.regex("^close_admin$"))
async def close_admin_callback(_, q: CallbackQuery):
    user_id = q.from_user.id
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {"creator", "administrator"}:
        await q.answer(
            "You're not even an admin, don't try this explosive shit!",
            show_alert=True,
        )
        return
    if user_status != "creator":
        await q.answer(
            "You're just an admin, not owner\nStay in your limits!",
            show_alert=True,
        )
        return
    await q.message.edit_text("Closed!")
    await q.answer("Closed menu!", show_alert=True)
    return


@Gojo.on_message(
    command("start") & (filters.group | filters.private),
)
async def start(c: Gojo, m: Message):
    if m.chat.type == "private":
        if len(m.text.split()) > 1:
            help_option = (m.text.split(None, 1)[1]).lower()

            if help_option.startswith("note") and (
                help_option not in ("note", "notes")
            ):
                await get_private_note(c, m, help_option)
                return
            if help_option.startswith("rules"):
                LOGGER.info(f"{m.from_user.id} fetched privaterules in {m.chat.id}")
                await get_private_rules(c, m, help_option)
                return

            help_msg, help_kb = await get_help_msg(m, help_option)

            if not help_msg:
                return

            await m.reply_text(
                help_msg,
                parse_mode="markdown",
                reply_markup=ikb(help_kb),
                quote=True,
                disable_web_page_preview=True,
            )
            return
        try:
            await m.reply_text(
                text="""Hey there! My name is Alita ✨.
      I'm here to help you manage your groups!
      Hit /help to find out more about how to use me in my full potential!

      Join my [News Channel](https://t.me/gojo_updates) to get information on all the latest updates.""",
                reply_markup=(await gen_start_kb(m)),
                quote=True,
                disable_web_page_preview=True,
            )
        except UserIsBlocked:
            LOGGER.warning(f"Bot blocked by {m.from_user.id}")
    else:
        await m.reply_text(
            text="I'm alive :3",
            quote=True,
        )
    return


@Gojo.on_callback_query(filters.regex("^start_back$"))
async def start_back(_, q: CallbackQuery):
    try:
        await q.message.edit_text(
            text="""Hey there! My name is Alita ✨.
      I'm here to help you manage your groups!
      Hit /help to find out more about how to use me in my full potential!

      Join my [News Channel](http://t.me/gojo_updates) to get information on all the latest updates.""",
            reply_markup=(await gen_start_kb(q.message)),
            disable_web_page_preview=True,
        )
    except MessageNotModified:
        pass
    await q.answer()
    return


@Gojo.on_callback_query(filters.regex("^commands$"))
async def commands_menu(_, q: CallbackQuery):
    keyboard = ikb(
        [
            *(await gen_cmds_kb(q)),
            [(f"« Back", "start_back")],
        ],
    )
    try:
        await q.message.edit_text(
            text="""Hey There! My name is Alita.
            I'm here to help you manage your groups!
            Commands available:
            × /start: Start the bot
            × /help: Give's you this message.""",
        reply_markup=keyboard,
        )
    except MessageNotModified:
        pass
    except QueryIdInvalid:
        await q.message.reply_text(
            text="""Hey There! My name is Alita.
            I'm here to help you manage your groups!
            Commands available:
            × /start: Start the bot
            × /help: Give's you this message.""",
            reply_markup=keyboard,
        )
    await q.answer()
    return


@Gojo.on_message(command("help"))
async def help_menu(_, m: Message):
    if len(m.text.split()) >= 2:
        help_option = (m.text.split(None, 1)[1]).lower()
        help_msg, help_kb = await get_help_msg(m, help_option)

        if not help_msg:
            LOGGER.error(f"No help_msg found for help_option - {help_option}!!")
            return

        LOGGER.info(
            f"{m.from_user.id} fetched help for '{help_option}' text in {m.chat.id}",
        )
        if m.chat.type == "private":
            await m.reply_text(
                help_msg,
                parse_mode="markdown",
                reply_markup=ikb(help_kb),
                quote=True,
                disable_web_page_preview=True,
            )
        else:
            await m.reply_text(
                text=f"Press the button below to get help for <i>{help_option}</i>",
                reply_markup=ikb(
                    [
                        [
                            (
                                "Help",
                                f"t.me/{Config.BOT_USERNAME}?start={help_option}",
                                "url",
                            ),
                        ],
                    ],
                ),
            )
    else:
        if m.chat.type == "private":
            keyboard = ikb(
                [
                    *(await gen_cmds_kb(m)),
                    [("« Back", "start_back")],
                ],
            )
            msg = """Hey There! My name is Alita.
      I'm here to help you manage your groups!
      Commands available:
       × /start: Start the bot
       × /help: Give's you this message."""
        else:
            keyboard = ikb(
                [[("Help", f"t.me/{Config.BOT_USERNAME}?start=help", "url")]],
            )
            msg = "Contact me in PM to get the list of possible commands."
        await m.reply_text(
            msg,
            reply_markup=keyboard,
        )

    return


@Gojo.on_callback_query(filters.regex("^get_mod."))
async def get_module_info(_, q: CallbackQuery):
    module = q.data.split(".", 1)[1]

    help_msg = f"**{str(module)}:**\n\n" + HELP_COMMANDS[module]["help_msg"],

    help_kb = HELP_COMMANDS[module]["buttons"] + [
        [("« " + "Back", "commands")],
    ]
    await q.message.edit_text(
        help_msg,
        parse_mode="markdown",
        reply_markup=ikb(help_kb),
    )
    await q.answer()
    return
