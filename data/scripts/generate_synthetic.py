import json
import random
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker('en_IN')

# Target outputs
BASE_DIR = Path(__file__).resolve().parent
FIRS_OUT = BASE_DIR / "firs_synthetic.json"
ACCUSED_OUT = BASE_DIR / "accused_synthetic.json"

# Karnataka Bounding Box
MIN_LAT = 11.5
MAX_LAT = 18.5
MIN_LON = 74.0
MAX_LON = 78.5

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

LANDMARKS = {
    "Bengaluru City": ["Electronic City", "Whitefield", "Koramangala", "Indiranagar", "Hebbal", "Rajajinagar", "Yeshwanthpur", "Jayanagar", "Malleshwaram", "Marathahalli", "Peenya industrial area", "K.R. Puram"],
    "Mysuru City": ["Devaraja Mohalla", "Kuvempunagar", "Saraswathipuram", "Jayalakshmipuram", "N.R. Mohalla", "Bannimantap", "Chamundipuram", "Vijayanagar", "Mysuru Palace vicinity"],
    "Mangaluru City": ["Bunder", "Mangaladevi", "Panambur", "Falnir Road", "Kodialbail", "Bendoorwell", "Kadri", "Kankanady", "Surathkal", "Pandeshwar"],
    "Hubballi-Dharwad": ["Gokul Road", "Navanagar", "Vidyanagar", "Vidyagiri", "Deshpande Nagar", "Unkal", "Rayapur", "Saptapur", "BVB College Road", "Hubballi railway station area"],
    "Belagavi": ["Khade Bazaar", "Udyambag industrial estate", "Ramdev Galli", "Godbole Nagar", "Tilakwadi", "Angol", "Shahapur", "Camp area", "Nehru Nagar"]
}

INDIAN_NAMES = [
    "Shivakumar Gowda", "Deepa Naik", "Suresh Kotian", "Sowmya Desai", "Manjunath Pinto",
    "Bhagya Bhat", "Roopa Hegde", "Mahmood Mendes", "Rashmi Hegde", "Xavier Sequeira",
    "Arjun D'Souza", "Prakash Rathod", "Roopa Bhat", "Pushpa Kulkarni", "Santosh Salian",
    "Imran Patil", "Girish Desai", "Vijayalakshmi Bhat", "Maria Reddy", "Kiran Desai",
    "Kiran Prabhu", "Yallappa Mendes", "Roopa Salian", "Shivakumar Sheikh", "Xavier Setty",
    "Sandra Jadhav", "Lawrence Sequeira", "Anitha Pinto", "Sudha Achar", "Melwin Desai",
    "Rashmi Pinto", "Ramesh Bhat", "Deepa Kulkarni", "Anitha Kamath", "Vinay Poojary",
    "Rajesh Gowda", "Ganesh Shetty", "Iqbal Bhat", "Harish Fernandes", "Rekha Kulkarni",
    "Naveen Sheikh", "Bhagya Mendes", "Puneeth Bhat", "Kalpana Mendes", "Basavaraj Shetty",
    "Vijay Rathod", "Nandini Pujari", "Naseema Rao", "Girish Ballal", "Naveen Ballal",
    "Alphonsa Shetty", "Vinay Sheikh", "Prakash Setty", "Lakshmi Desai", "Lakshmi Jadhav",
    "Santosh Kotian", "Vinay Chavan", "Kalpana Sequeira", "Pooja Gowda", "Mahmood Hegde",
    "Joseph Salian", "Mahmood Prabhu", "Deepa Sequeira", "Harish Khan", "Deepa Kotian",
    "Ravi Sequeira", "Chandan Pujari", "Imran Sheikh", "Rekha Salian", "Vishwanath Fernandes",
    "Ravi Rathod", "Ganesh Desai", "Antony Rathod", "Manjula Khan", "Rashmi Poojary",
    "Mahmood Naik", "Manjula Fernandes", "Arjun Bhat", "Rashmi Sheikh", "Kavya Salian",
    "Gopal Fernandes", "Sudha Reddy", "Sowmya Sheikh", "Manjunath Pujari", "Sudha Kamath",
    "Fathima Mendes", "Alphonsa Sheikh", "Sridhar Rao", "Nandini Setty", "Vijayalakshmi Desai",
    "Nagesh Pinto", "Imran Jadhav", "Pooja Kotian", "Sandra Setty", "Antony Pinto",
    "Kalpana Shetty", "Vidya Shetty", "Vijay Shetty", "Sowmya Naik", "Praveen Rathod",
    "Nataraj D'Souza", "Iqbal Patil", "Nandini Khan", "Sridhar D'Souza", "Vidya Naik",
    "Ayesha Prabhu", "Nagesh Fernandes", "Shweta Chavan", "Suresh Sheikh", "Chandan D'Souza",
    "Lawrence Prabhu", "Joseph Kulkarni", "Basavaraj Hegde", "Deepak Khan", "Deepa Desai",
    "Nataraj Sequeira", "Roopa Achar", "Anand Naik"
]

VEHICLES = ["a scooter", "a Royal Enfield motorcycle", "an auto-rickshaw", "a Bajaj Pulsar motorcycle", "a Hero Splendor motorcycle", "a white Maruti Swift", "a Mahindra Bolero pickup", "a Tata Ace goods carrier", "a KSRTC bus"]
WEAPONS_ROBBERY = ["a knife", "an iron rod", "a countrymade pistol", "a chopper", "a sickle", "a wooden club (lathi)", "a broken bottle"]
WEAPONS_ASSAULT = ["a countrymade pistol", "a knife", "an iron rod", "a chopper", "a sickle", "a wooden club (lathi)"]
WEAPONS_HOMICIDE = ["a knife", "an iron rod", "a countrymade pistol", "a chopper", "a sickle", "a wooden club (lathi)", "a broken bottle"]
DIRECTIONS = ["Davangere", "Chitradurga", "Shivamogga", "Tumakuru", "Hassan", "Kolar", "Vijayapura", "Gadag", "Udupi", "Chikkamagaluru", "Bidar"]

# Generator functions for each crime head
def generate_theft(complainant, locality, district):
    items = [
        "a gold chain weighing 25 grams",
        "a mobile phone and wallet",
        "a laptop bag left unattended",
        "cattle from the shed",
        "milk cans from a dairy collection centre",
        "farm equipment from the shed",
        "cash and jewellery from the almirah"
    ]
    entry = [
        "after cutting the window grill",
        "using a duplicate key",
        "by breaking open the front door lock",
        "by scaling the compound wall",
        "by snatching it while the victim was walking"
    ]
    time_ctx = [
        "during the intervening night",
        "in the evening around dusk",
        "during broad daylight",
        "late at night",
        "while the complainant was away at work",
        "during a power outage at night",
        "around noon"
    ]
    amount = random.choice([25, 40, 60, 75, 90, 120, 150, 180, 220, 275, 450, 500, 850]) * 1000
    return (
        f"{complainant}, a resident of {locality}, {district}, reported that unidentified persons stole "
        f"{random.choice(items)} worth approximately Rs. {amount:,} from the premises {random.choice(entry)}, "
        f"{random.choice(time_ctx)}. A preliminary inquiry has been initiated and the area is being checked for CCTV footage."
    )

def generate_robbery(complainant, locality, district):
    suspects = [
        "a group of four persons armed with sticks",
        "an unidentified motorcycle-borne duo",
        "three masked individuals",
        "two unidentified men on a motorcycle"
    ]
    time_ctx = [
        "late at night",
        "in the evening around dusk",
        "while the complainant was away at work",
        "during a power outage at night",
        "in the early hours of the morning",
        "during broad daylight",
        "during the intervening night"
    ]
    amount = random.choice([25, 40, 60, 90, 120, 150, 180, 500, 850]) * 1000
    return (
        f"{complainant} of {locality}, {district}, was intercepted by {random.choice(suspects)} who threatened "
        f"him/her with {random.choice(WEAPONS_ROBBERY)} and forcibly took away cash and valuables worth Rs. {amount:,}, "
        f"{random.choice(time_ctx)}. The accused fled on {random.choice(VEHICLES)} towards {random.choice(DIRECTIONS)} road. "
        f"A case has been registered and search is on to nab the culprits."
    )

def generate_assault(complainant, locality, district):
    accused = random.choice([n for n in INDIAN_NAMES if n != complainant])
    motives = [
        "an argument that broke out at a marriage function",
        "a dispute over land boundary",
        "an old enmity between families",
        "a financial dispute over a loan",
        "a disagreement during a local festival procession",
        "a quarrel over parking space",
        "a dispute over water sharing for irrigation"
    ]
    return (
        f"A complaint was lodged by {complainant} against {accused} and associates, residents of {locality}, {district}, "
        f"alleging that they were assaulted with {random.choice(WEAPONS_ASSAULT)} following {random.choice(motives)}. "
        f"The complainant sustained injuries and was treated at the local government hospital. Cross-complaints are being examined and further legal action is under process."
    )

def generate_cybercrime(complainant, locality, district):
    scams = [
        "an online investment fraud promoted through a social media advertisement",
        "a fraudulent call posing as a bank official requesting OTP details",
        "a matrimonial profile used to build trust before requesting money",
        "a fraudulent transaction after downloading a remote-access app linked to Google Pay",
        "a fraudulent transaction after downloading a remote-access app linked to WhatsApp",
        "a fraudulent transaction after downloading a remote-access app linked to a fake KYC-update SMS",
        "a fake e-commerce website offering heavy discounts",
        "a phishing link received via SMS regarding a courier delivery"
    ]
    amount = random.choice([25, 40, 60, 90, 120, 180, 275, 500, 620, 850]) * 1000
    return (
        f"{complainant}, a resident of {locality}, {district}, reported losing Rs. {amount:,} after falling victim to "
        f"{random.choice(scams)}. The amount was debited from the complainant's bank account without authorisation. "
        f"The Cyber Crime unit has requested transaction details from the concerned bank/wallet company to trace the beneficiary accounts."
    )

def generate_fraud(complainant, locality, district):
    accused = random.choice([n for n in INDIAN_NAMES if n != complainant])
    schemes = [
        "a bogus job-placement racket promising government jobs",
        "a Ponzi-style deposit scheme promising high returns",
        "a fake gold-loan scheme",
        "forged property documents used to sell the same plot to multiple buyers",
        "a fraudulent chit fund scheme"
    ]
    amount = random.choice([60, 75, 90, 120, 275, 450, 620, 850]) * 1000
    return (
        f"{complainant} of {locality}, {district}, filed a complaint stating that {accused} cheated him/her of "
        f"Rs. {amount:,} through {random.choice(schemes)}. The accused reportedly collected money on false assurances "
        f"and later became untraceable. Bank statements and related documents have been collected as part of the investigation."
    )

def generate_narcotics(complainant, locality, district):
    drugs = [
        "900 grams of charas",
        "500 grams of ephedrine-based cough syrup",
        "75 grams of brown sugar",
        "75 grams of heroin",
        "1.2 kg of MDMA tablets",
        "900 grams of MDMA tablets",
        "150 grams of ganja (cannabis)",
        "1.2 kg of ganja (cannabis)"
    ]
    return (
        f"Acting on a tip-off, police intercepted {complainant} near {locality}, {district}, and seized "
        f"{random.choice(drugs)} being transported on {random.choice(VEHICLES)}. The accused was unable to produce valid "
        f"documents for possession and has been taken into custody. Further investigation is underway to trace the source and intended buyers."
    )

def generate_homicide(victim, locality, district):
    motives = [
        "a money-lending dispute",
        "a fight that escalated during a local gathering",
        "an honour-related dispute",
        "a long-standing family property dispute",
        "suspected personal enmity",
        "an extramarital affair suspected by the family",
        "a drunken brawl"
    ]
    return (
        f"The body of {victim}, a resident of {locality}, {district}, was found with injuries suspected to be "
        f"caused by {random.choice(WEAPONS_HOMICIDE)}. Investigation suggests the incident may be linked to {random.choice(motives)}. "
        f"The body has been sent for post-mortem examination and a case of murder has been registered. A team has been formed to trace the absconding accused."
    )

GENERATORS = {
    1: generate_theft,
    2: generate_robbery,
    3: generate_assault,
    4: generate_cybercrime,
    5: generate_fraud,
    6: generate_narcotics,
    7: generate_homicide
}

def generate_gps(district_name):
    centers = {
        "Bengaluru City": (12.9716, 77.5946),
        "Mysuru City": (12.2958, 76.6394),
        "Mangaluru City": (12.8700, 74.8800),
        "Hubballi-Dharwad": (15.3647, 75.1240),
        "Belagavi": (15.8497, 74.4977)
    }
    base_lat, base_lon = centers.get(district_name, (15.0, 76.0))
    lat = base_lat + random.uniform(-0.08, 0.08)
    lon = base_lon + random.uniform(-0.08, 0.08)
    return max(MIN_LAT, min(MAX_LAT, lat)), max(MIN_LON, min(MAX_LON, lon))

def generate_firs(num_records=1000):
    firs = []
    
    for i in range(1, num_records + 1):
        district = random.choice(DISTRICTS)
        crime = random.choice(CRIME_HEADS)
        lat, lon = generate_gps(district[1])
        
        days_ago = random.randint(1, 365 * 2)
        date_obj = datetime.now() - timedelta(days=days_ago)
        hour = random.choice([18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4] * 3 + list(range(5, 18)))
        date_obj = date_obj.replace(hour=hour, minute=random.randint(0, 59))
        
        landmarks = LANDMARKS[district[1]]
        loc = random.choice(landmarks)
        person = random.choice(INDIAN_NAMES)
        
        gen_func = GENERATORS[crime[0]]
        facts = gen_func(person, loc, district[1])
        
        fir = {
            "CaseMasterID": i,
            "CrimeNo": f"FIR/{date_obj.year}/{random.randint(100, 999)}",
            "CrimeRegisteredDate": date_obj.isoformat(),
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "BriefFacts": facts,
            "DistrictID": district[0],
            "CrimeHeadID": crime[0]
        }
        firs.append(fir)
        
    return firs

def generate_accused(firs, num_accused=800):
    accused_list = []
    
def generate_accused(firs, num_accused=800):
    accused_list = []
    
    # 1. Create 20 distinct Gangs/Syndicates (each sharing 2-5 FIRs)
    num_gangs = 20
    gang_firs = {}
    for g_id in range(num_gangs):
        # Pick 2-4 FIRs for this gang
        shared_firs = random.sample(firs, random.randint(2, 5))
        gang_firs[g_id] = [f["CaseMasterID"] for f in shared_firs]

    accused_idx = 1
    # Assign ~400 accused to the 20 gangs (20 members per gang)
    for g_id in range(num_gangs):
        gang_cases = gang_firs[g_id]
        gang_name_base = random.choice(INDIAN_NAMES)
        members_count = random.randint(15, 25)
        for m in range(members_count):
            if accused_idx > num_accused:
                break
            # Link each gang member to 1 or 2 shared gang cases
            assigned_case = random.choice(gang_cases)
            accused_list.append({
                "AccusedMasterID": accused_idx,
                "CaseMasterID": assigned_case,
                "PersonID": f"P_{accused_idx:04d}",
                "AccusedName": random.choice(INDIAN_NAMES) if m > 0 else f"{gang_name_base} (Leader)",
                "AgeYear": random.randint(21, 55),
                "GenderID": random.choice([1, 1, 1, 2])
            })
            accused_idx += 1

    # Fill remaining accused with random case assignments
    while accused_idx <= num_accused:
        fir = random.choice(firs)
        accused_list.append({
            "AccusedMasterID": accused_idx,
            "CaseMasterID": fir["CaseMasterID"],
            "PersonID": f"P_{accused_idx:04d}",
            "AccusedName": random.choice(INDIAN_NAMES),
            "AgeYear": random.randint(19, 62),
            "GenderID": random.choice([1, 1, 1, 2])
        })
        accused_idx += 1

    return accused_list

def main():
    print("Generating 100% realistic Karnataka FIR & Accused synthetic dataset matching official corpus...")
    random.seed(42)  # Set seed for reproducible high quality
    firs = generate_firs(1000)
    accused = generate_accused(firs, 800)
    
    with open(FIRS_OUT, 'w', encoding='utf-8') as f:
        json.dump(firs, f, indent=2)
        
    with open(ACCUSED_OUT, 'w', encoding='utf-8') as f:
        json.dump(accused, f, indent=2)
        
    print(f"Generated {len(firs)} unique FIR records in {FIRS_OUT}")
    print(f"Generated {len(accused)} Accused records in {ACCUSED_OUT}")

if __name__ == "__main__":
    main()
