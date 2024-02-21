requirements .txt: Contains all the python packages that the project depends on, generate the file using :
pip freeze > requirements.txt



User Registration: User visits register.html → Submits registration form → Is redirected to login.html.

User Login: User logs in via login.html → Authentication process checks if the profile is complete.{

If the profile is incomplete, redirect to profile.html.

If the profile is complete, redirect to another page (e.g., a dashboard or the home page).
}
Profile Completion: User fills in and submits the required information on profile.html → Profile is marked as complete → User is redirected to another part of the application.

Overview:

register.html is solely for signing up new users.

login.html is solely for user authentication.

profile.html is dedicated to collecting and editing profile information.