# Travel diary
#### Video Demo:  <https://youtu.be/PD4SEm0bQR0>
#### Description:
Project by Nastassia Troska and Karina Pereverzeva

Our project is created to keep all necessary information about your trips in one place. 
It's helpful if you are traveling a lot or just like to keep things organized. 

Register:
The implementation of register is completed in such a way that it allows a user to register for an account via a form.

It requires that a user input a username, implemented as a text field whose name is username, and renders an apology if the user’s input is blank or the username already exists.
Also it requires that a user input a password, implemented as a text field whose name is password, and then that same password again, implemented as a text field whose name is confirmation, renders an apology if either input is blank or the passwords do not match.
Submits the user’s input via POST to /register.
And INSERTs the new user into users, storing a hash of the user’s password, not the password itself.

Log In:
In Log In user provides username and password via form and computer renders an apology if the user’s input is blank or not correct.
It submits the user’s input via POST to home page (/) and saves user's session.

Index:
Index displays links to user's upcoming and past trips and link to page where user can add a new trip.

Add:
Add requires a user input a trip name, town, county and arrive and departure dates. Implemented as a text fields whose names are name, town, country, arrive and departure and renders an apology if the user’s input is blank.
It submits the user’s input via POST to /future.
And inserts new information into trips.

Future:
Future displays an HTML table summarizing all of the future user’s trips, listing row by row each and every trip's information.
Also there is a possibility to edit (submits the user’s input via POST to /edit) trip's information and delete rows (submits the user’s input via POST to /delete).

Edit:
It requires a user input a trip name, town, county and arrive and departure dates and updates information in trips.

Past:
Past displays an HTML table summarizing all of the past user’s trips, listing row by row each and every trip's information.

Baggage:
It requires a user choose a trip's name and input an item.
It submits the user’s input via POST to /baggages.

Baggages:
Ufter choosing a trip's name baggages displays an HTML table summarizing all of the user’s items.
There are options to flag items which are already taken and to delete item (submits the user’s input via POST to /delete_bag).


