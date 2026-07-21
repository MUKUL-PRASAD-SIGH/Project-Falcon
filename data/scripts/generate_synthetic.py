import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('en_IN')

# Karnataka Bounding Box
MIN_LAT = 11.5
MAX_LAT = 18.5
MIN_LON = 74.0
MAX_LON = 78.5

# Crime Categories (CrimeHead)
CRIME_HEADS = [
    (1, "Theft"),
    (2, "Robbery"),
    (3, "Assault"),
    (4, "Cybercrime"),
    (5, "Fraud"),
    (6, "Narcotics"),
    (7, "Homicide")
]

DISTRICTS = [
    (1, "Bengaluru City"),
    (2, "Mysuru City"),
    (3, "Mangaluru City"),
    (4, "Hubballi-Dharwad"),
    (5, "Belagavi")
]

def generate_gps(district_name):
    # Slightly bias GPS towards specific city centers based on district name
    centers = {
        "Bengaluru City": (12.9716, 77.5946),
        "Mysuru City": (12.2958, 76.6394),
        "Mangaluru City": (12.8700, 74.8800),
        "Hubballi-Dharwad": (15.3647, 75.1240),
        "Belagavi": (15.8497, 74.4977)
    }
    base_lat, base_lon = centers.get(district_name, (15.0, 76.0))
    lat = base_lat + random.uniform(-0.1, 0.1)
    lon = base_lon + random.uniform(-0.1, 0.1)
    return max(MIN_LAT, min(MAX_LAT, lat)), max(MIN_LON, min(MAX_LON, lon))

def generate_firs(num_records=1000):
    firs = []
    
    for i in range(1, num_records + 1):
        district = random.choice(DISTRICTS)
        crime = random.choice(CRIME_HEADS)
        lat, lon = generate_gps(district[1])
        
        # Temporal clustering (night/weekend bias)
        days_ago = random.randint(1, 365 * 3) # last 3 years
        date_obj = datetime.now() - timedelta(days=days_ago)
        # Bias towards night (18:00 to 04:00)
        hour = random.choice([18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4] * 3 + list(range(5, 18)))
        date_obj = date_obj.replace(hour=hour, minute=random.randint(0, 59))
        
        fir = {
            "CaseMasterID": i,
            "CrimeNo": f"FIR/{date_obj.year}/{random.randint(100, 999)}",
            "CrimeRegisteredDate": date_obj.isoformat(),
            "latitude": lat,
            "longitude": lon,
            "BriefFacts": fake.text(max_nb_chars=200),
            "DistrictID": district[0],
            "CrimeHeadID": crime[0]
        }
        firs.append(fir)
        
    return firs

def generate_accused(firs, num_accused=800):
    accused_list = []
    # Create some repeat offenders (gang network)
    repeat_offenders = []
    for _ in range(50): # 50 repeat offenders
        repeat_offenders.append({
            "AccusedName": fake.name(),
            "AgeYear": random.randint(18, 55),
            "GenderID": random.choice([1, 2]),
        })
        
    for i in range(1, num_accused + 1):
        is_repeat = random.random() < 0.2
        if is_repeat:
            base_profile = random.choice(repeat_offenders)
            name = base_profile["AccusedName"]
            age = base_profile["AgeYear"]
            gender = base_profile["GenderID"]
        else:
            name = fake.name()
            age = random.randint(18, 65)
            gender = random.choice([1, 2])
            
        accused_list.append({
            "AccusedMasterID": i,
            "CaseMasterID": random.choice(firs)["CaseMasterID"],
            "AccusedName": name,
            "AgeYear": age,
            "GenderID": gender,
            "PersonID": f"A{random.randint(1, 3)}"
        })
        
    return accused_list

if __name__ == "__main__":
    print("Generating synthetic FIRs...")
    firs = generate_firs(1000)
    print("Generating synthetic Accused...")
    accused = generate_accused(firs, 1500)
    
    import os
    
    output_dir = os.path.dirname(__file__)
    firs_path = os.path.join(output_dir, 'firs_synthetic.json')
    accused_path = os.path.join(output_dir, 'accused_synthetic.json')
    
    with open(firs_path, 'w') as f:
        json.dump(firs, f, indent=2)
        
    with open(accused_path, 'w') as f:
        json.dump(accused, f, indent=2)
        
    print(f"Generated {len(firs)} FIRs and {len(accused)} Accused records.")
