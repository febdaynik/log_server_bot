import asyncio
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.text_decorations import html_decoration as html

from bot.keyboards.default import back_markup
from bot.keyboards.server import terminal_markup
from bot.utils.ssh import SshServer
from states import TerminalByServer

router = Router()


@router.callback_query(F.data.startswith("server:terminal:"))
async def terminal_server_callback(call: CallbackQuery, state: FSMContext, ssh_server: SshServer):
    await state.clear()

    proc = await ssh_server.ssh_server.create_process(term_type="xterm")

    msg = await call.message.edit_text(
        text="<b>Это терминал сервера</b>\n\n"
             "Вводите команды, и здесь будет показан вывод на них",
        reply_markup=back_markup(name="« В меню", callback_data=f"server:get:{ssh_server.server.id}"),
    )

    await state.set_state(TerminalByServer.command)
    return await state.update_data(msg=msg, ssh_server=ssh_server, proc=proc)


@router.message(TerminalByServer.command)
async def TerminalByServer_command_state(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    proc = data["proc"]

    proc.stdin.write(message.text + "\n")

    try:
        await asyncio.sleep(0.7)
        output = await proc.stdout.read(1024)
    except Exception as e:
        msg = await data["msg"].edit_text(text=f"Ошибка чтения вывода: {e}", reply_markup=data["msg"].reply_markup)
        return await state.update_data(msg=msg)

    with suppress(TelegramBadRequest):
        msg = await data["msg"].edit_text(
            text="<b>Это терминал сервера</b>\n\n"
                 f"<pre><code class=\"language-shell\">{html.quote(output)}</code></pre>"
                 "Вводите команды, и здесь будет показан вывод на них",
            reply_markup=data["msg"].reply_markup,
        )
        return await state.update_data(msg=msg)

    msg = await data["msg"].edit_text(
            text="<b>Это терминал сервера</b>\n\n"
                 f"<pre><code class=\"language-shell\">{html.quote(output)}</code></pre>"
                 "Ничего не изменилось, попробуйте ещё раз",
            reply_markup=terminal_markup(server_id=data["ssh_server"].server.id),
        )

    return await state.update_data(msg=msg)


