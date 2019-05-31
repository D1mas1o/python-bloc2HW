CREATE TABLE NewsCategory
(
NewsCategoryId integer PRIMARY KEY AUTOINCREMENT NOT NULL,
Name text UNIQUE
);

CREATE TABLE UsersCategory
(
NewsCategoryId integer REFERENCES NewsCategory(NewsCategoryId) NOT NULL,
UserId integer REFERENCES Users(UserId) NOT NULL,
CONSTRAINT  uniq_id PRIMARY KEY (NewsCategoryId,UserId)
);

CREATE TABLE Users 
(
UserId integer PRIMARY KEY NOT NULL,
FirstName text,
LastName text
);

CREATE TABLE UserKeyWords
(
UserId integer REFERENCES Users(UserId) NOT NULL,
KeyWordsId integer REFERENCES KeyWords(KeyWordsId) NOT NULL,
CONSTRAINT uniq_keyid PRIMARY KEY (UserId,KeyWordsId)
);

CREATE TABLE KeyWords
(
KeyWordsId integer PRIMARY KEY AUTOINCREMENT NOT NULL,
KeyWord text UNIQUE
);
