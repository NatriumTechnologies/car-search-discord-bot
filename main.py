import discord
import os
from dotenv import load_dotenv

import csv
import math

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = "$", intents = intents)


@bot.command(
    name = "ping",
    help = "Pongs back at ya. That's all.",
    brief = "pong"
)
async def finally_work_pls(ctx):
    await ctx.channel.send(f"pong :ping_pong:\nMy latency is **{round(bot.latency*1000)} ms**")



@bot.command()
async def GetCarListing(ctx):
    def check_author(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            return True
        return False
    def check_mile_radius(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            try:
                rad = float(m.content)
                if rad > 0:
                    return True
                return False
            except:
                return False
        return False
    
    def check_zip(m):
        if m.author == ctx.author and m.channel == ctx.channel and len(m.content.strip()) == 5:
            try:
                int(m.content)
                return True
            except:
                return False
        return False
    
    def check_price(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            try:
                int(m.content)
                return True
            except:
                return False
        return False
    
    def check_bodystyle(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            return m.content.lower() in ["coupe", "convertible", "sedan", "hatchback", "wagon", "pickup", "truck", "suv", "mini-van", "offroad", "bus", "van"]
        return False
    
    def check_car_mileage(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            try:
                int(m.content)
                return True
            except:
                return False
        return False
    
    def check_drive_type(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            return m.content.lower() in ["fwd", "rwd", "4wd"]
        return False
    
    async def end_routine(list_of_cars):
        await ctx.send("The list seems to be narrow enough. We found some cars you might like!")
        embed_color = 0xEF8A01
        urls = ""
        for car in list_of_cars:
            urls += car[1]
            urls += "\n"
        embed_to_send = discord.Embed(title = "List of car listings", description=urls, color=embed_color)
        await ctx.send(embed=embed_to_send)
    
    # Build a dictionary to map US zip codes to latitude and longitude
    zip_dict = {}
    with open('us_zip_codes.csv', 'r', newline = '') as f:
        zips = csv.reader(f)
        for row in zips:
            zip_dict[row[0]] = (row[1], row[2])
    
    # Get user's zip code
    await ctx.send("Enter your zip code:")
    zip_code = await bot.wait_for("message", check=check_zip)
    zip_code = zip_code.content
    # Convert this to latitude and longitude
    try:
        lat1, lon1 = zip_dict[zip_code]
        lat1, lon1 = float(lat1), float(lon1)
    except:
       await ctx.send("This ZIP code doesn't exist. Try the command again.")
    
    await ctx.send("Enter a mile radius within which to search:")
    mile_radius = await bot.wait_for("message", check=check_mile_radius)
    mile_radius = float(mile_radius.content)
    
    await ctx.send("What is your price limit?")
    price_limit = await bot.wait_for("message", check=check_price)
    user_price_limit = int(price_limit.content)
    
    await ctx.send("Noted! Working...")
    filtered_once = []
    valid_possible_cars = 0
    with open('vehicles.csv', 'r', newline = '') as f:
        cars = csv.reader(f)
        for car in cars:
            # First filter by price...
            price = car[4]
            try:
                price = int(price)
            except:
                continue
            
            if price > user_price_limit:
                continue
            
            # ...then by distance.
            lat2 = car[23]
            lon2 = car[24]
            # If no geolocation given, skip
            try:
                lat2 = float(lat2)
                lon2 = float(lon2)
            except:
                continue
            
            # This formula calculates distance in miles as-the-crow-flies between two positions given lat/long
            dist_from_car = math.acos(math.sin(math.radians(lat1))*math.sin(math.radians(lat2))
                                      +math.cos(math.radians(lat1))*math.cos(math.radians(lat2))
                                      *math.cos(math.radians(lon2-lon1)))*6371*0.62137119
            if dist_from_car > mile_radius:
                continue
                
            # Else, car is a valid proposition, note it down
            valid_possible_cars += 1
            filtered_once.append(car)
    
    if len(filtered_once) == 0:
        await ctx.send("Sorry, couldn't find any cars with the criteria you specified in your area.")
        return
    elif len(filtered_once) <= 10:
        end_routine(filtered_once)
        return
    
    await ctx.send(f"Found {valid_possible_cars} in your area.")
    
    # Filter by bodystyle.
    await ctx.send("What bodystyle are you looking for? Options are: coupe, convertible, sedan, hatchback, wagon, pickup, truck, SUV, mini-van, offroad, bus, van.")
    bodystyle = await bot.wait_for("message", check=check_bodystyle)
    user_bodystyle = bodystyle.content.lower()
    
    await ctx.send("Noted! Working...")
    filtered_by_bodystyle = []
    for car in filtered_once:
        try:
            if car[17].lower() == user_bodystyle:
                filtered_by_bodystyle.append(car)
        except:
            continue
    
    if len(filtered_by_bodystyle) == 0:
        await ctx.send("Sorry, couldn't find any cars with the criteria you specified in your area.")
        return
    if len(filtered_by_bodystyle) <= 10:
        await end_routine(filtered_by_bodystyle)
        return
    await ctx.send(f"Found {len(filtered_by_bodystyle)} {user_bodystyle}s in your area.")
    
    # Filter by mileage.
    await ctx.send("What's your maximum number of miles on the car?")
    car_mileage = await bot.wait_for("message", check=check_car_mileage)
    user_car_mileage = int(car_mileage.content)
    
    await ctx.send("Noted! Working...")
    filtered_by_mileage = []
    for car in filtered_by_bodystyle:
        try:
            if int(car[11]) <= user_car_mileage:
                filtered_by_mileage.append(car)
        except:
            continue
    
    if len(filtered_by_mileage) == 0:
        await ctx.send("Sorry, couldn't find any cars with the criteria you specified in your area.")
        return
    if len(filtered_by_mileage) <= 10:
        await end_routine(filtered_by_mileage)
        return
    await ctx.send(f"Found {len(filtered_by_mileage)} autos with that mileage in your area.")
    
    # Filter by drive type.
    await ctx.send("What drive type should it have? Options are: fwd, rwd, 4wd.")
    drive_type = await bot.wait_for("message", check=check_drive_type)
    user_drive_type = drive_type.content.lower()
    
    await ctx.send("Noted! Working...")
    filtered_by_drive = []
    for car in filtered_by_mileage:
        try:
            if car[15] <= user_drive_type:
                filtered_by_drive.append(car)
        except:
            continue
    
    if len(filtered_by_drive) == 0:
        await ctx.send("Sorry, couldn't find any cars with the criteria you specified in your area.")
        return
    if len(filtered_by_drive) <= 10:
        await end_routine(filtered_by_mileage)
        return
    await ctx.send("Done!")
    
    # We're done. If there are still too many results, send the closest 10 cars to the user. 
    closest_car_index = []
    for i, car in enumerate(filtered_by_drive):
        lat2 = float(car[23])
        lon2 = float(car[24])
        dist_from_car = math.acos(math.sin(math.radians(lat1))*math.sin(math.radians(lat2))
                                      +math.cos(math.radians(lat1))*math.cos(math.radians(lat2))
                                      *math.cos(math.radians(lon2-lon1)))*6371*0.62137119
        closest_car_index.append((dist_from_car, i))
    # Sort the closest cars
    closest_car_index.sort(key = lambda x: x[0])
    # Assemble list of cars from this indexer
    closest_ten_cars = [filtered_by_drive[x[1]] for x in closest_car_index][:10]
    await end_routine(closest_ten_cars)

bot.run(DISCORD_TOKEN)