import random
import json
import time
import os
import discord
from discord.ext import commands

# Initialize the bot with the Message Content Intent
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable Message Content Intent
bot = commands.Bot(command_prefix='!', intents=intents)

# List of 8 main cards (or elements)
original_main_cards = ['Black Swan','Deep Snow','Heavy rains of Autumn','Power Overwhelming','Power Overwhelming','Restlessness of Spring','Winter Storms','Imarins Blessings','Flood!']

# List of 6 secondary cards
original_secondary_cards = ['There be Dragons!','There be Dragons!','The Misty Mountains Cold','The Misty Mountains Cold','Bloodlust!','Bloodlust!']

# List of 5 third cards (used starting from turn 5)
original_third_cards = ['Seafarers!','Ferry!','Crab Infestation!','Plague!','Pirates!']

# List of 3 fourth cards (used starting from turn 10)
original_fourth_cards = ['The End is Nigh!','The End is Nigh!','Times Up!']

# Track cards that are in play after turn 10
cards_in_play = []

# Function to extract one card at a time and manage resets
def extract_card(card_list, original_list, list_name, current_turn, forced_card=None):
    if forced_card:
        # If a forced card is provided, use it
        extracted_card = forced_card
        card_list.remove(extracted_card)  # Remove the extracted card from the list
    else:
        if not card_list:
            raise ValueError(f"No more cards left in the {list_name} to extract.")
        
        extracted_card = random.choice(card_list)
        
        # If 'Black Swan' is drawn from the main deck, reset the list to the original
        while extracted_card == 'Black Swan' and list_name == "Main":
            print("Extracted Black Swan! Resetting the main deck to the original set.")
            card_list[:] = original_list[:]  # Reset the main deck to the original set
            
            # Draw an additional card from the main list after reset
            extracted_card = random.choice(card_list)
            print("Drawing an additional card from the main deck due to Black Swan being drawn.")
        else:
            card_list.remove(extracted_card)  # Remove the extracted card from the list

    # From turn 10 onward, add the card to the list of cards in play
    if current_turn >= 10 and extracted_card not in cards_in_play:
        cards_in_play.append(extracted_card)

    return extracted_card

# Function to save the current state of the card list to a JSON file
def save_list_to_json(card_list, file_name):
    with open(file_name, 'w') as json_file:
        json.dump(card_list, json_file)
    #print(f"{file_name} updated.")

# Function to load the state of the list from a JSON file
def load_list_from_json(file_name, original_list):
    try:
        with open(file_name, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return original_list[:]  # Return a fresh deck if the file doesn't exist

# Load or initialize the turn counter
def load_turn_from_json():
    try:
        with open(turn_file_name, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return 0  # Start at turn 0 if no file exists

# Function to save the current turn to a file
def save_turn_to_json(turn):
    with open(turn_file_name, 'w') as json_file:
        json.dump(turn, json_file)

# Function to save the current state of the cards in play to a JSON file
def save_in_play_cards(file_name):
    with open(file_name, 'w') as json_file:
        json.dump(cards_in_play, json_file)
    #print(f"Cards in play saved to {file_name}")

# Function to load the cards in play from a JSON file
def load_in_play_cards(file_name):
    try:
        with open(file_name, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return []  # Return empty if the file doesn't exist

def remove_json_files(file_names):
    for file_name in file_names:
        if os.path.exists(file_name):
            os.remove(file_name)
            #print(f"Removed {file_name}.")

# Example usage:
main_file_name = 'main_card_list_state.json'
secondary_file_name = 'secondary_card_list_state.json'
third_file_name = 'third_card_list_state.json'
fourth_file_name = 'fourth_card_list_state.json'
in_play_file_name = 'cards_in_play.json'
turn_file_name = 'turn_state.json'  # File to store the current turn number

# Load card lists from the JSON files
main_cards = load_list_from_json(main_file_name, original_main_cards)
secondary_cards = load_list_from_json(secondary_file_name, original_secondary_cards)
third_cards = load_list_from_json(third_file_name, original_third_cards)
fourth_cards = load_list_from_json(fourth_file_name, original_fourth_cards)

# Load initial turn counter
current_turn = load_turn_from_json()

# Load cards that are in play from the JSON file
cards_in_play = load_in_play_cards(in_play_file_name)

max_turns = 12  # Maximum number of turns allowed
#current_turn = 0

# Command to draw cards
@bot.command(name='draw')
async def draw(ctx):
    global current_turn, main_cards, secondary_cards, third_cards, fourth_cards, cards_in_play
    #time.sleep(1)
    if 1==1:
        current_turn += 1
        print(f"Turn {current_turn}:")
        response = f"Turn {current_turn}:\n"
        if current_turn == 1:
            extracted_main_card = extract_card(main_cards, original_main_cards, "Main", current_turn, 'Restlessness of Spring')
            extracted_secondary_card = extract_card(secondary_cards, original_secondary_cards, "Secondary", current_turn, 'The Misty Mountains Cold')
            response += f"Extracted Main Card: {extracted_main_card}\n"
            response += f"Extracted Secondary Card: {extracted_secondary_card}\n"
        else:
        # Extract from the main list
            extracted_main_card = extract_card(main_cards, original_main_cards, "Main", current_turn)
            print(f"Event Card Drawn is : {extracted_main_card}")
        
        # Save the current state of the main card list to JSON
            save_list_to_json(main_cards, main_file_name)

        # Check if secondary list is empty, and reset if necessary
            if not secondary_cards:
                print("Secondary deck is empty! Resetting it to the original set.")
                secondary_cards = original_secondary_cards[:]  # Reset secondary deck to original set
            # Extract from the secondary list
            extracted_secondary_card = extract_card(secondary_cards, original_secondary_cards, "Secondary", current_turn)
            print(f"Dragon Card Drawn is : {extracted_secondary_card}")

            # Save the current state of the secondary card list to JSON
            save_list_to_json(secondary_cards, secondary_file_name)
            response += f"Extracted Main Card: {extracted_main_card}\n"
            response += f"Extracted Secondary Card: {extracted_secondary_card}\n"
            # Starting from turn 5, extract from the third list
            if current_turn >= 5:
                if not third_cards:
                    print("Third deck is empty! Resetting it to the original set.")
                    third_cards = original_third_cards[:]  # Reset third deck to original set
                # Extract from the third list
                extracted_third_card = extract_card(third_cards, original_third_cards, "Third", current_turn)
                print(f"Sea Card Drawn is: {extracted_third_card}")
                response += f"Extracted Third Card: {extracted_third_card}\n"
                # Save the current state of the third card list to JSON
                save_list_to_json(third_cards, third_file_name)

            # Starting from turn 10, extract from the fourth list
            if current_turn >= 10:
                if not fourth_cards:
                    print("Fourth deck is empty! Resetting it to the original set.")
                    fourth_cards = original_fourth_cards[:]  # Reset fourth deck to original set
                # Extract from the fourth list
                extracted_fourth_card = extract_card(fourth_cards, original_fourth_cards, "Fourth", current_turn)
                response +=f"End Card Drawn is: {extracted_fourth_card}"
                if extracted_fourth_card == 'Times Up!':
                    #print("Times Up! drawn! Ending the game.")#
                    response += "Times Up! drawn! Ending the game."
                    await ctx.send(response)
                    await ctx.send("Game over.")
                    return        
                # Save the current state of the fourth card list to JSON
                save_list_to_json(fourth_cards, fourth_file_name)

            # Save the cards that are in play after each turn
                save_in_play_cards(in_play_file_name)
            
                response += f"Cards in play (after turn 10): {cards_in_play}"
    await ctx.send(response) 

    save_turn_to_json(current_turn)
print(f"Total turns taken: {current_turn}/{max_turns}.")

json_files = [main_file_name, secondary_file_name, third_file_name, fourth_file_name, in_play_file_name, turn_file_name]
remove_json_files(json_files)


@bot.command(name='status')
async def status(ctx):
    response = (
        f"Main Cards: {main_cards}\n"
        f"Secondary Cards: {secondary_cards}\n"
        f"Third Cards: {third_cards}\n"
        f"Fourth Cards: {fourth_cards}\n"
        f"In play: {cards_in_play}\n"
    )
    await ctx.send(response)


@bot.command(name='kill')
async def status(ctx):
    global current_turn, original_main_cards, original_secondary_cards, original_third_cards, original_fourth_cards
    response = (
        f"done"
    )
    json_files = [main_file_name, secondary_file_name, third_file_name, fourth_file_name, in_play_file_name, turn_file_name]
    remove_json_files(json_files)
    current_turn = 0
    await ctx.send(response)


token = 'MTEzMDc4MDI3NDU3MDA1MTY2Nw.Gvl-1P.0w_ZXK1uQQL_n9Qp1r4zUHqMp9ZLHnZR9Q9DyQ'
# Run the bot with your token
bot.run(token)
