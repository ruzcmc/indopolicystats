### Scraper

To run the scraper, please install Twint with the following command:

```bash
pip install --user --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint
```

Then install other package as well

```bash
pip install -r requirements.txt
```

Don't forget to copy or rename .env.example to .env then fill all field for database.

After that, you can run scraper.py as usual: `python scraper.py`