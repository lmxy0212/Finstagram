CREATE TABLE Person(
    username VARCHAR(20), 
    password CHAR(64), 
    firstName VARCHAR(20),
    lastName VARCHAR(20),
    bio VARCHAR(1000),
    PRIMARY KEY (username)
);


CREATE TABLE Friendgroup(
    groupOwner VARCHAR(20), 
    groupName VARCHAR(20), 
    description VARCHAR(1000), 
    PRIMARY KEY (groupOwner, groupName),
    FOREIGN KEY (groupOwner) REFERENCES Person(username)
);




CREATE TABLE Photo (
    photoID int AUTO_INCREMENT, 
    postingdate DATETIME,
    filepath VARCHAR(100),
    allFollowers Boolean,
    caption VARCHAR(100),
    photoPoster VARCHAR(20),
    PRIMARY KEY (photoID),
    FOREIGN KEY(photoPoster) REFERENCES Person(username)
);




CREATE TABLE Likes (
    username VARCHAR(20), 
    photoID int, 
    liketime DATETIME, 
    rating int,
    PRIMARY KEY(username, photoID), 
    FOREIGN KEY(username) REFERENCES Person(username),
    FOREIGN KEY(photoID) REFERENCES Photo(photoID)
);  


CREATE TABLE Tagged (
    username VARCHAR(20), 
    photoID int, 
    tagstatus Boolean, 
    PRIMARY KEY(username, photoID), 
    FOREIGN KEY(username) REFERENCES Person(username),
    FOREIGN KEY(photoID)REFERENCES Photo(photoID)
);              


CREATE TABLE SharedWith ( 
    groupOwner VARCHAR(20), 
    groupName VARCHAR(20), 
    photoID int, 
    PRIMARY KEY(groupOwner, groupName, photoID),
    FOREIGN KEY(groupOwner, groupName) REFERENCES Friendgroup(groupOwner, groupName), 
    FOREIGN KEY (photoID) REFERENCES Photo(photoID)
);


CREATE TABLE BelongTo (
    member_username VARCHAR(20), 
    owner_username VARCHAR(20),
    groupName VARCHAR(20), 
    PRIMARY KEY(member_username, owner_username, groupName), 
    FOREIGN KEY(member_username) REFERENCES Person(username),
    FOREIGN KEY(owner_username, groupName)REFERENCES Friendgroup(groupOwner, groupName)
);




CREATE TABLE Follow (
    username_followed VARCHAR(20), 
    username_follower VARCHAR(20), 
    followstatus Boolean,
    PRIMARY KEY(username_followed , username_follower),
    FOREIGN KEY(username_followed) REFERENCES Person(username),
    FOREIGN KEY(username_follower) REFERENCES Person(username)
);