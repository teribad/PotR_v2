import random
import json
import os
import discord
from discord.ext import commands

# Initialize the bot with the Message Content Intent
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable Message Content Intent
bot = commands.Bot(command_prefix='!', intents=intents)

# Original card lists
original_main_cards = ['Black Swan', 'Deep Snow', 'Heavy rains of Autumn', 'Power Overwhelming', 'Power Overwhelming',
                       'Restlessness of Spring', 'Winter Storms', 'Imarins Blessings', 'Flood!', 'Calms of Summer']
original_secondary_cards = ['There be Dragons!', 'There be Dragons!', 'The Misty Mountains Cold', 'The Misty Mountains Cold', 
                            'The Misty Mountains Cold','Bloodlust!', 'Bloodlust!']
original_third_cards = ['Seafarers!', 'Ferry!', 'Crab Infestation!', 'Plague!', 'Merchant Ships!']
original_fourth_cards = ['The End is Nigh!', 'The End is Nigh!', 'Times Up!']

cards_in_play = []

# Filenames
file_names = {
    "main": 'main_card_list_state.json',
    "secondary": 'secondary_card_list_state.json',
    "third": 'third_card_list_state.json',
    "fourth": 'fourth_card_list_state.json',
    "in_play": 'cards_in_play.json',
    "turn": 'turn_state.json'
}

# Utility function for synchronous file I/O
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_json(filename, default_value=None):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value if default_value is not None else []

def remove_files(filenames):
    for file in filenames:
        if os.path.exists(file):
            os.remove(file)

# Load or reset game state
def load_game_state():
    main_cards = load_json(file_names['main'], original_main_cards)
    secondary_cards = load_json(file_names['secondary'], original_secondary_cards)
    third_cards = load_json(file_names['third'], original_third_cards)
    fourth_cards = load_json(file_names['fourth'], original_fourth_cards)
    cards_in_play = load_json(file_names['in_play'], [])
    current_turn = load_json(file_names['turn'], 0)
    return main_cards, secondary_cards, third_cards, fourth_cards, cards_in_play, current_turn

# Draw a card and handle resets
def extract_card(card_list, original_list, list_name, current_turn, forced_card=None):
    notification = ""

    if forced_card:
        card = forced_card
        card_list.remove(card)
    else:
        if not card_list:
            card_list[:] = original_list[:]
        card = random.choice(card_list)
        card_list.remove(card)

    # Handle specific rules for "Black Swan"
    if card == 'Black Swan' and list_name == 'Main':
        card_list[:] = original_list[:]  # Reset the deck
        notification += "Black Swan was drawn! The main deck has been reset to the original set. Drawing another card...\n"
        card = random.choice(card_list)  # Redraw a new card
        card_list.remove(card)
        notification += f"New card drawn after Black Swan: {card}\n"

    # After turn 10, add the card to cards in play
    if current_turn >= 10 and card not in cards_in_play:
        cards_in_play.append(card)

    return card, notification


# Command to draw a card
@bot.command(name='draw')
async def draw(ctx):
    global cards_in_play

    # Load the current state of the game
    main_cards, secondary_cards, third_cards, fourth_cards, cards_in_play, current_turn = load_game_state()

    current_turn += 1
    response = f"Turn {current_turn}:\n"
    
    # Draw from main and secondary decks on the first turn
    if current_turn == 1:
        main_card, main_notification = extract_card(main_cards, original_main_cards, "Main", current_turn, 'Calms of Summer')
        secondary_card, _ = extract_card(secondary_cards, original_secondary_cards, "Secondary", current_turn, 'The Misty Mountains Cold')
        response += f"Main Card: {main_card}\nSecondary Card: {secondary_card}\n"
        response += main_notification
    else:
        main_card, main_notification = extract_card(main_cards, original_main_cards, "Main", current_turn)
        secondary_card, _ = extract_card(secondary_cards, original_secondary_cards, "Secondary", current_turn)
        response += f"Main Card: {main_card}\nSecondary Card: {secondary_card}\n"
        response += main_notification

    # Draw from third and fourth decks after specific turns
    if current_turn >= 5:
        third_card, _ = extract_card(third_cards, original_third_cards, "Third", current_turn)
        response += f"Third Card: {third_card}\n"

    if current_turn >= 10:
        fourth_card, _ = extract_card(fourth_cards, original_fourth_cards, "Fourth", current_turn)
        response += f"Fourth Card: {fourth_card}\n"

        # End the game if "Times Up!" is drawn
        if fourth_card == 'Times Up!':
            response += "Times Up! drawn! The game is over."
            cards_in_play_message = f"Cards in play (after turn 10): {', '.join(cards_in_play)}\n"
            response += cards_in_play_message
            await ctx.send(response)
            await ctx.send("Game over. Thank you for playing!")
            
            # Remove game files and stop further play
            json_files = [file_names['main'], file_names['secondary'], file_names['third'], file_names['fourth'], file_names['in_play'], file_names['turn']]
            remove_files(json_files)
            # Reset card lists and turn
            main_cards, secondary_cards, third_cards, fourth_cards = original_main_cards[:], original_secondary_cards[:], original_third_cards[:], original_fourth_cards[:]
            cards_in_play = []
            current_turn = 0        
            return

        # After turn 10, show cards in play
        cards_in_play_message = f"Cards in play (after turn 10): {', '.join(cards_in_play)}\n"
        response += cards_in_play_message

    # Save current state
    save_json(main_cards, file_names['main'])
    save_json(secondary_cards, file_names['secondary'])
    save_json(third_cards, file_names['third'])
    save_json(fourth_cards, file_names['fourth'])
    save_json(cards_in_play, file_names['in_play'])
    save_json(current_turn, file_names['turn'])

    await ctx.send(response)

# Command to check current status
@bot.command(name='status')
async def status(ctx):
    main_cards, secondary_cards, third_cards, fourth_cards, cards_in_play, current_turn = load_game_state()

    response = (
        f"Main Cards: {main_cards}\n"
        f"Secondary Cards: {secondary_cards}\n"
        f"Third Cards: {third_cards}\n"
        f"Fourth Cards: {fourth_cards}\n"
        f"In play: {cards_in_play}\n"
        f"Turn: {current_turn}\n"
    )
    await ctx.send(response)

# Command to reset the game to its initial state
@bot.command(name='setup')
async def setup(ctx):
    global cards_in_play

    # Reset card lists and turn
    main_cards, secondary_cards, third_cards, fourth_cards = original_main_cards[:], original_secondary_cards[:], original_third_cards[:], original_fourth_cards[:]
    cards_in_play = []
    current_turn = 0

    # Save reset state
    save_json(main_cards, file_names['main'])
    save_json(secondary_cards, file_names['secondary'])
    save_json(third_cards, file_names['third'])
    save_json(fourth_cards, file_names['fourth'])
    save_json(current_turn, file_names['turn'])
    save_json(cards_in_play, file_names['in_play'])

    await ctx.send("Game has been reset to its initial state.")

token = '. . .'
# Run the bot with your token
bot.run(token)
