# JOTS
## Journal of the Session

A webapp for taking fast notes, designed for business, school, and collaboration with groups. 

Currently, JOTS isn't hosted; however, feel free to use JOTS on your own computer, or host it for your own purposes. If you're interested in getting JOTS hosted, contact me via Github or LinkedIn. 

#### Features

- Fast, no hassle entry. 
– Share & Collaborate with others. 
– Select or create entry-specific tags on the fly.
– Sort notes by tags, and organize them into subject-specific articles. 
- Tags & Notes are organized by "Collection."
– Dark-Mode 

#### How to Set up

1. Clone from Github. 
2. Install Dependencies (see requirements.txt)
3. In terminal, paste the following lines after modifying the Secret Django Key (modifying gmail and email password to use the email-related features): 
echo "
SECRET_DJANGO_KEY = 'Generateyourownsecretkey, please'

EMAIL_HOST = 'smtp.gmail.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = 'YourName@gmail.com'

EMAIL_HOST_PASSWORD = 'emailpassword'

EMAIL_USE_TLS = True" > .env

#### WHY?

The note-taking apps out there just don't work the way we need them to, in terms of speed and organization. This app does.
