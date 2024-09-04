import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
# Import the app instance from the bot's __init__.py
from .. import app

# Store the current games and players
games = {}

# Define the Tic Tac Toe board layout
def create_board():
    return [['⬜' for _ in range(3)] for _ in range(3)]

# Convert the board to inline keyboard buttons
def board_to_keyboard(board, player1_id, player2_id):
    keyboard = []
    for i, row in enumerate(board):
        buttons = []
        for j, cell in enumerate(row):
            buttons.append(InlineKeyboardButton(cell, callback_data=f"move:{i}:{j}:{player1_id}:{player2_id}"))
        keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard)

# Check if there's a winner or a draw
def check_winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != '⬜':
            return row[0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != '⬜':
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != '⬜':
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != '⬜':
        return board[0][2]

    if all(cell != '⬜' for row in board for cell in row):
        return "Draw"

    return None

# Command to challenge another user
@app.on_message(filters.command("challenge") & filters.reply)
async def challenge_user(client, message):
    challenger_id = message.from_user.id
    challenged_user_id = message.reply_to_message.from_user.id

    # Send the challenge to the challenged user
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("ACCEPT", callback_data=f"accept:{challenger_id}:{challenged_user_id}")],
            [InlineKeyboardButton("DECLINE", callback_data=f"decline:{challenger_id}")]
        ]
    )
    await message.reply_to_message.reply("You have been challenged for a game..!", reply_markup=buttons)

    # Notify the challenger that their challenge has been sent
    await message.reply("Challenge sent!")

# Handle the accept/decline of the challenge
@app.on_callback_query(filters.regex(r"accept|decline"))
async def handle_challenge_response(client, callback_query):
    data = callback_query.data.split(":")
    action = data[0]
    challenger_id = int(data[1])
    
    if action == "accept":
        challenged_user_id = int(data[2])
        
        if callback_query.from_user.id != challenged_user_id:
            await callback_query.answer("You are not authorized to respond to this challenge!", show_alert=True)
            return

        # Start the game
        await callback_query.message.reply("⚡", quote=True)
        await asyncio.sleep(1)
        
        board = create_board()
        games[(challenger_id, challenged_user_id)] = {'board': board, 'turn': challenger_id, 'challenger_id': challenger_id, 'challenged_user_id': challenged_user_id}
        
        await callback_query.message.reply("Game started! It's your move.", reply_markup=board_to_keyboard(board, challenger_id, challenged_user_id))
        
    elif action == "decline":
        # Notify the challenger that the challenge was declined
        if len(data) > 2:
            challenged_user_id = int(data[2])
            if callback_query.from_user.id != challenged_user_id:
                await callback_query.answer("You are not authorized to respond to this challenge!", show_alert=True)
                return
        
        await client.send_message(challenger_id, "Your request has been declined.")
    
    await callback_query.message.delete()
    

# Handle moves
@app.on_callback_query(filters.regex(r"move"))
async def handle_move(client, callback_query):
    data = callback_query.data.split(":")
    row, col, player1_id, player2_id = map(int, data[1:])
    game = games.get((player1_id, player2_id))

    if not game or callback_query.from_user.id not in (player1_id, player2_id):
        return

    if game['turn'] != callback_query.from_user.id:
        await callback_query.answer("It's not your turn!", show_alert=True)
        return

    board = game['board']
    if board[row][col] != '⬜':
        await callback_query.answer("This spot is already taken!", show_alert=True)
        return

    board[row][col] = '❌' if game['turn'] == player1_id else '⭕'
    winner = check_winner(board)

    if winner:
        if winner == "Draw":
            text = "It's a draw!"
            points = 50
        else:
            text = f"{callback_query.from_user.first_name} wins!"
            points = 100
        
        # Reward points (implementation depends on your system)
        # award_points(callback_query.from_user.id, points)
        
        await callback_query.message.edit_text(text)
        games.pop((player1_id, player2_id), None)
    else:
        game['turn'] = player2_id if game['turn'] == player1_id else player1_id
        await callback_query.message.edit_reply_markup(reply_markup=board_to_keyboard(board, player1_id, player2_id))

    await callback_query.answer()

