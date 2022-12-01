CREATE TABLE `available_days` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `day` int NOT NULL,
 `start_time` datetime NOT NULL,
 `end_time` datetime NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `fitness_goals` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `goal` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `fitness_level` (
 `level` int NOT NULL,
 `description` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `genders` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `gender` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;

CREATE TABLE `registration` (
 `user_id` int NOT NULL AUTO_INCREMENT,
 `email` varchar(320) NOT NULL,
 `password` tinytext NOT NULL,
 `phone` tinytext NOT NULL,
 `first_name` tinytext NOT NULL,
 `last_name` tinytext NOT NULL,
 `birthdate` datetime NOT NULL,
 `about_you` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
 `gender` tinyint NOT NULL DEFAULT '0',
 `facebook` tinyint NOT NULL,
 `instagram` tinyint NOT NULL,
 `timestamp_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 `timestamp_edited` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `tokens` (
 `token_id` int NOT NULL AUTO_INCREMENT,
 `token` tinytext NOT NULL,
 `user_id` int NOT NULL,
 `auth_level` int NOT NULL,
 PRIMARY KEY (`token_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `user_information` (
 `user_id` int NOT NULL,
 `height` int NOT NULL,
 `weight` int NOT NULL,
 `body_fat_percentage` int NOT NULL,
 `fitness_level` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `specializations` (
 `ID` int NOT NULL AUTO_INCREMENT,
 `user_id` int NOT NULL,
 `specialization` tinytext NOT NULL,
 PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

CREATE TABLE `trainer_information` (
 `user_id` int NOT NULL,
 `social_security_number` tinytext NOT NULL,
 `identification` tinytext CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
 `rate` int NOT NULL,
 `payment_method` tinytext NOT NULL,
 `certification_photo` tinytext CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;