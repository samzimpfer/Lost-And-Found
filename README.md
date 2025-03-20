# Lost-And-Found

DISCLAIMER: This project is currently a work in progress. It is not ready to be deployed, and is more so a proof of concept. The following information documents the current state of the project, and there are many more precautions that must be taken before launching a lost and found app.

DESCRIPTION: This program is a lost and found website intended to be used on college campuses. It stores data on users, items, and claims on lost/found items in an SQLite database which users can interact with via a website built using Flask. To use the website, you must create an account, which will save your personal information to the database. Once you've created an account, you may use the website either to find an item you've lost, or report someone else's lost item that you've found. Users may browse and filter lost items and found items. If a user believes a found item is theirs, they may claim that item. Similarly, if a user believes they’ve found an item that has been reported lost, they may  file a claim on that item. In a future version of this project, there will be a verification system for filing any sort of claim.

DEPENDENCIES:
- Flask
- matplotlib
- numpy
- sqlite3

LEGAL ACKNOWLEDGEMENTS: There are obviously lots of legal precuations that must be taken before launching an app like this. The safety of others' items is the core focus of this app, and there are many implementations of security features that must be completed. As of right now, these would include but are not limited to a verification system for claiming items, rules specifying what types of items can and cannot be posted, a system to remove posts that expose any personal information, and a directory to more appropriate services for returning sensitive items. All of the data currently in the database was obtained using genrative AI. The users in the database do not represent real people. The categories that items may fall into and the current items that are in the database are not necessarily an accurate representation of what data will be allowed to be stored in the database.

FUTURE PLANS: I would ultimately like to transform this website into a mobile app. I plan on redesigning the UI with modern frameworks, likely React and Node.js. I will also store data on a platform other than SQLite in the final version of this project. This will be something I distribute to college campuses, and the first layer of secuirty will be logging in with a valid student ID.

STATUS:
Made new branch to start implementing React within

