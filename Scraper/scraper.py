import twint, datetime, json, os, dotenv, shutil
import pandas as pd
from sqlalchemy import create_engine

# Load environment
dotenv.load_dotenv('./.env')

# Get database data
db_uri = os.getenv("DB_HOST")
db_uname = os.getenv("DB_USERNAME")
db_pwd = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Create engine
engine = create_engine(f"mysql+pymysql://{db_uname}:{db_pwd}@{db_uri}/{db_name}")

"""
	Variabel geo:
	Pulau: Koordinat dan coveragenya
	
	Misal: Aceh dgn titik koordinat 3.382, 96.987, 340km
"""

geo = {
	"Aceh - Sumut sebagian": "3.381823735328289,96.98730468750001,340km",
	"Sumut sebagian - Sumbar - Riau - Sumsel - Lampung sebagian": "-1.8893059628373186,101.77734375000001,535km",
	"Papua dan Papua Barat": "-5.0121497248897136,134.85498033463958,770km",
	"Lampung - Jawa - Kalsel Kalbar Kalteng Kaltim sebagian - NTT - NTB - Bali": "-6.18424616128059,112.50000000000001,820km",
	"Sulawesi - Maluku - Kaltim Kalsel Kaltara - NTT - NTB": "-3.0308121226643703,121.11328125000001,880km",
}

"""
	Variabel keyword:
	Topik: Keyword
	
	Misal: topik KPK butuh keyword KPK, ASN, dan tes.
"""

keyword = {
	"KPK": "KPK ASN (tes OR ujian)",
	"COVID": "(COVID OR corona OR pandemi)",
	"Vaksinasi": "(vaksin OR vaksinasi)",
	"Mudik": "(mudik OR pemudik OR (pulang kampung))",
}

# Buat directory untuk save file
for pulau in geo.keys():
	if os.path.exists(f"./{pulau}") == False:
		os.mkdir(f"./{pulau}")

with open("info_terakhir.json", "r") as f:
	info_terakhir_scrape = json.loads(f.read())

tanggal_terakhir_scrape = info_terakhir_scrape["last_scrape_date"]
tanggal_hari_ini = datetime.date.today().strftime("%d %B %Y")
waktu_scrape = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

for topik, word in keyword.items():
	for pulau, koordinat in geo.items():
		filename = f"{pulau}/{topik} - {tanggal_hari_ini}.csv"

		# Twint search
		c = twint.Config()

		c.Search = word
		c.Limit = 500
		c.Lang = "in"
		c.Geo = koordinat
		c.Since = tanggal_terakhir_scrape
		c.Output = filename
		c.Store_csv = True

		twint.run.Search(c)

		# Use pandas to load downloaded data
		df = pd.read_csv(filename)
		df.set_index('id', inplace=True)
		df.fillna("", inplace=True)

		# Add geo coverage identifier
		df['geo'] = pulau

		# save to database
		df.to_sql(name=topik, con=engine, if_exists="append")

# Delete directory
for pulau in geo.keys():
	if os.path.exists(f"./{pulau}"):
		shutil.rmtree(f"./{pulau}", ignore_errors=True)

with open("info_terakhir.json", "w") as f:
	json.dump({"last_scrape_date": waktu_scrape}, f)