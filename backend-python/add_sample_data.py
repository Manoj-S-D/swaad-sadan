"""
Script to add sample subscription plans, catering packages, and event packages
Run this once to populate the database with initial data
"""
import sqlite3
import json
from datetime import datetime

# Connect to database
conn = sqlite3.connect('swaad_sadan.db')
cursor = conn.cursor()

print("Adding sample data to database...")

# ==================== SUBSCRIPTION PLANS ====================
subscription_plans = [
    {
        'name': 'Daily Lunch',
        'description': 'Fresh homemade lunch delivered daily',
        'duration': 30,
        'mealsPerDay': 1,
        'price': 4000,
        'features': json.dumps(['2 Rotis/Rice', '1 Sabzi', 'Dal', 'Salad & Pickle', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Daily Dinner',
        'description': 'Delicious dinner delivered to your doorstep',
        'duration': 30,
        'mealsPerDay': 1,
        'price': 4800,
        'features': json.dumps(['3 Rotis/Rice', '2 Sabzis', 'Dal', 'Raita/Curd', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Breakfast Combo',
        'description': 'Healthy breakfast to start your day',
        'duration': 30,
        'mealsPerDay': 1,
        'price': 2500,
        'features': json.dumps(['Poha/Upma/Idli/Paratha', 'Chutney', 'Tea/Coffee', 'Fresh & Healthy', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Complete Package',
        'description': 'Breakfast + Lunch + Dinner - All meals included',
        'duration': 30,
        'mealsPerDay': 3,
        'price': 10000,
        'features': json.dumps(['All 3 Meals', 'Variety Menu', 'Best Value', 'Premium Quality', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Weekly Lunch Pass',
        'description': 'Perfect for working professionals',
        'duration': 7,
        'mealsPerDay': 1,
        'price': 1200,
        'features': json.dumps(['Monday to Saturday', '2 Rotis/Rice', '1 Sabzi', 'Dal', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Premium 6-Month Pack',
        'description': 'Best value with 6 months commitment',
        'duration': 180,
        'mealsPerDay': 3,
        'price': 55000,
        'features': json.dumps(['All 3 Meals', 'Save ₹5000', 'Premium Menu', 'Priority Service', 'Free Delivery']),
        'isActive': 1
    }
]

print("\nAdding Subscription Plans...")
for plan in subscription_plans:
    cursor.execute('''
        INSERT INTO subscription_plans (name, description, duration, mealsPerDay, price, features, isActive)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (plan['name'], plan['description'], plan['duration'], plan['mealsPerDay'], 
          plan['price'], plan['features'], plan['isActive']))
    print(f"  ✓ {plan['name']} - ₹{plan['price']}")

# ==================== CATERING PACKAGES ====================
catering_packages = [
    {
        'name': 'Wedding Feast Package',
        'description': 'Complete catering solution for grand weddings',
        'type': 'Wedding',
        'minGuests': 100,
        'maxGuests': 500,
        'pricePerPerson': 450,
        'menuItems': json.dumps(['Welcome Drink', 'Paneer Tikka', 'Dal Makhani', 'Butter Naan', 'Veg Biryani', 'Raita', 'Gulab Jamun', 'Ice Cream']),
        'features': json.dumps(['Live Counter', 'Professional Waiters', 'Premium Crockery', 'Decoration Support', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Corporate Lunch Package',
        'description': 'Perfect for office events and meetings',
        'type': 'Corporate',
        'minGuests': 20,
        'maxGuests': 200,
        'pricePerPerson': 300,
        'menuItems': json.dumps(['Veg Pulao', 'Paneer Butter Masala', 'Dal Fry', 'Roti', 'Salad', 'Raita', 'Sweet']),
        'features': json.dumps(['Boxed Meals Available', 'On-time Delivery', 'Professional Setup', 'Disposable Cutlery']),
        'isActive': 1
    },
    {
        'name': 'Birthday Party Package',
        'description': 'Make birthdays special with delicious food',
        'type': 'Birthday',
        'minGuests': 30,
        'maxGuests': 150,
        'pricePerPerson': 350,
        'menuItems': json.dumps(['Pizza', 'Pasta', 'Spring Rolls', 'Manchurian', 'Fried Rice', 'Cake', 'Ice Cream', 'Mocktails']),
        'features': json.dumps(['Kid-Friendly Menu', 'Birthday Cake', 'Decoration Support', 'Party Games Setup']),
        'isActive': 1
    },
    {
        'name': 'Religious Ceremony Package',
        'description': 'Pure vegetarian satvik food for religious events',
        'type': 'Religious',
        'minGuests': 50,
        'maxGuests': 300,
        'pricePerPerson': 280,
        'menuItems': json.dumps(['Puri', 'Chole', 'Aloo Sabzi', 'Rice', 'Kadhi', 'Kheer', 'Prasadam']),
        'features': json.dumps(['No Onion/Garlic', 'Traditional Recipes', 'Prasadam Packing', 'Experienced Staff']),
        'isActive': 1
    },
    {
        'name': 'Naming Ceremony Special',
        'description': 'Traditional food for baby naming ceremony',
        'type': 'Other',
        'minGuests': 50,
        'maxGuests': 200,
        'pricePerPerson': 320,
        'menuItems': json.dumps(['Puri/Paratha', 'Paneer Sabzi', 'Kala Chana', 'Rice', 'Dal', 'Sweet Rice', 'Halwa']),
        'features': json.dumps(['Traditional Menu', 'Prasadam Included', 'Decoration Support', 'Free Delivery']),
        'isActive': 1
    },
    {
        'name': 'Budget-Friendly Package',
        'description': 'Quality food at affordable prices',
        'type': 'Other',
        'minGuests': 50,
        'maxGuests': 300,
        'pricePerPerson': 220,
        'menuItems': json.dumps(['Roti/Rice', 'Dal', 'Seasonal Sabzi', 'Salad', 'Pickle', 'Sweet']),
        'features': json.dumps(['Best Value', 'Quality Food', 'On-time Service', 'Hygienic Preparation']),
        'isActive': 1
    }
]

print("\nAdding Catering Packages...")
for pkg in catering_packages:
    cursor.execute('''
        INSERT INTO catering_packages (name, description, type, minGuests, maxGuests, pricePerPerson, menuItems, features, isActive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pkg['name'], pkg['description'], pkg['type'], pkg['minGuests'], pkg['maxGuests'], 
          pkg['pricePerPerson'], pkg['menuItems'], pkg['features'], pkg['isActive']))
    print(f"  ✓ {pkg['name']} - ₹{pkg['pricePerPerson']}/person ({pkg['minGuests']}-{pkg['maxGuests']} guests)")

# ==================== EVENT PACKAGES ====================
event_packages = [
    {
        'name': 'Baby Birthday Bash',
        'description': 'Complete celebration package for your little one',
        'eventType': 'Birthday',
        'capacity': 100,
        'price': 40000,
        'duration': '4 hours',
        'inclusions': json.dumps(['Food for all guests', 'Special kid-friendly menu', 'Birthday cake', 'Decoration', 'Games & Activities', 'Return gifts']),
        'venue': 'Your venue or ours',
        'isActive': 1
    },
    {
        'name': 'Naming Ceremony Package',
        'description': 'Traditional ceremony with pure veg food',
        'eventType': 'Religious',
        'capacity': 150,
        'price': 50000,
        'duration': '3 hours',
        'inclusions': json.dumps(['Authentic traditional menu', 'Prasadam arrangements', 'Priest coordination', 'Decoration', 'Photography', 'Music system']),
        'venue': 'Customer venue',
        'isActive': 1
    },
    {
        'name': 'Bride to Be Celebration',
        'description': 'Pre-wedding celebration for the bride',
        'eventType': 'Wedding',
        'capacity': 80,
        'price': 45000,
        'duration': '5 hours',
        'inclusions': json.dumps(['Modern & traditional menu', 'Special desserts', 'Decoration', 'DJ/Music', 'Photography', 'Games & Fun activities']),
        'venue': 'Your venue',
        'isActive': 1
    },
    {
        'name': 'Ganesha Homa Package',
        'description': 'Complete pooja catering service',
        'eventType': 'Religious',
        'capacity': 75,
        'price': 25000,
        'duration': '2 hours',
        'inclusions': json.dumps(['Satvik pure veg menu', 'Prasadam included', 'Priest coordination', 'Pooja materials', 'Traditional setup']),
        'venue': 'Home/Temple',
        'isActive': 1
    },
    {
        'name': 'Satyanarayana Pooja',
        'description': 'Traditional pooja with complete arrangements',
        'eventType': 'Religious',
        'capacity': 100,
        'price': 35000,
        'duration': '3 hours',
        'inclusions': json.dumps(['Complete pure veg menu', 'Prasadam packing', 'Priest coordination', 'Pooja setup', 'Traditional decoration']),
        'venue': 'Home',
        'isActive': 1
    },
    {
        'name': 'Engagement Party Package',
        'description': 'Celebrate your engagement in style',
        'eventType': 'Wedding',
        'capacity': 250,
        'price': 150000,
        'duration': '6 hours',
        'inclusions': json.dumps(['Premium menu', 'Welcome drinks', 'Live counters', 'DJ & Music', 'Decoration', 'Photography', 'Stage setup']),
        'venue': 'Banquet hall or outdoor',
        'isActive': 1
    },
    {
        'name': 'Housewarming Ceremony',
        'description': 'Traditional grihapravesh celebration',
        'eventType': 'Religious',
        'capacity': 80,
        'price': 28000,
        'duration': '3 hours',
        'inclusions': json.dumps(['Traditional menu', 'Prasadam', 'Priest coordination', 'Pooja materials', 'Simple decoration']),
        'venue': 'New home',
        'isActive': 1
    },
    {
        'name': 'Anniversary Celebration',
        'description': 'Make your anniversary memorable',
        'eventType': 'Other',
        'capacity': 120,
        'price': 60000,
        'duration': '4 hours',
        'inclusions': json.dumps(['Premium menu', 'Anniversary cake', 'Decoration', 'Music system', 'Photography', 'Special couple table']),
        'venue': 'Your choice',
        'isActive': 1
    }
]

print("\nAdding Event Packages...")
for event in event_packages:
    cursor.execute('''
        INSERT INTO event_packages (name, description, eventType, capacity, price, duration, inclusions, venue, isActive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event['name'], event['description'], event['eventType'], event['capacity'], 
          event['price'], event['duration'], event['inclusions'], event['venue'], event['isActive']))
    print(f"  ✓ {event['name']} - ₹{event['price']} (Up to {event['capacity']} people)")

# Commit changes
conn.commit()
conn.close()

print("\n" + "="*60)
print("✅ Sample data added successfully!")
print("="*60)
print(f"📦 {len(subscription_plans)} Subscription Plans added")
print(f"🍽️  {len(catering_packages)} Catering Packages added")
print(f"🎉 {len(event_packages)} Event Packages added")
print("="*60)
print("\nYou can now view these in the admin panel or on customer pages!")
