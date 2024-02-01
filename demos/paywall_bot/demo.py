"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.conf import settings
from hammett.core import Application, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.permission import ignore_permissions
from hammett.core.persistence import RedisPersistence

from permissions import PaywallPermission

MAIN_MENU_SCREEN_DESCRIPTION = (
    'Congratulations 🎊 You have paid successfully! '
    'Now you see desirable <b>MainMenuScreen</b> even after typing the /start command.\n'
    '\n'
    'If you want to try the demo one more time, click the button below to make a fake refund 👇'
)

FAKE_PAYMENT_SCREEN_DESCRIPTION = (
    'You must accept some rules to get the access to this bot. '
    'After that, the payment will be finished automatically. Do you accept the rules?\n'
    '\n'
    '(The payment is gonna be fake, because of none of the payment gateways are connected 😉)'
)

PAYMENT_SCREEN_DESCRIPTION = (
    "Welcome to HammettPaywallBot!\n"
    "\n"
    "Now you see <b>PaymentScreen</b> and you <i>won't see any of another screens</i> "
    "until you have paid 💰. Even if you try to type the /start command one more time, "
    "you will see this screen again and again. Check it out!"
)


class FakePaymentScreen(Screen):
    """The class implements FakePaymentScreen."""

    description = FAKE_PAYMENT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                '❌ No',
                PaymentScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE),
            Button(
                '✅ Yes',
                self.handle_fake_payment,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE),
        ]]

    @ignore_permissions([PaywallPermission])
    @register_button_handler
    async def handle_fake_payment(self, update, context):
        """Handle a button click and process a fake payment.

        It is better to decorate all the handlers which are used
        in a permission denied state.
        """
        user = update.effective_user
        settings.PAID_USERS.append(user.id)

        return await MainMenuScreen().move(update, context)

    @ignore_permissions([PaywallPermission])
    async def move(self, update, context, **kwargs):
        """Switch to the screen re-rendering the previous message.

        It is better to decorate all the handlers which are used
        in a permission denied state.
        """
        return await super().move(update, context, **kwargs)


class MainMenuScreen(StartMixin):
    """The class implements MainMenuScreen that is only available after the payment."""

    description = MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                '💸 Fake Refund',
                self.handle_fake_refund,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE),
        ]]

    @register_button_handler
    async def handle_fake_refund(self, update, context):
        """Handle a button click and do fake refund."""
        settings.PAID_USERS = []

        return await PaymentScreen().move(update, context)


class PaymentScreen(Screen):
    """The class implements PaymentScreen, which acts as a response
    if the user has not paid.
    """

    description = PAYMENT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                '💳 Pay',
                FakePaymentScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE),
        ]]

    @ignore_permissions([PaywallPermission])
    async def move(self, update, context, **kwargs):
        """Switch to the screen re-rendering the previous message.

        It is better to decorate all the handlers which are used
        in a permission denied state.
        """
        return await super().move(update, context, **kwargs)


def main():
    """Run the bot."""
    app = Application(
        'HammettPaywallBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {FakePaymentScreen, MainMenuScreen, PaymentScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
