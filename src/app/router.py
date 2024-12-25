from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.crud import create_user
from src.app.data_storage import user_data
from src.app.models import User
from src.app.service import get_user_by_chat_id, get_user_by_id, get_all_users
from src.app.service import create_user as create_user_service, delete_user as delete_user_service
from src.log_config import loggerApp
from src.app.schemas import UserBase, UserCreate, MarketBase, MarketCreate, MarketResponse, UserResponse
from src.app.database import get_db, get_async_session

import os, re
from fastapi import APIRouter, Depends, Request, HTTPException
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter()


# Endpoint to create a new user
@router.post("/users/", response_model=UserBase)
async def create_user(user: UserCreate):
    user = await create_user_service(user)
    return user


# Endpoint to get all users
@router.get("/users/", response_model=list[UserBase])
async  def get_users():
    users = await get_all_users()
    return users


# Additional endpoints for other models can be defined similarly...
@router.get("/users/{user_id}")
async def read_user(user_id: int):
    user = await get_user_by_id(user_id=user_id)
    return user if user else {"error": "User not found"}


# Example of getting a specific user by ID
# @router.get("/users/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# Example of deleting a user by ID
@router.delete("/users/{chat_id}", response_model=dict)
async def delete_user(chat_id: int):
    user = await delete_user_service(chat_id=chat_id)
    return {"detail": "User deleted successfully"}


# You can add similar CRUD operations for Pairs, Timeframe, Notifications, and Models.


# --------------------- Telegram Routers ----------------------

async def start(update: Update, context: CallbackContext):
    print("Start has been triggered ", update)
    user = await get_user_by_chat_id(chat_id=update.message.chat.id)

    if user:
        # User is registered, send personalized welcome message and options
        keyboard = [
            [InlineKeyboardButton("Select or Change Models", callback_data='select_models')],
            [InlineKeyboardButton("Select or Change Timeframe", callback_data='select_timeframe')],
            [InlineKeyboardButton("Account Management", callback_data='account_management')],
            [InlineKeyboardButton("Delete Me", callback_data='delete_me')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Welcome back, {user.name}! Please choose an option:",
            reply_markup=reply_markup
        )
    else:
        # User is not registered, show registration options
        keyboard = [
            [InlineKeyboardButton("Register", callback_data='register')],
            [InlineKeyboardButton("About Us", callback_data='about_us')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Welcome! This is Athena Assistance. Please choose an option:",
            reply_markup=reply_markup
        )
    return 0


async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    if query.data == 'register':
        await query.edit_message_text(text="Please enter your name:")
        user_data[query.from_user.id] = {'step': 'name'}  # Set the user's step to 'name'

    elif query.data == 'about_us':
        await query.edit_message_text(
            text="About Us: I am a trading assitance robat that has been written by @Iman_n68")

    elif query.data == 'select_models':
        await query.edit_message_text(text="Please select a model from the list below:")
        # Here you would typically present the user with model options

    elif query.data == 'select_timeframe':
        await query.edit_message_text(text="Please select a timeframe from the list below:")
        # Here you would typically present the user with timeframe options

    elif query.data == 'account_management':
        await query.edit_message_text(text="What would you like to do in account management?")
        # You could provide options for account management here

    elif query.data == 'delete_me':
        await query.edit_message_text(text="Are you sure you want to delete your account? (yes/no)")

        delete_keyboard = [
            [InlineKeyboardButton("Yes", callback_data='confirm_delete')],
            [InlineKeyboardButton("No", callback_data='cancel_delete')]
        ]
        delete_reply_markup = InlineKeyboardMarkup(delete_keyboard)

        await query.edit_message_text(
            text="Are you sure you want to delete your account?",
            reply_markup=delete_reply_markup
        )

    elif query.data == 'confirm_delete':

        chat_id = query.from_user.id  # Get the user's chat ID
        await delete_user_service(chat_id)
        await query.edit_message_text(text="Your account has been deleted.")

    elif query.data == 'cancel_delete':
        await query.edit_message_text(text="Account deletion canceled.")

    else:
        await query.edit_message_text(text="Unknown option selected.")

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    step = user_data.get(user_id, {}).get('step')

    if step == 'name':
        user_data[user_id]['name'] = update.message.text
        user_data[user_id]['step'] = 'email'  # Move to the next step
        await update.message.reply_text("Please enter your email:")

    elif step == 'email':
        if validate_email(update.message.text):
            user_data[user_id]['email'] = update.message.text
            user_data[user_id]['step'] = 'mobile'  # Move to the next step
            await update.message.reply_text("Please enter your mobile number (format: 0098 912 123 4567):")
        else:
            await update.message.reply_text("Invalid email format. Please enter a valid email:")

    elif step == 'mobile':
        if validate_mobile(update.message.text):
            user_data[user_id]['mobile'] = update.message.text
            user = UserCreate(
                name=user_data[user_id]['name'].title(),
                email=user_data[user_id]['email'].lower(),
                mobile=user_data[user_id]['mobile'],
                telegram_chat_id=chat_id,
                active=1
            )
            # Call the create_user function to save data in the database
            new_user = await create_user_service(user)

            await update.message.reply_text(
                f"Registration complete!\nName: {new_user.name}\nEmail: {new_user.email}\nMobile: {new_user.mobile}")
            del user_data[user_id]  # Clear user data after completion
        else:
            await update.message.reply_text("Invalid mobile number format. Please enter a valid mobile number:")

    else:
        print("Echo has been triggered ", update)
        try:
            await update.message.reply_text(f"You said: {update.message.text}")
        except Exception as e:
            loggerApp.error("Error in echo handler: %s", str(e))


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def validate_mobile(mobile):
    mobile_regex = r'^0098\s\d{3}\s\d{3}\s\d{4}$'
    return re.match(mobile_regex, mobile) is not None
